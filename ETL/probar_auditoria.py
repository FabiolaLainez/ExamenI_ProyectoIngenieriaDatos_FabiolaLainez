
import uuid

from auditoria import registrar_inicio, registrar_fin


def probar_auditoria():

    execution_id = str(uuid.uuid4())

    try:
        print("Iniciando prueba de auditoría...")

        auditoria_id = registrar_inicio(
            execution_id=execution_id,
            pipeline_name="ETL_EmpresaComercial",
            stage_name="PRUEBA_AUDITORIA",
            source_object="EmpresaComercial",
            target_object="ETL.AuditoriaEjecucion"
        )

        print("Registro de inicio exitoso.")
        print("AuditoriaID:", auditoria_id)

        registrar_fin(
            auditoria_id=auditoria_id,
            status="EXITOSO",
            rows_read=100,
            inserted=100,
            updated=0,
            rejected=0
        )

        print("Registro de finalización exitoso.")

    except Exception as error:
        print("Error en la prueba:", error)


if __name__ == "__main__":
    probar_auditoria()
