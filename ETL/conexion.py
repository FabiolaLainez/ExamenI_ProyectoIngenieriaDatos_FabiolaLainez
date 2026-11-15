
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


# =====================================================
# CONFIGURACION DE SQL SERVER
# =====================================================

SERVIDOR = r"LAPTOP-U5VB9OIS\SQLEXPRESS"
BASE_DATOS = "EmpresaComercial"
DRIVER = "ODBC Driver 17 for SQL Server"


# =====================================================
# CADENA DE CONEXION
# =====================================================

cadena_conexion = quote_plus(
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVIDOR};"
    f"DATABASE={BASE_DATOS};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


# =====================================================
# CREAR ENGINE
# =====================================================

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={cadena_conexion}",
    pool_pre_ping=True,
    fast_executemany=True
)


# =====================================================
# PROBAR CONEXION
# =====================================================

def probar_conexion():

    try:

        with engine.connect() as conexion:

            resultado = conexion.execute(
                text("""
                    SELECT
                        DB_NAME() AS BaseDatos,
                        @@SERVERNAME AS Servidor
                """)
            )

            datos = resultado.fetchone()

            print("=" * 50)
            print("CONEXION EXITOSA")
            print("=" * 50)

            print(f"Servidor: {datos.Servidor}")
            print(f"Base de datos: {datos.BaseDatos}")

            return True

    except Exception as error:

        print("ERROR DE CONEXION")
        print(error)

        return False


# =====================================================
# CERRAR CONEXION
# =====================================================

def cerrar_conexion():

    engine.dispose()
    print("Conexion cerrada correctamente.")


# =====================================================
# EJECUCION DIRECTA
# =====================================================

if __name__ == "__main__":
    probar_conexion()
