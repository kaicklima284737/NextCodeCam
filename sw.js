// Service worker: app shell offline + cache em tempo de execução das bibliotecas (jsQR, Tesseract, jsPDF).
// Chamadas de IA e Firebase nunca são cacheadas.
const V='camacad-v2',SHELL=['./','index.html','config.js','manifest.webmanifest','icons/icon-192.png','icons/icon-512.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!=V).map(x=>caches.delete(x)))).then(()=>clients.claim())));
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!='GET'||/generativelanguage|firebaseio/.test(r.url))return;
e.respondWith(caches.match(r).then(h=>{const n=fetch(r).then(x=>{if(x.ok||x.type=='opaque')caches.open(V).then(c=>c.put(r,x.clone()));return x}).catch(()=>h);return h||n}))});
