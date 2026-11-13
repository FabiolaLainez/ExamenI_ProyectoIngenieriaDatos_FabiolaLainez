
from extraccion import extraer_datos
from transformacion import transformar_datos
from carga_raw import cargar_raw
from carga_clean import cargar_clean


def ejecutar_etl():

    try:

        print("\n================================")
        print(" INICIANDO PROCESO ETL")
        print("================================")

        # 1. EXTRACCION
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
        cargar_raw(datos)

        # 3. CLEAN / VALIDATED
        datos_limpios, auditoria_calidad = transformar_datos(datos)

        # Verificar transformacion
        errores_calidad = [
            registro for registro in auditoria_calidad
            if registro["Estado"] != "EXITOSO"
        ]

        if errores_calidad:
            raise Exception(
                "La transformacion contiene errores."
            )

        # 4. CARGA CLEAN
        cargar_clean(datos_limpios, auditoria_calidad)

        print("\n================================")
        print(" PROCESO ETL COMPLETADO")
        print("================================")

    except Exception as error:

        print("\n================================")
        print(" ERROR EN EL PROCESO ETL")
        print("================================")
        print(error)


if __name__ == "__main__":
    ejecutar_etl()
