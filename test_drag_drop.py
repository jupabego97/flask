#!/usr/bin/env python3
"""
Script para probar específicamente el drag and drop
"""
import requests
import time

BASE_URL = "http://localhost:5000"

def test_drag_drop():
    print("🧪 Probando drag and drop...")

    # 1. Crear una tarjeta de prueba
    print("\n1. Creando tarjeta de prueba...")
    nueva_tarjeta = {
        "nombre_propietario": "Test Drag Drop",
        "problema": "Problema de prueba para drag drop",
        "whatsapp": "+573001234567",
        "fecha_limite": "2025-12-31"
    }

    response = requests.post(f"{BASE_URL}/api/tarjetas", json=nueva_tarjeta)
    if response.status_code == 201:
        tarjeta = response.json()
        tarjeta_id = tarjeta['id']
        print(f"✅ Tarjeta creada: ID {tarjeta_id}, columna inicial: {tarjeta['columna']}")
    else:
        print(f"❌ Error creando tarjeta: {response.status_code}")
        return

    # 2. Mover la tarjeta a otra columna
    print(f"\n2. Moviendo tarjeta {tarjeta_id} a columna 'diagnosticada'...")
    update_data = {"columna": "diagnosticada"}
    response = requests.put(f"{BASE_URL}/api/tarjetas/{tarjeta_id}", json=update_data)

    if response.status_code == 200:
        tarjeta_actualizada = response.json()
        print(f"✅ Tarjeta actualizada: columna = {tarjeta_actualizada['columna']}")
    else:
        print(f"❌ Error actualizando: {response.status_code} - {response.text}")
        return

    # 3. Verificar que se guardó correctamente leyendo todas las tarjetas
    print("\n3. Verificando persistencia en base de datos...")
    time.sleep(1)  # Esperar un poco
    response = requests.get(f"{BASE_URL}/api/tarjetas")

    if response.status_code == 200:
        tarjetas = response.json()
        tarjeta_encontrada = None
        for t in tarjetas:
            if t['id'] == tarjeta_id:
                tarjeta_encontrada = t
                break

        if tarjeta_encontrada:
            print(f"📊 Estado en BD: ID {tarjeta_encontrada['id']}, columna: {tarjeta_encontrada['columna']}")
            if tarjeta_encontrada['columna'] == 'diagnosticada':
                print("✅ ¡ÉXITO! La tarjeta se guardó correctamente en la nueva columna")
            else:
                print(f"❌ ERROR: La tarjeta sigue en la columna '{tarjeta_encontrada['columna']}' en lugar de 'diagnosticada'")
        else:
            print("❌ ERROR: No se encontró la tarjeta en la base de datos")
    else:
        print(f"❌ Error obteniendo tarjetas: {response.status_code}")

    # 4. Limpiar: eliminar la tarjeta de prueba
    print(f"\n4. Limpiando: eliminando tarjeta de prueba...")
    response = requests.delete(f"{BASE_URL}/api/tarjetas/{tarjeta_id}")
    if response.status_code == 204:
        print("✅ Tarjeta de prueba eliminada")
    else:
        print(f"⚠️ No se pudo eliminar la tarjeta de prueba: {response.status_code}")

if __name__ == "__main__":
    print("⏳ Esperando que la aplicación esté lista...")
    time.sleep(3)
    test_drag_drop()
