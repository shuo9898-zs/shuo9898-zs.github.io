const previews = [...document.querySelectorAll('video[data-preview]')];
const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
let previewsPaused = motionPreference.matches || Boolean(navigator.connection?.saveData);
const visiblePreviews = new Set();
const motionButtons = [...document.querySelectorAll('[data-motion-toggle]')];

function syncPreviews() {
  previews.forEach((video) => {
    const shouldPlay = !previewsPaused && !document.hidden && visiblePreviews.has(video)
      && !video.closest('[data-project-group]')?.hidden;
    video.toggleAttribute('data-static', motionPreference.matches && previewsPaused);
    if (shouldPlay) {
      if (!video.src) {
        video.src = video.dataset.preview;
        video.muted = true;
        video.load();
      }
      video.play().catch(() => {}); // Poster remains visible if autoplay is unavailable.
    } else {
      video.pause();
    }
  });
  motionButtons.forEach((button) => {
    button.textContent = previewsPaused ? 'Play previews' : 'Pause previews';
  });
}

if (previews.length && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(({ target, isIntersecting }) => {
      if (isIntersecting) visiblePreviews.add(target);
      else visiblePreviews.delete(target);
    });
    syncPreviews();
  }, { threshold: 0.15 });
  previews.forEach((video) => {
    const start = Number(video.dataset.previewStart) || 0;
    const end = Number(video.dataset.previewEnd) || 0;
    video.addEventListener('loadedmetadata', () => {
      if (start > 0 && start < video.duration) video.currentTime = start;
    });
    video.addEventListener('loadeddata', () => {
      if (!video.seeking) video.setAttribute('data-ready', '');
    });
    video.addEventListener('seeked', () => video.setAttribute('data-ready', ''));
    video.addEventListener('timeupdate', () => {
      if (end > start && video.currentTime >= end) video.currentTime = start;
    });
    observer.observe(video);
  });
  motionButtons.forEach((button) => {
    button.hidden = false;
    button.addEventListener('click', () => {
      previewsPaused = !previewsPaused;
      syncPreviews();
    });
  });
  motionPreference.addEventListener('change', () => {
    previewsPaused = motionPreference.matches;
    syncPreviews();
  });
  document.addEventListener('visibilitychange', syncPreviews);
  syncPreviews();
}

document.querySelectorAll('[data-project-filters]').forEach((filters) => {
  const items = [...document.querySelectorAll('[data-project-group]')];
  const count = document.querySelector('[data-filter-count]');
  filters.hidden = false;
  filters.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-filter]');
    if (!button) return;
    filters.querySelectorAll('button').forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
    let visible = 0;
    items.forEach((item) => {
      item.hidden = button.dataset.filter !== 'all' && item.dataset.projectGroup !== button.dataset.filter;
      if (!item.hidden) visible += 1;
    });
    if (count) count.textContent = `${visible} ${visible === 1 ? 'project' : 'projects'}`;
    syncPreviews();
  });
});

document.querySelectorAll('[data-copy-citation]').forEach((button) => {
  button.hidden = !navigator.clipboard;
  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(button.closest('details').querySelector('code').textContent);
      button.textContent = 'Copied';
      setTimeout(() => { button.textContent = 'Copy BibTeX'; }, 2000);
    } catch {
      button.textContent = 'Select the citation above to copy';
    }
  });
});

document.querySelector('[data-print-cv]')?.addEventListener('click', () => window.print());
