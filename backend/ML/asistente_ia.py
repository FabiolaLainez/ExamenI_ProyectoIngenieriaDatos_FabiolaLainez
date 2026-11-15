import os
from dotenv import load_dotenv
from google import genai
from sqlalchemy import text

from conexion import engine

# Cargar variables del archivo .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("No se encontró GEMINI_API_KEY en el archivo .env")

# Conectar con Gemini
cliente = genai.Client(api_key=API_KEY)

MODELO = "gemini-3.8-flash"


def obtener_contexto_empresa():
    """
    Consulta información resumida del Data Warehouse
    para que Gemini responda usando datos reales.
    """

    with engine.connect() as conexion:

        resumen = conexion.execute(text("""
            SELECT
                COUNT(DISTINCT FV.IDVenta) AS cantidad_ventas,
                SUM(FV.Subtotal) AS ventas_totales,
                SUM(FV.Cantidad) AS unidades_vendidas,
                COUNT(DISTINCT FV.ClienteSK) AS clientes
            FROM DW.FactVentas FV
        """)).mappings().first()

        ventas_categoria = conexion.execute(text("""
            SELECT TOP 10
                DP.NombreCategoria AS categoria,
                SUM(FV.Subtotal) AS ventas
            FROM DW.FactVentas FV
            INNER JOIN DW.DimProducto DP
                ON FV.ProductoSK = DP.ProductoSK
            GROUP BY DP.NombreCategoria
            ORDER BY ventas DESC
        """)).mappings().all()

        ventas_mensuales = conexion.execute(text("""
            SELECT
                DF.Anio AS anio,
                DF.Mes AS mes,
                DF.NombreMes AS nombre_mes,
                SUM(FV.Subtotal) AS ventas
            FROM DW.FactVentas FV
            INNER JOIN DW.DimFecha DF
                ON FV.FechaKey = DF.FechaKey
            GROUP BY DF.Anio, DF.Mes, DF.NombreMes
            ORDER BY DF.Anio, DF.Mes
        """)).mappings().all()

    contexto = {
        "resumen_general": dict(resumen) if resumen else {},
        "ventas_por_categoria": [dict(fila) for fila in ventas_categoria],
        "ventas_mensuales": [dict(fila) for fila in ventas_mensuales]
    }

    return contexto


def consultar_gemini(pregunta: str):
    """
    Envía la pregunta y los datos reales de EmpresaComercial
    a Gemini para generar una respuesta.
    """

    contexto = obtener_contexto_empresa()

    instrucciones = f"""
    Eres un asistente de inteligencia empresarial
    especializado en analizar los datos de EmpresaComercial.

    Tu función es ayudar a la empresa a comprender sus ventas,
    clientes, productos y comportamiento comercial.

    REGLAS:
    - Responde siempre en español.
    - Utiliza los datos proporcionados.
    - No inventes cifras ni información.
    - Si los datos no permiten responder, indícalo.
    - Explica los resultados de manera sencilla y profesional.
    - Ofrece recomendaciones empresariales cuando sea apropiado.
    - Diferencia los datos reales de tus interpretaciones.
    - La moneda oficial de los datos es el lempira hondureño (L).
    - Presenta todos los importes monetarios en L, no en dólares.

    INFORMACIÓN DEL DATA WAREHOUSE:

    {contexto}

    PREGUNTA DEL USUARIO:

    {pregunta}
    """

    respuesta = cliente.models.generate_content(
        model=MODELO,
        contents=instrucciones
    )

    return respuesta.text
