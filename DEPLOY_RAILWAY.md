# 🚀 Guía de Despliegue en Railway

## Paso a Paso Completo

### 1️⃣ Preparar el Repositorio en GitHub

#### A. Inicializar Git (si no lo has hecho)

```bash
cd "D:\Desktop\python\flask copy"
git init
git add .
git commit -m "Initial commit: Sistema Nanotronics v3.0"
```

#### B. Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. **Nombre**: `sistema-reparaciones-nanotronics` (o el que prefieras)
3. **Descripción**: "Sistema de gestión de reparaciones con IA integrada"
4. **Público** o **Privado** (tú eliges)
5. **NO marques** "Add README" ni ".gitignore" (ya los tenemos)
6. Click en **"Create repository"**

#### C. Subir el Código a GitHub

```bash
# Reemplaza TU_USUARIO con tu usuario de GitHub
git remote add origin https://github.com/TU_USUARIO/sistema-reparaciones-nanotronics.git
git branch -M main
git push -u origin main
```

---

### 2️⃣ Desplegar en Railway

#### A. Crear Cuenta en Railway

1. Ve a https://railway.app
2. Click en **"Start a New Project"**
3. Inicia sesión con GitHub (recomendado)

#### B. Crear Base de Datos PostgreSQL

1. En Railway, click en **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway creará automáticamente la base de datos
3. **Importante**: Railway generará automáticamente la variable `DATABASE_URL`

#### C. Conectar tu Repositorio GitHub

1. Click en **"New"** → **"GitHub Repo"**
2. Autoriza a Railway a acceder a tu GitHub (si es la primera vez)
3. Selecciona el repositorio: `sistema-reparaciones-nanotronics`
4. Railway comenzará el deployment automáticamente

#### D. Configurar Variables de Entorno

1. En tu proyecto de Railway, click en el servicio (tu app)
2. Ve a la pestaña **"Variables"**
3. Agrega las siguientes variables:

```
GEMINI_API_KEY=AIzaSyB7LTOd7bsW16jtLbLAuV2RAGRp8t2HDEU
ENVIRONMENT=production
ALLOWED_ORIGINS=https://tu-app.railway.app
```

**Importante**: 
- `DATABASE_URL` ya está configurado automáticamente por Railway
- `PORT` también es asignado automáticamente por Railway
- Reemplaza `https://tu-app.railway.app` con tu URL real cuando la obtengas

#### E. Inicializar la Base de Datos

**Opción 1: Desde Railway CLI**

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Conectar al proyecto
railway link

# Ejecutar comando para crear tablas
railway run python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ BD creada')"
```

**Opción 2: Crear script de migración automática**

Railway ejecutará automáticamente las migraciones si agregas esto al final de `app.py`:

```python
# Solo en el primer deploy, las tablas se crean automáticamente
# gracias a db.create_all() que ya está en el código
```

---

### 3️⃣ Verificar el Despliegue

#### A. Obtener tu URL

1. En Railway, ve a **"Settings"** de tu servicio
2. En la sección **"Domains"**, verás tu URL generada
3. Ejemplo: `https://sistema-reparaciones-nanotronics-production.up.railway.app`

#### B. Actualizar ALLOWED_ORIGINS

1. Copia tu URL de Railway
2. Ve a **"Variables"**
3. Edita `ALLOWED_ORIGINS` y pon tu URL:
   ```
   ALLOWED_ORIGINS=https://tu-url-real.railway.app
   ```
4. Railway redesplegará automáticamente

#### C. Probar la Aplicación

1. Abre tu URL de Railway en el navegador
2. Deberías ver el sistema de reparaciones funcionando
3. Prueba:
   - ✅ Crear una tarjeta
   - ✅ Moverla entre columnas
   - ✅ Abrir estadísticas
   - ✅ Exportar datos

---

### 4️⃣ Migrar Datos Existentes (Opcional)

Si ya tienes datos en Neon y quieres moverlos a Railway:

#### A. Obtener DATABASE_URL de Railway

```bash
# Desde Railway CLI
railway variables

# O desde la interfaz web: Settings → Variables → DATABASE_URL
```

#### B. Migrar datos desde Neon a Railway

```python
# Crear script temporal: migrate_to_railway.py
import psycopg2

NEON_URL = "postgresql://neondb_owner:npg_c48DVpgJWZQT@ep-odd-breeze-adieoy6s-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
RAILWAY_URL = "postgresql://postgres:...@...railway.app/railway"  # Tu URL de Railway

# Conectar a ambas
neon_conn = psycopg2.connect(NEON_URL)
railway_conn = psycopg2.connect(RAILWAY_URL)

# Copiar datos
neon_cur = neon_conn.cursor()
railway_cur = railway_conn.cursor()

# Obtener datos de Neon
neon_cur.execute("SELECT * FROM repair_cards ORDER BY id")
records = neon_cur.fetchall()

# Insertar en Railway
for record in records:
    railway_cur.execute("""
        INSERT INTO repair_cards VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, record)

railway_conn.commit()
print(f"✅ {len(records)} registros migrados")
```

#### C. O usar pg_dump/pg_restore

```bash
# Exportar desde Neon
pg_dump "$NEON_URL" > backup.sql

# Importar a Railway
psql "$RAILWAY_URL" < backup.sql
```

---

### 5️⃣ Configuración Adicional de Railway

#### A. Configurar Dominio Personalizado (Opcional)

1. En Railway, ve a **"Settings"** → **"Domains"**
2. Click en **"Custom Domain"**
3. Agrega tu dominio: `reparaciones.tu-dominio.com`
4. Configura el DNS con el CNAME que te da Railway
5. Actualiza `ALLOWED_ORIGINS` con tu dominio personalizado

#### B. Configurar Health Checks

Railway monitorea automáticamente tu app usando el endpoint `/health`

Verifica que funciona:
```bash
curl https://tu-app.railway.app/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "gemini_ai": "healthy"
  }
}
```

#### C. Ver Logs

1. En Railway, click en tu servicio
2. Ve a la pestaña **"Logs"**
3. Verás todos los logs en tiempo real

---

## 📋 Checklist de Despliegue

- [ ] Código subido a GitHub
- [ ] Proyecto creado en Railway
- [ ] PostgreSQL agregado en Railway
- [ ] Repositorio conectado a Railway
- [ ] Variables de entorno configuradas:
  - [ ] `GEMINI_API_KEY`
  - [ ] `ENVIRONMENT=production`
  - [ ] `ALLOWED_ORIGINS` (con URL de Railway)
- [ ] Base de datos inicializada (tablas creadas)
- [ ] URL de Railway obtenida
- [ ] Aplicación probada y funcionando
- [ ] (Opcional) Datos migrados desde Neon
- [ ] (Opcional) Dominio personalizado configurado

---

## 🔧 Solución de Problemas

### Error: "Application failed to respond"

**Causa**: El puerto no está configurado correctamente  
**Solución**: Asegúrate de que `app.py` usa `port=int(os.getenv('PORT', 5000))`

### Error: "Database connection failed"

**Causa**: Railway no puede conectar a la BD  
**Solución**: 
1. Verifica que PostgreSQL esté agregado al proyecto
2. Verifica que `DATABASE_URL` existe en las variables

### Error: "CORS policy blocked"

**Causa**: `ALLOWED_ORIGINS` no incluye tu URL de Railway  
**Solución**: Actualiza `ALLOWED_ORIGINS` con tu URL real

### Las tarjetas no cargan

**Causa**: Tablas no existen en la base de datos  
**Solución**: Ejecuta el script de inicialización de BD

---

## 🎯 Comandos Útiles de Railway CLI

```bash
# Ver logs en tiempo real
railway logs

# Ejecutar comando en Railway
railway run python -c "print('Hello from Railway')"

# Ver variables de entorno
railway variables

# Conectarse a la BD de Railway
railway connect

# Deployar manualmente
railway up
```

---

## 📚 Recursos Adicionales

- **Railway Docs**: https://docs.railway.app
- **PostgreSQL en Railway**: https://docs.railway.app/databases/postgresql
- **Variables de Entorno**: https://docs.railway.app/develop/variables

---

## ✅ ¡Listo!

Tu aplicación ya está desplegada y accesible desde cualquier parte del mundo 🌍

**URL de ejemplo**: `https://sistema-reparaciones-nanotronics.up.railway.app`

---

**¿Necesitas ayuda?** Revisa los logs en Railway o contacta al soporte.

