/* 쿵짝 서비스워커 — 오프라인 지원.
   게임 파일을 바꾸면 CACHE 버전을 올려야 새 파일이 적용된다. */
const CACHE = 'kungjjak-v29';  /* 노래 120BPM · 로고는 굴러와서 쿵 */
const ASSETS = [
  './', './index.html', './manifest.json',
  './icons/icon-192.png', './icons/icon-512.png',
  './icons/icon-maskable-512.png', './icons/apple-touch-icon.png',
  './privacy.html'
];

self.addEventListener('install', e => {
  e.waitUntil(
    /* cache:'reload' — 브라우저 HTTP 캐시를 건너뛰고 서버에서 받는다. GitHub Pages 가
       10분 캐시(max-age=600)를 걸어서, 배포 직후 설치되면 새 캐시에 옛 파일이 담길 수 있다. */
    caches.open(CACHE)
      .then(c => c.addAll(ASSETS.map(u => new Request(u, {cache: 'reload'}))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.mode === 'navigate') {
    /* 페이지(게임 본체)는 네트워크 먼저 — 인터넷이 되면 늘 최신 게임을 받고, 안 되면 캐시로 뜬다.
       캐시 먼저이던 때는 배포해도 옛 게임이 계속 떠서, 아이폰에서 고친 게 안 보였다(2026-09-12). */
    e.respondWith(
      fetch(e.request).then(res => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {});
        }
        return res;
      }).catch(() => caches.match(e.request, {ignoreSearch: true})
        .then(hit => hit || caches.match('./index.html')))
    );
    return;
  }
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {});
      return res;
    }).catch(() => caches.match('./index.html')))
  );
});
