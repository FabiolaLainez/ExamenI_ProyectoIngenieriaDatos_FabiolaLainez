
from sqlalchemy import text
from conexion import engine


# ============================================================
# CONFIGURACION
# ============================================================

NOMBRE_PIPELINE = "Carga_DataWarehouse"

TABLAS_HECHOS = [
    "DW.FactVentas",
    "DW.FactPagos",
    "DW.FactInventario"
]


# ============================================================
# FUNCIONES GENERALES
# ============================================================

def ejecutar_consulta(conn, consulta):
    resultado = conn.execute(text(consulta))
    return resultado


def mostrar_resumen(conn):
    print("\n" + "=" * 55)
    print("RESUMEN DEL DATA WAREHOUSE")
    print("=" * 55)

    for tabla in TABLAS_HECHOS:
        cantidad = conn.execute(
            text(f"SELECT COUNT(*) FROM {tabla}")
        ).scalar_one()

        print(f"{tabla}: {cantidad:,} registros")


def validar_dimensiones(conn):
    """
    Comprueba que todas las filas de las tablas Ready
    tengan una dimensión compatible según su fecha de operación.
    """

    print("\nVALIDANDO DIMENSIONES...")

    validaciones = {

        "CLIENTES - VENTAS": """
            SELECT COUNT(*)
            FROM Ready.Ready_FactVentas f
            INNER JOIN Ready.Ready_DimCliente rc
                ON rc.ClienteKey = f.ClienteKey
            INNER JOIN DW.DimFecha df
                ON df.FechaKey = f.FechaKey
            WHERE NOT EXISTS (
                SELECT 1
                FROM DW.DimCliente d
                WHERE d.IDCliente = rc.IDCliente
                  AND df.Fecha >= d.FechaInicio
                  AND df.Fecha < d.FechaFin
            )
        """,

        "EMPLEADOS - VENTAS": """
            SELECT COUNT(*)
            FROM Ready.Ready_FactVentas f
            INNER JOIN Ready.Ready_DimEmpleado re
                ON re.EmpleadoKey = f.EmpleadoKey
            INNER JOIN DW.DimFecha df
                ON df.FechaKey = f.FechaKey
            WHERE NOT EXISTS (
                SELECT 1
                FROM DW.DimEmpleado d
                WHERE d.IDEmpleado = re.IDEmpleado
                  AND df.Fecha >= d.FechaInicio
                  AND df.Fecha < d.FechaFin
            )
        """,

        "PRODUCTOS - VENTAS": """
            SELECT COUNT(*)
            FROM Ready.Ready_FactVentas f
            INNER JOIN Ready.Ready_DimProducto rp
                ON rp.ProductoKey = f.ProductoKey
            INNER JOIN DW.DimFecha df
                ON df.FechaKey = f.FechaKey
            WHERE NOT EXISTS (
                SELECT 1
                FROM DW.DimProducto d
                WHERE d.IDProducto = rp.IDProducto
                  AND df.Fecha >= d.FechaInicio
                  AND df.Fecha < d.FechaFin
            )
        """,

        "CLIENTES - PAGOS": """
            SELECT COUNT(*)
            FROM Ready.Ready_FactPagos f
            INNER JOIN Ready.Ready_DimCliente rc
                ON rc.ClienteKey = f.ClienteKey
            INNER JOIN DW.DimFecha df
                ON df.FechaKey = f.FechaKey
            WHERE NOT EXISTS (
                SELECT 1
                FROM DW.DimCliente d
                WHERE d.IDCliente = rc.IDCliente
                  AND df.Fecha >= d.FechaInicio
                  AND df.Fecha < d.FechaFin
            )
        """,

        "PRODUCTOS - INVENTARIO": """
            SELECT COUNT(*)
            FROM Ready.Ready_FactMovimientosInventario f
            INNER JOIN Ready.Ready_DimProducto rp
                ON rp.ProductoKey = f.ProductoKey
            INNER JOIN DW.DimFecha df
                ON df.FechaKey = f.FechaKey
            WHERE NOT EXISTS (
                SELECT 1
                FROM DW.DimProducto d
                WHERE d.IDProducto = rp.IDProducto
                  AND df.Fecha >= d.FechaInicio
                  AND df.Fecha < d.FechaFin
            )
        """,

        "EMPLEADOS - INVENTARIO": """
            SELECT COUNT(*)
            FROM Ready.Ready_FactMovimientosInventario f
            INNER JOIN Ready.Ready_DimEmpleado re
                ON re.EmpleadoKey = f.EmpleadoKey
            INNER JOIN DW.DimFecha df
                ON df.FechaKey = f.FechaKey
            WHERE NOT EXISTS (
                SELECT 1
                FROM DW.DimEmpleado d
                WHERE d.IDEmpleado = re.IDEmpleado
                  AND df.Fecha >= d.FechaInicio
                  AND df.Fecha < d.FechaFin
            )
        """
    }

    errores = 0

    for nombre, consulta in validaciones.items():

        cantidad = conn.execute(text(consulta)).scalar_one()

        if cantidad > 0:
            print(f"ERROR: {nombre}: {cantidad} registros sin dimension.")
            errores += cantidad
        else:
            print(f"OK: {nombre}: 0 registros sin dimension.")

    if errores > 0:
        raise Exception(
            f"Existen {errores} registros sin una dimension compatible."
        )

    print("Todas las dimensiones son compatibles.")


def validar_fechas(conn):

    print("\nVALIDANDO CLAVES DE FECHA...")

    consultas = {

        "VENTAS": """
            SELECT COUNT(*)
            FROM Ready.Ready_FactVentas f
            LEFT JOIN DW.DimFecha d
                ON d.FechaKey = f.FechaKey
            WHERE d.FechaKey IS NULL
        """,

        "PAGOS": """
            SELECT COUNT(*)
            FROM Ready.Ready_FactPagos f
            LEFT JOIN DW.DimFecha d
                ON d.FechaKey = f.FechaKey
            WHERE d.FechaKey IS NULL
        """,

        "INVENTARIO": """
            SELECT COUNT(*)
            FROM Ready.Ready_FactMovimientosInventario f
            LEFT JOIN DW.DimFecha d
                ON d.FechaKey = f.FechaKey
            WHERE d.FechaKey IS NULL
        """
    }

    for nombre, consulta in consultas.items():

        cantidad = conn.execute(text(consulta)).scalar_one()

        if cantidad > 0:
            raise Exception(
                f"{nombre}: existen {cantidad} fechas sin correspondencia."
            )

        print(f"OK: {nombre}: fechas compatibles.")


def validar_cantidades_inventario(conn):

    print("\nVALIDANDO CANTIDADES DE INVENTARIO...")

    cantidad = conn.execute(text("""
        SELECT COUNT(*)
        FROM Ready.Ready_FactMovimientosInventario
        WHERE Cantidad IS NULL
           OR Cantidad <> FLOOR(Cantidad)
    """)).scalar_one()

    if cantidad > 0:
        raise Exception(
            f"Existen {cantidad} cantidades nulas o decimales. "
            "No se pueden convertir de forma segura a INT."
        )

    print("OK: todas las cantidades son enteras.")


# ============================================================
# CARGA FACT VENTAS
# ============================================================

def cargar_fact_ventas(conn):

    print("\nCARGANDO DW.FactVentas...")

    consulta = """
        INSERT INTO DW.FactVentas
        (
            IDDetalle,
            IDVenta,
            FechaKey,
            ClienteSK,
            EmpleadoSK,
            ProductoSK,
            Cantidad,
            PrecioUnitario,
            Descuento,
            Subtotal,
            EstadoVenta
        )
        SELECT
            f.IDDetalle,
            f.IDVenta,
            f.FechaKey,
            dc.ClienteSK,
            de.EmpleadoSK,
            dp.ProductoSK,
            f.Cantidad,
            f.PrecioUnitario,
            f.Descuento,
            f.Subtotal,
            f.EstadoVenta

        FROM Ready.Ready_FactVentas f

        INNER JOIN Ready.Ready_DimCliente rc
            ON rc.ClienteKey = f.ClienteKey

        INNER JOIN Ready.Ready_DimEmpleado re
            ON re.EmpleadoKey = f.EmpleadoKey

        INNER JOIN Ready.Ready_DimProducto rp
            ON rp.ProductoKey = f.ProductoKey

        INNER JOIN DW.DimFecha df
            ON df.FechaKey = f.FechaKey

        CROSS APPLY
        (
            SELECT TOP (1)
                d.ClienteSK
            FROM DW.DimCliente d
            WHERE d.IDCliente = rc.IDCliente
              AND df.Fecha >= d.FechaInicio
              AND df.Fecha < d.FechaFin
            ORDER BY d.FechaInicio DESC, d.ClienteSK DESC
        ) dc

        CROSS APPLY
        (
            SELECT TOP (1)
                d.EmpleadoSK
            FROM DW.DimEmpleado d
            WHERE d.IDEmpleado = re.IDEmpleado
              AND df.Fecha >= d.FechaInicio
              AND df.Fecha < d.FechaFin
            ORDER BY d.FechaInicio DESC, d.EmpleadoSK DESC
        ) de

        CROSS APPLY
        (
            SELECT TOP (1)
                d.ProductoSK
            FROM DW.DimProducto d
            WHERE d.IDProducto = rp.IDProducto
              AND df.Fecha >= d.FechaInicio
              AND df.Fecha < d.FechaFin
            ORDER BY d.FechaInicio DESC, d.ProductoSK DESC
        ) dp

        WHERE NOT EXISTS
        (
            SELECT 1
            FROM DW.FactVentas existente
            WHERE existente.IDDetalle = f.IDDetalle
        );
    """

    resultado = conn.execute(text(consulta))

    print(f"Ventas insertadas: {resultado.rowcount:,}")

    return resultado.rowcount


# ============================================================
# CARGA FACT PAGOS
# ============================================================

def cargar_fact_pagos(conn):

    print("\nCARGANDO DW.FactPagos...")

    consulta = """
        INSERT INTO DW.FactPagos
        (
            IDPago,
            IDVenta,
            FechaKey,
            ClienteSK,
            Monto,
            MetodoPago,
            EstadoPago
        )
        SELECT
            f.IDPago,
            f.IDVenta,
            f.FechaKey,
            dc.ClienteSK,
            f.Monto,
            f.MetodoPago,
            f.EstadoPago

        FROM Ready.Ready_FactPagos f

        -- Relacion directa: evita multiplicar pagos
        INNER JOIN Ready.Ready_DimCliente rc
            ON rc.ClienteKey = f.ClienteKey

        INNER JOIN DW.DimFecha df
            ON df.FechaKey = f.FechaKey

        CROSS APPLY
        (
            SELECT TOP (1)
                d.ClienteSK
            FROM DW.DimCliente d
            WHERE d.IDCliente = rc.IDCliente
              AND df.Fecha >= d.FechaInicio
              AND df.Fecha < d.FechaFin
            ORDER BY d.FechaInicio DESC, d.ClienteSK DESC
        ) dc

        WHERE NOT EXISTS
        (
            SELECT 1
            FROM DW.FactPagos existente
            WHERE existente.IDPago = f.IDPago
        );
    """

    resultado = conn.execute(text(consulta))

    print(f"Pagos insertados: {resultado.rowcount:,}")

    return resultado.rowcount


# ============================================================
# CARGA FACT INVENTARIO
# ============================================================

def cargar_fact_inventario(conn):

    print("\nCARGANDO DW.FactInventario...")

    consulta = """
        INSERT INTO DW.FactInventario
        (
            IDMovimiento,
            FechaKey,
            ProductoSK,
            EmpleadoSK,
            TipoMovimiento,
            Cantidad,
            Motivo
        )
        SELECT
            f.IDMovimiento,
            f.FechaKey,
            dp.ProductoSK,
            de.EmpleadoSK,
            f.TipoMovimiento,
            CAST(f.Cantidad AS INT),
            f.Motivo

        FROM Ready.Ready_FactMovimientosInventario f

        INNER JOIN Ready.Ready_DimProducto rp
            ON rp.ProductoKey = f.ProductoKey

        INNER JOIN Ready.Ready_DimEmpleado re
            ON re.EmpleadoKey = f.EmpleadoKey

        INNER JOIN DW.DimFecha df
            ON df.FechaKey = f.FechaKey

        CROSS APPLY
        (
            SELECT TOP (1)
                d.ProductoSK
            FROM DW.DimProducto d
            WHERE d.IDProducto = rp.IDProducto
              AND df.Fecha >= d.FechaInicio
              AND df.Fecha < d.FechaFin
            ORDER BY d.FechaInicio DESC, d.ProductoSK DESC
        ) dp

        CROSS APPLY
        (
            SELECT TOP (1)
                d.EmpleadoSK
            FROM DW.DimEmpleado d
            WHERE d.IDEmpleado = re.IDEmpleado
              AND df.Fecha >= d.FechaInicio
              AND df.Fecha < d.FechaFin
            ORDER BY d.FechaInicio DESC, d.EmpleadoSK DESC
        ) de

        WHERE NOT EXISTS
        (
            SELECT 1
            FROM DW.FactInventario existente
            WHERE existente.IDMovimiento = f.IDMovimiento
        );
    """

    resultado = conn.execute(text(consulta))

    print(f"Movimientos insertados: {resultado.rowcount:,}")

    return resultado.rowcount


# ============================================================
# EJECUCION PRINCIPAL
# ============================================================

def ejecutar_carga_dw():

    print("\n" + "=" * 55)
    print("INICIANDO CARGA DEL DATA WAREHOUSE")
    print("=" * 55)

    try:

        # Una sola transaccion para las tres tablas
        with engine.begin() as conn:

            print("\nCONEXION EXITOSA A SQL SERVER.")

            # 1. Validaciones previas
            validar_fechas(conn)
            validar_dimensiones(conn)
            validar_cantidades_inventario(conn)

            # 2. Cargar tablas de hechos
            insertadas_ventas = cargar_fact_ventas(conn)

            insertados_pagos = cargar_fact_pagos(conn)

            insertados_inventario = cargar_fact_inventario(conn)

            # 3. Mostrar resumen antes de confirmar
            mostrar_resumen(conn)

            print("\n" + "=" * 55)
            print("RESULTADO DE LA EJECUCION")
            print("=" * 55)

            print(f"Ventas nuevas: {insertadas_ventas:,}")
            print(f"Pagos nuevos: {insertados_pagos:,}")
            print(f"Movimientos nuevos: {insertados_inventario:,}")

            total = (
                insertadas_ventas
                + insertados_pagos
                + insertados_inventario
            )

            print(f"Total de registros nuevos: {total:,}")

        # La transaccion se confirma al salir correctamente
        print("\n" + "=" * 55)
        print("CARGA DEL DATA WAREHOUSE COMPLETADA")
        print("=" * 55)

    except Exception as error:

        print("\n" + "=" * 55)
        print("ERROR EN LA CARGA DEL DATA WAREHOUSE")
        print("=" * 55)

        print(f"Detalle: {error}")
        print("La transaccion fue cancelada si estaba en ejecucion.")
        raise


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    ejecutar_carga_dw()
