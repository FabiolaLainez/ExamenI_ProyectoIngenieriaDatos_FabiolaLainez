
import pandas as pd
from sqlalchemy import create_engine, text
from conexion import conexion

# Tablas de nuestra base de datos
TABLAS = [
    "Categorias",
    "Clientes",
    "Empleados",
    "Productos",
    "Ventas",
    "DetallesVenta",
    "Pagos",
    "MovimientosInventario"
]

def extraer_datos():

    datos = {}

    print("\n================================")
    print(" INICIANDO EXTRACCION DE DATOS")
    print("================================")

    for tabla in TABLAS:

        consulta = text(f"SELECT * FROM dbo.[{tabla}]")

        df = pd.read_sql_query(
            consulta,
            conexion
        )

        datos[tabla] = df

        print(f"\nTabla: {tabla}")
        print(f"Registros extraidos: {len(df)}")
        print(f"Columnas: {list(df.columns)}")

    print("\nEXTRACCION COMPLETADA")

    return datos


if __name__ == "__main__":
    datos = extraer_datos()
