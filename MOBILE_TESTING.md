# 📱 Probando la App en tu Celular

## 🚀 Método 1: Red Local WiFi (Recomendado)

### Paso 1: Verificar tu IP local
Tu dirección IP local es: `192.168.100.138`

### Paso 2: Conectar celular a la misma red WiFi
- Asegúrate de que tu celular esté conectado a la **misma red WiFi** que tu computadora
- Verifica que ambos dispositivos estén en la misma red (mismo router)

### Paso 3: Configurar Firewall (Windows)
Ejecuta PowerShell como **Administrador** y ejecuta:

```powershell
# Permitir conexiones entrantes al puerto 5000
New-NetFirewallRule -DisplayName "Flask App" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

### Paso 4: Acceder desde tu celular
Abre el navegador de tu celular y ve a:
```
http://192.168.100.138:5000
```

## 🌐 Método 2: Ngrok (Acceso desde Internet)

### Instalación de Ngrok:
```bash
# Descargar ngrok desde https://ngrok.com/download
# O instalar con Chocolatey:
choco install ngrok
```

### Crear cuenta gratuita en Ngrok:
1. Ve a https://ngrok.com
2. Regístrate (cuenta gratuita disponible)
3. Obtén tu auth token

### Configurar Ngrok:
```bash
ngrok config add-authtoken TU_AUTH_TOKEN_AQUI
```

### Exponer la aplicación:
```bash
# Desde el directorio de la app
ngrok http 5000
```

### Acceder desde cualquier lugar:
Ngrok te dará una URL como:
```
https://abc123.ngrok.io
```
Usa esta URL en tu celular.

## 🔧 Solución de Problemas

### ❌ "No se puede conectar"
- ✅ Verifica que ambos dispositivos estén en la misma red WiFi
- ✅ Confirma que la aplicación esté corriendo (`python app.py`)
- ✅ Verifica el firewall de Windows
- ✅ Prueba con la IP correcta

### ❌ "Página no carga"
- ✅ Asegúrate de que la app esté corriendo en `host='0.0.0.0'`
- ✅ Verifica que no haya antivirus bloqueando
- ✅ Intenta reiniciar la aplicación

### ❌ "Funcionalidades no funcionan en móvil"
- ✅ La app está optimizada para móvil
- ✅ Funciones de cámara requieren HTTPS en algunos navegadores
- ✅ Para pruebas completas, usa ngrok con HTTPS

## 📋 Checklist de Prueba

### En tu celular:
- [ ] ✅ Página carga correctamente
- [ ] ✅ Diseño responsive funciona
- [ ] ✅ Botón "Nueva Reparación" visible
- [ ] ✅ Modal se abre correctamente
- [ ] ✅ Captura de imagen funciona
- [ ] ✅ Procesamiento IA (si tienes clave API)
- [ ] ✅ Grabación de audio funciona
- [ ] ✅ Creación de tarjetas funciona

## 🎯 Funcionalidades Móviles Especiales

### 📷 Cámara del Celular:
- ✅ Acceso directo a cámara trasera
- ✅ Vista previa de imagen capturada
- ✅ Procesamiento automático con IA

### 🎤 Grabación de Voz:
- ✅ Acceso al micrófono del celular
- ✅ Transcripción automática
- ✅ Indicadores visuales de grabación

### 👆 Interfaz Táctil:
- ✅ Botones optimizados para toque
- ✅ Navegación por gestos
- ✅ Formularios adaptados a móvil

¡La aplicación está completamente optimizada para uso móvil! 🚀📱✨
