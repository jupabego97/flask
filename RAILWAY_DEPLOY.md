# 🚂 Despliegue en Railway

## 📋 Requisitos Previos

1. **Cuenta en Railway:** https://railway.app
2. **Cuenta en GitHub:** Para conectar el repositorio
3. **Clave API de Gemini:** (Opcional) https://makersuite.google.com/app/apikey

## 🚀 Pasos de Despliegue

### Paso 1: Preparar el Código
Los archivos necesarios ya están configurados:
- ✅ `requirements.txt` - Dependencias completas
- ✅ `Procfile` - Configuración de Railway
- ✅ `app.py` - Aplicación preparada para producción

### Paso 2: Crear Repositorio en GitHub
1. Ve a https://github.com y crea un nuevo repositorio
2. Sube todos los archivos del proyecto (excepto `__pycache__`, `.env`, bases de datos locales)

### Paso 3: Desplegar en Railway

#### Opción A: Desde GitHub (Recomendado)
1. Ve a https://railway.app y haz login
2. Click en "New Project" → "Deploy from GitHub repo"
3. Selecciona tu repositorio
4. Railway detectará automáticamente Python y configurará todo

#### Opción B: Desde Railway CLI
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Conectar al proyecto
railway init

# Desplegar
railway up
```

### Paso 4: Configurar Variables de Entorno

En el dashboard de Railway, ve a "Variables" y configura:

```env
# Clave API de Gemini (opcional)
GEMINI_API_KEY=tu_clave_api_aqui
```

> **Nota:** Railway automáticamente configura `DATABASE_URL` para PostgreSQL

### Paso 5: Configurar Base de Datos

Railway automáticamente:
- ✅ Crea instancia PostgreSQL
- ✅ Configura `DATABASE_URL`
- ✅ Maneja migraciones automáticamente

### Paso 6: Verificar Despliegue

Una vez desplegado, Railway te dará una URL como:
```
https://reparaciones-it-production.up.railway.app
```

## 🔧 Configuración de Producción

### Variables de Entorno en Railway:
```
GEMINI_API_KEY=tu_clave_api_real
```

### Base de Datos:
- ✅ PostgreSQL automático
- ✅ Conexión SSL
- ✅ Respaldos automáticos

## 🎯 Características de Producción

### ✅ Optimizaciones Implementadas:
- ✅ **Gunicorn** como servidor WSGI
- ✅ **PostgreSQL** en lugar de SQLite
- ✅ **Sin modo debug** en producción
- ✅ **Manejo de errores** robusto
- ✅ **SSL automático** (HTTPS)

### ✅ Funcionalidades que Funcionan:
- ✅ **IA de Gemini** (con clave API)
- ✅ **Cámara y micrófono** (HTTPS requerido)
- ✅ **Responsive design** completo
- ✅ **Base de datos** PostgreSQL
- ✅ **Subida de archivos** automática

## 🚨 Solución de Problemas

### ❌ "Application failed to respond"
```bash
# Verificar logs en Railway dashboard
# Posibles causas:
# - Error en requirements.txt
# - DATABASE_URL no configurada
# - Puerto no configurado correctamente
```

### ❌ "Database connection failed"
- Railway configura automáticamente DATABASE_URL
- Verifica que no haya errores en la inicialización

### ❌ "IA features not working"
- Verifica que `GEMINI_API_KEY` esté configurada
- La app funciona sin IA (modo manual inteligente)

## 📊 Monitoreo y Mantenimiento

### Logs en Railway:
- ✅ Logs en tiempo real
- ✅ Errores de aplicación
- ✅ Uso de recursos

### Base de Datos:
- ✅ Respaldos automáticos
- ✅ Escalado automático
- ✅ Conexiones SSL

## 🎉 ¡Despliegue Completado!

Tu aplicación estará disponible en una URL como:
```
https://tu-app-railway.up.railway.app
```

### Próximos Pasos:
1. ✅ **Probar funcionalidades** en la URL de producción
2. ✅ **Configurar dominio** personalizado (opcional)
3. ✅ **Configurar monitoreo** adicional si es necesario

¡La aplicación está completamente preparada para producción en Railway! 🚀✨
