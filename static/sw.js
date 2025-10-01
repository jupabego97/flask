// Service Worker para Nano - PWA de Reparaciones IT
const CACHE_NAME = 'nano-reparaciones-v3.0.0';
const STATIC_CACHE = 'nano-static-v3.0.0';
const DYNAMIC_CACHE = 'nano-dynamic-v3.0.0';
const IMAGES_CACHE = 'nano-images-v3.0.0';

// Recursos a cachear inicialmente (críticos para primera carga)
const STATIC_ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/sw.js',
    '/static/browserconfig.xml',
    // Bootstrap y Font Awesome (CDNs confiables)
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js'
];

// Recursos adicionales para cache agresivo
const ADDITIONAL_CACHE = [
    '/static/icons/icon-72.png',
    '/static/icons/icon-96.png',
    '/static/icons/icon-128.png',
    '/static/icons/icon-144.png',
    '/static/icons/icon-152.png',
    '/static/icons/icon-192.png',
    '/static/icons/icon-384.png',
    '/static/icons/icon-512.png',
    '/static/icons/nano-logo.svg',
    '/static/icons/nano-icon-circle.svg'
];

// Recursos dinámicos a cachear
const DYNAMIC_ASSETS = [
    '/api/tarjetas'
];

// Instalación del Service Worker
self.addEventListener('install', (event) => {
    console.log('📦 Nano Service Worker: Instalando versión 3.0.0...');
    event.waitUntil(
        Promise.all([
            // Cache básico crítico
            caches.open(STATIC_CACHE).then((cache) => {
                console.log('📦 Nano: Cacheando recursos críticos...');
                return cache.addAll(STATIC_ASSETS).catch(err => {
                    console.warn('⚠️ Algunos recursos no pudieron cachearse:', err);
                    return Promise.resolve();
                });
            }),
            // Cache agresivo de iconos y logos
            caches.open(IMAGES_CACHE).then((cache) => {
                console.log('📦 Nano: Cacheando iconos y logos PWA...');
                return cache.addAll(ADDITIONAL_CACHE).catch(err => {
                    console.warn('⚠️ Algunos iconos no pudieron cachearse:', err);
                    return Promise.resolve();
                });
            })
        ])
        .then(() => {
            console.log('✅ Nano Service Worker: Instalación completada');
            return self.skipWaiting();
        })
        .catch((error) => {
            console.error('❌ Nano Service Worker: Error en instalación:', error);
        })
    );
});

// Activación del Service Worker
self.addEventListener('activate', (event) => {
    console.log('🚀 Service Worker: Activando...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                        console.log('🗑️ Service Worker: Eliminando cache antiguo:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('🚀 Service Worker: Activación completada');
            return self.clients.claim();
        })
    );
});

// Función para verificar conectividad
function isOnline() {
    return navigator.onLine;
}

// Interceptar solicitudes de red
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Estrategia de cache para recursos estáticos críticos
    if (STATIC_ASSETS.some(asset => request.url.includes(asset))) {
        event.respondWith(
            caches.match(request)
                .then((response) => {
                    if (response) {
                        return response;
                    }
                    // Si no está en cache, intentar red
                    return fetch(request).then((fetchResponse) => {
                        // Solo cachear respuestas exitosas
                        if (fetchResponse.status === 200) {
                            const responseClone = fetchResponse.clone();
                            caches.open(STATIC_CACHE).then((cache) => {
                                cache.put(request, responseClone);
                            });
                        }
                        return fetchResponse;
                    });
                })
        );
        return;
    }

    // Estrategia de cache para iconos (cache-first, agresivo)
    if (request.url.includes('/static/icons/')) {
        event.respondWith(
            caches.match(request)
                .then((response) => {
                    return response || fetch(request).then((fetchResponse) => {
                        if (fetchResponse.status === 200) {
                            const responseClone = fetchResponse.clone();
                            caches.open(IMAGES_CACHE).then((cache) => {
                                cache.put(request, responseClone);
                            });
                        }
                        return fetchResponse;
                    });
                })
        );
        return;
    }

    // Estrategia de cache para API (network-first con fallback)
    if (request.method === 'GET' && DYNAMIC_ASSETS.some(asset => request.url.includes(asset))) {
        event.respondWith(
            fetch(request)
                .then((response) => {
                    // Cachear respuestas exitosas
                    if (response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(DYNAMIC_CACHE).then((cache) => {
                            cache.put(request, responseClone);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    // Fallback a cache si no hay red
                    return caches.match(request);
                })
        );
        return;
    }

    // Para otras solicitudes, intentar red primero, luego cache
    event.respondWith(
        fetch(request)
            .catch(() => {
                return caches.match(request);
            })
    );
});

// Manejar mensajes desde el cliente
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

// Actualizar cache cuando hay cambios
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'UPDATE_CACHE') {
        console.log('🔄 Service Worker: Actualizando cache...');
        event.waitUntil(
            caches.open(DYNAMIC_CACHE).then((cache) => {
                return fetch('/api/tarjetas').then((response) => {
                    if (response.ok) {
                        return cache.put('/api/tarjetas', response);
                    }
                });
            })
        );
    }
});
