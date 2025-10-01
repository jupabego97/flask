// Service Worker para PWA de Reparaciones IT
const CACHE_NAME = 'reparaciones-it-v1.0.0';
const STATIC_CACHE = 'static-v1.0.0';
const DYNAMIC_CACHE = 'dynamic-v1.0.0';

// Recursos a cachear inicialmente
const STATIC_ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/sw.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js'
];

// Recursos dinámicos a cachear
const DYNAMIC_ASSETS = [
    '/api/tarjetas'
];

// Instalación del Service Worker
self.addEventListener('install', (event) => {
    console.log('📦 Service Worker: Instalando...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('📦 Service Worker: Cacheando recursos estáticos...');
                return cache.addAll(STATIC_ASSETS);
            })
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

// Interceptar solicitudes de red
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Estrategia de cache para recursos estáticos
    if (STATIC_ASSETS.some(asset => request.url.includes(asset))) {
        event.respondWith(
            caches.match(request)
                .then((response) => {
                    return response || fetch(request).then((fetchResponse) => {
                        return caches.open(STATIC_CACHE).then((cache) => {
                            cache.put(request, fetchResponse.clone());
                            return fetchResponse;
                        });
                    });
                })
        );
        return;
    }

    // Estrategia de cache para API (solo GET)
    if (request.method === 'GET' && DYNAMIC_ASSETS.some(asset => request.url.includes(asset))) {
        event.respondWith(
            caches.open(DYNAMIC_CACHE).then((cache) => {
                return fetch(request).then((response) => {
                    // Cachear solo respuestas exitosas
                    if (response.status === 200) {
                        cache.put(request, response.clone());
                    }
                    return response;
                }).catch(() => {
                    // Si falla la red, intentar desde cache
                    return cache.match(request);
                });
            })
        );
        return;
    }

    // Para otras solicitudes, intentar red primero, luego cache
    event.respondWith(
        fetch(request).catch(() => {
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
