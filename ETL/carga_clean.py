
from conexion import conexion
import pandas as pd

# CONFIGURACION

ESQUEMA = "Clean"



# CREAR ESQUEMA CLEAN


def crear_esquema_clean():

    with conexion.begin() as conn:

        conn.exec_driver_sql("""
            IF NOT EXISTS (
                SELECT 1
                FROM sys.schemas
                WHERE name = 'Clean'
            )
            BEGIN
                EXEC('CREATE SCHEMA Clean');
            END;
        """)

    print("\nEsquema Clean verificado correctamente.")



# CARGAR DATOS LIMPIOS


def cargar_clean(datos_limpios, auditoria_calidad):

    print("\n================================")
    print(" INICIANDO CARGA CLEAN")
    print("================================")

    if not isinstance(datos_limpios, dict):
        raise TypeError(
            "Los datos limpios deben ser un diccionario."
        )

    crear_esquema_clean()

    total_registros = 0

    # Cargar las ocho tablas
    for tabla, df in datos_limpios.items():

        nombre_tabla = f"Clean_{tabla}"

        try:

            df.to_sql(
                name=nombre_tabla,
                con=conexion,
                schema=ESQUEMA,
                if_exists="replace",
                index=False,
                chunksize=500
            )

            registros = len(df)
            total_registros += registros

            print(f"\nTabla cargada: {nombre_tabla}")
            print(f"Registros: {registros}")

        except Exception as error:

            print(f"\nERROR AL CARGAR: {nombre_tabla}")
            print(error)

            raise

    # Cargar auditoria de calidad
    try:

        df_auditoria = pd.DataFrame(auditoria_calidad)

        df_auditoria.to_sql(
            name="AuditoriaCalidad",
            con=conexion,
            schema=ESQUEMA,
            if_exists="replace",
            index=False,
            chunksize=500
        )

        print("\nAuditoria de calidad cargada correctamente.")

    except Exception as error:

        print("\nERROR AL CARGAR AUDITORIA")
        print(error)

        raise

    print("\n================================")
    print(" CARGA CLEAN COMPLETADA")
    print("================================")

    print("Tablas de datos:", len(datos_limpios))
    print("Total de registros:", total_registros)
    print("Registros de auditoria:", len(auditoria_calidad))


# ==========================================
# EJECUCION INDEPENDIENTE
# ==========================================

if __name__ == "__main__":

    import pandas as pd
    from extraccion import extraer_datos
    from transformacion import transformar_datos

    datos, auditoria = extraer_datos()

    errores = [
        registro for registro in auditoria
        if registro["estado"] != "EXITOSO"
    ]

    if errores:
        raise Exception("Existen errores en la extraccion.")

    datos_limpios, auditoria_calidad = transformar_datos(datos)

    cargar_clean(datos_limpios, auditoria_calidad)
