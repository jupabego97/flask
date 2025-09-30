# 🚀 Sistema de Reparaciones IT con IA

Aplicación web avanzada para gestionar reparaciones de equipos tecnológicos usando un tablero Kanban inteligente con integración de IA de Google Gemini.

## ✨ Características Principales

### 🤖 **Inteligencia Artificial Integrada**
- **OCR automático**: Extrae nombre, teléfono y detalles del equipo desde fotos de recibos
- **Transcripción de voz**: Convierte audio a texto para describir problemas
- **Análisis inteligente**: Detecta automáticamente si incluye cargador
- **Procesamiento automático**: Sin necesidad de escribir manualmente

### 📱 **Interfaz Moderna y Responsive**
- **4 columnas Kanban**: Ingresado, Diagnosticada, Para entregar, Listos
- **Información completa de cada tarjeta**:
  - Nombre del propietario (extraído por IA)
  - Tipo de problema (voz → texto automático)
  - Número de WhatsApp (reconocido por IA)
  - Fecha de inicio (automática)
  - Fecha límite (configurable)
  - Foto del equipo
  - Estado del cargador
- **Funcionalidad WhatsApp**: Botón para enviar mensajes directamente
- **Arrastrar y soltar**: Mover tarjetas entre columnas
- **Diseño móvil**: Optimizado para tablets y smartphones

## 🚀 Despliegue

### Opción 1: Render (Recomendado - Fácil Setup)
```bash
# 1. Crear cuenta en Render: https://render.com
# 2. Conectar repositorio de GitHub
# 3. Render configura automáticamente PostgreSQL + SSL + HTTPS
# 4. Agregar variable: GEMINI_API_KEY=tu_clave (opcional)
# ¡Listo! URL automática: https://tu-app.onrender.com
```

### Opción 2: Railway (Escalable - Producción Avanzada)
```bash
# 1. Crear cuenta en Railway: https://railway.app
# 2. Conectar repositorio de GitHub
# 3. Railway configura automáticamente PostgreSQL + SSL
# 4. Agregar variable: GEMINI_API_KEY=tu_clave
# ¡Listo! URL automática: https://tu-app.up.railway.app
```

### Opción 3: Instalación Local (Desarrollo)

1. **Instalar Python** (si no está instalado):
   - Descargar desde https://python.org
   - Marcar "Add Python to PATH"

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar IA (opcional)**:
   ```bash
   # Crear archivo .env
   echo "GEMINI_API_KEY=tu_clave_api" > .env
   ```
   *Obtén clave gratuita en: https://makersuite.google.com/app/apikey*

4. **Ejecutar aplicación**:
   ```bash
   python app.py
   ```

### Opción 3: Instalación Automática (Windows)
```bash
# Ejecutar archivo run.bat incluido
run.bat
```

**URLs disponibles:**
- **Local**: `http://localhost:5000`
- **Red local**: `http://192.168.X.X:5000`
- **Render**: `https://tu-app.onrender.com`
- **Railway**: `https://tu-app.up.railway.app`

## 🎯 Uso de la Aplicación

### 🤖 Crear Reparaciones con IA (Flujo Inteligente)

#### Paso 1: Iniciar Nueva Reparación
- Click en **"Nueva Reparación"** (botón grande en header)
- Se abre modal con 4 pasos automatizados

#### Paso 2: Capturar Información del Equipo
- **📷 Opción A**: Usar cámara del dispositivo
- **📁 Opción B**: Seleccionar foto desde archivos
- La app automáticamente reconoce: laptop, PC, tablet, etc.

#### Paso 3: Procesamiento IA Automático
- **🤖 IA analiza** la imagen en segundos
- **📝 Extrae automáticamente**:
  - Nombre del cliente
  - Número de WhatsApp
  - Si incluye cargador
- **✏️ Usuario verifica** y puede corregir

#### Paso 4: Descripción por Voz
- **🎤 Grabar audio** describiendo el problema
- **📝 IA transcribe** automáticamente a texto
- **✅ Verificación final** antes de crear

#### Paso 5: ¡Listo!
- Tarjeta creada automáticamente en columna "Ingresado"
- Toda información guardada y organizada

### 📋 Gestionar Reparaciones (Kanban)

#### Mover entre Estados:
- **🔵 Ingresado**: Equipos recién recibidos
- **🟡 Diagnosticada**: Problema identificado y presupuesto dado
- **🟠 Para Entregar**: Equipo reparado, listo para recoger
- **🟢 Listos**: Reparaciones completadas y entregadas

#### Funcionalidades de Cada Tarjeta:
- **📱 WhatsApp**: Contactar directamente al cliente
- **📅 Fechas**: Inicio automático, límite configurable
- **🖼️ Foto**: Visualizar el equipo reparado
- **🔌 Cargador**: Estado claramente indicado
- **✏️ Editar**: Modificar cualquier información
- **🗑️ Eliminar**: Remover tarjetas no deseadas

### 🎨 Interfaz y Navegación

#### Diseño Responsive:
- **💻 Desktop**: Interfaz completa con todas las funciones
- **📱 Tablet**: Optimizada para pantallas medianas
- **📱 Móvil**: Funciones táctiles y simplificadas

#### Búsqueda Inteligente:
- **🔍 Barra de búsqueda**: Filtrar por nombre, problema o WhatsApp
- **⚡ Búsqueda en tiempo real**: Resultados instantáneos

#### Feedback Visual:
- **🎯 Drag & Drop**: Columnas se iluminan al arrastrar
- **⚠️ Estados**: Fechas vencidas en rojo
- **✅ Confirmaciones**: Mensajes claros de éxito/error

### 🔧 Configuración Avanzada

#### Variables de Entorno:
```env
# Base de datos (Railway configura automáticamente)
DATABASE_URL=postgresql://...

# IA de Gemini (opcional)
GEMINI_API_KEY=tu_clave_aqui

# Entorno
FLASK_ENV=development  # o production
```

#### Base de Datos:
- **Desarrollo**: SQLite automático
- **Producción**: PostgreSQL en Railway
- **Migraciones**: Automáticas al iniciar

### 🚨 Solución de Problemas

#### IA no funciona:
- Verificar `GEMINI_API_KEY` en variables de entorno
- La app funciona perfectamente **sin IA** (modo manual)

#### Problemas de conexión:
- Railway: Verificar logs en dashboard
- Local: Asegurar puerto 5000 disponible

#### Funcionalidades móviles:
- Requieren **HTTPS** para cámara/micrófono
- Railway proporciona SSL automáticamente

### 📚 Recursos Adicionales

- 🌐 **Despliegue en Render**: `RENDER_DEPLOY.md`
- 🚂 **Despliegue en Railway**: `RAILWAY_DEPLOY.md`
- 📱 **Pruebas móviles**: `MOBILE_TESTING.md`
- 🤖 **Configuración IA**: `README_GEMINI.md`

---

**¡La aplicación combina lo mejor de la tecnología moderna con una interfaz intuitiva para maximizar la eficiencia en el taller de reparaciones!** 🚀✨
