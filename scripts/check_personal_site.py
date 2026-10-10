"""Check the published artifact for broken personal-page assets and template leaks."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
pages = ['index.html', 'projects/index.html', 'publications/index.html', 'cv/index.html', 'contact/index.html']
errors = []

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids = [], set()
        self.h1 = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'h1':
            self.h1 += 1
        if attrs.get('id'):
            if attrs['id'] in self.ids:
                errors.append('Duplicate element ID: ' + attrs['id'])
            self.ids.add(attrs['id'])
        if tag == 'img' and not attrs.get('alt'):
            errors.append('Image missing alternative text')
        for key in ('href', 'src'):
            if key in attrs:
                self.refs.append(attrs[key])

for relative in pages:
    file = root / relative
    if not file.exists():
        errors.append('Missing page: ' + relative)
        continue
    text = file.read_text(encoding='utf-8')
    for placeholder in ['GitHub University', 'Paper Title Number', 'Your Sidebar Name', 'https://...', '{{', '{%', 'content="noindex"']:
        if placeholder in text:
            errors.append(relative + ': unwanted placeholder: ' + placeholder)
    page = Page()
    page.feed(text)
    if page.h1 != 1:
        errors.append(relative + ': expected one main heading')
    if '<link rel="canonical"' not in text or 'name="description"' not in text:
        errors.append(relative + ': missing search metadata')
    for ref in page.refs:
        parsed = urlsplit(ref)
        if parsed.scheme or parsed.netloc:
            continue
        if parsed.path.startswith('/wz-plan/'):
            continue  # Separate GitHub Pages project repository.
        if not parsed.path:
            if parsed.fragment and parsed.fragment not in page.ids:
                errors.append(relative + ': missing anchor: ' + ref)
            continue
        target = root / unquote(parsed.path).lstrip('/') if parsed.path.startswith('/') else file.parent / unquote(parsed.path)
        if parsed.path.endswith('/'):
            target = target / 'index.html'
        if not target.is_file():
            errors.append(relative + ': missing local link/asset: ' + ref)

if root.name == '_site':
    for pattern in ('files/paper*.pdf', 'files/slides*.pdf', 'publication/*paper-title*', 'publications/*paper-title*', 'cv-json/index.html'):
        for file in root.glob(pattern):
            errors.append('Template example published: ' + str(file.relative_to(root)))

if errors:
    raise SystemExit('\n'.join(errors))
print('Validated 5 personal pages: local links, images, headings, metadata, and template cleanup')
