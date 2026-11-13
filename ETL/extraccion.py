
import pandas as pd
from sqlalchemy import text
from datetime import datetime
from time import time

from conexion import conexion


# ==========================================
# CONFIGURACION DE TABLAS
# ==========================================

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


# ==========================================
# PROCESO DE EXTRACCION
# ==========================================

def extraer_datos():

    datos = {}
    auditoria = []

    fecha_inicio = datetime.now()

    print("\n================================")
    print(" INICIANDO EXTRACCION DE DATOS")
    print("================================")

    for tabla in TABLAS:

        inicio = time()

        registro = {
            "tabla": tabla,
            "fecha_extraccion": datetime.now(),
            "registros": 0,
            "estado": "ERROR",
            "mensaje": None,
            "duracion_segundos": 0
        }

        try:

            consulta = text(
                f"SELECT * FROM dbo.[{tabla}]"
            )

            df = pd.read_sql_query(
                consulta,
                conexion
            )

            datos[tabla] = df

            registro["registros"] = len(df)
            registro["estado"] = "EXITOSO"
            registro["mensaje"] = "Extraccion completada"

            print(f"\nTabla: {tabla}")
            print(f"Registros extraidos: {len(df)}")
            print(f"Columnas: {list(df.columns)}")

        except Exception as error:

            registro["mensaje"] = str(error)

            print(f"\nERROR EN TABLA: {tabla}")
            print(error)

        finally:

            registro["duracion_segundos"] = round(
                time() - inicio, 2
            )

            auditoria.append(registro)

    fecha_fin = datetime.now()

    print("\n================================")
    print(" RESUMEN DE EXTRACCION")
    print("================================")

    print("Inicio:", fecha_inicio)
    print("Fin:", fecha_fin)

    total_registros = sum(
        len(df) for df in datos.values()
    )

    print("Total de registros:", total_registros)

    exitosas = sum(
        1 for a in auditoria
        if a["estado"] == "EXITOSO"
    )

    fallidas = len(auditoria) - exitosas

    print("Tablas exitosas:", exitosas)
    print("Tablas fallidas:", fallidas)

    print("\nEXTRACCION FINALIZADA")

    return datos, auditoria


# ==========================================
# EJECUCION INDEPENDIENTE
# ==========================================

if __name__ == "__main__":

    datos, auditoria = extraer_datos()
