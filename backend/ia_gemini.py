
import os
from dotenv import load_dotenv
from google import genai

# Cargar variables del archivo .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("No se encontró GEMINI_API_KEY en el archivo .env")

# Crear cliente de Gemini
cliente_gemini = genai.Client(api_key=API_KEY)

MODELO = "gemini-2.5-flash"


def consultar_gemini(pregunta, contexto):
    instrucciones = f"""
    Eres un asistente especializado en análisis de datos empresariales
    de la empresa EmpresaComercial.

    Tu función es analizar información de ventas, clientes, productos,
    pagos e inventario.

    Reglas:
    - Responde siempre en español.
    - Utiliza únicamente los datos proporcionados.
    - Explica los resultados de manera sencilla y profesional.
    - Si no hay información suficiente, indícalo.
    - No inventes cifras ni estadísticas.

    INFORMACIÓN DE LA EMPRESA:
    {contexto}

    PREGUNTA DEL USUARIO:
    {pregunta}
    """

    respuesta = cliente_gemini.models.generate_content(
        model=MODELO,
        contents=instrucciones
    )

    return respuesta.text
