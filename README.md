# 🔧 Sistema de Reparaciones Nanotronics

Sistema completo de gestión de reparaciones de dispositivos electrónicos con IA integrada (Google Gemini), sincronización en tiempo real y análisis de negocio.

![Version](https://img.shields.io/badge/version-3.0-blue)
![Python](https://img.shields.io/badge/python-3.11-green)
![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Características Principales

### 🎯 Gestión de Reparaciones
- **Tablero Kanban** con drag & drop para gestión visual
- **4 Estados**: Ingresado → Diagnóstico → Para Entregar → Completado
- **Sincronización en tiempo real** con WebSockets (SocketIO)
- **PWA completa** - Funciona offline y se puede instalar como app

### 🤖 Inteligencia Artificial Integrada
- **Extracción de datos desde fotos** con Google Gemini
- **Transcripción de audio** para descripciones de problemas
- **Procesamiento de multimedia** concurrente

### 📊 Análisis y Reportes
- **Dashboard de estadísticas** con métricas clave:
  - Total de reparaciones por estado
  - Tiempos promedio en cada etapa
  - Top 5 problemas más frecuentes
  - Tendencias mensuales
- **Exportación de datos** a CSV/Excel con filtros
- **Gráficos interactivos** con Chart.js

### 🔧 Gestión Técnica
- **Notas técnicas** - Documenta el diagnóstico y solución aplicada
- **Historial de cambios** - Timeline automático de cada movimiento
- **Registro fotográfico** de cada dispositivo

### 🔍 Búsqueda y Filtros
- **Filtros avanzados** combinables:
  - Por estado
  - Por rango de fechas
  - Con/sin cargador
  - Con/sin diagnóstico técnico
- **Búsqueda en tiempo real** en todos los campos
- **Contador de resultados** dinámico

### 🎨 Experiencia de Usuario
- **Modo oscuro** con persistencia automática
- **Diseño responsive** - Optimizado para móvil y desktop
- **Atajos de teclado** para acciones rápidas
- **Notificaciones visuales** de cambios en tiempo real

### 🔒 Seguridad y Performance
- **Rate limiting** en endpoints críticos
- **Validación de entrada** con Marshmallow
- **Logging estructurado** con Loguru
- **Caché inteligente** con Redis/SimpleCache
- **Compresión HTTP** con Flask-Compress
- **Pool de conexiones** PostgreSQL optimizado

## 🚀 Despliegue Rápido en Railway

### Opción 1: Deploy con un Click

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/TU_USUARIO/TU_REPO)

### Opción 2: Deploy Manual

1. **Fork/Clone este repositorio**

2. **Crea un nuevo proyecto en Railway**: https://railway.app

3. **Agrega PostgreSQL**:
   - Click en "New" → "Database" → "Add PostgreSQL"
   - Railway generará automáticamente `DATABASE_URL`

4. **Conecta tu repositorio de GitHub**:
   - Click en "New" → "GitHub Repo"
   - Selecciona este repositorio

5. **Configura las variables de entorno**:
   ```
   GEMINI_API_KEY=tu_api_key_de_google_gemini
   ENVIRONMENT=production
   ALLOWED_ORIGINS=https://tu-app.railway.app
   ```
   (No necesitas configurar `DATABASE_URL`, Railway lo hace automáticamente)

6. **Deploy automático**: 
   - Railway detectará el `Procfile` y desplegará automáticamente
   - Obtendrás una URL tipo: `https://tu-app.railway.app`

## 💻 Instalación Local

### Requisitos
- Python 3.11+
- PostgreSQL (o usar Neon/Supabase)
- Google Gemini API Key

### Pasos

1. **Clonar el repositorio**:
```bash
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO
```

2. **Crear entorno virtual**:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Edita .env con tus credenciales
```

5. **Crear las tablas de la base de datos**:
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ BD creada')"
```

6. **Iniciar el servidor**:
```bash
python app.py
```

7. **Abrir en el navegador**: http://localhost:5000

## 📱 Uso en Móvil

### Instalar como PWA

**Android (Chrome)**:
1. Abre la aplicación en Chrome
2. Menú (⋮) → "Agregar a pantalla de inicio"
3. ¡Listo! Funciona como app nativa

**iOS (Safari)**:
1. Abre la aplicación en Safari
2. Botón Compartir (⎙) → "Agregar a pantalla de inicio"
3. ¡Listo! Funciona como app nativa

## 🔧 Tecnologías Utilizadas

### Backend
- **Flask 3.0** - Framework web
- **SQLAlchemy** - ORM para base de datos
- **PostgreSQL** - Base de datos principal
- **Flask-SocketIO** - WebSockets para tiempo real
- **Eventlet** - Servidor asíncrono
- **Google Gemini AI** - Procesamiento de imágenes y audio
- **Marshmallow** - Validación de datos
- **Loguru** - Logging estructurado

### Frontend
- **HTML5/CSS3/JavaScript** - Vanilla JS (sin frameworks)
- **Bootstrap 5.3** - UI components
- **Chart.js 4.4** - Gráficos interactivos
- **Font Awesome 6.4** - Iconos
- **Service Worker** - PWA y offline support

### Integraciones
- **Neon PostgreSQL** - Base de datos en la nube
- **Google Gemini API** - IA para procesamiento multimedia
- **Railway** - Hosting y deployment

## 📊 Estructura del Proyecto

```
flask copy/
├── app.py                              # Backend principal
├── gemini_service.py                   # Servicio de IA
├── requirements.txt                    # Dependencias Python
├── Procfile                           # Configuración Railway/Heroku
├── runtime.txt                        # Versión de Python
├── .env.example                       # Plantilla de variables de entorno
├── .gitignore                         # Archivos ignorados por Git
├── README.md                          # Este archivo
├── templates/
│   └── index.html                     # Frontend SPA
├── static/
│   ├── icons/                         # Iconos PWA
│   ├── manifest.json                  # PWA manifest
│   └── sw.js                         # Service Worker
└── Documentación/
    ├── GUIA_NUEVAS_FUNCIONES.md      # Tutorial de usuario
    ├── MEJORAS_FASE3_COMPLETADAS.md  # Changelog técnico
    └── INSTRUCCIONES_FINALES.md      # Guía de despliegue
```

## 📚 Documentación

- **[Guía de Usuario](GUIA_NUEVAS_FUNCIONES.md)** - Tutorial completo de todas las funciones
- **[Mejoras Implementadas](MEJORAS_FASE3_COMPLETADAS.md)** - Changelog técnico detallado
- **[Instrucciones Finales](INSTRUCCIONES_FINALES.md)** - Guía de despliegue y configuración

## 🔐 Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión PostgreSQL | `postgresql://user:pass@host/db` |
| `GEMINI_API_KEY` | API Key de Google Gemini | `AIzaSy...` |
| `ENVIRONMENT` | Entorno de ejecución | `production` o `development` |
| `PORT` | Puerto del servidor | `5000` (Railway lo asigna automáticamente) |
| `ALLOWED_ORIGINS` | Orígenes permitidos CORS | `https://tu-app.railway.app` |

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👤 Autor

**Sistema de Reparaciones Nanotronics**
- Versión 3.0 - Octubre 2025
- Con IA integrada y análisis de negocio

## 🙏 Agradecimientos

- Google Gemini AI por el procesamiento inteligente
- Neon PostgreSQL por la base de datos confiable
- Railway por el hosting simplificado
- La comunidad de Flask por el excelente framework

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub!

🐛 ¿Encontraste un bug? [Reportalo aquí](https://github.com/TU_USUARIO/TU_REPO/issues)
