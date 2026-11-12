
import pandas as pd
from sqlalchemy import text
from conexion import conexion


def consultar_tabla(tabla):

    return pd.read_sql_query(
        text(f"SELECT * FROM Staging.[Stg_{tabla}]"),
        conexion
    )


def validar_calidad():

    print("\n================================")
    print(" INICIANDO CONTROL DE CALIDAD")
    print("================================")

    # Cargar tablas
    clientes = consultar_tabla("Clientes")
    productos = consultar_tabla("Productos")
    ventas = consultar_tabla("Ventas")
    detalles = consultar_tabla("DetallesVenta")
    pagos = consultar_tabla("Pagos")
    empleados = consultar_tabla("Empleados")
    categorias = consultar_tabla("Categorias")
    movimientos = consultar_tabla("MovimientosInventario")

    errores = []

    # 1. Validar clientes
    for columna in ["IDCliente", "DNI", "Nombres", "Apellidos"]:
        cantidad = clientes[columna].isna().sum()

        if cantidad > 0:
            errores.append(
                f"Clientes: {cantidad} registros sin {columna}"
            )

    # 2. Validar productos
    productos_sin_categoria = (
        ~productos["IDCategoria"].isin(
            categorias["IDCategoria"]
        )
    ).sum()

    if productos_sin_categoria > 0:
        errores.append(
            f"Productos: {productos_sin_categoria} categorías inexistentes"
        )

    precios_invalidos = (
        (productos["PrecioCompra"] < 0) |
        (productos["PrecioVenta"] < 0)
    ).sum()

    if precios_invalidos > 0:
        errores.append(
            f"Productos: {precios_invalidos} precios negativos"
        )

    # 3. Validar ventas
    ventas_sin_cliente = (
        ~ventas["IDCliente"].isin(clientes["IDCliente"])
    ).sum()

    if ventas_sin_cliente > 0:
        errores.append(
            f"Ventas: {ventas_sin_cliente} clientes inexistentes"
        )

    ventas_sin_empleado = (
        ~ventas["IDEmpleado"].isin(empleados["IDEmpleado"])
    ).sum()

    if ventas_sin_empleado > 0:
        errores.append(
            f"Ventas: {ventas_sin_empleado} empleados inexistentes"
        )

    # 4. Validar detalles de venta
    detalles_sin_venta = (
        ~detalles["IDVenta"].isin(ventas["IDVenta"])
    ).sum()

    if detalles_sin_venta > 0:
        errores.append(
            f"Detalles: {detalles_sin_venta} ventas inexistentes"
        )

    detalles_sin_producto = (
        ~detalles["IDProducto"].isin(productos["IDProducto"])
    ).sum()

    if detalles_sin_producto > 0:
        errores.append(
            f"Detalles: {detalles_sin_producto} productos inexistentes"
        )

    # 5. Validar pagos
    pagos_sin_venta = (
        ~pagos["IDVenta"].isin(ventas["IDVenta"])
    ).sum()

    if pagos_sin_venta > 0:
        errores.append(
            f"Pagos: {pagos_sin_venta} ventas inexistentes"
        )

    pagos_negativos = (pagos["Monto"] < 0).sum()

    if pagos_negativos > 0:
        errores.append(
            f"Pagos: {pagos_negativos} montos negativos"
        )

    # 6. Validar movimientos de inventario
    movimientos_sin_producto = (
        ~movimientos["IDProducto"].isin(productos["IDProducto"])
    ).sum()

    if movimientos_sin_producto > 0:
        errores.append(
            f"Inventario: {movimientos_sin_producto} productos inexistentes"
        )

    print("\nRESULTADOS DE VALIDACION")

    if errores:

        for error in errores:
            print("ERROR:", error)

    else:

        print("No se encontraron inconsistencias.")

    print("\nValidación finalizada.")

    return errores


if __name__ == "__main__":
    validar_calidad()
