"""
Script para obtener la IP local y generar instrucciones para conectar desde móvil
"""
import socket
import os

def obtener_ip_local():
    """Obtiene la IP local de la máquina"""
    try:
        # Crear un socket UDP (no necesita conexión real)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # No necesita estar conectado, solo necesitamos la interfaz de red
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except Exception:
        return "No se pudo obtener IP"

def main():
    print("=" * 70)
    print("📱 GUÍA RÁPIDA PARA PROBAR EN MÓVIL")
    print("=" * 70)
    print()
    
    ip = obtener_ip_local()
    puerto = os.getenv('PORT', '5000')
    
    print(f"✅ Tu IP local es: {ip}")
    print(f"✅ Puerto configurado: {puerto}")
    print()
    
    print("📱 INSTRUCCIONES:")
    print("-" * 70)
    print("1. Asegúrate de que tu celular esté en la MISMA red WiFi que tu PC")
    print("2. Asegúrate de que el servidor esté corriendo (python app.py)")
    print("3. En el navegador de tu celular (Chrome o Safari), abre:")
    print()
    print(f"   🌐 http://{ip}:{puerto}")
    print()
    print("4. ¡Listo! La app debería cargar en tu celular")
    print()
    
    print("📲 INSTALAR COMO APP (PWA):")
    print("-" * 70)
    print("Android (Chrome):")
    print("  → Menú (⋮) → 'Agregar a pantalla de inicio'")
    print()
    print("iOS (Safari):")
    print("  → Compartir (⎙) → 'Agregar a pantalla de inicio'")
    print()
    
    print("🔧 SI NO CONECTA:")
    print("-" * 70)
    print("1. Verifica que estén en la misma red WiFi")
    print("2. Desactiva temporalmente el firewall o abre el puerto 5000:")
    print("   PowerShell (Admin):")
    print("   New-NetFirewallRule -DisplayName 'Flask' -Direction Inbound \\")
    print("   -LocalPort 5000 -Protocol TCP -Action Allow")
    print()
    
    print("=" * 70)
    print("📚 Más información: Ver GUIA_MOVIL.md")
    print("=" * 70)

if __name__ == "__main__":
    main()

