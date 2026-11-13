
import uuid

from extraccion import extraer_datos
from transformacion import transformar_datos

from carga_raw import cargar_raw
from carga_clean import cargar_clean
from carga_ready import cargar_ready

from auditoria import registrar_inicio, registrar_fin


def contar_registros(datos):
    """Calcula la cantidad de registros de los DataFrames."""
    total = 0

    for tabla in datos.values():
        total += len(tabla)

    return total


def ejecutar_etapa(
    execution_id,
    nombre_etapa,
    origen,
    destino,
    funcion,
    rows_read=0,
    inserted=0
):
    """Ejecuta una etapa y registra su resultado en auditoría."""

    auditoria_id = registrar_inicio(
        execution_id=execution_id,
        pipeline_name="ETL_EmpresaComercial",
        stage_name=nombre_etapa,
        source_object=origen,
        target_object=destino
    )

    try:
        resultado = funcion()

        registrar_fin(
            auditoria_id=auditoria_id,
            status="EXITOSO",
            rows_read=rows_read,
            inserted=inserted,
            updated=0,
            rejected=0
        )

        print(f"Auditoría registrada: {nombre_etapa}")

        return resultado

    except Exception as error:

        registrar_fin(
            auditoria_id=auditoria_id,
            status="ERROR",
            rows_read=rows_read,
            inserted=0,
            updated=0,
            rejected=0,
            error_detail=str(error)
        )

        raise


def ejecutar_etl():

    execution_id = str(uuid.uuid4())

    try:

        print("\n================================")
        print(" INICIANDO PROCESO ETL COMPLETO")
        print("================================")

        # 1. EXTRACCION
        print("\nETAPA 1: EXTRACCION")

        auditoria_id = registrar_inicio(
            execution_id=execution_id,
            pipeline_name="ETL_EmpresaComercial",
            stage_name="EXTRACCION",
            source_object="EmpresaComercial",
            target_object="Memoria_Python"
        )

        try:
            datos, auditoria_extraccion = extraer_datos()

            errores = [
                registro for registro in auditoria_extraccion
                if registro["estado"] != "EXITOSO"
            ]

            if errores:
                raise Exception(
                    f"La extracción contiene errores: {errores}"
                )

            total_extraido = contar_registros(datos)

            registrar_fin(
                auditoria_id=auditoria_id,
                status="EXITOSO",
                rows_read=total_extraido,
                inserted=total_extraido
            )

        except Exception as error:
            registrar_fin(
                auditoria_id=auditoria_id,
                status="ERROR",
                error_detail=str(error)
            )
            raise

        # 2. LANDING / RAW
        print("\nETAPA 2: LANDING / RAW")

        total_raw = contar_registros(datos)

        ejecutar_etapa(
            execution_id,
            "CARGA_RAW",
            "Memoria_Python",
            "Raw",
            lambda: cargar_raw(datos),
            rows_read=total_raw,
            inserted=total_raw
        )

        # 3. CLEAN / VALIDATED
        print("\nETAPA 3: CLEAN / VALIDATED")

        auditoria_id = registrar_inicio(
            execution_id=execution_id,
            pipeline_name="ETL_EmpresaComercial",
            stage_name="TRANSFORMACION",
            source_object="Raw",
            target_object="Clean"
        )

        try:
            datos_limpios, auditoria_calidad = transformar_datos(datos)

            errores_calidad = [
                registro for registro in auditoria_calidad
                if registro["Estado"] != "EXITOSO"
            ]

            if errores_calidad:
                raise Exception(
                    f"La transformación contiene errores: {errores_calidad}"
                )

            total_clean = contar_registros(datos_limpios)

            registrar_fin(
                auditoria_id=auditoria_id,
                status="EXITOSO",
                rows_read=total_raw,
                inserted=total_clean
            )

        except Exception as error:
            registrar_fin(
                auditoria_id=auditoria_id,
                status="ERROR",
                error_detail=str(error)
            )
            raise

        ejecutar_etapa(
            execution_id,
            "CARGA_CLEAN",
            "Datos_Transformados",
            "Clean",
            lambda: cargar_clean(datos_limpios, auditoria_calidad),
            rows_read=total_clean,
            inserted=total_clean
        )

        # 4. READY / INTEGRATION
        print("\nETAPA 4: READY / INTEGRATION")

        ejecutar_etapa(
            execution_id,
            "CARGA_READY",
            "Clean",
            "Ready",
            cargar_ready,
            rows_read=total_clean
        )

        # 5. FINALIZACION
        print("\n================================")
        print(" PROCESO ETL COMPLETADO")
        print(" TODAS LAS CAPAS FUERON CARGADAS")
        print("================================")

        print("Execution ID:", execution_id)

    except Exception as error:

        print("\n================================")
        print(" ERROR EN EL PROCESO ETL")
        print("================================")

        print(error)


if __name__ == "__main__":
    ejecutar_etl()
