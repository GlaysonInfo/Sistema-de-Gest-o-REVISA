// REVISA Mobile - Service Worker
// Enables offline support, caching, and background sync

const CACHE_NAME = 'revisa-mobile-v1';
const RUNTIME_CACHE = 'revisa-mobile-runtime-v1';
const OFFLINE_URL = './index.html';

const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './app.js',
  './styles.css',
  './manifest.json',
  './assets/logo-revisa.png'
];

// Install event - cache assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Service Worker] Caching assets');
      return cache.addAll(ASSETS_TO_CACHE).catch((err) => {
        console.warn('[Service Worker] Some assets failed to cache:', err);
      });
    })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip cross-origin requests
  if (url.origin !== self.location.origin) {
    return;
  }

  // API requests - network first with cache fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(apiRequest(request));
    return;
  }

  // Static assets - cache first
  event.respondWith(cacheFirst(request));
});

// Network first strategy for API calls
async function apiRequest(request) {
  try {
    const response = await fetch(request);
    if (response.status === 200) {
      // Cache successful responses
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.log('[Service Worker] Network failed, trying cache:', request.url);
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    // Return offline response if available
    return new Response(
      JSON.stringify({
        error: 'offline',
        message: 'Você está offline. Os dados estão sendo sincronizados quando a conexão retornar.',
        timestamp: new Date().toISOString()
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Cache first strategy for static assets
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) {
    return cached;
  }

  try {
    const response = await fetch(request);
    if (response.status === 200) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.log('[Service Worker] Fetch failed:', request.url);
    return new Response('Offline', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

// Background sync - sync pending requests when online
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-intakes') {
    event.waitUntil(syncPendingIntakes());
  }
});

async function syncPendingIntakes() {
  try {
    console.log('[Service Worker] Syncing pending intakes...');
    // This would be implemented in the app.js to specifically handle pending data
    self.clients.matchAll().then((clients) => {
      clients.forEach((client) => {
        client.postMessage({
          type: 'BACKGROUND_SYNC',
          action: 'sync-intakes'
        });
      });
    });
  } catch (error) {
    console.error('[Service Worker] Sync failed:', error);
  }
}

// Message handling - allow app to communicate with SW
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    caches.delete(RUNTIME_CACHE);
  }
});
