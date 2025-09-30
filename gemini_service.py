import os
import base64
import io
import re

# Imports opcionales para IA
try:
    import google.generativeai as genai
    from PIL import Image
    import requests
    from dotenv import load_dotenv
    GEMINI_AVAILABLE = True
    load_dotenv()
    print("🤖 Dependencias de IA disponibles")
except ImportError as e:
    GEMINI_AVAILABLE = False
    print(f"⚠️ Dependencias de IA no disponibles: {e}")
    print("La aplicación funcionará en modo básico sin IA")

class GeminiService:
    def __init__(self):
        if not GEMINI_AVAILABLE:
            print("🔄 Modo básico: IA no disponible")
            return

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            raise ValueError("GEMINI_API_KEY no configurada")

        try:
            genai.configure(api_key=api_key)
            # Usar el mismo modelo para ambas funciones (visión y texto)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Servicio de Gemini inicializado correctamente")
        except Exception as e:
            raise ValueError(f"Error configurando Gemini: {e}")

    def extract_client_info_from_image(self, image_data, image_format='jpeg'):
        """
        Extrae información del cliente desde una imagen usando Gemini
        """
        if not GEMINI_AVAILABLE:
            return {"nombre": "Cliente", "telefono": "", "tiene_cargador": False}

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
Analiza esta imagen de un equipo electrónico (laptop, computadora, tablet, etc.) y extrae la siguiente información si está visible:

1. NOMBRE DEL CLIENTE: Busca cualquier etiqueta, sticker, papel o texto que indique el nombre del propietario
2. NÚMERO DE WHATSAPP: Busca números de teléfono con formato +57, +1, etc. o números de 10 dígitos
3. CARGADOR: Determina si hay un cargador visible en la imagen (cable de alimentación, adaptador de corriente)
4. TIPO DE EQUIPO: Identifica qué tipo de dispositivo es (laptop, PC, tablet, etc.)
5. MARCA Y MODELO: Si es posible identificar la marca y modelo del equipo

IMPORTANTE: 
- Si no puedes encontrar información específica, responde "NO_ENCONTRADO"
- Para el cargador, responde solo "SÍ" o "NO"
- Para números de WhatsApp, incluye el código de país si está visible

            Responde ÚNICAMENTE con un JSON válido en este formato exacto:
            {
                "nombre": "Nombre del cliente",
                "telefono": "número de teléfono",
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

                # Extraer información del cargador
                tiene_cargador = bool(re.search(r'(?:cargador|charger).*?(?:sí|si|yes|tiene|incluye)', text, re.IGNORECASE))

                # Si menciona "sin cargador" o "no incluye", marcar como false
                if re.search(r'(?:sin cargador|no incluye|no tiene)', text, re.IGNORECASE):
                    tiene_cargador = False

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
        if not GEMINI_AVAILABLE:
            return "Transcripción no disponible - dependencias de IA faltantes"

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
