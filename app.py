
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress
from flask_caching import Cache
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime
import os
import asyncio
import concurrent.futures
import sys
import atexit
from dotenv import load_dotenv
from gemini_service import GeminiService
import eventlet
from loguru import logger

# Cargar variables de entorno desde .env
import pathlib
env_path = pathlib.Path('.') / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Configurar Loguru (reemplaza print statements)
logger.remove()  # Remover handler por defecto
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO" if os.getenv('ENVIRONMENT') == 'production' else "DEBUG"
)
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    compression="zip",
    level="DEBUG"
)

app = Flask(__name__)

# Configuración de base de datos (PostgreSQL con optimizaciones)
database_url = os.getenv('DATABASE_URL', 'sqlite:///reparaciones_it_migrated.db')

# Railway/Heroku usan postgres:// pero SQLAlchemy requiere postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

# Log para debugging
logger.info(f"Conectando a BD: {database_url[:50]}...")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 20
}

db = SQLAlchemy(app)

# Inicializar Flask-Migrate para migraciones de BD
migrate = Migrate(app, db)

# Configurar Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.getenv('REDIS_URL', "memory://")
)

# Configurar Compresión
Compress(app)

# Configurar Cache
cache_config = {
    'CACHE_TYPE': 'redis' if os.getenv('REDIS_URL') else 'SimpleCache',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    'CACHE_DEFAULT_TIMEOUT': 300
}
app.config.update(cache_config)
cache = Cache(app)

# Obtener dominios permitidos desde variable de entorno
allowed_origins_env = os.getenv('ALLOWED_ORIGINS', '*')
is_production = os.getenv('ENVIRONMENT') == 'production'

# Si está en desarrollo, permitir acceso desde red local
if not is_production and allowed_origins_env == '*':
    allowed_origins = '*'  # Permitir todos en desarrollo
else:
    allowed_origins = allowed_origins_env.split(',')

logger.info(f"CORS configurado para: {allowed_origins}")

# Inicializar SocketIO para sincronización en tiempo real
socketio = SocketIO(
    app,
    cors_allowed_origins=allowed_origins,
    async_mode='eventlet',
    logger=False if is_production else True,
    engineio_logger=False if is_production else True,
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1000000
)

# ThreadPoolExecutor global reutilizable
executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=4,
    thread_name_prefix='gemini_worker'
)

# Limpiar executor al cerrar app
@atexit.register
def cleanup_executor():
    logger.info("Cerrando ThreadPoolExecutor...")
    executor.shutdown(wait=True)

# Inicializar servicio de Gemini
try:
    gemini_service = GeminiService()
    logger.info("Servicio de Gemini inicializado correctamente")
except Exception as e:
    logger.warning(f"Servicio de Gemini no disponible: {e}")
    logger.info("La aplicacion funcionara sin funcionalidades de IA")
    gemini_service = None

# ========== SCHEMAS DE VALIDACIÓN (Marshmallow) ==========

class TarjetaSchema(Schema):
    """Schema para validar datos de tarjetas de reparación"""
    nombre_propietario = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'El nombre del propietario es obligatorio'}
    )
    problema = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=500),
        error_messages={'required': 'La descripción del problema es obligatoria'}
    )
    whatsapp = fields.Str(
        required=True,
        validate=validate.Regexp(
            r'^\+?[1-9]\d{1,14}$',
            error='Número de WhatsApp inválido. Debe ser un número internacional válido'
        )
    )
    fecha_limite = fields.Date(
        required=True,
        error_messages={'required': 'La fecha límite es obligatoria'}
    )
    imagen_url = fields.Url(allow_none=True)
    tiene_cargador = fields.Str(
        validate=validate.OneOf(['si', 'no']),
        load_default='si'
    )
    notas_tecnicas = fields.Str(
        allow_none=True,
        validate=validate.Length(max=2000),
        load_default=None
    )

tarjeta_schema = TarjetaSchema()

# ========== EVENTOS DE SOCKETIO ==========

@socketio.on('connect')
def handle_connect():
    logger.info(f"Cliente conectado: {request.sid}")
    emit('status', {'message': 'Conectado al servidor en tiempo real'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Cliente desconectado: {request.sid}")

@socketio.on('join')
def handle_join(data=None):
    logger.info(f"Cliente se unió: {request.sid}")
    emit('status', {'message': 'Unido al canal de sincronización'})

# ========== MODELO DE DATOS ==========

class TarjetaReparacion(db.Model):
    __tablename__ = 'repair_cards'

    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.Text, nullable=False, index=True)  # Índice para búsqueda
    whatsapp_number = db.Column(db.Text, nullable=False, index=True)  # Índice para búsqueda
    problem = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False, index=True)  # Índice para filtrado
    start_date = db.Column(db.DateTime, nullable=False, index=True)  # Índice para ordenar
    due_date = db.Column(db.DateTime, nullable=False, index=True)  # Índice para filtrar
    image_url = db.Column(db.Text, nullable=True)
    has_charger = db.Column(db.Text, nullable=True)
    ingresado_date = db.Column(db.DateTime, nullable=False)
    diagnosticada_date = db.Column(db.DateTime, nullable=True)
    para_entregar_date = db.Column(db.DateTime, nullable=True)
    entregados_date = db.Column(db.DateTime, nullable=True)
    technical_notes = db.Column(db.Text, nullable=True)  # Diagnóstico/solución técnica

    def to_dict(self):
        return {
            'id': self.id,
            'nombre_propietario': self.owner_name,  # Mapeo a nombres de la app
            'problema': self.problem,
            'whatsapp': self.whatsapp_number,
            'fecha_inicio': self.start_date.strftime('%Y-%m-%d %H:%M:%S') if self.start_date else None,
            'fecha_limite': self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            'columna': self.status,
            'imagen_url': self.image_url,  # URL de la imagen del dispositivo
            'tiene_cargador': self.has_charger,  # Si tiene cargador incluido
            'fecha_diagnosticada': self.diagnosticada_date.strftime('%Y-%m-%d %H:%M:%S') if self.diagnosticada_date else None,
            'fecha_para_entregar': self.para_entregar_date.strftime('%Y-%m-%d %H:%M:%S') if self.para_entregar_date else None,
            'fecha_entregada': self.entregados_date.strftime('%Y-%m-%d %H:%M:%S') if self.entregados_date else None,
            'notas_tecnicas': self.technical_notes  # Diagnóstico técnico
        }

class StatusHistory(db.Model):
    __tablename__ = 'status_history'

    id = db.Column(db.Integer, primary_key=True)
    tarjeta_id = db.Column(db.Integer, db.ForeignKey('repair_cards.id', ondelete='CASCADE'), nullable=False, index=True)
    old_status = db.Column(db.Text, nullable=True)
    new_status = db.Column(db.Text, nullable=False)
    changed_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tarjeta_id': self.tarjeta_id,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'changed_at': self.changed_at.strftime('%Y-%m-%d %H:%M:%S') if self.changed_at else None
        }

@app.route('/')
def index():
    return render_template('index.html')

# Rutas PWA para archivos estáticos
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/static/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/static/browserconfig.xml')
def browserconfig():
    return send_from_directory('static', 'browserconfig.xml')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')

# ========== HEALTH CHECK ENDPOINT ==========

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar salud de la aplicación"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {}
    }
    
    try:
        # Verificar conexión a BD
        db.session.execute('SELECT 1')
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        logger.error(f"Error en health check de BD: {e}")
        health_status['services']['database'] = 'unhealthy'
        health_status['status'] = 'degraded'
    
    # Verificar Gemini
    health_status['services']['gemini_ai'] = 'healthy' if gemini_service else 'unavailable'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

# ========== API ENDPOINTS ==========

@app.route('/api/tarjetas', methods=['GET'])
def get_tarjetas():
    """Obtener tarjetas con paginación opcional"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', type=int)
        
        # Si no se especifica paginación, devolver todas (compatibilidad con frontend)
        if page is None or per_page is None:
            tarjetas = TarjetaReparacion.query.order_by(
                TarjetaReparacion.start_date.desc()
            ).all()
            response_data = [tarjeta.to_dict() for tarjeta in tarjetas]
            logger.info(f"Devolviendo {len(response_data)} tarjetas (sin paginación)")
        else:
            # Con paginación
            per_page = min(per_page, 100)  # Máximo 100 por página
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
            logger.info(f"Devolviendo página {page} con {len(pagination.items)} tarjetas")
        
        response = jsonify(response_data)
        
        # Headers para prevenir cache del navegador y asegurar sincronización en tiempo real
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        logger.exception(f"Error obteniendo tarjetas: {e}")
        return jsonify({'error': 'Error al obtener tarjetas'}), 500

@app.route('/api/tarjetas', methods=['POST'])
@limiter.limit("10 per minute")
def create_tarjeta():
    """Crear nueva tarjeta de reparación con validación"""
    try:
        # Validar datos de entrada con Marshmallow
        data = tarjeta_schema.load(request.get_json())
        
        # Crear tarjeta
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
        
        # Invalidar cache
        cache.delete_memoized(get_tarjetas)
        
        # Emitir evento de SocketIO
        tarjeta_data = nueva_tarjeta.to_dict()
        socketio.emit('tarjeta_creada', tarjeta_data)
        logger.info(f"Tarjeta creada - ID {tarjeta_data['id']}")
        
        return jsonify(tarjeta_data), 201
        
    except ValidationError as err:
        logger.warning(f"Validación fallida al crear tarjeta: {err.messages}")
        return jsonify({'error': 'Datos inválidos', 'details': err.messages}), 400
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error creando tarjeta: {e}")
        return jsonify({'error': 'Error al crear tarjeta'}), 500

# Estados válidos que coinciden exactamente con los IDs de las columnas HTML
ESTADOS_VALIDOS = ['ingresado', 'diagnosticada', 'para_entregar', 'listos']

@app.route('/api/tarjetas/<int:id>', methods=['PUT'])
@limiter.limit("30 per minute")
def update_tarjeta(id):
    """Actualizar tarjeta de reparación"""
    try:
        tarjeta = TarjetaReparacion.query.get_or_404(id)
        data = request.get_json()
        
        # Actualizar campos si están presentes en la solicitud
        if 'nombre_propietario' in data:
            tarjeta.owner_name = data['nombre_propietario']
        if 'problema' in data:
            tarjeta.problem = data['problema']
        if 'whatsapp' in data:
            tarjeta.whatsapp_number = data['whatsapp']
        if 'fecha_limite' in data:
            tarjeta.due_date = datetime.strptime(data['fecha_limite'], '%Y-%m-%d')
        if 'imagen_url' in data:
            tarjeta.image_url = data['imagen_url'] if data['imagen_url'] else None
        if 'tiene_cargador' in data:
            tarjeta.has_charger = data['tiene_cargador']
        if 'notas_tecnicas' in data:
            tarjeta.technical_notes = data['notas_tecnicas'] if data['notas_tecnicas'] else None
        
        # Manejar cambio de columna/estado (drag & drop)
        if 'columna' in data:
            nuevo_estado = data['columna']
            
            # Validar que el estado sea válido
            if nuevo_estado not in ESTADOS_VALIDOS:
                return jsonify({'error': f'Estado no válido. Estados permitidos: {ESTADOS_VALIDOS}'}), 400
            
            # Registrar cambio en historial
            old_status = tarjeta.status
            if old_status != nuevo_estado:
                history_entry = StatusHistory(
                    tarjeta_id=tarjeta.id,
                    old_status=old_status,
                    new_status=nuevo_estado,
                    changed_at=datetime.now()
                )
                db.session.add(history_entry)
            
            tarjeta.status = nuevo_estado
            
            # Actualizar fechas de estado según corresponda
            if nuevo_estado == 'diagnosticada' and not tarjeta.diagnosticada_date:
                tarjeta.diagnosticada_date = datetime.utcnow()
            elif nuevo_estado == 'para_entregar' and not tarjeta.para_entregar_date:
                tarjeta.para_entregar_date = datetime.utcnow()
            elif nuevo_estado == 'listos' and not tarjeta.entregados_date:
                tarjeta.entregados_date = datetime.utcnow()
        
        db.session.commit()
        
        # Invalidar cache
        cache.delete_memoized(get_tarjetas)
        
        # Emitir evento de SocketIO
        tarjeta_data = tarjeta.to_dict()
        socketio.emit('tarjeta_actualizada', tarjeta_data)
        logger.info(f"Tarjeta actualizada - ID {tarjeta_data['id']}")
        
        return jsonify(tarjeta_data)
        
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error actualizando tarjeta {id}: {e}")
        return jsonify({'error': 'Error al actualizar tarjeta'}), 500

@app.route('/api/tarjetas/<int:id>', methods=['DELETE'])
@limiter.limit("20 per minute")
def delete_tarjeta(id):
    """Eliminar tarjeta de reparación"""
    try:
        tarjeta = TarjetaReparacion.query.get_or_404(id)
        tarjeta_data = tarjeta.to_dict()
        
        db.session.delete(tarjeta)
        db.session.commit()
        
        # Invalidar cache
        cache.delete_memoized(get_tarjetas)
        
        # Emitir evento de SocketIO
        socketio.emit('tarjeta_eliminada', {'id': id})
        logger.info(f"Tarjeta eliminada - ID {id}")
        
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error eliminando tarjeta {id}: {e}")
        return jsonify({'error': 'Error al eliminar tarjeta'}), 500

@app.route('/api/tarjetas/<int:id>/historial', methods=['GET'])
def get_tarjeta_historial(id):
    """Obtener historial de cambios de estado de una tarjeta"""
    try:
        tarjeta = TarjetaReparacion.query.get_or_404(id)
        historial = StatusHistory.query.filter_by(tarjeta_id=id).order_by(StatusHistory.changed_at.desc()).all()
        
        return jsonify([h.to_dict() for h in historial])
        
    except Exception as e:
        logger.exception(f"Error obteniendo historial de tarjeta {id}: {e}")
        return jsonify({'error': 'Error al obtener historial'}), 500

@app.route('/api/estadisticas', methods=['GET'])
@cache.cached(timeout=300)  # Cache por 5 minutos
def get_estadisticas():
    """Obtener estadísticas del sistema"""
    try:
        from sqlalchemy import func, extract
        from datetime import timedelta
        
        # Total por estado
        por_estado = db.session.query(
            TarjetaReparacion.status,
            func.count(TarjetaReparacion.id).label('total')
        ).group_by(TarjetaReparacion.status).all()
        
        totales_por_estado = {estado: total for estado, total in por_estado}
        
        # Tiempo promedio en cada estado (calculado desde las fechas de transición)
        tiempos_promedio = {}
        
        # Ingresado a Diagnosticada
        ingresado_diag = db.session.query(
            func.avg(
                func.extract('epoch', TarjetaReparacion.diagnosticada_date - TarjetaReparacion.ingresado_date) / 86400
            ).label('dias')
        ).filter(TarjetaReparacion.diagnosticada_date.isnot(None)).scalar()
        tiempos_promedio['ingresado_a_diagnosticada'] = round(ingresado_diag or 0, 1)
        
        # Diagnosticada a Para Entregar
        diag_entregar = db.session.query(
            func.avg(
                func.extract('epoch', TarjetaReparacion.para_entregar_date - TarjetaReparacion.diagnosticada_date) / 86400
            ).label('dias')
        ).filter(TarjetaReparacion.para_entregar_date.isnot(None)).filter(
            TarjetaReparacion.diagnosticada_date.isnot(None)
        ).scalar()
        tiempos_promedio['diagnosticada_a_para_entregar'] = round(diag_entregar or 0, 1)
        
        # Para Entregar a Entregados
        entregar_entregado = db.session.query(
            func.avg(
                func.extract('epoch', TarjetaReparacion.entregados_date - TarjetaReparacion.para_entregar_date) / 86400
            ).label('dias')
        ).filter(TarjetaReparacion.entregados_date.isnot(None)).filter(
            TarjetaReparacion.para_entregar_date.isnot(None)
        ).scalar()
        tiempos_promedio['para_entregar_a_entregados'] = round(entregar_entregado or 0, 1)
        
        # Reparaciones completadas vs pendientes (último mes)
        hace_un_mes = datetime.now() - timedelta(days=30)
        completadas_mes = TarjetaReparacion.query.filter(
            TarjetaReparacion.status == 'listos',
            TarjetaReparacion.entregados_date >= hace_un_mes
        ).count()
        
        pendientes = TarjetaReparacion.query.filter(
            TarjetaReparacion.status != 'listos'
        ).count()
        
        # Top 5 problemas más frecuentes
        problemas_freq = db.session.query(
            TarjetaReparacion.problem,
            func.count(TarjetaReparacion.id).label('cantidad')
        ).group_by(TarjetaReparacion.problem).order_by(
            func.count(TarjetaReparacion.id).desc()
        ).limit(5).all()
        
        top_problemas = [{'problema': prob, 'cantidad': cant} for prob, cant in problemas_freq]
        
        # Tasa de reparaciones con/sin cargador
        con_cargador = TarjetaReparacion.query.filter_by(has_charger='si').count()
        sin_cargador = TarjetaReparacion.query.filter_by(has_charger='no').count()
        total_tarjetas = con_cargador + sin_cargador
        
        tasa_cargador = {
            'con_cargador': con_cargador,
            'sin_cargador': sin_cargador,
            'porcentaje_con_cargador': round((con_cargador / total_tarjetas * 100) if total_tarjetas > 0 else 0, 1)
        }
        
        # Tendencia últimos 6 meses (reparaciones ingresadas por mes)
        seis_meses_atras = datetime.now() - timedelta(days=180)
        tendencia = db.session.query(
            func.date_trunc('month', TarjetaReparacion.start_date).label('mes'),
            func.count(TarjetaReparacion.id).label('total')
        ).filter(
            TarjetaReparacion.start_date >= seis_meses_atras
        ).group_by(
            func.date_trunc('month', TarjetaReparacion.start_date)
        ).order_by('mes').all()
        
        tendencia_meses = [
            {
                'mes': mes.strftime('%Y-%m') if mes else None,
                'total': total
            } for mes, total in tendencia
        ]
        
        # Reparaciones con notas técnicas
        con_notas = TarjetaReparacion.query.filter(
            TarjetaReparacion.technical_notes.isnot(None),
            TarjetaReparacion.technical_notes != ''
        ).count()
        
        estadisticas = {
            'totales_por_estado': totales_por_estado,
            'tiempos_promedio_dias': tiempos_promedio,
            'completadas_ultimo_mes': completadas_mes,
            'pendientes': pendientes,
            'top_problemas': top_problemas,
            'tasa_cargador': tasa_cargador,
            'tendencia_6_meses': tendencia_meses,
            'total_reparaciones': total_tarjetas,
            'con_notas_tecnicas': con_notas,
            'generado_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(estadisticas)
        
    except Exception as e:
        logger.exception(f"Error generando estadísticas: {e}")
        return jsonify({'error': 'Error al generar estadísticas'}), 500

@app.route('/api/exportar', methods=['GET'])
@limiter.limit("10 per hour")
def exportar_datos():
    """Exportar datos a CSV o Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        from flask import send_file
        
        # Obtener parámetros de filtro
        formato = request.args.get('formato', 'csv')  # csv o excel
        estado = request.args.get('estado', None)
        fecha_desde = request.args.get('fecha_desde', None)
        fecha_hasta = request.args.get('fecha_hasta', None)
        
        # Construir query con filtros
        query = TarjetaReparacion.query
        
        if estado and estado != 'todos':
            query = query.filter_by(status=estado)
        
        if fecha_desde:
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            query = query.filter(TarjetaReparacion.start_date >= fecha_desde_dt)
        
        if fecha_hasta:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            query = query.filter(TarjetaReparacion.start_date <= fecha_hasta_dt)
        
        # Obtener datos
        tarjetas = query.all()
        
        # Convertir a DataFrame
        datos = []
        for t in tarjetas:
            datos.append({
                'ID': t.id,
                'Cliente': t.owner_name,
                'WhatsApp': t.whatsapp_number,
                'Problema': t.problem,
                'Estado': t.status,
                'Fecha Inicio': t.start_date.strftime('%Y-%m-%d %H:%M') if t.start_date else '',
                'Fecha Límite': t.due_date.strftime('%Y-%m-%d') if t.due_date else '',
                'Tiene Cargador': t.has_charger,
                'Notas Técnicas': t.technical_notes or '',
                'URL Imagen': t.image_url or '',
                'Fecha Diagnóstico': t.diagnosticada_date.strftime('%Y-%m-%d %H:%M') if t.diagnosticada_date else '',
                'Fecha Para Entregar': t.para_entregar_date.strftime('%Y-%m-%d %H:%M') if t.para_entregar_date else '',
                'Fecha Entregado': t.entregados_date.strftime('%Y-%m-%d %H:%M') if t.entregados_date else ''
            })
        
        df = pd.DataFrame(datos)
        
        if df.empty:
            return jsonify({'error': 'No hay datos para exportar con los filtros especificados'}), 404
        
        # Generar archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if formato == 'excel':
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Reparaciones')
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'reparaciones_nanotronics_{timestamp}.xlsx'
            )
        else:  # CSV
            output = BytesIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')  # utf-8-sig para Excel
            output.seek(0)
            
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'reparaciones_nanotronics_{timestamp}.csv'
            )
        
    except Exception as e:
        logger.exception(f"Error exportando datos: {e}")
        return jsonify({'error': 'Error al exportar datos', 'details': str(e)}), 500

@app.route('/api/procesar-imagen', methods=['POST'])
@limiter.limit("5 per minute")
def procesar_imagen():
    """Procesa una imagen para extraer información del cliente usando Gemini"""
    if not gemini_service:
        return jsonify({'error': 'Servicio de IA no disponible'}), 503
    
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No se proporcionó imagen'}), 400
        
        # Procesar la imagen con Gemini
        resultado = gemini_service.extract_client_info_from_image(image_data)
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.exception(f"Error procesando imagen: {e}")
        return jsonify({'error': 'Error procesando la imagen', 'details': str(e)}), 500

@app.route('/api/transcribir-audio', methods=['POST'])
@limiter.limit("5 per minute")
def transcribir_audio():
    """Transcribe audio usando Gemini"""
    if not gemini_service:
        return jsonify({'error': 'Servicio de IA no disponible'}), 503
    
    try:
        # Verificar si hay archivo de audio
        if 'audio' not in request.files:
            return jsonify({'error': 'No se proporcionó archivo de audio'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'Archivo de audio vacío'}), 400
        
        # Leer el archivo de audio
        audio_data = audio_file.read()
        
        # Transcribir con Gemini
        transcripcion = gemini_service.transcribe_audio(audio_data)
        
        return jsonify({'transcripcion': transcripcion})
        
    except Exception as e:
        logger.exception(f"Error transcribiendo audio: {e}")
        return jsonify({'error': 'Error procesando el audio', 'details': str(e)}), 500

@app.route('/api/procesar-multimedia', methods=['POST'])
@limiter.limit("3 per minute")
def procesar_multimedia():
    """Procesa imagen y audio concurrentemente usando ThreadPoolExecutor global"""
    if not gemini_service:
        return jsonify({'error': 'Servicio de IA no disponible'}), 503
    
    try:
        import base64
        data = request.get_json()
        image_data = data.get('image')
        audio_data = data.get('audio')
        
        if not image_data:
            return jsonify({'error': 'No se proporcionó imagen'}), 400
        
        # Si no hay audio, procesar solo imagen
        if not audio_data:
            logger.info('Procesando solo imagen (sin audio)')
            resultado_imagen = gemini_service.extract_client_info_from_image(image_data)
            return jsonify({
                'imagen': resultado_imagen,
                'audio': {'error': 'No se proporcionó audio'}
            })
        
        logger.info('Procesando imagen y audio concurrentemente')
        
        # Crear funciones para ejecutar en threads separados
        def procesar_imagen_task():
            try:
                return gemini_service.extract_client_info_from_image(image_data)
            except Exception as e:
                logger.error(f"Error procesando imagen: {e}")
                return {'error': f'Error procesando imagen: {str(e)}'}
        
        def procesar_audio_task():
            try:
                # Convertir base64 a bytes si es necesario
                if isinstance(audio_data, str) and audio_data.startswith('data:audio'):
                    header, encoded = audio_data.split(",", 1)
                    audio_bytes = base64.b64decode(encoded)
                else:
                    audio_bytes = audio_data
                
                return gemini_service.transcribe_audio(audio_bytes)
            except Exception as e:
                logger.error(f"Error procesando audio: {e}")
                return f'Error procesando audio: {str(e)}'
        
        # Usar executor global para ejecutar tareas concurrentemente
        future_imagen = executor.submit(procesar_imagen_task)
        future_audio = executor.submit(procesar_audio_task)
        
        # Esperar resultados con timeout de 30 segundos
        try:
            resultado_imagen = future_imagen.result(timeout=30)
            resultado_audio = future_audio.result(timeout=30)
            
            logger.info('Procesamiento concurrente completado')
            
            return jsonify({
                'imagen': resultado_imagen,
                'audio': resultado_audio
            })
            
        except concurrent.futures.TimeoutError:
            logger.warning('Timeout en procesamiento concurrente')
            return jsonify({
                'imagen': {'error': 'Timeout procesando imagen'},
                'audio': {'error': 'Timeout procesando audio'}
            }), 408
    
    except Exception as e:
        logger.exception(f"Error en procesamiento multimedia: {e}")
        return jsonify({'error': 'Error en procesamiento multimedia', 'details': str(e)}), 500

# ========== MANEJADORES DE ERROR GLOBALES ==========

@app.errorhandler(ValidationError)
def handle_validation_error(e):
    """Manejar errores de validación de Marshmallow"""
    logger.warning(f"Error de validación: {e.messages}")
    return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400

@app.errorhandler(404)
def handle_not_found(e):
    """Manejar recursos no encontrados"""
    return jsonify({'error': 'Recurso no encontrado'}), 404

@app.errorhandler(429)
def handle_rate_limit(e):
    """Manejar límite de tasa excedido"""
    logger.warning(f"Rate limit excedido: {request.remote_addr}")
    return jsonify({'error': 'Demasiadas solicitudes. Por favor intenta más tarde.'}), 429

@app.errorhandler(500)
def handle_internal_error(e):
    """Manejar errores internos del servidor"""
    logger.exception("Error interno del servidor")
    db.session.rollback()
    return jsonify({'error': 'Error interno del servidor'}), 500

@app.errorhandler(Exception)
def handle_generic_error(e):
    """Manejar errores no capturados"""
    logger.exception(f"Error no manejado: {e}")
    db.session.rollback()
    return jsonify({'error': 'Error inesperado', 'message': str(e)}), 500

# ========== INICIALIZACIÓN ==========

if __name__ == '__main__':
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    with app.app_context():
        db.create_all()
        logger.info("Tablas de base de datos creadas/verificadas")
    
    # Configuración para desarrollo y producción
    port = int(os.getenv('PORT', 5000))
    is_development = os.getenv('ENVIRONMENT') != 'production'
    
    if is_development:
        logger.info("Iniciando servidor de DESARROLLO con SocketIO...")
        logger.info(f"Servidor corriendo en http://0.0.0.0:{port}")
        socketio.run(app, host='0.0.0.0', port=port, debug=True)
    else:
        logger.info("Iniciando servidor de PRODUCCION con SocketIO...")
        logger.info(f"Puerto: {port}")
        socketio.run(app, host='0.0.0.0', port=port)
