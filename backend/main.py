
from datetime import date
from pathlib import Path
import csv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from conexion import engine


# =========================================================
# CONFIGURACION DE FASTAPI
# =========================================================

app = FastAPI(
    title="API EmpresaComercial",
    version="1.0.0",
    description="API para el Dashboard de Business Intelligence"
)


# =========================================================
# CONFIGURACION CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def construir_filtros(
    fecha_inicio=None,
    fecha_fin=None,
    categoria_id=None,
    empleado_id=None
):
    condiciones = []
    parametros = {}

    if fecha_inicio:
        condiciones.append("DF.Fecha >= :fecha_inicio")
        parametros["fecha_inicio"] = fecha_inicio

    if fecha_fin:
        condiciones.append("DF.Fecha <= :fecha_fin")
        parametros["fecha_fin"] = fecha_fin

    if categoria_id is not None:
        condiciones.append("DP.IDCategoria = :categoria_id")
        parametros["categoria_id"] = categoria_id

    if empleado_id is not None:
        condiciones.append("DE.IDEmpleado = :empleado_id")
        parametros["empleado_id"] = empleado_id

    where = " AND ".join(condiciones) if condiciones else "1=1"

    return where, parametros


def convertir_resultado(resultado):
    if resultado is None:
        return 0

    if hasattr(resultado, "as_tuple"):
        return float(resultado)

    return resultado


# =========================================================
# ENDPOINT PRINCIPAL
# =========================================================

@app.get("/")
def inicio():
    return {
        "mensaje": "API EmpresaComercial funcionando correctamente"
    }


# =========================================================
# COMPROBAR CONEXION
# =========================================================

@app.get("/conexion")
def probar_conexion():
    try:
        with engine.connect() as conexion:
            resultado = conexion.execute(
                text("SELECT DB_NAME() AS base_datos")
            ).mappings().first()

        return {
            "estado": "Conectado",
            "base_datos": resultado["base_datos"]
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error de conexion: {str(error)}"
        )


# =========================================================
# DASHBOARD: RESUMEN EJECUTIVO
# =========================================================

@app.get("/api/dashboard/resumen")
def obtener_resumen(
    fecha_inicio: date = None,
    fecha_fin: date = None,
    categoria_id: int = None,
    empleado_id: int = None
):

    where, parametros = construir_filtros(
        fecha_inicio,
        fecha_fin,
        categoria_id,
        empleado_id
    )

    consulta = text(f"""
        SELECT
            COALESCE(SUM(FV.Subtotal), 0) AS ventas_totales,
            COALESCE(SUM(FV.Cantidad), 0) AS unidades_vendidas,
            COUNT(DISTINCT FV.ClienteSK) AS clientes_registrados,

            CASE
                WHEN COUNT(DISTINCT FV.IDVenta) = 0 THEN 0
                ELSE SUM(FV.Subtotal) * 1.0 /
                     COUNT(DISTINCT FV.IDVenta)
            END AS ticket_promedio,

            COUNT(DISTINCT FV.IDVenta) AS cantidad_ventas

        FROM DW.FactVentas FV

        INNER JOIN DW.DimFecha DF
            ON FV.FechaKey = DF.FechaKey

        INNER JOIN DW.DimProducto DP
            ON FV.ProductoSK = DP.ProductoSK

        INNER JOIN DW.DimEmpleado DE
            ON FV.EmpleadoSK = DE.EmpleadoSK

        WHERE {where}
    """)

    try:
        with engine.connect() as conexion:
            resultado = conexion.execute(
                consulta,
                parametros
            ).mappings().first()

        return {
            "ventas_totales": convertir_resultado(
                resultado["ventas_totales"]
            ),
            "unidades_vendidas": convertir_resultado(
                resultado["unidades_vendidas"]
            ),
            "clientes_registrados": convertir_resultado(
                resultado["clientes_registrados"]
            ),
            "ticket_promedio": convertir_resultado(
                resultado["ticket_promedio"]
            ),
            "cantidad_ventas": convertir_resultado(
                resultado["cantidad_ventas"]
            )
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener resumen: {str(error)}"
        )


# =========================================================
# DASHBOARD: VENTAS MENSUALES
# =========================================================

@app.get("/api/dashboard/ventas-mensuales")
def obtener_ventas_mensuales(
    fecha_inicio: date = None,
    fecha_fin: date = None,
    categoria_id: int = None,
    empleado_id: int = None
):

    where, parametros = construir_filtros(
        fecha_inicio,
        fecha_fin,
        categoria_id,
        empleado_id
    )

    consulta = text(f"""
        SELECT
            DF.Anio AS anio,
            DF.Mes AS mes,
            DF.NombreMes AS nombre_mes,
            SUM(FV.Subtotal) AS ventas

        FROM DW.FactVentas FV

        INNER JOIN DW.DimFecha DF
            ON FV.FechaKey = DF.FechaKey

        INNER JOIN DW.DimProducto DP
            ON FV.ProductoSK = DP.ProductoSK

        INNER JOIN DW.DimEmpleado DE
            ON FV.EmpleadoSK = DE.EmpleadoSK

        WHERE {where}

        GROUP BY
            DF.Anio,
            DF.Mes,
            DF.NombreMes

        ORDER BY
            DF.Anio,
            DF.Mes
    """)

    try:
        with engine.connect() as conexion:
            resultados = conexion.execute(
                consulta,
                parametros
            ).mappings().all()

        return [
            {
                "anio": fila["anio"],
                "mes": fila["mes"],
                "nombre_mes": fila["nombre_mes"],
                "ventas": convertir_resultado(fila["ventas"])
            }
            for fila in resultados
        ]

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener ventas mensuales: {str(error)}"
        )


# =========================================================
# DASHBOARD: VENTAS POR CATEGORIA
# =========================================================

@app.get("/api/dashboard/ventas-categoria")
def obtener_ventas_categoria(
    fecha_inicio: date = None,
    fecha_fin: date = None,
    categoria_id: int = None,
    empleado_id: int = None
):

    where, parametros = construir_filtros(
        fecha_inicio,
        fecha_fin,
        categoria_id,
        empleado_id
    )

    consulta = text(f"""
        SELECT
            DP.IDCategoria AS categoria_id,
            DP.NombreCategoria AS categoria,
            SUM(FV.Subtotal) AS ventas,
            SUM(FV.Cantidad) AS unidades_vendidas

        FROM DW.FactVentas FV

        INNER JOIN DW.DimFecha DF
            ON FV.FechaKey = DF.FechaKey

        INNER JOIN DW.DimProducto DP
            ON FV.ProductoSK = DP.ProductoSK

        INNER JOIN DW.DimEmpleado DE
            ON FV.EmpleadoSK = DE.EmpleadoSK

        WHERE {where}

        GROUP BY
            DP.IDCategoria,
            DP.NombreCategoria

        ORDER BY ventas DESC
    """)

    try:
        with engine.connect() as conexion:
            resultados = conexion.execute(
                consulta,
                parametros
            ).mappings().all()

        return [
            {
                "categoria_id": fila["categoria_id"],
                "categoria": fila["categoria"],
                "ventas": convertir_resultado(fila["ventas"]),
                "unidades_vendidas": convertir_resultado(
                    fila["unidades_vendidas"]
                )
            }
            for fila in resultados
        ]

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener ventas por categoria: {str(error)}"
        )


# =========================================================
# CONSULTAR VENTAS
# =========================================================

@app.get("/api/ventas")
def obtener_ventas():
    try:
        consulta = text("""
            SELECT TOP 500
                FV.IDVenta AS id_venta,
                FV.IDDetalle AS id_detalle,
                DF.Fecha AS fecha,
                CONCAT(DC.Nombres, ' ', DC.Apellidos) AS cliente,
                CONCAT(DE.Nombres, ' ', DE.Apellidos) AS empleado,
                DP.NombreProducto AS producto,
                FV.Cantidad AS cantidad,
                FV.PrecioUnitario AS precio_unitario,
                FV.Descuento AS descuento,
                FV.Subtotal AS subtotal,
                FV.EstadoVenta AS estado

            FROM DW.FactVentas FV

            INNER JOIN DW.DimFecha DF
                ON FV.FechaKey = DF.FechaKey

            INNER JOIN DW.DimCliente DC
                ON FV.ClienteSK = DC.ClienteSK

            INNER JOIN DW.DimEmpleado DE
                ON FV.EmpleadoSK = DE.EmpleadoSK

            INNER JOIN DW.DimProducto DP
                ON FV.ProductoSK = DP.ProductoSK

            ORDER BY FV.IDVenta DESC, FV.IDDetalle DESC
        """)

        with engine.connect() as conexion:
            resultados = conexion.execute(
                consulta
            ).mappings().all()

        return [dict(fila) for fila in resultados]

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# =========================================================
# CONSULTAR CLIENTES
# =========================================================

@app.get("/api/clientes")
def obtener_clientes():
    try:
        consulta = text("""
            SELECT
                ClienteSK AS cliente_sk,
                IDCliente AS id_cliente,
                Nombres AS nombres,
                Apellidos AS apellidos,
                DNI AS dni,
                Telefono AS telefono,
                Correo AS correo,
                Direccion AS direccion,
                FechaRegistro AS fecha_registro,
                FechaInicio AS fecha_inicio,
                FechaFin AS fecha_fin,
                EsActual AS es_actual

            FROM DW.DimCliente

            WHERE EsActual = 1

            ORDER BY ClienteSK
        """)

        with engine.connect() as conexion:
            resultados = conexion.execute(
                consulta
            ).mappings().all()

        return [dict(fila) for fila in resultados]

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# =========================================================
# CONSULTAR PRODUCTOS
# =========================================================

@app.get("/api/productos")
def obtener_productos():
    try:
        consulta = text("""
            SELECT
                ProductoSK AS producto_sk,
                IDProducto AS id_producto,
                NombreProducto AS nombre_producto,
                Descripcion AS descripcion,
                IDCategoria AS id_categoria,
                NombreCategoria AS categoria,
                PrecioCompra AS precio_compra,
                PrecioVenta AS precio_venta,
                Estado AS estado,
                FechaInicio AS fecha_inicio,
                FechaFin AS fecha_fin,
                EsActual AS es_actual

            FROM DW.DimProducto

            WHERE EsActual = 1

            ORDER BY ProductoSK
        """)

        with engine.connect() as conexion:
            resultados = conexion.execute(
                consulta
            ).mappings().all()

        return [dict(fila) for fila in resultados]

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# =========================================================
# CONSULTAR PAGOS
# =========================================================

@app.get("/api/pagos")
def obtener_pagos():
    try:
        consulta = text("""
            SELECT
                FP.IDPago AS id_pago,
                FP.IDVenta AS id_venta,
                DF.Fecha AS fecha,
                CONCAT(DC.Nombres, ' ', DC.Apellidos) AS cliente,
                FP.Monto AS monto,
                FP.MetodoPago AS metodo_pago,
                FP.EstadoPago AS estado

            FROM DW.FactPagos FP

            INNER JOIN DW.DimFecha DF
                ON FP.FechaKey = DF.FechaKey

            INNER JOIN DW.DimCliente DC
                ON FP.ClienteSK = DC.ClienteSK

            ORDER BY FP.IDPago DESC
        """)

        with engine.connect() as conexion:
            resultados = conexion.execute(
                consulta
            ).mappings().all()

        return [dict(fila) for fila in resultados]

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# =========================================================
# CONSULTAR INVENTARIO
# =========================================================

@app.get("/api/inventario")
def obtener_inventario():
    try:
        consulta = text("""
            SELECT
                FI.IDMovimiento AS id_movimiento,
                DF.Fecha AS fecha,
                DP.IDProducto AS id_producto,
                DP.NombreProducto AS producto,
                CONCAT(DE.Nombres, ' ', DE.Apellidos) AS empleado,
                FI.TipoMovimiento AS tipo_movimiento,
                FI.Cantidad AS cantidad,
                FI.Motivo AS motivo

            FROM DW.FactInventario FI

            INNER JOIN DW.DimFecha DF
                ON FI.FechaKey = DF.FechaKey

            INNER JOIN DW.DimProducto DP
                ON FI.ProductoSK = DP.ProductoSK

            INNER JOIN DW.DimEmpleado DE
                ON FI.EmpleadoSK = DE.EmpleadoSK

            ORDER BY FI.IDMovimiento DESC
        """)

        with engine.connect() as conexion:
            resultados = conexion.execute(
                consulta
            ).mappings().all()

        return [dict(fila) for fila in resultados]

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# =========================================================
# ESTADO DEL DATA WAREHOUSE
# =========================================================

@app.get("/api/datawarehouse")
def obtener_estado_datawarehouse():
    try:
        consultas = {
            "DimFecha": "SELECT COUNT(*) FROM DW.DimFecha",
            "DimCliente": "SELECT COUNT(*) FROM DW.DimCliente",
            "DimEmpleado": "SELECT COUNT(*) FROM DW.DimEmpleado",
            "DimProducto": "SELECT COUNT(*) FROM DW.DimProducto",
            "FactVentas": "SELECT COUNT(*) FROM DW.FactVentas",
            "FactPagos": "SELECT COUNT(*) FROM DW.FactPagos",
            "FactInventario": "SELECT COUNT(*) FROM DW.FactInventario"
        }

        resultado = {}

        with engine.connect() as conexion:
            for tabla, consulta in consultas.items():
                resultado[tabla] = conexion.execute(
                    text(consulta)
                ).scalar_one()

        resultado["total_registros"] = sum(resultado.values())

        return resultado

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# =========================================================
# MACHINE LEARNING: PRONOSTICO DE VENTAS
# =========================================================

@app.get("/api/ml/pronostico")
def obtener_pronostico():

    try:
        # Ruta del archivo generado por entrenamiento.py
        carpeta_backend = Path(__file__).resolve().parent

        archivo_pronostico = (
            carpeta_backend / "ML" / "pronostico_7_dias.csv"
        )

        if not archivo_pronostico.exists():
            raise HTTPException(
                status_code=404,
                detail=(
                    "No existe el archivo pronostico_7_dias.csv. "
                    "Ejecuta primero entrenamiento.py."
                )
            )

        pronosticos = []

        with open(
            archivo_pronostico,
            mode="r",
            encoding="utf-8-sig",
            newline=""
        ) as archivo:

            lector = csv.DictReader(archivo)

            columnas_requeridas = {
                "Fecha",
                "VentasPronosticadas"
            }

            if not lector.fieldnames or not columnas_requeridas.issubset(
                set(lector.fieldnames)
            ):
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "El CSV no contiene las columnas "
                        "Fecha y VentasPronosticadas."
                    )
                )

            for fila in lector:
                pronosticos.append({
                    "fecha": fila["Fecha"],
                    "ventas_pronosticadas": round(
                        float(fila["VentasPronosticadas"]),
                        2
                    )
                })

        return {
            "modelo": "RandomForestRegressor",
            "horizonte_dias": len(pronosticos),
            "pronosticos": pronosticos
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener pronosticos: {str(error)}"
        )
