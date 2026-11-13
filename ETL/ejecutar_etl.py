
from extraccion import extraer_datos
from transformacion import transformar_datos
from carga import cargar_datos


def ejecutar_etl():

    try:

        print("\n================================")
        print(" INICIANDO PROCESO ETL")
        print("================================")

        # 1. EXTRACCION
        resultado = extraer_datos()

        datos, auditoria = resultado

        # Verificar que la extraccion fue exitosa
        errores = [
            registro for registro in auditoria
            if registro["estado"] != "EXITOSO"
        ]

        if errores:
            raise Exception(
                "La extraccion contiene tablas con errores."
            )

        # 2. TRANSFORMACION
        datos_limpios = transformar_datos(datos)

        # 3. CARGA
        cargar_datos(datos_limpios)

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
