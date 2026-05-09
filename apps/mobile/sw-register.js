// Register service worker for offline support and PWA features
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js')
      .then((reg) => {
        console.log('[PWA] Service Worker registered:', reg);
        // Check for updates periodically
        setInterval(() => {
          reg.update();
        }, 60000); // Every minute
      })
      .catch((error) => {
        console.warn('[PWA] Service Worker registration failed:', error);
      });
  });
  
  // Handle SW updates
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    console.log('[PWA] Service Worker updated');
    window.location.reload();
  });
} else {
  console.warn('[PWA] Service Worker not supported in this browser');
}

// Request install prompt
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  console.log('[PWA] Install prompt is available');
  // Show install button if needed
  const installBtn = document.getElementById('installBtn');
  if (installBtn) {
    installBtn.style.display = 'block';
    installBtn.addEventListener('click', () => {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('[PWA] User installed the app');
        }
        deferredPrompt = null;
      });
    });
  }
});

// Track installation
window.addEventListener('appinstalled', () => {
  console.log('[PWA] App installed successfully');
  deferredPrompt = null;
});
