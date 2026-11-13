
from sqlalchemy import text
from conexion import conexion


def registrar_inicio(
    execution_id,
    pipeline_name,
    stage_name,
    source_object=None,
    target_object=None,
    watermark_start=None
):
    consulta = text("""
        INSERT INTO ETL.AuditoriaEjecucion (
            execution_id,
            pipeline_name,
            stage_name,
            start_time,
            source_object,
            target_object,
            status,
            watermark_start
        )
        OUTPUT INSERTED.AuditoriaID
        VALUES (
            :execution_id,
            :pipeline_name,
            :stage_name,
            SYSDATETIME(),
            :source_object,
            :target_object,
            'EN_PROCESO',
            :watermark_start
        );
    """)

    with conexion.begin() as conn:
        auditoria_id = conn.execute(
            consulta,
            {
                "execution_id": execution_id,
                "pipeline_name": pipeline_name,
                "stage_name": stage_name,
                "source_object": source_object,
                "target_object": target_object,
                "watermark_start": watermark_start
            }
        ).scalar_one()

    return auditoria_id


def registrar_fin(
    auditoria_id,
    status,
    rows_read=0,
    inserted=0,
    updated=0,
    rejected=0,
    error_detail=None,
    watermark_end=None
):
    consulta = text("""
        UPDATE ETL.AuditoriaEjecucion
        SET
            end_time = SYSDATETIME(),
            rows_read = :rows_read,
            inserted = :inserted,
            updated = :updated,
            rejected = :rejected,
            status = :status,
            error_detail = :error_detail,
            watermark_end = :watermark_end
        WHERE AuditoriaID = :auditoria_id;
    """)

    with conexion.begin() as conn:
        conn.execute(
            consulta,
            {
                "auditoria_id": auditoria_id,
                "rows_read": rows_read,
                "inserted": inserted,
                "updated": updated,
                "rejected": rejected,
                "status": status,
                "error_detail": error_detail,
                "watermark_end": watermark_end
            }
        )
