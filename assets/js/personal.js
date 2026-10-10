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
