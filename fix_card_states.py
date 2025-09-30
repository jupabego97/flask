"""
Script para normalizar los estados de las tarjetas existentes en la base de datos.
Asegura que todos los estados coincidan exactamente con los IDs de las columnas HTML.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import dotenv

# Cargar variables de entorno
dotenv.load_dotenv()

app = Flask(__name__)

# Configuración de base de datos (SQLite para desarrollo, PostgreSQL para producción)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///reparaciones_it_migrated.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

def normalizar_estados():
    """Normaliza los estados de las tarjetas para que coincidan con los IDs de las columnas HTML"""

    # Mapeo de estados incorrectos a estados correctos
    mapeo_estados = {
        'paraentregar': 'para_entregar',  # Agregar guion bajo
        'entregados': 'listos',          # Mapear 'entregados' a 'listos'
        'para_entregar': 'para_entregar', # Ya correcto
        'diagnosticada': 'diagnosticada', # Ya correcto
        'ingresado': 'ingresado',         # Ya correcto
        'listos': 'listos'                # Ya correcto
    }

    with app.app_context():
        tarjetas = TarjetaReparacion.query.all()
        cambios = 0

        print("🔍 Analizando tarjetas existentes...")

        for tarjeta in tarjetas:
            estado_original = tarjeta.status
            estado_normalizado = mapeo_estados.get(estado_original, estado_original)

            if estado_original != estado_normalizado:
                print(f"📝 Tarjeta ID {tarjeta.id}: '{estado_original}' → '{estado_normalizado}'")
                tarjeta.status = estado_normalizado
                cambios += 1

        if cambios > 0:
            db.session.commit()
            print(f"✅ Se normalizaron {cambios} tarjetas")
        else:
            print("✅ Todas las tarjetas ya tienen estados correctos")

        # Verificar distribución final
        print("\n📊 Distribución final de estados:")
        from collections import Counter
        estados = [t.status for t in tarjetas]
        for estado, count in Counter(estados).items():
            print(f"  {estado}: {count} tarjetas")

if __name__ == "__main__":
    normalizar_estados()
