
from sqlalchemy import text
from datetime import date

from conexion import conexion



# CONFIGURACION GENERAL


FECHA_FIN_ABIERTA = date(9999, 12, 31)



# 1. DIMENSION FECHA


def cargar_dw_fecha(conn):

    print("\nCARGANDO DW.DimFecha...")

    fechas = conn.execute(text("""
        SELECT
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
        FROM Ready.Ready_DimFecha
    """)).mappings().all()

    insertadas = 0

    for fecha in fechas:

        existe = conn.execute(text("""
            SELECT COUNT(*)
            FROM DW.DimFecha
            WHERE FechaKey = :fecha_key
        """), {
            "fecha_key": fecha["FechaKey"]
        }).scalar_one()

        if existe == 0:

            conn.execute(text("""
                INSERT INTO DW.DimFecha (
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
            """), dict(fecha))

            insertadas += 1

    total = conn.execute(text("""
        SELECT COUNT(*)
        FROM DW.DimFecha
    """)).scalar_one()

    print("Fechas leidas:", len(fechas))
    print("Fechas insertadas:", insertadas)
    print("Total de fechas en DW:", total)


# 2. DIMENSION CLIENTE - SCD TIPO 2

def cargar_dw_cliente(conn):

    print("\nCARGANDO DW.DimCliente...")

    clientes = conn.execute(text("""
        SELECT
            IDCliente,
            Nombres,
            Apellidos,
            DNI,
            Telefono,
            Correo,
            Direccion,
            FechaRegistro
        FROM Ready.Ready_DimCliente
    """)).mappings().all()

    insertados = 0
    actualizados = 0
    sin_cambios = 0

    fecha_actual = date.today()

    atributos = [
        "Nombres",
        "Apellidos",
        "DNI",
        "Telefono",
        "Correo",
        "Direccion",
        "FechaRegistro"
    ]

    for cliente in clientes:

        existente = conn.execute(text("""
            SELECT TOP 1 *
            FROM DW.DimCliente
            WHERE IDCliente = :id_cliente
              AND EsActual = 1
        """), {
            "id_cliente": cliente["IDCliente"]
        }).mappings().first()

        # CLIENTE NUEVO

        if existente is None:

            fecha_inicio = (
                cliente["FechaRegistro"]
                or fecha_actual
            )

            conn.execute(text("""
                INSERT INTO DW.DimCliente (
                    IDCliente,
                    Nombres,
                    Apellidos,
                    DNI,
                    Telefono,
                    Correo,
                    Direccion,
                    FechaRegistro,
                    FechaInicio,
                    FechaFin,
                    EsActual
                )
                VALUES (
                    :IDCliente,
                    :Nombres,
                    :Apellidos,
                    :DNI,
                    :Telefono,
                    :Correo,
                    :Direccion,
                    :FechaRegistro,
                    :FechaInicio,
                    :FechaFin,
                    1
                )
            """), {
                **dict(cliente),
                "FechaInicio": fecha_inicio,
                "FechaFin": FECHA_FIN_ABIERTA
            })

            insertados += 1
            continue

        # COMPARAR ATRIBUTOS

        cambio = any(
            existente[campo] != cliente[campo]
            for campo in atributos
        )

        if not cambio:

            sin_cambios += 1
            continue

        # SI LA VERSION ACTUAL COMENZO HOY,
        # ACTUALIZAR ESA MISMA VERSION

        if existente["FechaInicio"] >= fecha_actual:

            conn.execute(text("""
                UPDATE DW.DimCliente
                SET
                    Nombres = :Nombres,
                    Apellidos = :Apellidos,
                    DNI = :DNI,
                    Telefono = :Telefono,
                    Correo = :Correo,
                    Direccion = :Direccion,
                    FechaRegistro = :FechaRegistro
                WHERE ClienteSK = :ClienteSK
            """), {
                **dict(cliente),
                "ClienteSK": existente["ClienteSK"]
            })

        else:

            # CERRAR VERSION ANTERIOR
            # FechaFin es exclusiva.

            conn.execute(text("""
                UPDATE DW.DimCliente
                SET
                    FechaFin = :FechaFin,
                    EsActual = 0
                WHERE ClienteSK = :ClienteSK
            """), {
                "FechaFin": fecha_actual,
                "ClienteSK": existente["ClienteSK"]
            })

            # CREAR NUEVA VERSION

            conn.execute(text("""
                INSERT INTO DW.DimCliente (
                    IDCliente,
                    Nombres,
                    Apellidos,
                    DNI,
                    Telefono,
                    Correo,
                    Direccion,
                    FechaRegistro,
                    FechaInicio,
                    FechaFin,
                    EsActual
                )
                VALUES (
                    :IDCliente,
                    :Nombres,
                    :Apellidos,
                    :DNI,
                    :Telefono,
                    :Correo,
                    :Direccion,
                    :FechaRegistro,
                    :FechaInicio,
                    :FechaFin,
                    1
                )
            """), {
                **dict(cliente),
                "FechaInicio": fecha_actual,
                "FechaFin": FECHA_FIN_ABIERTA
            })

        actualizados += 1

    total_actuales = conn.execute(text("""
        SELECT COUNT(*)
        FROM DW.DimCliente
        WHERE EsActual = 1
    """)).scalar_one()

    print("\nRESUMEN DIMENSION CLIENTE")
    print("Clientes leidos:", len(clientes))
    print("Nuevos clientes:", insertados)
    print("Clientes actualizados:", actualizados)
    print("Sin cambios:", sin_cambios)
    print("Versiones actuales:", total_actuales)



# 3. DIMENSION EMPLEADO - SCD TIPO 2


def cargar_dw_empleado(conn):

    print("\nCARGANDO DW.DimEmpleado...")

    empleados = conn.execute(text("""
        SELECT
            IDEmpleado,
            Nombres,
            Apellidos,
            Cargo,
            FechaContratacion
        FROM Ready.Ready_DimEmpleado
    """)).mappings().all()

    insertados = 0
    actualizados = 0
    sin_cambios = 0

    fecha_actual = date.today()

    atributos = [
        "Nombres",
        "Apellidos",
        "Cargo",
        "FechaContratacion"
    ]

    for empleado in empleados:

        existente = conn.execute(text("""
            SELECT TOP 1 *
            FROM DW.DimEmpleado
            WHERE IDEmpleado = :id_empleado
              AND EsActual = 1
        """), {
            "id_empleado": empleado["IDEmpleado"]
        }).mappings().first()

        # EMPLEADO NUEVO

        if existente is None:

            fecha_inicio = (
                empleado["FechaContratacion"]
                or fecha_actual
            )

            conn.execute(text("""
                INSERT INTO DW.DimEmpleado (
                    IDEmpleado,
                    Nombres,
                    Apellidos,
                    Cargo,
                    FechaContratacion,
                    FechaInicio,
                    FechaFin,
                    EsActual
                )
                VALUES (
                    :IDEmpleado,
                    :Nombres,
                    :Apellidos,
                    :Cargo,
                    :FechaContratacion,
                    :FechaInicio,
                    :FechaFin,
                    1
                )
            """), {
                **dict(empleado),
                "FechaInicio": fecha_inicio,
                "FechaFin": FECHA_FIN_ABIERTA
            })

            insertados += 1
            continue

        # COMPARAR ATRIBUTOS

        cambio = any(
            existente[campo] != empleado[campo]
            for campo in atributos
        )

        if not cambio:

            sin_cambios += 1
            continue

        # ACTUALIZAR VERSION CREADA HOY

        if existente["FechaInicio"] >= fecha_actual:

            conn.execute(text("""
                UPDATE DW.DimEmpleado
                SET
                    Nombres = :Nombres,
                    Apellidos = :Apellidos,
                    Cargo = :Cargo,
                    FechaContratacion = :FechaContratacion
                WHERE EmpleadoSK = :EmpleadoSK
            """), {
                **dict(empleado),
                "EmpleadoSK": existente["EmpleadoSK"]
            })

        else:

            # CERRAR VERSION ANTERIOR

            conn.execute(text("""
                UPDATE DW.DimEmpleado
                SET
                    FechaFin = :FechaFin,
                    EsActual = 0
                WHERE EmpleadoSK = :EmpleadoSK
            """), {
                "FechaFin": fecha_actual,
                "EmpleadoSK": existente["EmpleadoSK"]
            })

            # CREAR NUEVA VERSION

            conn.execute(text("""
                INSERT INTO DW.DimEmpleado (
                    IDEmpleado,
                    Nombres,
                    Apellidos,
                    Cargo,
                    FechaContratacion,
                    FechaInicio,
                    FechaFin,
                    EsActual
                )
                VALUES (
                    :IDEmpleado,
                    :Nombres,
                    :Apellidos,
                    :Cargo,
                    :FechaContratacion,
                    :FechaInicio,
                    :FechaFin,
                    1
                )
            """), {
                **dict(empleado),
                "FechaInicio": fecha_actual,
                "FechaFin": FECHA_FIN_ABIERTA
            })

        actualizados += 1

    total_actuales = conn.execute(text("""
        SELECT COUNT(*)
        FROM DW.DimEmpleado
        WHERE EsActual = 1
    """)).scalar_one()

    print("\nRESUMEN DIMENSION EMPLEADO")
    print("Empleados leidos:", len(empleados))
    print("Nuevos empleados:", insertados)
    print("Empleados actualizados:", actualizados)
    print("Sin cambios:", sin_cambios)
    print("Versiones actuales:", total_actuales)



# 4. DIMENSION PRODUCTO - SCD TIPO 2


def cargar_dw_producto(conn):

    print("\nCARGANDO DW.DimProducto...")

    productos = conn.execute(text("""
        SELECT
            IDProducto,
            NombreProducto,
            Descripcion,
            IDCategoria,
            NombreCategoria,
            DescripcionCategoria,
            PrecioCompra,
            PrecioVenta,
            Estado
        FROM Ready.Ready_DimProducto
    """)).mappings().all()

    insertados = 0
    actualizados = 0
    sin_cambios = 0

    fecha_actual = date.today()

    atributos = [
        "NombreProducto",
        "Descripcion",
        "IDCategoria",
        "NombreCategoria",
        "DescripcionCategoria",
        "PrecioCompra",
        "PrecioVenta",
        "Estado"
    ]

    for producto in productos:

        existente = conn.execute(text("""
            SELECT TOP 1 *
            FROM DW.DimProducto
            WHERE IDProducto = :id_producto
              AND EsActual = 1
        """), {
            "id_producto": producto["IDProducto"]
        }).mappings().first()

        # PRODUCTO NUEVO

        if existente is None:

            conn.execute(text("""
                INSERT INTO DW.DimProducto (
                    IDProducto,
                    NombreProducto,
                    Descripcion,
                    IDCategoria,
                    NombreCategoria,
                    DescripcionCategoria,
                    PrecioCompra,
                    PrecioVenta,
                    Estado,
                    FechaInicio,
                    FechaFin,
                    EsActual
                )
                VALUES (
                    :IDProducto,
                    :NombreProducto,
                    :Descripcion,
                    :IDCategoria,
                    :NombreCategoria,
                    :DescripcionCategoria,
                    :PrecioCompra,
                    :PrecioVenta,
                    :Estado,
                    :FechaInicio,
                    :FechaFin,
                    1
                )
            """), {
                **dict(producto),
                "FechaInicio": fecha_actual,
                "FechaFin": FECHA_FIN_ABIERTA
            })

            insertados += 1
            continue

        # COMPARAR ATRIBUTOS

        cambio = any(
            existente[campo] != producto[campo]
            for campo in atributos
        )

        if not cambio:

            sin_cambios += 1
            continue

        # ACTUALIZAR VERSION CREADA HOY

        if existente["FechaInicio"] >= fecha_actual:

            conn.execute(text("""
                UPDATE DW.DimProducto
                SET
                    NombreProducto = :NombreProducto,
                    Descripcion = :Descripcion,
                    IDCategoria = :IDCategoria,
                    NombreCategoria = :NombreCategoria,
                    DescripcionCategoria = :DescripcionCategoria,
                    PrecioCompra = :PrecioCompra,
                    PrecioVenta = :PrecioVenta,
                    Estado = :Estado
                WHERE ProductoSK = :ProductoSK
            """), {
                **dict(producto),
                "ProductoSK": existente["ProductoSK"]
            })

        else:

            # CERRAR VERSION ANTERIOR

            conn.execute(text("""
                UPDATE DW.DimProducto
                SET
                    FechaFin = :FechaFin,
                    EsActual = 0
                WHERE ProductoSK = :ProductoSK
            """), {
                "FechaFin": fecha_actual,
                "ProductoSK": existente["ProductoSK"]
            })

            # CREAR NUEVA VERSION

            conn.execute(text("""
                INSERT INTO DW.DimProducto (
                    IDProducto,
                    NombreProducto,
                    Descripcion,
                    IDCategoria,
                    NombreCategoria,
                    DescripcionCategoria,
                    PrecioCompra,
                    PrecioVenta,
                    Estado,
                    FechaInicio,
                    FechaFin,
                    EsActual
                )
                VALUES (
                    :IDProducto,
                    :NombreProducto,
                    :Descripcion,
                    :IDCategoria,
                    :NombreCategoria,
                    :DescripcionCategoria,
                    :PrecioCompra,
                    :PrecioVenta,
                    :Estado,
                    :FechaInicio,
                    :FechaFin,
                    1
                )
            """), {
                **dict(producto),
                "FechaInicio": fecha_actual,
                "FechaFin": FECHA_FIN_ABIERTA
            })

        actualizados += 1

    total_actuales = conn.execute(text("""
        SELECT COUNT(*)
        FROM DW.DimProducto
        WHERE EsActual = 1
    """)).scalar_one()

    print("\nRESUMEN DIMENSION PRODUCTO")
    print("Productos leidos:", len(productos))
    print("Nuevos productos:", insertados)
    print("Productos actualizados:", actualizados)
    print("Sin cambios:", sin_cambios)
    print("Versiones actuales:", total_actuales)


# 5. PROCESO PRINCIPAL DATA WAREHOUSE


def cargar_dw():

    print("\n================================")
    print(" INICIANDO CARGA DATA WAREHOUSE")
    print("================================")

    try:

        with conexion.begin() as conn:

            # DIMENSIONES

            cargar_dw_fecha(conn)

            cargar_dw_cliente(conn)

            cargar_dw_empleado(conn)

            cargar_dw_producto(conn)

        print("\n================================")
        print(" CARGA DW COMPLETADA")
        print("================================")

    except Exception as error:

        print("\n================================")
        print(" ERROR EN LA CARGA DW")
        print("================================")

        print("Detalle:", error)

        raise



# 6. EJECUCION

if __name__ == "__main__":

    cargar_dw()
