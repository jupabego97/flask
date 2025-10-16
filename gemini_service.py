import google.generativeai as genai
import os
import base64
import io
from PIL import Image
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

load_dotenv()

# ========== PROMPT CONSTANTE (optimizado y cacheado) ==========
PROMPT_EXTRACT_INFO = """
Analiza esta imagen de un equipo electrónico y extrae:

1. NOMBRE DEL CLIENTE: Busca en etiquetas, stickers o papeles
2. TELÉFONO/WHATSAPP: Busca números con códigos como +57, +1, etc.
3. CARGADOR: ¿Hay cable, adaptador o cargador visible?
   - Cable negro/gris conectado → SÍ
   - Adaptador de pared → SÍ
   - Sin elementos de carga → NO

Responde SOLO con JSON:
{
    "nombre": "Nombre o 'Cliente'",
    "telefono": "número o vacío",
    "tiene_cargador": true/false
}
"""

class GeminiService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            raise ValueError("GEMINI_API_KEY no configurada")
        
        try:
            genai.configure(api_key=api_key)
            # Usar el mismo modelo para ambas funciones (visión y texto)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        except Exception as e:
            raise ValueError(f"Error configurando Gemini: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def extract_client_info_from_image(self, image_data, image_format='jpeg'):
        """Extrae información del cliente desde una imagen usando Gemini con retry"""
        try:
            # Convertir base64 a imagen PIL si es necesario
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                header, encoded = image_data.split(",", 1)
                image_data = base64.b64decode(encoded)
            
            # Crear imagen PIL
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = image_data
            
            # Usar prompt optimizado (constante global)
            # Enviar a Gemini con timeout implícito (retry maneja timeouts)
            response = self.model.generate_content([PROMPT_EXTRACT_INFO, image])

            if not response.text:
                logger.warning("Gemini no devolvió respuesta")
                return {"nombre": "Cliente", "telefono": "", "tiene_cargador": False}
            
            # Intentar parsear JSON de la respuesta
            import json
            import re
            
            try:
                # Intentar parsear directamente como JSON
                result = json.loads(response.text.strip())
                logger.debug(f"Resultado de Gemini: {result}")
                return result
            except json.JSONDecodeError:
                # Fallback: extraer manualmente con regex simplificado
                logger.warning("Respuesta de Gemini no es JSON válido, usando fallback")
                text = response.text.lower()
                
                # Extraer nombre
                nombre_match = re.search(r'nombre[:\s]*["\']?([^"\'\n\r]+)', text, re.IGNORECASE)
                nombre = nombre_match.group(1).strip() if nombre_match else "Cliente"
                nombre = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]', '', nombre).strip() or "Cliente"
                
                # Extraer teléfono
                telefono_match = re.search(r'telefono[:\s]*["\']?([^"\'\n\r]+)', text, re.IGNORECASE)
                telefono = telefono_match.group(1).strip() if telefono_match else ""
                telefono = re.sub(r'[^\d+\-\s]', '', telefono).strip()
                
                # Extraer cargador (simplificado)
                tiene_cargador = bool(re.search(r'tiene_cargador[:\s]*(true|sí|si|yes)', text, re.IGNORECASE))
                
                result = {
                    "nombre": nombre,
                    "telefono": telefono,
                    "tiene_cargador": tiene_cargador
                }
                
                logger.debug(f"Resultado parseado manualmente: {result}")
                return result
        
        except Exception as e:
            logger.exception(f"Error procesando imagen: {e}")
            return {"nombre": "Cliente", "telefono": "", "tiene_cargador": False}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def transcribe_audio(self, audio_data):
        """Transcribe audio usando Gemini con retry y mejor cleanup"""
        import tempfile
        import os
        import atexit
        
        temp_file_path = None
        uploaded_file = None
        
        try:
            # Guardar audio en archivo temporal
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Registrar para limpieza automática
            atexit.register(lambda: os.path.exists(temp_file_path) and os.unlink(temp_file_path))
            
            # Prompt optimizado
            prompt = "Transcribe exactamente lo que dice la persona. Solo el texto, sin explicaciones."
            
            # Enviar audio a Gemini
            uploaded_file = genai.upload_file(temp_file_path, mime_type='audio/wav')
            response = self.model.generate_content([prompt, uploaded_file])
            
            # Limpiar archivo de Gemini
            if uploaded_file:
                genai.delete_file(uploaded_file.name)
            
            result = response.text.strip() if response.text else "No se pudo transcribir el audio"
            logger.debug(f"Audio transcrito: {result[:50]}...")
            
            return result
        
        except Exception as e:
            logger.exception(f"Error transcribiendo audio: {e}")
            return f"Error al transcribir el audio: {e}"
        
        finally:
            # Limpiar archivo temporal del sistema
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.debug("Archivo temporal de audio eliminado")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar archivo temporal: {e}")
