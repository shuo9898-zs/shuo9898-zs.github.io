// Only the demonstration selected by the visitor plays.
const moduleVideos = [...document.querySelectorAll('.module-video video')];
moduleVideos.forEach(video => {
  video.addEventListener('play', () => {
    moduleVideos.forEach(other => { if (other !== video) other.pause(); });
  });
  const reportMediaError = () => {
    const figure = video.closest('figure');
    if (figure.querySelector('.media-error')) return;
    const message = document.createElement('p');
    message.className = 'media-error';
    message.setAttribute('role', 'status');
    message.textContent = 'The video could not be loaded. Refresh the page and try again.';
    figure.appendChild(message);
  };
  video.addEventListener('error', reportMediaError);
  video.querySelector('source')?.addEventListener('error', reportMediaError);
});

document.querySelectorAll('.cosim-carousel').forEach(carousel => {
  const track = carousel.querySelector('.cosim-track');
  const slides = [...carousel.querySelectorAll('.cosim-slide')];
  const selectors = [...carousel.querySelectorAll('.cosim-picker button')];
  const arrows = [...carousel.querySelectorAll('.cosim-arrow')];
  const [previous, next] = arrows;
  let current = 0;

  function reflect(index) {
    current = Math.max(0, Math.min(slides.length - 1, index));
    selectors.forEach((button, i) => button.setAttribute('aria-current', String(i === current)));
    previous.disabled = current === 0;
    next.disabled = current === slides.length - 1;
    slides.forEach((slide, i) => {
      if (i !== current) slide.querySelectorAll('video').forEach(video => video.pause());
    });
  }

  function show(index) {
    reflect(index);
    track.scrollTo({left: current * track.clientWidth, behavior: 'auto'});
  }

  previous.addEventListener('click', () => show(current - 1));
  next.addEventListener('click', () => show(current + 1));
  selectors.forEach((button, index) => button.addEventListener('click', () => show(index)));
  track.addEventListener('scroll', () => {
    if (track.clientWidth) reflect(Math.round(track.scrollLeft / track.clientWidth));
  }, {passive: true});
  track.addEventListener('keydown', event => {
    if (event.target !== track) return;
    if (event.key === 'ArrowRight') { event.preventDefault(); show(current + 1); }
    if (event.key === 'ArrowLeft') { event.preventDefault(); show(current - 1); }
  });
  window.addEventListener('resize', () => track.scrollTo({left: current * track.clientWidth, behavior: 'auto'}));
});
