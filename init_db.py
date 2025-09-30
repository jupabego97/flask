#!/usr/bin/env python3
"""
Script para inicializar la base de datos
Compatible con Railway, Render y otros servicios de despliegue
"""

import os
import sys
from app import app, db

def init_database():
    """Inicializar la base de datos"""
    try:
        with app.app_context():
            print("🔄 Creando tablas de base de datos...")
            db.create_all()
            print("✅ Base de datos inicializada correctamente")
            return True
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        # No fallar el despliegue si hay error en BD
        # La app intentará crear tablas en runtime
        return False

if __name__ == '__main__':
    success = init_database()
    if not success:
        print("⚠️ Inicialización de BD falló, pero continuando con el despliegue...")
        sys.exit(0)  # No fallar el build
