
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Configuración de SQL Server
SERVIDOR = r"LAPTOP-U5VB9OIS\SQLEXPRESS"
BASE_DATOS = "EmpresaComercial"
DRIVER = "ODBC Driver 17 for SQL Server"

# Cadena de conexión
cadena_conexion = quote_plus(
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVIDOR};"
    f"DATABASE={BASE_DATOS};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

# Crear conexión
engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={cadena_conexion}",
    pool_pre_ping=True
)

print("Configuración de conexión creada correctamente.")
