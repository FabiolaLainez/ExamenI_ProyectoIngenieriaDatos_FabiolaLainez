
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

SERVIDOR = r"LAPTOP-U5VB9OIS\SQLEXPRESS"
BASE_DATOS = "EmpresaComercial"
CONTROLADOR = "ODBC Driver 17 for SQL Server"

cadena_conexion = (
    f"DRIVER={{{CONTROLADOR}}};"
    f"SERVER={SERVIDOR};"
    f"DATABASE={BASE_DATOS};"
    "Trusted_Connection=yes;"
)

conexion = create_engine(
    "mssql+pyodbc:///?odbc_connect="
    + quote_plus(cadena_conexion)
)

try:
    with conexion.connect() as conn:
        resultado = conn.execute(
            text("SELECT DB_NAME()")
        ).scalar()

        print("CONEXION EXITOSA")
        print("Base de datos:", resultado)

except Exception as error:
    print("ERROR DE CONEXION:")
    print(error)
