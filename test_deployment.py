#!/usr/bin/env python3
"""
Script para probar el despliegue antes de subir a producción
"""

import os
import sys

def test_imports():
    """Probar imports básicos"""
    try:
        print("🔄 Probando imports básicos...")

        import flask
        print(f"✅ Flask {flask.__version__}")

        from flask_sqlalchemy import SQLAlchemy
        print("✅ Flask-SQLAlchemy")

        import psycopg2
        print("✅ psycopg2")

        try:
            import gunicorn
            print("✅ gunicorn")
        except ImportError:
            print("⚠️ gunicorn no instalado (normal en desarrollo)")

        return True
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False

def test_app():
    """Probar inicialización de la app"""
    try:
        print("🔄 Probando inicialización de app...")

        from app import app
        print("✅ App importada correctamente")

        # Probar contexto de app
        with app.app_context():
            print("✅ App context funciona")

        return True
    except Exception as e:
        print(f"❌ Error en app: {e}")
        return False

def test_database():
    """Probar conexión a base de datos"""
    try:
        print("🔄 Probando base de datos...")

        from app import app, db
        with app.app_context():
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT 1"))
                print("✅ Base de datos conectada")

        return True
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Probando despliegue de Reparaciones IT")
    print("=" * 50)

    tests = [
        ("Imports", test_imports),
        ("App", test_app),
        ("Database", test_database),
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"\n📋 Test: {name}")
        if test_func():
            passed += 1
        print("-" * 30)

    print(f"\n📊 Resultados: {passed}/{total} tests pasaron")

    if passed == total:
        print("🎉 ¡Todos los tests pasaron! Listo para despliegue.")
        sys.exit(0)
    else:
        print("⚠️ Algunos tests fallaron. Revisa los errores arriba.")
        sys.exit(1)

if __name__ == '__main__':
    main()
