
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

from datetime import timedelta
from sqlalchemy import text
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Permite importar conexion.py desde backend
RUTA_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(RUTA_BACKEND)

from conexion import engine


# =====================================================
# CONFIGURACION
# =====================================================

CARPETA_ML = os.path.dirname(os.path.abspath(__file__))

RUTA_MODELO = os.path.join(CARPETA_ML, "modelo_ventas.pkl")
RUTA_METRICAS = os.path.join(CARPETA_ML, "metricas.json")
RUTA_PREDICCIONES = os.path.join(CARPETA_ML, "predicciones_prueba.csv")
RUTA_PRONOSTICO = os.path.join(CARPETA_ML, "pronostico_7_dias.csv")

VARIABLES = [
    "venta_lag_1",
    "venta_lag_7",
    "venta_lag_14",
    "venta_lag_30",
    "promedio_7",
    "promedio_14",
    "promedio_30",
    "dia_semana",
    "mes",
    "dia_mes"
]


# =====================================================
# 1. EXTRAER DATOS DEL DATA WAREHOUSE
# =====================================================

def extraer_datos():

    consulta = """
        SELECT
            DF.Fecha,
            SUM(FV.Subtotal) AS VentasTotales
        FROM DW.FactVentas FV
        INNER JOIN DW.DimFecha DF
            ON FV.FechaKey = DF.FechaKey
        GROUP BY DF.Fecha
        ORDER BY DF.Fecha;
    """

    with engine.connect() as conexion:
        df = pd.read_sql_query(text(consulta), conexion)

    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["VentasTotales"] = pd.to_numeric(
        df["VentasTotales"], errors="coerce"
    )

    df = df.dropna().sort_values("Fecha").reset_index(drop=True)

    # Verificar que no existan fechas duplicadas
    if df["Fecha"].duplicated().any():
        raise ValueError("Existen fechas duplicadas en los datos.")

    # Completar el calendario diario
    calendario = pd.date_range(
        start=df["Fecha"].min(),
        end=df["Fecha"].max(),
        freq="D"
    )

    df = (
        df.set_index("Fecha")
        .reindex(calendario, fill_value=0)
        .rename_axis("Fecha")
        .reset_index()
    )

    if len(df) < 60:
        raise ValueError("No hay suficientes días para entrenar el modelo.")

    if (df["VentasTotales"] < 0).any():
        raise ValueError("Se encontraron ventas negativas. Revisar los datos.")

    print("\nDATOS EXTRAIDOS")
    print("---------------------------")
    print("Cantidad de días:", len(df))
    print("Primera fecha:", df["Fecha"].min().date())
    print("Última fecha:", df["Fecha"].max().date())
    print("Ventas acumuladas:", df["VentasTotales"].sum())

    return df


# =====================================================
# 2. CONSTRUIR VARIABLES PREDICTORAS
# =====================================================

def construir_variables(historial, fecha):

    historial = np.array(historial, dtype=float)

    return {
        "venta_lag_1": historial[-1],
        "venta_lag_7": historial[-7],
        "venta_lag_14": historial[-14],
        "venta_lag_30": historial[-30],
        "promedio_7": np.mean(historial[-7:]),
        "promedio_14": np.mean(historial[-14:]),
        "promedio_30": np.mean(historial[-30:]),
        "dia_semana": fecha.day_of_week,
        "mes": fecha.month,
        "dia_mes": fecha.day
    }


def preparar_dataset(df):

    valores = df["VentasTotales"].tolist()
    fechas = df["Fecha"].tolist()

    filas = []

    for i in range(30, len(df)):

        variables = construir_variables(
            valores[:i],
            fechas[i]
        )

        variables["objetivo"] = valores[i]
        variables["fecha"] = fechas[i]

        filas.append(variables)

    dataset = pd.DataFrame(filas)

    return dataset


# =====================================================
# 3. ENTRENAMIENTO Y PRUEBA CRONOLOGICA
# =====================================================

def entrenar_modelo():

    df = extraer_datos()
    dataset = preparar_dataset(df)

    X = dataset[VARIABLES]
    y = dataset["objetivo"]

    # Separación cronológica 80/20
    punto_corte = int(len(dataset) * 0.80)

    X_train = X.iloc[:punto_corte]
    X_test = X.iloc[punto_corte:]

    y_train = y.iloc[:punto_corte]
    y_test = y.iloc[punto_corte:]

    fechas_test = dataset["fecha"].iloc[punto_corte:]

    print("\nDIVISION DE DATOS")
    print("---------------------------")
    print("Entrenamiento:", len(X_train))
    print("Prueba:", len(X_test))

    # Modelo Random Forest
    modelo = RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    modelo.fit(X_train, y_train)

    # Predicciones de prueba
    predicciones = modelo.predict(X_test)
    predicciones = np.maximum(predicciones, 0)

    # Baseline: repetir el valor de hace 7 días
    baseline = dataset["venta_lag_7"].iloc[punto_corte:].values

    # Métricas del modelo
    mae = mean_absolute_error(y_test, predicciones)

    rmse = np.sqrt(
        mean_squared_error(y_test, predicciones)
    )

    # MAPE: se excluyen días con ventas reales iguales a cero
    reales = y_test.to_numpy()
    mascara = reales != 0

    if mascara.any():
        mape = np.mean(
            np.abs(
                (reales[mascara] - predicciones[mascara])
                / reales[mascara]
            )
        ) * 100
    else:
        mape = None

    # Métricas baseline
    mae_baseline = mean_absolute_error(y_test, baseline)

    rmse_baseline = np.sqrt(
        mean_squared_error(y_test, baseline)
    )

    if mascara.any():
        mape_baseline = np.mean(
            np.abs(
                (reales[mascara] - baseline[mascara])
                / reales[mascara]
            )
        ) * 100
    else:
        mape_baseline = None

    metricas = {
        "modelo": "RandomForestRegressor",
        "version": "1.0",
        "fecha_entrenamiento": pd.Timestamp.now().isoformat(),
        "dias_historicos": len(df),
        "registros_entrenamiento": len(X_train),
        "registros_prueba": len(X_test),
        "MAE": float(mae),
        "RMSE": float(rmse),
        "MAPE": float(mape) if mape is not None else None,
        "baseline_MAE": float(mae_baseline),
        "baseline_RMSE": float(rmse_baseline),
        "baseline_MAPE": float(mape_baseline)
        if mape_baseline is not None else None
    }

    # Guardar predicciones de prueba
    resultados = pd.DataFrame({
        "Fecha": fechas_test,
        "VentasReales": y_test.values,
        "Prediccion": predicciones,
        "Baseline": baseline
    })

    resultados.to_csv(
        RUTA_PREDICCIONES,
        index=False,
        encoding="utf-8-sig"
    )

    # Guardar el modelo y sus variables
    joblib.dump(
        {
            "modelo": modelo,
            "variables": VARIABLES
        },
        RUTA_MODELO
    )

    with open(RUTA_METRICAS, "w", encoding="utf-8") as archivo:
        json.dump(metricas, archivo, indent=4, ensure_ascii=False)

    print("\nRESULTADOS DEL MODELO")
    print("---------------------------")
    print(f"MAE: {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"MAPE: {mape:.2f}%" if mape is not None else "MAPE: No disponible")

    print("\nRESULTADOS DEL BASELINE")
    print("---------------------------")
    print(f"MAE: {mae_baseline:.2f}")
    print(f"RMSE: {rmse_baseline:.2f}")

    print("\nModelo guardado correctamente.")


# =====================================================
# 4. PRONOSTICO DE LOS PROXIMOS 7 DIAS
# =====================================================

def generar_pronostico():

    df = extraer_datos()

    paquete = joblib.load(RUTA_MODELO)
    modelo = paquete["modelo"]

    historial = df["VentasTotales"].tolist()
    ultima_fecha = df["Fecha"].max()

    pronosticos = []

    for dia in range(1, 8):

        fecha_futura = ultima_fecha + timedelta(days=dia)

        variables = construir_variables(
            historial,
            fecha_futura
        )

        entrada = pd.DataFrame([variables])[VARIABLES]

        prediccion = float(modelo.predict(entrada)[0])
        prediccion = max(0, prediccion)

        pronosticos.append({
            "Fecha": fecha_futura.strftime("%Y-%m-%d"),
            "VentasPronosticadas": round(prediccion, 2)
        })

        # Predicción recursiva
        historial.append(prediccion)

    resultado = pd.DataFrame(pronosticos)

    resultado.to_csv(
        RUTA_PRONOSTICO,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nPRONOSTICO DE LOS PROXIMOS 7 DIAS")
    print(resultado.to_string(index=False))


# =====================================================
# EJECUCION
# =====================================================

if __name__ == "__main__":

    entrenar_modelo()
    generar_pronostico()
