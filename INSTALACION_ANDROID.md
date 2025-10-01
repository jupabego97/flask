# 📱 Guía de Instalación en Android

## ✅ Requisitos Cumplidos para PWA

La aplicación Nano cumple con **todos** los requisitos de Chrome para ser instalable en Android:

### 1. ✅ Manifest Web App (manifest.json)
- Nombre: "Nano - Sistema de Reparaciones"
- Nombre corto: "Nano"
- start_url: "/"
- display: "standalone"
- Iconos: 192x192 y 512x512 (requeridos)

### 2. ✅ Service Worker
- Registrado en `/static/sw.js`
- Versión: 3.0.0
- Con estrategias de cache offline

### 3. ✅ HTTPS o localhost
- Funciona en localhost para desarrollo
- **Debe desplegarse con HTTPS en producción**

### 4. ✅ Iconos requeridos
- icon-192.png ✅
- icon-512.png ✅
- Ambos con purpose: "any maskable"

---

## 🚀 Cómo Instalar en Android

### Método 1: Banner Automático
1. Abre la app en **Chrome para Android**
2. Espera 3-5 segundos
3. Aparecerá un banner en la parte inferior: **"Instalar Nano"**
4. Toca **"Instalar"**
5. ¡Listo! La app aparecerá en tu pantalla de inicio

### Método 2: Menú de Chrome
1. Abre `https://nano.up.railway.app` en Chrome Android
2. Toca el menú **⋮** (tres puntos arriba a la derecha)
3. Selecciona **"Agregar a pantalla de inicio"** o **"Instalar aplicación"**
4. Confirma la instalación
5. La app se instalará con el ícono de Nano

### Método 3: Barra de direcciones
1. Busca el ícono **⊕** (plus) en la barra de direcciones
2. Toca el ícono
3. Selecciona **"Instalar"**

---

## 🔧 Solución de Problemas

### "No se puede instalar esta app"

**Causas comunes:**

1. **No estás usando HTTPS**
   - Solución: Despliega en Railway, Vercel, Netlify, etc.
   - Localhost también funciona para pruebas

2. **El Service Worker no se registró**
   - Abre DevTools en Chrome (chrome://inspect)
   - Ve a la pestaña "Application" > "Service Workers"
   - Debe aparecer `/static/sw.js` como activo

3. **Los iconos no se cargan**
   - Verifica que `/static/icons/icon-192.png` y `icon-512.png` existan
   - Abre las URLs directamente para verificar

4. **El manifest.json tiene errores**
   - Abre `/static/manifest.json` en el navegador
   - Verifica que sea JSON válido
   - Usa Chrome DevTools > Application > Manifest

---

## 🌐 Despliegue en Producción

### Railway (Recomendado)
```bash
# Ya está configurado en GitHub
# Railway detecta automáticamente los cambios y despliega
# URL: https://nano.up.railway.app
```

### Vercel
```bash
npm install -g vercel
vercel deploy
```

### Heroku
```bash
git push heroku master
```

### Requisitos:
- ✅ **HTTPS obligatorio** (todos los servicios lo incluyen)
- ✅ Service Worker funcionando
- ✅ Manifest.json accesible

---

## 🧪 Verificar que tu PWA es Instalable

### En Chrome Desktop:
1. Abre DevTools (F12)
2. Ve a **Application** > **Manifest**
3. Verifica que no haya errores en rojo
4. Ve a **Service Workers**
5. Debe aparecer como "activated and is running"

### En Chrome Android:
1. Abre `chrome://flags`
2. Busca "Desktop PWAs"
3. Habilita todas las opciones relacionadas con PWA
4. Reinicia Chrome
5. Vuelve a intentar instalar

---

## ✨ Características de la PWA Instalada

Una vez instalada, Nano se comporta como una app nativa:

- ✅ **Ícono en el launcher** de Android
- ✅ **Splash screen** con logo de Nano al abrir
- ✅ **Funciona offline** (gracias al Service Worker)
- ✅ **Sin barra de navegador** (modo standalone)
- ✅ **Notificaciones push** (si se implementan)
- ✅ **Acceso rápido** desde la pantalla de inicio
- ✅ **Actualizaciones automáticas** cuando hay nueva versión

---

## 📊 Checklist de Instalación

Antes de intentar instalar, verifica:

- [ ] La app está desplegada con **HTTPS** (no HTTP)
- [ ] El Service Worker está registrado y activo
- [ ] Los iconos 192x192 y 512x512 se cargan correctamente
- [ ] El manifest.json es válido y accesible
- [ ] Estás usando Chrome para Android (versión 80+)
- [ ] No estás en modo incógnito
- [ ] Esperaste al menos 3-5 segundos para el banner

---

## 🆘 Si Aún No Funciona

1. **Borra cache y datos de Chrome**
   - Ajustes > Apps > Chrome > Almacenamiento > Borrar datos

2. **Desinstala y reinstala Chrome**
   - En casos extremos

3. **Verifica la consola del navegador**
   ```
   chrome://inspect
   ```
   Busca errores relacionados con Service Worker o manifest

4. **Usa Lighthouse**
   - Chrome DevTools > Lighthouse
   - Ejecuta auditoría PWA
   - Corrige los errores que encuentre

---

## 📝 Notas Importantes

- **Railway.app proporciona HTTPS automáticamente** ✅
- El Service Worker solo funciona en **HTTPS o localhost**
- Los iconos deben ser **PNG cuadrados**
- El manifest debe estar en `/static/manifest.json`
- El Service Worker debe estar en la raíz del scope (`/static/sw.js`)

---

**¿Problemas?** Revisa la consola del navegador (F12) y busca errores en rojo.

**Fecha:** 2025-10-01  
**Versión:** 3.0.0

