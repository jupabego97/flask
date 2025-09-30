"""
Test de conexión y operaciones CRUD con PostgreSQL
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_get_tarjetas():
    """Probar obtener todas las tarjetas"""
    print("🔍 Probando GET /api/tarjetas...")
    try:
        response = requests.get(f"{BASE_URL}/api/tarjetas")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito: {len(data)} tarjetas encontradas")
            if data:
                print(f"📝 Primera tarjeta: ID {data[0]['id']} - {data[0]['nombre_propietario']}")
            return len(data)
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return 0
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return 0

def test_create_tarjeta():
    """Probar crear una nueva tarjeta"""
    print("\n➕ Probando POST /api/tarjetas...")
    nueva_tarjeta = {
        "nombre_propietario": "Test User",
        "problema": "Prueba de conexión PostgreSQL",
        "whatsapp": "+573001234567",
        "fecha_limite": "2025-12-31"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/tarjetas",
            json=nueva_tarjeta,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 201:
            data = response.json()
            print(f"✅ Tarjeta creada: ID {data['id']} - {data['nombre_propietario']}")
            return data['id']
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_update_tarjeta(tarjeta_id):
    """Probar actualizar una tarjeta"""
    print(f"\n🔄 Probando PUT /api/tarjetas/{tarjeta_id}...")
    update_data = {"columna": "diagnosticada"}

    try:
        response = requests.put(
            f"{BASE_URL}/api/tarjetas/{tarjeta_id}",
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Tarjeta actualizada: ID {data['id']} - Estado: {data['columna']}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_delete_tarjeta(tarjeta_id):
    """Probar eliminar una tarjeta"""
    print(f"\n🗑️ Probando DELETE /api/tarjetas/{tarjeta_id}...")

    try:
        response = requests.delete(f"{BASE_URL}/api/tarjetas/{tarjeta_id}")

        if response.status_code == 204:
            print(f"✅ Tarjeta eliminada: ID {tarjeta_id}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    print("🧪 Test de Conexión PostgreSQL")
    print("=" * 35)

    # Esperar un poco para que la aplicación esté lista
    print("⏳ Esperando que la aplicación esté lista...")
    time.sleep(2)

    # Test 1: Obtener tarjetas existentes
    initial_count = test_get_tarjetas()

    # Test 2: Crear nueva tarjeta
    nueva_id = test_create_tarjeta()

    if nueva_id:
        # Test 3: Verificar que se creó
        count_after_create = test_get_tarjetas()
        if count_after_create == initial_count + 1:
            print("✅ Verificación: Nueva tarjeta creada correctamente")
        else:
            print(f"⚠️ Verificación: Conteo inesperado ({count_after_create} vs {initial_count + 1})")

        # Test 4: Actualizar tarjeta
        test_update_tarjeta(nueva_id)

        # Test 5: Eliminar tarjeta
        if test_delete_tarjeta(nueva_id):
            # Test 6: Verificar eliminación
            final_count = test_get_tarjetas()
            if final_count == initial_count:
                print("✅ Verificación: Tarjeta eliminada correctamente")
            else:
                print(f"⚠️ Verificación: Conteo final inesperado ({final_count} vs {initial_count})")

    print("\n🎉 ¡Test completado!")

if __name__ == "__main__":
    main()
