
import pandas as pd
from datetime import datetime

# Columnas que contienen fechas en cada tabla
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


def transformar_datos(datos):

    datos_limpios = {}

    print("\n================================")
    print(" INICIANDO TRANSFORMACION")
    print("================================")

    for tabla, df_original in datos.items():

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

            # Convertir textos vacíos en valores nulos
            df[columna] = df[columna].replace(
                r"^\s*$",
                pd.NA,
                regex=True
            )

        # 3. Validar columnas de fechas
        fechas_invalidas = 0

        for columna in COLUMNAS_FECHA.get(tabla, []):

            valores_originales = df[columna]

            fechas_convertidas = pd.to_datetime(
                valores_originales,
                errors="coerce"
            )

            fechas_invalidas += (
                valores_originales.notna()
                & fechas_convertidas.isna()
            ).sum()

            df[columna] = fechas_convertidas

        # 4. Contar valores nulos
        total_nulos = int(df.isna().sum().sum())

        # 5. Agregar fecha de procesamiento
        df["FechaCarga"] = datetime.now()

        # 6. Guardar DataFrame transformado
        datos_limpios[tabla] = df

        # Mostrar resultados
        print(f"\nTabla: {tabla}")
        print(f"Registros iniciales: {registros_iniciales}")
        print(f"Duplicados eliminados: {duplicados}")
        print(f"Fechas invalidas: {fechas_invalidas}")
        print(f"Valores nulos: {total_nulos}")
        print(f"Registros finales: {len(df)}")

    print("\n================================")
    print(" TRANSFORMACION COMPLETADA")
    print("================================")

    return datos_limpios


if __name__ == "__main__":

    from extraccion import extraer_datos

    # Extraer datos desde SQL Server
    datos = extraer_datos()

    # Transformar los datos
    datos_limpios = transformar_datos(datos)
