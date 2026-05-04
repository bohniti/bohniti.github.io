// Phase 10 — Gallery lightbox (page-scoped IIFE).
//
// Loaded only from layouts/gallery/single.html via <script src="js/lightbox.js" defer>
// (D-14 — NOT loaded from baseof.html; keeps blog/about/home pages JS-free).
//
// Decisions implemented:
//   D-08  Native <dialog>.showModal() — focus trap, Esc, top-layer, aria-modal all free.
//   D-09  Single <dialog id="gallery-lightbox"> in DOM, mutated in place per click.
//   D-10  Backdrop click closes via `e.target === dialog`.
//   D-11  Manual body-scroll-lock — save document.body.style.overflow, set 'hidden', restore.
//   D-14  Page-scoped IIFE (~80 LOC); no globals leaked.
//   D-15  Click → preventDefault → swap dialog content → showModal(); arrow keys; touch swipe;
//         body lock save/restore on open/close; NO preloading (Pitfall 11).
//   D-16  DOM-walk siblings for prev/next: Array.from(grid.children).indexOf(a) ± 1 mod len.
//   D-17  dialog.setAttribute('aria-label', `Photo ${n} of ${total}`) on open and each nav.
//   D-18  50px deltaX threshold for touch swipe; vertical swipe (deltaY > deltaX) is no-op.
//   D-19  Read full URL from a.href (Pitfall 7 — NOT from inner <img src>, which is the thumb).
//   REQ GALLERY-04  figcaption textContent uses empty-string fallback for caption-less photos.

(function () {
  'use strict';

  const dialog = document.querySelector('dialog#gallery-lightbox');
  const grid   = document.querySelector('.gallery-grid');
  if (!dialog || !grid) return;

  const img      = dialog.querySelector('.gallery-lightbox-img');
  const caption  = dialog.querySelector('.gallery-lightbox-caption');
  const closeBtn = dialog.querySelector('.gallery-lightbox-close');
  const prevBtn  = dialog.querySelector('.gallery-lightbox-prev');
  const nextBtn  = dialog.querySelector('.gallery-lightbox-next');

  if (!img || !caption || !closeBtn || !prevBtn || !nextBtn) return;

  const items = Array.from(grid.querySelectorAll('a.gallery-item'));
  const total = items.length;
  if (total === 0) return;

  let activeIdx = -1;
  let savedBodyOverflow = '';
  let touchStartX = 0;
  let touchStartY = 0;

  function showAt(idx) {
    if (idx < 0) idx = total - 1;
    if (idx >= total) idx = 0;
    activeIdx = idx;

    const a = items[idx];
    img.src     = a.getAttribute('href');           // Pitfall 7: full URL is on <a href>, not inner <img>.
    img.alt     = a.dataset.alt || '';              // D-03 / Pitfall 12: lightbox alt is REQUIRED per author convention.
    caption.textContent = a.dataset.caption || '';  // REQ GALLERY-04 / D-02: empty string for caption-less photos.

    // D-17 — screen-reader announces position on open and each nav.
    dialog.setAttribute('aria-label', 'Photo ' + (idx + 1) + ' of ' + total);
  }

  function open(idx) {
    showAt(idx);
    // D-11 — save current overflow value, lock body scroll.
    savedBodyOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    // D-08 — native focus trap, Esc handling, top-layer, aria-modal all free.
    dialog.showModal();
  }

  function next() { showAt(activeIdx + 1); }
  function prev() { showAt(activeIdx - 1); }

  // (1) Bind click on every gallery item — preventDefault preserves JS-disabled fallback (D-19).
  items.forEach(function (a, idx) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      open(idx);
    });
  });

  // (3) Arrow keys — Esc is free via showModal().
  dialog.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft')  { e.preventDefault(); prev(); }
    if (e.key === 'ArrowRight') { e.preventDefault(); next(); }
  });

  // (4) Close button.
  closeBtn.addEventListener('click', function () { dialog.close(); });

  // Prev / next buttons (UI affordance for mouse users; keyboard already covered).
  prevBtn.addEventListener('click', function (e) { e.stopPropagation(); prev(); });
  nextBtn.addEventListener('click', function (e) { e.stopPropagation(); next(); });

  // (5) Backdrop click → close (D-10).
  dialog.addEventListener('click', function (e) {
    if (e.target === dialog) dialog.close();
  });

  // (6) Touch swipe — 50px deltaX threshold (D-18).
  dialog.addEventListener('touchstart', function (e) {
    if (e.touches.length !== 1) return;
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
  }, { passive: true });

  dialog.addEventListener('touchend', function (e) {
    if (e.changedTouches.length !== 1) return;
    const dx = e.changedTouches[0].clientX - touchStartX;
    const dy = e.changedTouches[0].clientY - touchStartY;
    if (Math.abs(dy) > Math.abs(dx)) return; // vertical swipe is no-op (D-18).
    if (Math.abs(dx) < 50) return;            // below threshold — no nav.
    if (dx > 0) prev(); else next();
  });

  // (8) Restore body scroll on close (D-11).
  dialog.addEventListener('close', function () {
    document.body.style.overflow = savedBodyOverflow;
  });

  // (9) NO image preloading (Pitfall 11; deferred GALLERY-FUT-02).
})();
