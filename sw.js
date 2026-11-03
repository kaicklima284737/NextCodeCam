// Arquivos do próprio site: rede primeiro (atualizações chegam na hora); cache só como reserva offline.
// Bibliotecas externas: cache primeiro. IA e Firebase nunca são cacheados.
const V='camacad-v4',SHELL=['./','index.html','manifest.webmanifest','icons/icon-192.png','icons/icon-512.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!=V).map(x=>caches.delete(x)))).then(()=>clients.claim())));
self.addEventListener('fetch',e=>{const r=e.request,u=new URL(r.url);
  if(r.method!='GET'||u.pathname.startsWith('/api/')||/generativelanguage|firebaseio|identitytoolkit|securetoken|accounts\.google/.test(r.url))return;
  if(u.origin==location.origin){e.respondWith(fetch(r).then(x=>{if(x.ok)caches.open(V).then(c=>c.put(r,x.clone()));return x}).catch(()=>caches.match(r).then(h=>h||caches.match('index.html'))));return}
  e.respondWith(caches.match(r).then(h=>h||fetch(r).then(x=>{(x.ok||x.type=='opaque')&&caches.open(V).then(c=>c.put(r,x.clone()));return x})))});
