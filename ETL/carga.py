
from sqlalchemy import text
from conexion import conexion


def cargar_datos(datos):

    print("\n================================")
    print(" INICIANDO CARGA A STAGING")
    print("================================")

    # Crear esquema Staging
    with conexion.begin() as conn:

        conn.execute(text("""
            IF NOT EXISTS (
                SELECT 1
                FROM sys.schemas
                WHERE name = 'Staging'
            )
            BEGIN
                EXEC('CREATE SCHEMA Staging');
            END;
        """))

    # Cargar cada tabla transformada
    for tabla, df in datos.items():

        nombre_tabla = f"Stg_{tabla}"

        try:

            df.to_sql(
                name=nombre_tabla,
                con=conexion,
                schema="Staging",
                if_exists="replace",
                index=False,
                chunksize=500
            )

            print(f"\nTabla cargada: {nombre_tabla}")
            print(f"Registros cargados: {len(df)}")

        except Exception as error:

            print(f"\nError al cargar {nombre_tabla}")
            print(error)

            raise

    print("\n================================")
    print(" CARGA A STAGING COMPLETADA")
    print("================================")
