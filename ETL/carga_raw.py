
from conexion import conexion


# ==========================================
# CONFIGURACION
# ==========================================

ESQUEMA = "Raw"

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
# CREAR ESQUEMA RAW
# ==========================================

def crear_esquema_raw():

    with conexion.begin() as conn:

        conn.exec_driver_sql("""
            IF NOT EXISTS (
                SELECT 1
                FROM sys.schemas
                WHERE name = 'Raw'
            )
            BEGIN
                EXEC('CREATE SCHEMA Raw');
            END;
        """)

    print("\nEsquema Raw verificado correctamente.")


# ==========================================
# CARGA DE DATOS RAW
# ==========================================

def cargar_raw(datos):

    print("\n================================")
    print(" INICIANDO CARGA LANDING / RAW")
    print("================================")

    # Verificar que recibimos un diccionario
    if not isinstance(datos, dict):
        raise TypeError(
            "La carga Raw requiere un diccionario de DataFrames."
        )

    # Crear esquema
    crear_esquema_raw()

    total_registros = 0

    for tabla in TABLAS:

        if tabla not in datos:
            raise ValueError(
                f"No se encontraron datos para la tabla {tabla}."
            )

        df = datos[tabla]

        try:

            # Cargar datos originales sin transformaciones
            df.to_sql(
                name=tabla,
                con=conexion,
                schema=ESQUEMA,
                if_exists="replace",
                index=False,
                chunksize=500
            )

            registros = len(df)
            total_registros += registros

            print(f"\nTabla cargada: {ESQUEMA}.{tabla}")
            print(f"Registros: {registros}")

        except Exception as error:

            print(f"\nERROR AL CARGAR: {tabla}")
            print(error)

            raise

    print("\n================================")
    print(" CARGA RAW COMPLETADA")
    print("================================")

    print("Tablas cargadas:", len(TABLAS))
    print("Total de registros:", total_registros)


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
            "No se puede cargar Raw: existen errores de extracción."
        )

    cargar_raw(datos)
