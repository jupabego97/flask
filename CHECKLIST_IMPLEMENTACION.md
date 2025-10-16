# ✅ CHECKLIST DE IMPLEMENTACIÓN

Este documento es una guía práctica paso a paso para implementar las mejoras identificadas.

---

## 🔴 FASE 1: CRÍTICO (Semana 1)

### **1.1 Seguridad Básica**

#### ✅ **Validación de Entrada con Marshmallow**

**Archivo**: `app.py`

**Paso 1**: Instalar dependencias
```bash
pip install marshmallow flask-marshmallow
```

**Paso 2**: Crear schemas de validación
```python
# Agregar después de las importaciones
from marshmallow import Schema, fields, validate, ValidationError

class TarjetaSchema(Schema):
    nombre_propietario = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=100)
    )
    problema = fields.Str(
        required=True, 
        validate=validate.Length(min=5, max=500)
    )
    whatsapp = fields.Str(
        required=True,
        validate=validate.Regexp(r'^\+?[1-9]\d{1,14}$')
    )
    fecha_limite = fields.Date(required=True)
    imagen_url = fields.Url(allow_none=True)
    tiene_cargador = fields.Str(
        validate=validate.OneOf(['si', 'no']),
        missing='si'
    )

tarjeta_schema = TarjetaSchema()
```

**Paso 3**: Modificar endpoint `create_tarjeta` (línea 126)
```python
@app.route('/api/tarjetas', methods=['POST'])
def create_tarjeta():
    try:
        # Validar datos de entrada
        data = tarjeta_schema.load(request.get_json())
        
        nueva_tarjeta = TarjetaReparacion(
            owner_name=data['nombre_propietario'],
            problem=data['problema'],
            whatsapp_number=data['whatsapp'],
            start_date=datetime.utcnow(),
            due_date=data['fecha_limite'],
            status='ingresado',
            ingresado_date=datetime.utcnow(),
            image_url=data.get('imagen_url'),
            has_charger=data.get('tiene_cargador', 'si')
        )
        
        db.session.add(nueva_tarjeta)
        db.session.commit()
        
        # Emitir evento de SocketIO
        tarjeta_data = nueva_tarjeta.to_dict()
        socketio.emit('tarjeta_creada', tarjeta_data)
        
        return jsonify(tarjeta_data), 201
        
    except ValidationError as err:
        return jsonify({'error': 'Datos inválidos', 'details': err.messages}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error creando tarjeta: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
```

**Tiempo estimado**: 2 horas

---

#### ✅ **Rate Limiting con Flask-Limiter**

**Paso 1**: Instalar
```bash
pip install Flask-Limiter
```

**Paso 2**: Configurar en `app.py` (después de línea 22)
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Usar Redis en producción
)
```

**Paso 3**: Aplicar límites a endpoints críticos
```python
@app.route('/api/tarjetas', methods=['POST'])
@limiter.limit("10 per minute")  # Máximo 10 creaciones por minuto
def create_tarjeta():
    # ... código existente

@app.route('/api/procesar-imagen', methods=['POST'])
@limiter.limit("5 per minute")  # Máximo 5 procesamiento IA por minuto
def procesar_imagen():
    # ... código existente

@app.route('/api/procesar-multimedia', methods=['POST'])
@limiter.limit("3 per minute")  # Máximo 3 procesamiento multimedia por minuto
def procesar_multimedia():
    # ... código existente
```

**Tiempo estimado**: 1 hora

---

#### ✅ **Migrar a PostgreSQL en Producción**

**Paso 1**: Actualizar `app.py` (línea 19)
```python
# Obtener DATABASE_URL y corregir para SQLAlchemy
database_url = os.getenv('DATABASE_URL', 'sqlite:///reparaciones_it_migrated.db')

# Railway/Heroku usan postgres:// pero SQLAlchemy requiere postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

**Paso 2**: Actualizar `requirements.txt`
```
psycopg2-binary>=2.9.0  # Ya existe
```

**Paso 3**: Crear migraciones con Flask-Migrate
```bash
pip install Flask-Migrate
```

**Paso 4**: Configurar migraciones en `app.py`
```python
from flask_migrate import Migrate

migrate = Migrate(app, db)
```

**Paso 5**: Inicializar migraciones
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

**Tiempo estimado**: 2 horas

---

#### ✅ **Logging Estructurado con Loguru**

**Paso 1**: Instalar
```bash
pip install loguru
```

**Paso 2**: Configurar en `app.py` (al inicio)
```python
from loguru import logger
import sys

# Configurar logger
logger.remove()  # Remover handler por defecto
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    compression="zip",
    level="DEBUG"
)
```

**Paso 3**: Reemplazar todos los `print()` con `logger`
```python
# ANTES
print(f"🔗 Cliente conectado: {request.sid}")

# DESPUÉS
logger.info(f"Cliente conectado: {request.sid}")
```

**Paso 4**: Agregar contexto a logs
```python
try:
    # ... código
except Exception as e:
    logger.exception(f"Error procesando imagen: {e}")
    # El .exception() incluye el stack trace completo
```

**Tiempo estimado**: 3 horas

---

#### ✅ **Health Check Endpoint**

**Paso 1**: Agregar endpoint en `app.py`
```python
@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar salud de la aplicación"""
    try:
        # Verificar conexión a BD
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        logger.error(f"Error en health check de BD: {e}")
        db_status = 'unhealthy'
    
    # Verificar Gemini
    gemini_status = 'healthy' if gemini_service else 'unavailable'
    
    health = {
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'database': db_status,
            'gemini_ai': gemini_status
        }
    }
    
    status_code = 200 if health['status'] == 'healthy' else 503
    return jsonify(health), status_code
```

**Tiempo estimado**: 30 minutos

---

#### ✅ **Manejo Global de Excepciones**

**Paso 1**: Agregar manejadores de error en `app.py`
```python
@app.errorhandler(ValidationError)
def handle_validation_error(e):
    logger.warning(f"Validation error: {e.messages}")
    return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400

@app.errorhandler(404)
def handle_not_found(e):
    return jsonify({'error': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def handle_internal_error(e):
    logger.exception("Error interno del servidor")
    db.session.rollback()
    return jsonify({'error': 'Error interno del servidor'}), 500

@app.errorhandler(Exception)
def handle_generic_error(e):
    logger.exception(f"Error no manejado: {e}")
    db.session.rollback()
    return jsonify({'error': 'Error inesperado', 'message': str(e)}), 500
```

**Tiempo estimado**: 1 hora

---

#### ✅ **Configurar CORS Restrictivo**

**Paso 1**: Modificar `app.py` (línea 25-34)
```python
# Obtener dominios permitidos desde variable de entorno
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')

socketio = SocketIO(
    app,
    cors_allowed_origins=allowed_origins,  # Solo dominios permitidos
    async_mode='eventlet',
    logger=False,              # Desactivar en producción
    engineio_logger=False,     # Desactivar en producción
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1000000
)
```

**Paso 2**: Configurar variable de entorno `.env`
```
ALLOWED_ORIGINS=https://tudominio.com,https://www.tudominio.com
```

**Tiempo estimado**: 30 minutos

---

#### ✅ **Agregar Índices a Base de Datos**

**Paso 1**: Modificar modelo en `app.py` (línea 60)
```python
class TarjetaReparacion(db.Model):
    __tablename__ = 'repair_cards'

    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.Text, nullable=False, index=True)  # Índice para búsqueda
    whatsapp_number = db.Column(db.Text, nullable=False, index=True)  # Índice para búsqueda
    problem = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False, index=True)  # Índice para filtrado por estado
    start_date = db.Column(db.DateTime, nullable=False, index=True)  # Índice para ordenar
    due_date = db.Column(db.DateTime, nullable=False, index=True)  # Índice para filtrar vencidas
    # ... resto de campos
```

**Paso 2**: Crear migración
```bash
flask db migrate -m "Add indexes for performance"
flask db upgrade
```

**Tiempo estimado**: 1 hora

---

### **Resumen Fase 1**
- ✅ Validación de entrada
- ✅ Rate limiting
- ✅ PostgreSQL en producción
- ✅ Logging estructurado
- ✅ Health check
- ✅ Manejo de excepciones
- ✅ CORS restrictivo
- ✅ Índices en BD

**Total estimado**: 11 horas  
**Resultado**: App segura y estable

---

## 🟡 FASE 2: PERFORMANCE (Semana 2)

### **2.1 Paginación en API**

**Paso 1**: Modificar endpoint `get_tarjetas` (línea 114)
```python
@app.route('/api/tarjetas', methods=['GET'])
def get_tarjetas():
    # Obtener parámetros de paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Validar parámetros
    per_page = min(per_page, 100)  # Máximo 100 por página
    
    # Query paginado
    pagination = TarjetaReparacion.query.order_by(
        TarjetaReparacion.start_date.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    response_data = {
        'tarjetas': [tarjeta.to_dict() for tarjeta in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }
    
    response = jsonify(response_data)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response
```

**Paso 2**: Actualizar frontend para manejar paginación

**Tiempo estimado**: 3 horas

---

### **2.2 Implementar Cache con Redis**

**Paso 1**: Instalar
```bash
pip install redis flask-caching
```

**Paso 2**: Configurar en `app.py`
```python
from flask_caching import Cache

# Configurar cache
cache_config = {
    'CACHE_TYPE': 'redis' if os.getenv('REDIS_URL') else 'simple',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutos
}
app.config.update(cache_config)
cache = Cache(app)

# Usar cache en endpoints de lectura
@app.route('/api/tarjetas', methods=['GET'])
@cache.cached(timeout=60, query_string=True)  # Cache 1 minuto
def get_tarjetas():
    # ... código existente
```

**Paso 3**: Invalidar cache en operaciones de escritura
```python
@app.route('/api/tarjetas', methods=['POST'])
def create_tarjeta():
    # ... crear tarjeta
    cache.delete_memoized(get_tarjetas)  # Invalidar cache
    return jsonify(tarjeta_data), 201
```

**Tiempo estimado**: 2 horas

---

### **2.3 Separar JavaScript a Archivos Externos**

**Paso 1**: Crear `static/js/app.js`
```bash
mkdir -p "flask copy/static/js"
```

**Paso 2**: Mover todo el JavaScript de `index.html` a `app.js`

**Paso 3**: Referenciar en `index.html`
```html
<script src="/static/js/app.js"></script>
```

**Paso 4**: Minificar con Terser
```bash
npm install -g terser
terser static/js/app.js -o static/js/app.min.js -c -m
```

**Tiempo estimado**: 4 horas

---

### **2.4 Lazy Loading de Imágenes**

**Paso 1**: Agregar librería `lazysizes` en `index.html`
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js" async></script>
```

**Paso 2**: Modificar generación de tarjetas (en JavaScript)
```javascript
// ANTES
<img src="${imagen_url}" class="img-fluid mb-2">

// DESPUÉS
<img data-src="${imagen_url}" class="img-fluid mb-2 lazyload">
```

**Tiempo estimado**: 1 hora

---

### **2.5 Optimizar Gemini Service**

**Paso 1**: Versionar modelo en `gemini_service.py` (línea 20)
```python
self.model = genai.GenerativeModel('gemini-1.5-flash')  # Versión específica
```

**Paso 2**: Cachear prompts frecuentes
```python
# Mover prompt a constante al inicio del archivo
PROMPT_EXTRACT_INFO = """
Analiza esta imagen...
[prompt completo]
"""

class GeminiService:
    def __init__(self):
        # ... código existente
        self._prompt_cache = {}  # Cache de prompts
```

**Paso 3**: Agregar retry con backoff exponencial
```bash
pip install tenacity
```

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class GeminiService:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def extract_client_info_from_image(self, image_data, image_format='jpeg'):
        # ... código existente
```

**Tiempo estimado**: 3 horas

---

### **2.6 Comprimir Respuestas**

**Paso 1**: Instalar
```bash
pip install flask-compress
```

**Paso 2**: Configurar en `app.py`
```python
from flask_compress import Compress

Compress(app)
```

**Tiempo estimado**: 15 minutos

---

### **2.7 ThreadPoolExecutor Global**

**Paso 1**: Modificar `app.py` (antes de rutas)
```python
# Crear executor global
executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=4,
    thread_name_prefix='gemini_worker'
)

# Limpiar al cerrar app
import atexit
atexit.register(lambda: executor.shutdown(wait=True))
```

**Paso 2**: Usar executor global en `procesar_multimedia` (línea 319)
```python
# ANTES
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:

# DESPUÉS
# Usar el executor global
future_imagen = executor.submit(procesar_imagen)
future_audio = executor.submit(procesar_audio)
```

**Tiempo estimado**: 1 hora

---

### **Resumen Fase 2**
- ✅ Paginación
- ✅ Cache con Redis
- ✅ JavaScript separado
- ✅ Lazy loading
- ✅ Gemini optimizado
- ✅ Compresión
- ✅ ThreadPoolExecutor global

**Total estimado**: 14 horas  
**Resultado**: App 5x más rápida

---

## 🟢 FASE 3: FEATURES (Semana 3)

### **3.1 Búsqueda y Filtrado**

**Paso 1**: Agregar endpoint de búsqueda en `app.py`
```python
@app.route('/api/tarjetas/search', methods=['GET'])
@limiter.limit("30 per minute")
def search_tarjetas():
    query = request.args.get('q', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    date_from = request.args.get('date_from', '', type=str)
    date_to = request.args.get('date_to', '', type=str)
    
    # Construir query
    q = TarjetaReparacion.query
    
    # Filtrar por texto
    if query:
        search_pattern = f'%{query}%'
        q = q.filter(
            db.or_(
                TarjetaReparacion.owner_name.ilike(search_pattern),
                TarjetaReparacion.problem.ilike(search_pattern),
                TarjetaReparacion.whatsapp_number.ilike(search_pattern)
            )
        )
    
    # Filtrar por estado
    if status_filter:
        q = q.filter(TarjetaReparacion.status == status_filter)
    
    # Filtrar por rango de fechas
    if date_from:
        q = q.filter(TarjetaReparacion.start_date >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        q = q.filter(TarjetaReparacion.start_date <= datetime.strptime(date_to, '%Y-%m-%d'))
    
    # Ejecutar query
    tarjetas = q.order_by(TarjetaReparacion.start_date.desc()).all()
    
    return jsonify([t.to_dict() for t in tarjetas])
```

**Paso 2**: Agregar UI de búsqueda en frontend

**Tiempo estimado**: 5 horas

---

### **3.2 Notificaciones Push**

**Paso 1**: Agregar soporte en Service Worker (`sw.js`)
```javascript
// Manejar notificaciones push
self.addEventListener('push', (event) => {
    const data = event.data.json();
    const options = {
        body: data.body,
        icon: '/static/icons/icon-192.png',
        badge: '/static/icons/icon-72.png',
        vibrate: [200, 100, 200],
        data: {
            url: data.url || '/'
        }
    };
    
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Manejar click en notificación
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});
```

**Paso 2**: Solicitar permiso en frontend
```javascript
// En index.html
async function solicitarPermisoNotificaciones() {
    if ('Notification' in window && 'serviceWorker' in navigator) {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            console.log('✅ Permiso de notificaciones concedido');
        }
    }
}
```

**Tiempo estimado**: 4 horas

---

### **3.3 Analytics**

**Paso 1**: Agregar endpoint de métricas
```python
@app.route('/api/estadisticas', methods=['GET'])
@cache.cached(timeout=300)  # Cache 5 minutos
def get_estadisticas():
    stats = {
        'total_tarjetas': TarjetaReparacion.query.count(),
        'por_estado': {
            'ingresado': TarjetaReparacion.query.filter_by(status='ingresado').count(),
            'diagnosticada': TarjetaReparacion.query.filter_by(status='diagnosticada').count(),
            'para_entregar': TarjetaReparacion.query.filter_by(status='para_entregar').count(),
            'listos': TarjetaReparacion.query.filter_by(status='listos').count(),
        },
        'tiempo_promedio': calcular_tiempo_promedio(),
        'vencidas': TarjetaReparacion.query.filter(
            TarjetaReparacion.due_date < datetime.utcnow(),
            TarjetaReparacion.status != 'listos'
        ).count()
    }
    return jsonify(stats)

def calcular_tiempo_promedio():
    # Calcular tiempo promedio de reparación
    completadas = TarjetaReparacion.query.filter_by(status='listos').all()
    if not completadas:
        return 0
    
    tiempos = [
        (t.entregados_date - t.ingresado_date).total_seconds() / 86400
        for t in completadas
        if t.entregados_date and t.ingresado_date
    ]
    
    return sum(tiempos) / len(tiempos) if tiempos else 0
```

**Paso 2**: Crear dashboard visual

**Tiempo estimado**: 6 horas

---

### **Resumen Fase 3**
- ✅ Búsqueda y filtrado
- ✅ Notificaciones push
- ✅ Analytics y estadísticas

**Total estimado**: 15 horas  
**Resultado**: Features que usuarios necesitan

---

## 💎 FASE 4: POLISH (Semana 4+)

### **4.1 Tests Unitarios**

**Paso 1**: Instalar pytest
```bash
pip install pytest pytest-cov pytest-flask
```

**Paso 2**: Crear `tests/test_api.py`
```python
import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_health_check(client):
    """Test endpoint de salud"""
    rv = client.get('/health')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['status'] in ['healthy', 'degraded']

def test_create_tarjeta(client):
    """Test crear tarjeta"""
    data = {
        'nombre_propietario': 'Juan Pérez',
        'problema': 'Pantalla rota',
        'whatsapp': '+573001234567',
        'fecha_limite': '2025-10-20'
    }
    rv = client.post('/api/tarjetas', json=data)
    assert rv.status_code == 201
    json_data = rv.get_json()
    assert json_data['nombre_propietario'] == 'Juan Pérez'
```

**Paso 3**: Ejecutar tests
```bash
pytest --cov=app --cov-report=html
```

**Tiempo estimado**: 10 horas

---

### **4.2 CI/CD con GitHub Actions**

**Paso 1**: Crear `.github/workflows/tests.yml`
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest --cov=app
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**Tiempo estimado**: 3 horas

---

### **4.3 Documentación con Swagger**

**Paso 1**: Instalar
```bash
pip install flask-swagger-ui
```

**Paso 2**: Configurar en `app.py`
```python
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Nanotronics API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
```

**Paso 3**: Crear `static/swagger.json`

**Tiempo estimado**: 6 horas

---

### **Resumen Fase 4**
- ✅ Tests (80% coverage)
- ✅ CI/CD
- ✅ Documentación

**Total estimado**: 19 horas  
**Resultado**: Calidad enterprise

---

## 📋 CHECKLIST FINAL

### **Antes de Deploy**

- [ ] Todas las variables de entorno configuradas
- [ ] Base de datos PostgreSQL configurada
- [ ] Redis configurado (opcional pero recomendado)
- [ ] ALLOWED_ORIGINS configurado correctamente
- [ ] GEMINI_API_KEY configurada
- [ ] Logs configurados y rotados
- [ ] Health check funcionando
- [ ] Tests pasando
- [ ] Backup de BD actual
- [ ] Plan de rollback definido

### **Post-Deploy**

- [ ] Verificar `/health` responde 200
- [ ] Verificar métricas en dashboard
- [ ] Monitorear logs por 1 hora
- [ ] Verificar rate limiting funciona
- [ ] Probar creación/edición/eliminación
- [ ] Verificar SocketIO conecta
- [ ] Probar en móvil
- [ ] Verificar PWA instala correctamente

---

## 🆘 TROUBLESHOOTING

### **Error: "Rate limit exceeded"**
**Solución**: Aumentar límites en configuración de Flask-Limiter

### **Error: "Connection pool exhausted"**
**Solución**: Aumentar `pool_size` en configuración de SQLAlchemy

### **Error: "Gemini API timeout"**
**Solución**: Verificar GEMINI_API_KEY y conectividad

### **Error: "SocketIO no conecta"**
**Solución**: Verificar CORS y eventlet instalado

---

## 📞 SOPORTE

Si encuentras problemas:
1. Revisar logs en `logs/app.log`
2. Verificar `/health` endpoint
3. Consultar documentación de librerías
4. Crear issue en GitHub

---

**¡Buena suerte con la implementación!** 🚀

