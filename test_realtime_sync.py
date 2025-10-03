#!/usr/bin/env python3
"""
Script para probar la sincronización en tiempo real con SocketIO
"""
import socketio
import time
import requests

BASE_URL = "http://localhost:5000"

def test_socketio_connection():
    """Probar conexión SocketIO"""
    print("🧪 Probando conexión SocketIO...")

    # Crear cliente SocketIO
    sio = socketio.Client()

    @sio.on('connect')
    def on_connect():
        print("✅ Conectado a SocketIO")
        sio.emit('join')

    @sio.on('disconnect')
    def on_disconnect():
        print("📴 Desconectado de SocketIO")

    @sio.on('status')
    def on_status(data):
        print(f"📡 Estado: {data['message']}")

    @sio.on('tarjeta_creada')
    def on_tarjeta_creada(tarjeta):
        print(f"📦 Evento recibido - Nueva tarjeta: {tarjeta['nombre_propietario']}")

    @sio.on('tarjeta_actualizada')
    def on_tarjeta_actualizada(tarjeta):
        print(f"🔄 Evento recibido - Tarjeta movida: {tarjeta['nombre_propietario']} -> {tarjeta['columna']}")

    @sio.on('tarjeta_eliminada')
    def on_tarjeta_eliminada(data):
        print(f"🗑️ Evento recibido - Tarjeta eliminada: ID {data['id']}")

    try:
        # Conectar a SocketIO
        sio.connect(BASE_URL)
        print("🔗 Intentando conectar a SocketIO...")
        time.sleep(2)  # Esperar conexión

        # Crear una tarjeta de prueba via HTTP
        print("\n📝 Creando tarjeta de prueba...")
        nueva_tarjeta = {
            "nombre_propietario": "Test Sincronización",
            "problema": "Problema para probar sincronización en tiempo real",
            "whatsapp": "+573001234567",
            "fecha_limite": "2025-12-31"
        }

        response = requests.post(f"{BASE_URL}/api/tarjetas", json=nueva_tarjeta)
        if response.status_code == 201:
            tarjeta = response.json()
            tarjeta_id = tarjeta['id']
            print(f"✅ Tarjeta creada: ID {tarjeta_id}")

            # Esperar evento SocketIO
            time.sleep(2)

            # Mover la tarjeta
            print(f"\n🔄 Moviendo tarjeta {tarjeta_id} a 'diagnosticada'...")
            update_data = {"columna": "diagnosticada"}
            response = requests.put(f"{BASE_URL}/api/tarjetas/{tarjeta_id}", json=update_data)

            if response.status_code == 200:
                print("✅ Tarjeta movida correctamente")

                # Esperar evento SocketIO
                time.sleep(2)

                # Eliminar la tarjeta
                print(f"\n🗑️ Eliminando tarjeta {tarjeta_id}...")
                response = requests.delete(f"{BASE_URL}/api/tarjetas/{tarjeta_id}")

                if response.status_code == 204:
                    print("✅ Tarjeta eliminada correctamente")

                    # Esperar evento SocketIO
                    time.sleep(2)
                else:
                    print(f"❌ Error eliminando: {response.status_code}")
            else:
                print(f"❌ Error moviendo: {response.status_code}")
        else:
            print(f"❌ Error creando tarjeta: {response.status_code}")

        # Desconectar
        sio.disconnect()
        print("\n✅ Prueba completada")

    except Exception as e:
        print(f"❌ Error en prueba SocketIO: {e}")

if __name__ == "__main__":
    print("🚀 Probando sincronización en tiempo real con SocketIO")
    print("=" * 50)
    test_socketio_connection()
