
from datetime import timedelta
from sqlalchemy import text

from conexion import conexion



# CONFIGURACION


ESQUEMA = "Ready"

# VALIDAR RELACIONES DE LOS DATOS


def validar_integridad(conn):

    validaciones = {

        "Ventas sin cliente": """
            SELECT COUNT(*)
            FROM Clean.Clean_Ventas v
            LEFT JOIN Clean.Clean_Clientes c
                ON v.IDCliente = c.IDCliente
            WHERE c.IDCliente IS NULL
        """,

        "Ventas sin empleado": """
            SELECT COUNT(*)
            FROM Clean.Clean_Ventas v
            LEFT JOIN Clean.Clean_Empleados e
                ON v.IDEmpleado = e.IDEmpleado
            WHERE e.IDEmpleado IS NULL
        """,

        "Detalles sin venta": """
            SELECT COUNT(*)
            FROM Clean.Clean_DetallesVenta d
            LEFT JOIN Clean.Clean_Ventas v
                ON d.IDVenta = v.IDVenta
            WHERE v.IDVenta IS NULL
        """,

        "Detalles sin producto": """
            SELECT COUNT(*)
            FROM Clean.Clean_DetallesVenta d
            LEFT JOIN Clean.Clean_Productos p
                ON d.IDProducto = p.IDProducto
            WHERE p.IDProducto IS NULL
        """,

        "Productos sin categoria": """
            SELECT COUNT(*)
            FROM Clean.Clean_Productos p
            LEFT JOIN Clean.Clean_Categorias c
                ON p.IDCategoria = c.IDCategoria
            WHERE c.IDCategoria IS NULL
        """,

        "Pagos sin venta": """
            SELECT COUNT(*)
            FROM Clean.Clean_Pagos p
            LEFT JOIN Clean.Clean_Ventas v
                ON p.IDVenta = v.IDVenta
            WHERE v.IDVenta IS NULL
        """,

        "Movimientos sin producto": """
            SELECT COUNT(*)
            FROM Clean.Clean_MovimientosInventario m
            LEFT JOIN Clean.Clean_Productos p
                ON m.IDProducto = p.IDProducto
            WHERE p.IDProducto IS NULL
        """,

        "Movimientos sin empleado": """
            SELECT COUNT(*)
            FROM Clean.Clean_MovimientosInventario m
            LEFT JOIN Clean.Clean_Empleados e
                ON m.IDEmpleado = e.IDEmpleado
            WHERE e.IDEmpleado IS NULL
        """
    }

    print("\n================================")
    print(" VALIDANDO INTEGRIDAD REFERENCIAL")
    print("================================")

    for nombre, consulta in validaciones.items():

        cantidad = conn.execute(
            text(consulta)
        ).scalar_one()

        print(f"{nombre}: {cantidad}")

        if cantidad > 0:
            raise ValueError(
                f"Se encontraron {cantidad} registros en: {nombre}"
            )

    print("\nTodas las relaciones son validas.")



# GENERAR DIMENSION FECHA


def cargar_dim_fecha(conn):

    print("\nGenerando dimension calendario...")

    consulta = text("""
        SELECT
            MIN(Fecha) AS FechaMinima,
            MAX(Fecha) AS FechaMaxima
        FROM (
            SELECT CAST(FechaVenta AS DATE) AS Fecha
            FROM Clean.Clean_Ventas

            UNION ALL

            SELECT CAST(FechaPago AS DATE)
            FROM Clean.Clean_Pagos

            UNION ALL

            SELECT CAST(FechaMovimiento AS DATE)
            FROM Clean.Clean_MovimientosInventario
        ) AS Fechas
    """)

    resultado = conn.execute(consulta).mappings().one()

    fecha_minima = resultado["FechaMinima"]
    fecha_maxima = resultado["FechaMaxima"]

    if fecha_minima is None or fecha_maxima is None:
        raise ValueError(
            "No se encontraron fechas para generar el calendario."
        )

    nombres_meses = [
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    nombres_dias = [
        "Lunes", "Martes", "Miercoles", "Jueves",
        "Viernes", "Sabado", "Domingo"
    ]

    fechas = []

    fecha_actual = fecha_minima

    while fecha_actual <= fecha_maxima:

        fechas.append({
            "FechaKey": int(fecha_actual.strftime("%Y%m%d")),
            "Fecha": fecha_actual,
            "Anio": fecha_actual.year,
            "Trimestre": (fecha_actual.month - 1) // 3 + 1,
            "Mes": fecha_actual.month,
            "NombreMes": nombres_meses[fecha_actual.month - 1],
            "Dia": fecha_actual.day,
            "DiaSemana": fecha_actual.isoweekday(),
            "NombreDia": nombres_dias[fecha_actual.weekday()],
            "EsFinDeSemana": (
                1 if fecha_actual.weekday() >= 5 else 0
            )
        })

        fecha_actual += timedelta(days=1)

    conn.execute(
        text("""
            INSERT INTO Ready.Ready_DimFecha (
                FechaKey,
                Fecha,
                Anio,
                Trimestre,
                Mes,
                NombreMes,
                Dia,
                DiaSemana,
                NombreDia,
                EsFinDeSemana
            )
            VALUES (
                :FechaKey,
                :Fecha,
                :Anio,
                :Trimestre,
                :Mes,
                :NombreMes,
                :Dia,
                :DiaSemana,
                :NombreDia,
                :EsFinDeSemana
            )
        """),
        fechas
    )

    print("Fechas generadas:", len(fechas))



# CARGAR DIMENSION CLIENTE


def cargar_dim_cliente(conn):

    conn.execute(text("""
        INSERT INTO Ready.Ready_DimCliente (
            IDCliente,
            Nombres,
            Apellidos,
            DNI,
            Telefono,
            Correo,
            Direccion,
            FechaRegistro
        )
        SELECT
            IDCliente,
            Nombres,
            Apellidos,
            DNI,
            Telefono,
            Correo,
            Direccion,
            CAST(FechaRegistro AS DATE)
        FROM Clean.Clean_Clientes
    """))

    print(
        "Clientes cargados:",
        conn.execute(
            text("SELECT COUNT(*) FROM Ready.Ready_DimCliente")
        ).scalar_one()
    )


# CARGAR DIMENSION EMPLEADO


def cargar_dim_empleado(conn):

    conn.execute(text("""
        INSERT INTO Ready.Ready_DimEmpleado (
            IDEmpleado,
            Nombres,
            Apellidos,
            Cargo,
            FechaContratacion
        )
        SELECT
            IDEmpleado,
            Nombres,
            Apellidos,
            Cargo,
            CAST(FechaContratacion AS DATE)
        FROM Clean.Clean_Empleados
    """))

    print(
        "Empleados cargados:",
        conn.execute(
            text("SELECT COUNT(*) FROM Ready.Ready_DimEmpleado")
        ).scalar_one()
    )



# CARGAR DIMENSION PRODUCTO


def cargar_dim_producto(conn):

    conn.execute(text("""
        INSERT INTO Ready.Ready_DimProducto (
            IDProducto,
            NombreProducto,
            Descripcion,
            IDCategoria,
            NombreCategoria,
            DescripcionCategoria,
            PrecioCompra,
            PrecioVenta,
            Estado
        )
        SELECT
            p.IDProducto,
            p.NombreProducto,
            p.Descripcion,
            p.IDCategoria,
            c.NombreCategoria,
            c.Descripcion,
            p.PrecioCompra,
            p.PrecioVenta,
            p.Estado
        FROM Clean.Clean_Productos p
        INNER JOIN Clean.Clean_Categorias c
            ON p.IDCategoria = c.IDCategoria
    """))

    print(
        "Productos cargados:",
        conn.execute(
            text("SELECT COUNT(*) FROM Ready.Ready_DimProducto")
        ).scalar_one()
    )



# CARGAR HECHOS DE VENTAS
# Granularidad: una fila por detalle


def cargar_fact_ventas(conn):

    conn.execute(text("""
        INSERT INTO Ready.Ready_FactVentas (
            IDDetalle,
            IDVenta,
            FechaKey,
            ClienteKey,
            EmpleadoKey,
            ProductoKey,
            Cantidad,
            PrecioUnitario,
            Descuento,
            Subtotal,
            EstadoVenta
        )
        SELECT
            d.IDDetalle,
            v.IDVenta,
            f.FechaKey,
            c.ClienteKey,
            e.EmpleadoKey,
            p.ProductoKey,
            d.Cantidad,
            d.PrecioUnitario,
            d.Descuento,
            d.Subtotal,
            v.EstadoVenta
        FROM Clean.Clean_DetallesVenta d

        INNER JOIN Clean.Clean_Ventas v
            ON d.IDVenta = v.IDVenta

        INNER JOIN Ready.Ready_DimFecha f
            ON CAST(v.FechaVenta AS DATE) = f.Fecha

        INNER JOIN Ready.Ready_DimCliente c
            ON v.IDCliente = c.IDCliente

        INNER JOIN Ready.Ready_DimEmpleado e
            ON v.IDEmpleado = e.IDEmpleado

        INNER JOIN Ready.Ready_DimProducto p
            ON d.IDProducto = p.IDProducto
    """))

    print(
        "Detalles de venta cargados:",
        conn.execute(
            text("SELECT COUNT(*) FROM Ready.Ready_FactVentas")
        ).scalar_one()
    )



# CARGAR HECHOS DE PAGOS
# Granularidad: una fila por pago


def cargar_fact_pagos(conn):

    conn.execute(text("""
        INSERT INTO Ready.Ready_FactPagos (
            IDPago,
            IDVenta,
            FechaKey,
            ClienteKey,
            Monto,
            MetodoPago,
            EstadoPago
        )
        SELECT
            p.IDPago,
            p.IDVenta,
            f.FechaKey,
            c.ClienteKey,
            p.Monto,
            p.MetodoPago,
            p.EstadoPago
        FROM Clean.Clean_Pagos p

        INNER JOIN Clean.Clean_Ventas v
            ON p.IDVenta = v.IDVenta

        INNER JOIN Ready.Ready_DimFecha f
            ON CAST(p.FechaPago AS DATE) = f.Fecha

        INNER JOIN Ready.Ready_DimCliente c
            ON v.IDCliente = c.IDCliente
    """))

    print(
        "Pagos cargados:",
        conn.execute(
            text("SELECT COUNT(*) FROM Ready.Ready_FactPagos")
        ).scalar_one()
    )


# CARGAR HECHOS DE INVENTARIO
# Granularidad: una fila por movimiento


def cargar_fact_inventario(conn):

    conn.execute(text("""
        INSERT INTO Ready.Ready_FactMovimientosInventario (
            IDMovimiento,
            FechaKey,
            ProductoKey,
            EmpleadoKey,
            TipoMovimiento,
            Cantidad,
            Motivo
        )
        SELECT
            m.IDMovimiento,
            f.FechaKey,
            p.ProductoKey,
            e.EmpleadoKey,
            m.TipoMovimiento,
            m.Cantidad,
            m.Motivo
        FROM Clean.Clean_MovimientosInventario m

        INNER JOIN Ready.Ready_DimFecha f
            ON CAST(m.FechaMovimiento AS DATE) = f.Fecha

        INNER JOIN Ready.Ready_DimProducto p
            ON m.IDProducto = p.IDProducto

        INNER JOIN Ready.Ready_DimEmpleado e
            ON m.IDEmpleado = e.IDEmpleado
    """))

    print(
        "Movimientos de inventario cargados:",
        conn.execute(
            text("""
                SELECT COUNT(*)
                FROM Ready.Ready_FactMovimientosInventario
            """)
        ).scalar_one()
    )



# PROCESO PRINCIPAL DE CARGA READY


def cargar_ready():

    print("\n================================")
    print(" INICIANDO READY / INTEGRATION")
    print("================================")

    # Una sola transaccion para toda la carga
    with conexion.begin() as conn:

        # 1. Validar relaciones
        validar_integridad(conn)

        # 2. Limpiar tablas anteriores
        print("\nLimpiando carga anterior...")

        conn.execute(text("""
            DELETE FROM Ready.Ready_FactMovimientosInventario;
            DELETE FROM Ready.Ready_FactPagos;
            DELETE FROM Ready.Ready_FactVentas;

            DELETE FROM Ready.Ready_DimProducto;
            DELETE FROM Ready.Ready_DimEmpleado;
            DELETE FROM Ready.Ready_DimCliente;
            DELETE FROM Ready.Ready_DimFecha;
        """))

        # Reiniciar claves sustitutas
        conn.exec_driver_sql("""
            DBCC CHECKIDENT ('Ready.Ready_DimCliente', RESEED, 0);
            DBCC CHECKIDENT ('Ready.Ready_DimEmpleado', RESEED, 0);
            DBCC CHECKIDENT ('Ready.Ready_DimProducto', RESEED, 0);

            DBCC CHECKIDENT ('Ready.Ready_FactVentas', RESEED, 0);
            DBCC CHECKIDENT ('Ready.Ready_FactPagos', RESEED, 0);
            DBCC CHECKIDENT (
                'Ready.Ready_FactMovimientosInventario',
                RESEED,
                0
            );
        """)

        # 3. Cargar dimensiones
        print("\nCARGANDO DIMENSIONES")

        cargar_dim_fecha(conn)
        cargar_dim_cliente(conn)
        cargar_dim_empleado(conn)
        cargar_dim_producto(conn)

        # 4. Cargar tablas de hechos
        print("\nCARGANDO TABLAS DE HECHOS")

        cargar_fact_ventas(conn)
        cargar_fact_pagos(conn)
        cargar_fact_inventario(conn)

        # 5. Resumen de carga
        print("\n================================")
        print(" RESUMEN READY")
        print("================================")

        tablas = [
            "Ready_DimFecha",
            "Ready_DimCliente",
            "Ready_DimEmpleado",
            "Ready_DimProducto",
            "Ready_FactVentas",
            "Ready_FactPagos",
            "Ready_FactMovimientosInventario"
        ]

        for tabla in tablas:

            cantidad = conn.execute(
                text(f"SELECT COUNT(*) FROM Ready.{tabla}")
            ).scalar_one()

            print(f"{tabla}: {cantidad}")

    # La transaccion se confirma al salir correctamente
    print("\n================================")
    print(" CARGA READY COMPLETADA")
    print("================================")



# EJECUCION INDEPENDIENTE


if __name__ == "__main__":

    cargar_ready()
