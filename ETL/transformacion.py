
import pandas as pd
from datetime import datetime


# ==========================================
# CONFIGURACION DE FECHAS
# ==========================================

COLUMNAS_FECHA = {
    "Categorias": [],
    "Clientes": ["FechaRegistro"],
    "Empleados": ["FechaContratacion"],
    "Productos": [],
    "Ventas": ["FechaVenta"],
    "DetallesVenta": [],
    "Pagos": ["FechaPago"],
    "MovimientosInventario": ["FechaMovimiento"]
}


# ==========================================
# PROCESO DE TRANSFORMACION
# ==========================================

def transformar_datos(datos):

    datos_limpios = {}
    auditoria_calidad = []

    fecha_carga = datetime.now()

    print("\n================================")
    print(" INICIANDO CLEAN / VALIDATED")
    print("================================")

    for tabla, df_original in datos.items():

        try:

            df = df_original.copy()

            registros_iniciales = len(df)

            # 1. ELIMINAR DUPLICADOS
            df = df.drop_duplicates()

            duplicados = registros_iniciales - len(df)

            # 2. LIMPIAR ESPACIOS EN COLUMNAS DE TEXTO
            columnas_texto = df.select_dtypes(
                include=["object", "string"]
            ).columns

            for columna in columnas_texto:

                df[columna] = df[columna].apply(
                    lambda valor: valor.strip()
                    if isinstance(valor, str)
                    else valor
                )

                df[columna] = df[columna].replace(
                    r"^\s*$",
                    pd.NA,
                    regex=True
                )

            # 3. VALIDAR Y CONVERTIR FECHAS
            fechas_invalidas = 0

            for columna in COLUMNAS_FECHA.get(tabla, []):

                if columna in df.columns:

                    valores_originales = df[columna]

                    fechas_convertidas = pd.to_datetime(
                        valores_originales,
                        errors="coerce"
                    )

                    fechas_invalidas += int(
                        (
                            valores_originales.notna()
                            & fechas_convertidas.isna()
                        ).sum()
                    )

                    df[columna] = fechas_convertidas

            # 4. CONTABILIZAR VALORES NULOS
            total_nulos = int(
                df.isna().sum().sum()
            )

            # 5. AGREGAR FECHA DE CARGA
            df["FechaCarga"] = fecha_carga

            # Guardar DataFrame limpio
            datos_limpios[tabla] = df

            # 6. REGISTRAR AUDITORIA
            auditoria_calidad.append({
                "Tabla": tabla,
                "FechaAuditoria": fecha_carga,
                "RegistrosIniciales": registros_iniciales,
                "DuplicadosEliminados": duplicados,
                "FechasInvalidas": fechas_invalidas,
                "ValoresNulos": total_nulos,
                "RegistrosFinales": len(df),
                "Estado": "EXITOSO",
                "Mensaje": "Transformacion completada"
            })

            print(f"\nTabla: {tabla}")
            print(f"Registros iniciales: {registros_iniciales}")
            print(f"Duplicados eliminados: {duplicados}")
            print(f"Fechas invalidas: {fechas_invalidas}")
            print(f"Valores nulos: {total_nulos}")
            print(f"Registros finales: {len(df)}")

        except Exception as error:

            auditoria_calidad.append({
                "Tabla": tabla,
                "FechaAuditoria": fecha_carga,
                "RegistrosIniciales": len(df_original),
                "DuplicadosEliminados": 0,
                "FechasInvalidas": 0,
                "ValoresNulos": 0,
                "RegistrosFinales": 0,
                "Estado": "ERROR",
                "Mensaje": str(error)
            })

            print(f"\nERROR EN TRANSFORMACION: {tabla}")
            print(error)

            raise

    print("\n================================")
    print(" TRANSFORMACION COMPLETADA")
    print("================================")

    return datos_limpios, auditoria_calidad


# ==========================================
# EJECUCION INDEPENDIENTE
# ==========================================

if __name__ == "__main__":

    from extraccion import extraer_datos

    datos, auditoria = extraer_datos()

    errores = [
        registro for registro in auditoria
        if registro["estado"] != "EXITOSO"
    ]

    if errores:
        raise Exception(
            "Existen errores en la extraccion."
        )

    datos_limpios, auditoria_calidad = transformar_datos(datos)

    print("\nTablas transformadas:", len(datos_limpios))
    print("Registros de auditoria:", len(auditoria_calidad))
