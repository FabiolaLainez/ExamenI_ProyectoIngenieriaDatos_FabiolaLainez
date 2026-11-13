

from sqlalchemy import text
from conexion import conexion


def cargar_datos(datos):

    print("\n================================")
    print(" INICIANDO CARGA A STAGING")
    print("================================")

    try:

        # Una sola transaccion para toda la carga
        with conexion.begin() as conn:

            # 1. Crear esquema Staging si no existe
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

            total_registros = 0

            # 2. Cargar cada tabla transformada
            for tabla, df in datos.items():

                nombre_tabla = f"Stg_{tabla}"

                print(f"\nProcesando: {nombre_tabla}")

                # Verificar si la tabla existe
                existe = conn.execute(
                    text("""
                        SELECT OBJECT_ID(
                            :nombre,
                            'U'
                        )
                    """),
                    {"nombre": f"Staging.{nombre_tabla}"}
                ).scalar()

                if existe:

                    # Limpiar registros anteriores
                    conn.execute(
                        text(
                            f"TRUNCATE TABLE "
                            f"Staging.[{nombre_tabla}]"
                        )
                    )

                    # Insertar nuevos registros
                    df.to_sql(
                        name=nombre_tabla,
                        con=conn,
                        schema="Staging",
                        if_exists="append",
                        index=False,
                        chunksize=500
                    )

                else:

                    # Crear tabla en la primera ejecucion
                    df.to_sql(
                        name=nombre_tabla,
                        con=conn,
                        schema="Staging",
                        if_exists="fail",
                        index=False,
                        chunksize=500
                    )

                registros = len(df)
                total_registros += registros

                print(f"Tabla cargada: {nombre_tabla}")
                print(f"Registros cargados: {registros}")

            print("\n================================")
            print(" RESUMEN DE CARGA")
            print("================================")

            print("Tablas procesadas:", len(datos))
            print("Total de registros:", total_registros)

        print("\n================================")
        print(" CARGA A STAGING COMPLETADA")
        print("================================")

    except Exception as error:

        print("\n================================")
        print(" ERROR EN LA CARGA A STAGING")
        print("================================")

        print(error)

        raise
