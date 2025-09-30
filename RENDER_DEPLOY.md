# 🌐 Despliegue en Render

## 📋 Requisitos Previos

1. **Cuenta en Render:** https://render.com
2. **Cuenta en GitHub:** Para conectar el repositorio
3. **Clave API de Gemini:** (Opcional) https://makersuite.google.com/app/apikey

## 🚀 Pasos de Despliegue

### Paso 1: Preparar el Código
Los archivos necesarios ya están configurados:
- ✅ `render.yaml` - Configuración automática de Render
- ✅ `requirements.txt` - Dependencias completas
- ✅ `init_db.py` - Inicialización de base de datos
- ✅ `runtime.txt` - Versión de Python

### Paso 2: Crear Repositorio en GitHub
1. Ve a https://github.com y crea un nuevo repositorio
2. Sube todos los archivos del proyecto (excepto `__pycache__`, `.env`, bases de datos locales)

### Paso 3: Desplegar en Render

#### Opción A: Despliegue Automático (Recomendado)
1. Ve a https://render.com y haz login
2. Click en **"New Web Service"**
3. Conecta tu repositorio de GitHub
4. Render detectará automáticamente `render.yaml`

#### Opción B: Configuración Manual
Si no usas `render.yaml`, configura manualmente:
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt && python init_db.py`
- **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`

### Paso 4: Configurar Base de Datos

#### Opción A: PostgreSQL Automático (Recomendado)
En el `render.yaml` ya está configurado:
```yaml
databases:
  - name: reparaciones-db
    databaseName: reparaciones_it
    user: reparaciones_user
    plan: free
```

#### Opción B: PostgreSQL Manual
1. Crea una nueva **PostgreSQL** database en Render
2. Copia la **DATABASE_URL** externa
3. Agrégala como variable de entorno

### Paso 5: Configurar Variables de Entorno

En el dashboard de tu web service, ve a **Environment**:

#### Variables Obligatorias:
```env
FLASK_ENV=production
```

#### Variables Opcionales:
```env
GEMINI_API_KEY=tu_clave_api_aqui
```

### Paso 6: ¡Despliegue Completado!

Render automáticamente:
- ✅ Construye la aplicación con Python 3.11
- ✅ Instala todas las dependencias
- ✅ Inicializa la base de datos
- ✅ Proporciona URL HTTPS automática

## 🎯 Características de Render

### ✅ Ventajas:
- **Free Tier Generoso:** 750 horas/mes gratis
- **SSL Automático:** HTTPS incluido
- **PostgreSQL Integrado:** Base de datos automática
- **Deploy desde GitHub:** Integración perfecta
- **Monitoreo Básico:** Logs y métricas

### ⚠️ Limitaciones del Free Tier:
- **750 horas/mes** (alrededor 31 días)
- **Base de datos suspendida** después de 30 días de inactividad
- **Escalado limitado** (solo 1 instancia)

### 💰 Planes de Pago:
- **Starter:** $7/mes - Sin límites de tiempo
- **Standard:** $25/mes - Más recursos
- **Pro:** $50+ - Características avanzadas

## 🔧 Configuración Avanzada

### Health Check (Opcional)
En **Settings** → **Health Check**:
```
Path: /
Interval: 30 seconds
Timeout: 10 seconds
```

### Auto-Deploy
Activa **Auto-Deploy** para que Render actualice automáticamente cuando hagas push a GitHub.

### Custom Domain
En **Settings** → **Custom Domains** puedes configurar tu propio dominio.

## 🚨 Solución de Problemas

### ❌ "Build failed"
**Posibles causas:**
- Error en `requirements.txt`
- Problema con `init_db.py`
- Versión de Python incompatible

**Solución:**
```bash
# Verificar logs de build en Render dashboard
# Posibles fixes:
# - Revisar requirements.txt
# - Simplificar init_db.py
# - Cambiar versión de Python en runtime.txt
```

### ❌ "Application failed to start"
**Causas comunes:**
- Error de conexión a base de datos
- Variable `DATABASE_URL` incorrecta
- Puerto no configurado correctamente

**Solución:**
- Verificar logs de la aplicación
- Confirmar `DATABASE_URL` en variables de entorno
- Asegurar que `gunicorn` esté en requirements.txt

### ❌ "Database connection failed"
**Posibles issues:**
- Database suspendida (Free tier)
- Credenciales incorrectas
- Conexión SSL requerida

**Solución:**
- Reactivar database desde Render dashboard
- Verificar `DATABASE_URL` format
- Confirmar configuración SSL

## 📊 Monitoreo y Mantenimiento

### Logs en Render:
- ✅ **Build Logs:** Proceso de construcción
- ✅ **Runtime Logs:** Logs de la aplicación
- ✅ **Database Logs:** Actividad de PostgreSQL

### Métricas Disponibles:
- ✅ **Response Time**
- ✅ **Throughput**
- ✅ **Error Rate**
- ✅ **CPU/Memory Usage**

## 🎉 ¡Despliegue Listo!

### URLs de Acceso:
- **Render URL:** `https://tu-app.onrender.com`
- **Base de Datos:** PostgreSQL automática

### Próximos Pasos:
1. ✅ **Probar funcionalidades** en producción
2. ✅ **Configurar monitoreo** adicional si es necesario
3. ✅ **Configurar backup** de base de datos (opcional)

## 🔄 Comparación: Render vs Railway

| Característica | Render | Railway |
|---|---|---|
| **Free Tier** | 750h/mes | 512MB RAM, limitado |
| **PostgreSQL** | Incluido | Incluido |
| **Auto-scaling** | Limitado | Mejor |
| **Custom Domain** | ✅ | ✅ |
| **GitHub Integration** | ✅ | ✅ |
| **Pricing** | Predecible | Basado en uso |

**Recomendación:**
- **Render:** Perfecto para proyectos personales y prototipos
- **Railway:** Mejor para aplicaciones en crecimiento

¡Tu aplicación está lista para desplegarse en Render con configuración profesional! 🚀✨
