#!/usr/bin/env python3
"""
Script para inicializar la base de datos
Se ejecuta automáticamente en Railway después del despliegue
"""

import os
from app import app, db

def init_database():
    """Inicializar la base de datos"""
    with app.app_context():
        print("🔄 Creando tablas de base de datos...")
        db.create_all()
        print("✅ Base de datos inicializada correctamente")

if __name__ == '__main__':
    init_database()
