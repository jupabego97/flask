// Service Worker para PWA de Reparaciones IT
const CACHE_NAME = 'reparaciones-it-v2.0.0';
const STATIC_CACHE = 'static-v2.0.0';
const DYNAMIC_CACHE = 'dynamic-v2.0.0';
const IMAGES_CACHE = 'images-v2.0.0';

// Recursos a cachear inicialmente (críticos para primera carga)
const STATIC_ASSETS = [
    '/',
    '/static/manifest.json',
    '/sw.js',
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
    '/static/icons/icon-512.png'
];

// Recursos dinámicos a cachear (solo recursos estáticos, NO APIs)
const DYNAMIC_ASSETS = [
    // Las APIs no se cachean para evitar datos obsoletos
    // '/api/tarjetas' - REMOVIDO para permitir sincronización en tiempo real
];

// Instalación del Service Worker
self.addEventListener('install', (event) => {
    console.log('📦 Service Worker: Instalando versión 2.0.0...');
    event.waitUntil(
        Promise.all([
            // Cache básico crítico
            caches.open(STATIC_CACHE).then((cache) => {
                console.log('📦 Service Worker: Cacheando recursos críticos...');
                return cache.addAll(STATIC_ASSETS);
            }),
            // Cache agresivo de iconos
            caches.open(IMAGES_CACHE).then((cache) => {
                console.log('📦 Service Worker: Cacheando iconos PWA...');
                return cache.addAll(ADDITIONAL_CACHE);
            })
        ])
        .then(() => {
            console.log('📦 Service Worker: Instalación completada');
            return self.skipWaiting();
        })
        .catch((error) => {
            console.error('❌ Service Worker: Error en instalación:', error);
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
                        // Solo cachear respuestas exitosas de GET requests
                        if (fetchResponse.status === 200 && request.method === 'GET') {
                            const responseClone = fetchResponse.clone();
                            caches.open(STATIC_CACHE).then((cache) => {
                                cache.put(request, responseClone).catch((error) => {
                                    console.log('⚠️ No se pudo cachear:', request.url, error);
                                });
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

// Limpiar cache de API cuando hay actualizaciones (NO cachear)
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'CLEAR_API_CACHE') {
        console.log('🧹 Service Worker: Limpiando cache de API...');
        event.waitUntil(
            caches.open(DYNAMIC_CACHE).then((cache) => {
                return cache.delete('/api/tarjetas');
            }).then(() => {
                console.log('✅ Cache de API limpiado');
            }).catch((error) => {
                console.log('⚠️ Error limpiando cache:', error);
            })
        );
    }
});

// Evento legacy de actualización de cache (ya no cachea APIs)
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'UPDATE_CACHE') {
        console.log('🔄 Service Worker: Evento UPDATE_CACHE legacy - APIs ya no se cachean');
        // No hacer nada - las APIs no se cachean para permitir sincronización en tiempo real
    }
});
