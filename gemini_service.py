import google.generativeai as genai
import os
import base64
import io
from PIL import Image
import requests
from dotenv import load_dotenv

load_dotenv()

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

    def extract_client_info_from_image(self, image_data, image_format='jpeg'):
        """
        Extrae información del cliente desde una imagen usando Gemini
        """
        try:
            # Convertir base64 a imagen PIL si es necesario
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                # Es base64 con data URL
                header, encoded = image_data.split(",", 1)
                image_data = base64.b64decode(encoded)

            # Crear imagen PIL
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = image_data

            # Crear prompt para extracción de información
            prompt = """
Analiza esta imagen de un equipo electrónico y extrae información específica:

1. NOMBRE DEL CLIENTE: Busca etiquetas, stickers, papeles o cualquier texto que indique el nombre del propietario del equipo.

2. NÚMERO DE WHATSAPP/TELÉFONO: Busca números de teléfono visibles, especialmente con códigos de país como +57, +1, etc.

3. CARGADOR: ES MUY IMPORTANTE detectar si hay un cargador o adaptador de corriente visible en la imagen.
   - Busca cables de alimentación, adaptadores, cargadores USB, transformadores
   - Si ves cualquier tipo de cable o dispositivo de carga conectado al equipo, marca como SÍ
   - Si no hay ningún elemento de carga visible, marca como NO
   - Considera también si hay referencias escritas a "cargador incluido" o "sin cargador"

INSTRUCCIONES ESPECÍFICAS PARA CARGADOR:
- Si hay un cable negro/gris conectado al equipo → SÍ
- Si hay un adaptador rectangular (de pared) → SÍ
- Si hay un cargador USB visible → SÍ
- Si NO hay ningún elemento de carga visible → NO
- Si hay duda, pero parece que podría haber un cargador parcialmente visible → SÍ

IMPORTANTE:
- Para "tiene_cargador" usa solo true (SÍ) o false (NO)
- Si no encuentras nombre, usa "Cliente"
- Si no encuentras teléfono, deja vacío ""

Responde ÚNICAMENTE con JSON válido:
{
    "nombre": "Nombre encontrado o 'Cliente'",
    "telefono": "número encontrado o vacío",
    "tiene_cargador": true/false
}
            """

            # Enviar a Gemini
            response = self.model.generate_content([prompt, image])

            if not response.text:
                return {"nombre": "Cliente", "telefono": "", "tiene_cargador": False}

            # Intentar parsear JSON de la respuesta
            import json
            import re

            try:
                # Primero intentar parsear directamente como JSON
                result = json.loads(response.text.strip())
                return result
            except json.JSONDecodeError:
                # Si no puede parsear JSON, extraer manualmente con regex y parsing inteligente
                text = response.text.lower()

                # Extraer nombre y limpiar (solo letras y espacios)
                nombre_match = re.search(r'nombre[:\s]*([^\n\r]+)', text, re.IGNORECASE)
                nombre = nombre_match.group(1).strip() if nombre_match else "Cliente"
                # Limpiar nombre: solo letras, espacios y algunos caracteres especiales comunes en nombres
                nombre = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]', '', nombre).strip()
                # Si queda vacío después de limpiar, usar valor por defecto
                if not nombre or nombre.isspace():
                    nombre = "Cliente"

                # Extraer teléfono/WhatsApp
                telefono_match = re.search(r'(?:telefono|teléfono|whatsapp|phone)[:\s]*([^\n\r]+)', text, re.IGNORECASE)
                telefono = telefono_match.group(1).strip() if telefono_match else ""

                # Limpiar teléfono (quitar espacios, mantener números y +)
                telefono = re.sub(r'[^\d+\-\s]', '', telefono).strip()

                # Extraer información del cargador con lógica más robusta
                tiene_cargador = False

                # Buscar indicadores positivos de cargador
                indicadores_cargador = [
                    r'(?:cargador|charger|adaptador).*?(?:sí|si|yes|true|incluye|tiene|presente|visible)',
                    r'(?:cable|cord).*?(?:alimentación|power|energía)',
                    r'(?:usb).*?(?:charger|cargador)',
                    r'(?:power).*?(?:supply|adapter|cable)',
                    r'(?:con cargador|incluye cargador|cargador incluido)',
                    r'(?:sí.*cargador|cargador.*sí)',
                    r'(?:true|cargador.*true)',
                    r'(?:cable.*conectado|cable.*visible)',
                    r'(?:adaptador.*visible|transformador.*visible)',
                    r'(?:fuente.*alimentación|power.*source)'
                ]

                # Buscar indicadores negativos de cargador
                indicadores_sin_cargador = [
                    r'(?:sin cargador|no incluye|no tiene)',
                    r'(?:cargador.*no|cargador.*false)',
                    r'(?:false.*cargador)',
                    r'(?:no.*cargador|cargador.*no)',
                    r'(?:sin.*cable|no.*cable)',
                    r'(?:falta.*cargador|cargador.*falta)'
                ]

                # Verificar indicadores positivos
                for patron in indicadores_cargador:
                    if re.search(patron, text, re.IGNORECASE):
                        tiene_cargador = True
                        break

                # Si hay indicadores positivos pero también negativos, priorizar negativo
                for patron in indicadores_sin_cargador:
                    if re.search(patron, text, re.IGNORECASE):
                        tiene_cargador = False
                        break

                # Si no hay indicadores claros, buscar palabras clave relacionadas con cargadores
                if not any(re.search(patron, text, re.IGNORECASE) for patron in indicadores_cargador + indicadores_sin_cargador):
                    # Buscar palabras sueltas relacionadas con cargadores
                    palabras_cargador = ['cable', 'adaptador', 'transformador', 'charger', 'power', 'usb', 'alimentación']
                    if any(palabra in text for palabra in palabras_cargador):
                        # Si encuentra palabras relacionadas, asumir que hay cargador
                        tiene_cargador = True

                # Log para debugging (solo en desarrollo)
                print(f"🤖 IA procesó: nombre='{nombre}', telefono='{telefono}', tiene_cargador={tiene_cargador}")
                print(f"   Texto completo de IA: {text[:200]}...")  # Primeros 200 caracteres

                return {
                    "nombre": nombre,
                    "telefono": telefono,
                    "tiene_cargador": tiene_cargador
                }

        except Exception as e:
            print(f"Error procesando imagen: {e}")
            return {"nombre": "Cliente", "telefono": "", "tiene_cargador": False}

    def transcribe_audio(self, audio_data):
        """
        Transcribe audio usando Gemini
        """
        import tempfile
        import os

        temp_file = None
        try:
            # Guardar audio en archivo temporal
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            # Crear prompt para transcripción
            prompt = """
            Transcribe exactamente lo que dice la persona en este audio.
            Solo devuelve el texto transcrito, sin explicaciones adicionales.
            Si no puedes transcribir claramente, devuelve un mensaje indicando que no se pudo entender.
            """

            # Enviar audio a Gemini
            audio_file = genai.upload_file(temp_file_path, mime_type='audio/wav')
            response = self.model.generate_content([prompt, audio_file])

            # Limpiar archivo temporal
            genai.delete_file(audio_file.name)

            return response.text.strip() if response.text else "No se pudo transcribir el audio"

        except Exception as e:
            print(f"Error transcribiendo audio: {e}")
            return f"Error al transcribir el audio: {e}"
        finally:
            # Limpiar archivo temporal del sistema
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
