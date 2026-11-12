
from extraccion import extraer_datos
from transformacion import transformar_datos
from carga import cargar_datos


def ejecutar_etl():

    try:

        print("\nINICIANDO PROCESO ETL COMPLETO")

        # 1. EXTRACT
        datos = extraer_datos()

        # 2. TRANSFORM
        datos_limpios = transformar_datos(datos)

        # 3. LOAD
        cargar_datos(datos_limpios)

        print("\n================================")
        print(" PROCESO ETL FINALIZADO")
        print("================================")

    except Exception as error:

        print("\nERROR EN EL PROCESO ETL")
        print(error)


if __name__ == "__main__":
    ejecutar_etl()
