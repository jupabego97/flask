# Configuración de Gemini AI

## Requisitos

Para usar las funcionalidades de IA en la aplicación, necesitas configurar una clave API de Google Gemini.

## Pasos para configurar Gemini:

1. **Obtén una clave API de Gemini:**
   - Ve a https://makersuite.google.com/app/apikey
   - Crea una cuenta si no tienes una
   - Genera una nueva clave API

2. **Configura las variables de entorno:**
   - Crea un archivo `.env` en la raíz del proyecto
   - Agrega las siguientes variables:

   ```env
   # Configuración de la base de datos
   DATABASE_URL=sqlite:///reparaciones_it_migrated.db

   # Clave de API de Gemini
   GEMINI_API_KEY=tu_clave_api_aqui
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## Funcionalidades de IA implementadas:

### 1. Procesamiento de Imágenes
- **OCR inteligente**: Extrae nombre, teléfono y si incluye cargador del recibo
- **Análisis contextual**: Gemini analiza el contenido de la imagen para identificar información relevante

### 2. Transcripción de Voz
- **Grabación de audio**: Permite grabar voz para describir el problema
- **Transcripción automática**: Convierte audio a texto usando Gemini

## Cómo usar el flujo con IA:

1. **Paso 1**: Captura foto del recibo (cámara o archivo)
2. **Paso 2**: IA extrae datos automáticamente
3. **Paso 3**: Graba voz o escribe la descripción del problema
4. **Paso 4**: Verifica y confirma la creación

## Notas importantes:

- La aplicación funciona sin Gemini, pero las funcionalidades de IA estarán deshabilitadas
- Asegúrate de tener permisos de cámara y micrófono en tu navegador
- La clave API es gratuita para uso básico de Gemini
