const CACHE_NAME = 'marche-live-v2.1'; // Incrementato
const ASSETS = [
    '/',
    '/index.html',
    '/style.css',
    '/main.js',
    '/logo.svg'
];

self.addEventListener('install', (event) => {
    self.skipWaiting(); // Forza l'attivazione immediata
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS);
        })
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
            );
        })
    );
});

self.addEventListener('fetch', (event) => {
    // Strategia Network First: prova la rete, se fallisce usa la cache
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});
