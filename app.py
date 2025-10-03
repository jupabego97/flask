
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
from gemini_service import GeminiService

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

# Configuración de base de datos (SQLite para desarrollo, PostgreSQL para producción)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///reparaciones_it_migrated.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Inicializar servicio de Gemini
try:
    gemini_service = GeminiService()
    print("Servicio de Gemini inicializado correctamente")
except Exception as e:
    print(f"Servicio de Gemini no disponible: {e}")
    print("La aplicacion funcionara sin funcionalidades de IA")
    gemini_service = None

class TarjetaReparacion(db.Model):
    __tablename__ = 'repair_cards'  # Nombre de la tabla en Supabase

    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.Text, nullable=False)  # nombre_propietario en Supabase
    whatsapp_number = db.Column(db.Text, nullable=False)  # whatsapp en Supabase
    problem = db.Column(db.Text, nullable=False)  # problema en Supabase
    status = db.Column(db.Text, nullable=False)  # columna en Supabase
    start_date = db.Column(db.DateTime, nullable=False)  # fecha_inicio en Supabase
    due_date = db.Column(db.DateTime, nullable=False)  # fecha_limite en Supabase
    image_url = db.Column(db.Text, nullable=True)
    has_charger = db.Column(db.Text, nullable=True)
    ingresado_date = db.Column(db.DateTime, nullable=False)
    diagnosticada_date = db.Column(db.DateTime, nullable=True)
    para_entregar_date = db.Column(db.DateTime, nullable=True)
    entregados_date = db.Column(db.DateTime, nullable=True)

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
            'fecha_entregada': self.entregados_date.strftime('%Y-%m-%d %H:%M:%S') if self.entregados_date else None
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

@app.route('/api/tarjetas', methods=['GET'])
def get_tarjetas():
    tarjetas = TarjetaReparacion.query.all()
    return jsonify([tarjeta.to_dict() for tarjeta in tarjetas])

@app.route('/api/tarjetas', methods=['POST'])
def create_tarjeta():
    data = request.get_json()

    nueva_tarjeta = TarjetaReparacion(
        owner_name=data['nombre_propietario'],  # Mapeo a campos de Supabase
        problem=data['problema'],
        whatsapp_number=data['whatsapp'],
        start_date=datetime.utcnow(),  # Fecha de inicio automática
        due_date=datetime.strptime(data['fecha_limite'], '%Y-%m-%d'),
        status='ingresado',  # Estado inicial
        ingresado_date=datetime.utcnow(),  # Fecha de ingreso
        image_url=data.get('imagen_url'),  # URL de imagen (opcional)
        has_charger=data.get('tiene_cargador', 'si')  # Si incluye cargador (por defecto 'si')
    )

    db.session.add(nueva_tarjeta)
    db.session.commit()

    return jsonify(nueva_tarjeta.to_dict()), 201

# Estados válidos que coinciden exactamente con los IDs de las columnas HTML
ESTADOS_VALIDOS = ['ingresado', 'diagnosticada', 'para_entregar', 'listos']

@app.route('/api/tarjetas/<int:id>', methods=['PUT'])
def update_tarjeta(id):
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

    # Manejar cambio de columna/estado (drag & drop)
    if 'columna' in data:
        nuevo_estado = data['columna']

        # Validar que el estado sea válido
        if nuevo_estado not in ESTADOS_VALIDOS:
            return jsonify({'error': f'Estado no válido. Estados permitidos: {ESTADOS_VALIDOS}'}), 400

        tarjeta.status = nuevo_estado  # Actualizar estado

        # Actualizar fechas de estado según corresponda
        if nuevo_estado == 'diagnosticada' and not tarjeta.diagnosticada_date:
            tarjeta.diagnosticada_date = datetime.utcnow()
        elif nuevo_estado == 'para_entregar' and not tarjeta.para_entregar_date:
            tarjeta.para_entregar_date = datetime.utcnow()
        elif nuevo_estado == 'listos' and not tarjeta.entregados_date:
            tarjeta.entregados_date = datetime.utcnow()

    db.session.commit()
    return jsonify(tarjeta.to_dict())

@app.route('/api/tarjetas/<int:id>', methods=['DELETE'])
def delete_tarjeta(id):
    tarjeta = TarjetaReparacion.query.get_or_404(id)
    db.session.delete(tarjeta)
    db.session.commit()
    return '', 204

@app.route('/api/procesar-imagen', methods=['POST'])
def procesar_imagen():
    """
    Procesa una imagen para extraer información del cliente usando Gemini
    """
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
        print(f"Error procesando imagen: {e}")
        return jsonify({'error': 'Error procesando la imagen', 'details': str(e)}), 500

@app.route('/api/transcribir-audio', methods=['POST'])
def transcribir_audio():
    """
    Transcribe audio usando Gemini
    """
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
        print(f"Error transcribiendo audio: {e}")
        return jsonify({'error': 'Error procesando el audio', 'details': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    # Configuración para desarrollo y producción
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') == 'development'

    if debug_mode:
        # Desarrollo: permitir conexiones desde cualquier IP
        app.run(host='0.0.0.0', port=port, debug=True, load_dotenv=False)
    else:
        # Producción: usar gunicorn (Railway)
        # Esta línea no se ejecutará cuando use gunicorn
        app.run(host='0.0.0.0', port=port, debug=False)
