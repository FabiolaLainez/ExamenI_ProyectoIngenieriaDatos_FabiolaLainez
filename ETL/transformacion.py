
import pandas as pd
from datetime import datetime

# ==========================================
# CONFIGURACION DE COLUMNAS DE FECHAS
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

    fecha_procesamiento = datetime.now()

    print("\n================================")
    print(" INICIANDO TRANSFORMACION")
    print("================================")

    for tabla, df_original in datos.items():

        try:

            # Trabajar sobre una copia
            df = df_original.copy()

            registros_iniciales = len(df)

            # 1. Eliminar duplicados exactos
            df = df.drop_duplicates()

            duplicados = registros_iniciales - len(df)

            # 2. Limpiar columnas de texto
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

            # 3. Validar columnas de fechas
            fechas_invalidas = 0

            for columna in COLUMNAS_FECHA.get(tabla, []):

                if columna not in df.columns:
                    print(
                        f"ADVERTENCIA: No existe "
                        f"{columna} en {tabla}"
                    )
                    continue

                valores_originales = df[columna]

                fechas_convertidas = pd.to_datetime(
                    valores_originales,
                    errors="coerce"
                )

                invalidas = (
                    valores_originales.notna()
                    & fechas_convertidas.isna()
                )

                fechas_invalidas += int(invalidas.sum())

                df[columna] = fechas_convertidas

            # 4. Contabilizar valores nulos
            total_nulos = int(
                df.isna().sum().sum()
            )

            # 5. Agregar fecha de procesamiento
            df["FechaCarga"] = fecha_procesamiento

            # 6. Guardar DataFrame transformado
            datos_limpios[tabla] = df

            # 7. Mostrar resultados
            print(f"\nTabla: {tabla}")
            print(f"Registros iniciales: {registros_iniciales}")
            print(f"Duplicados eliminados: {duplicados}")
            print(f"Fechas invalidas: {fechas_invalidas}")
            print(f"Valores nulos: {total_nulos}")
            print(f"Registros finales: {len(df)}")

        except Exception as error:

            print(f"\nERROR TRANSFORMANDO TABLA: {tabla}")
            print(error)

            raise

    print("\n================================")
    print(" TRANSFORMACION COMPLETADA")
    print("================================")

    return datos_limpios


# ==========================================
# EJECUCION INDEPENDIENTE
# ==========================================

if __name__ == "__main__":

    from extraccion import extraer_datos

    resultado_extraccion = extraer_datos()

    # Compatibilidad con la extraccion que devuelve
    # (datos, auditoria) o solamente datos.

    if isinstance(resultado_extraccion, tuple):
        datos, auditoria_extraccion = resultado_extraccion
    else:
        datos = resultado_extraccion

    datos_limpios = transformar_datos(datos)
