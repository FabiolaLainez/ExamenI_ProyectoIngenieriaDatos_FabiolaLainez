
from extraccion import extraer_datos
from transformacion import transformar_datos

from carga_raw import cargar_raw
from carga_clean import cargar_clean
from carga_ready import cargar_ready


def ejecutar_etl():

    try:

        print("\n================================")
        print(" INICIANDO PROCESO ETL COMPLETO")
        print("================================")

        # 1. EXTRACCION
        print("\nETAPA 1: EXTRACCION")

        datos, auditoria_extraccion = extraer_datos()

        errores = [
            registro for registro in auditoria_extraccion
            if registro["estado"] != "EXITOSO"
        ]

        if errores:
            raise Exception(
                "La extraccion contiene errores."
            )

        # 2. LANDING / RAW
        print("\nETAPA 2: LANDING / RAW")

        cargar_raw(datos)

        # 3. CLEAN / VALIDATED
        print("\nETAPA 3: CLEAN / VALIDATED")

        datos_limpios, auditoria_calidad = transformar_datos(datos)

        errores_calidad = [
            registro for registro in auditoria_calidad
            if registro["Estado"] != "EXITOSO"
        ]

        if errores_calidad:
            raise Exception(
                "La transformacion contiene errores."
            )

        cargar_clean(datos_limpios, auditoria_calidad)

        # 4. READY / INTEGRATION
        print("\nETAPA 4: READY / INTEGRATION")

        cargar_ready()

        # 5. FINALIZACION
        print("\n================================")
        print(" PROCESO ETL COMPLETADO")
        print(" TODAS LAS CAPAS FUERON CARGADAS")
        print("================================")

    except Exception as error:

        print("\n================================")
        print(" ERROR EN EL PROCESO ETL")
        print("================================")

        print(error)


if __name__ == "__main__":
    ejecutar_etl()
