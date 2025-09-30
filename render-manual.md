# 🚨 Render - Configuración Manual (Si render.yaml falla)

Si el `render.yaml` está causando problemas, usa esta configuración manual:

## Configuración Manual en Render

### 1. Crear Web Service
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`

### 2. Variables de Entorno
```
FLASK_ENV=production
GEMINI_API_KEY=tu_clave_aqui  # Opcional
```

### 3. Crear Base de Datos
- Crear **PostgreSQL** database por separado
- Copiar la **DATABASE_URL** externa
- Agregarla como variable de entorno

## 🚨 Solución de Problemas Comunes

### Error: "subprocess-exited-with-error"
**Posibles causas y soluciones:**

#### 1. **OpenCV falla al compilar**
```bash
# Cambiar en requirements.txt:
# opencv-python==4.9.0.80  →  opencv-python-headless==4.9.0.80
```

#### 2. **Pip install falla**
```bash
# Verificar requirements.txt
# Remover versiones específicas si es necesario
# Usar: pip install --upgrade pip
```

#### 3. **Build timeout**
```bash
# Simplificar build command:
# Build Command: pip install -r requirements.txt
# (remover init_db.py del build)
```

#### 4. **Database connection fails**
```bash
# Verificar DATABASE_URL format
# Asegurar que la DB esté activa
# Verificar credenciales
```

#### 5. **Gunicorn fails**
```bash
# Verificar que gunicorn esté en requirements.txt
# Cambiar start command: python app.py
```

## Alternativas de Build Commands

### Opción 1: Build Simple
```
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
```

### Opción 2: Build con Python directo
```
Build Command: pip install -r requirements.txt
Start Command: python app.py
```

### Opción 3: Build con requirements específicos
```bash
# Si falla opencv, usar versión más simple:
echo "Flask==3.0.0" > requirements_simple.txt
echo "Flask-SQLAlchemy==3.1.1" >> requirements_simple.txt
echo "psycopg2-binary==2.9.9" >> requirements_simple.txt
echo "gunicorn==21.2.0" >> requirements_simple.txt

# Build Command: pip install -r requirements_simple.txt
```

## Verificación de Logs

### En Render Dashboard:
1. Ir a **Service** → **Logs**
2. Ver **Build Logs** para errores de instalación
3. Ver **Runtime Logs** para errores de aplicación

### Comandos útiles para debugging:
```bash
# Verificar Python version
python --version

# Verificar pip
pip --version

# Instalar dependencias manualmente
pip install Flask==3.0.0
pip install gunicorn==21.2.0
pip install psycopg2-binary==2.9.9
```

## 🚀 Última Opción: Build Local

Si todo falla, puedes hacer build local y subir archivos compilados:

```bash
# Local
pip install -r requirements.txt -t dist/
zip -r dist.zip dist/

# Subir dist.zip a Render
# Build Command: unzip dist.zip && pip install -r requirements.txt
```

¡Esta guía debería resolver el error "subprocess-exited-with-error"! 🎯
