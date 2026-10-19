"""Build personal pages from verified profile data, using only the standard library."""
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / '_data/personal.json').read_text(encoding='utf-8'))

def e(value):
    return escape(str(value), quote=True)

def link(label, url, css=''):
    attrs = ' target="_blank" rel="noopener noreferrer"' if url.startswith('https://') or url.endswith('.pdf') else ''
    return f'<a href="{e(url)}"{attrs} class="{e(css)}">{label}</a>'

def profile_links():
    return '<div class="profile-links">' + ''.join([
        link('Email', 'mailto:' + DATA['email'], 'button-link primary'),
        link('Google Scholar', DATA['scholar'], 'button-link'),
        link('GitHub', DATA['github'], 'button-link'),
        link('LinkedIn', DATA['linkedin'], 'button-link'),
        link('CV (PDF) <span aria-hidden="true">↗</span>', DATA['resume'], 'button-link'),
    ]) + '</div>'

def project_authors(item):
    names = ', '.join('<strong>' + e(name) + '</strong>' if name == DATA['name'] else e(name) for name in item['authors'])
    return names + (', et al.' if item.get('authors_et_al') else '')

def projects(compact=False):
    rows = []
    for item in DATA['projects']:
        resources = ''.join(link(e(ref['label']), ref['url']) for ref in item['links'])
        tags = ''.join(f'<span>{e(tag)}</span>' for tag in item['tags'])
        preview = ''
        if item.get('preview'):
            preview = f'''<video class="research-preview" muted loop playsinline preload="none" poster="{e(item['image'])}" width="640" height="360" aria-hidden="true" data-preview="{e(item['preview'])}" data-preview-start="{e(item.get('preview_start', 0))}" data-preview-end="{e(item.get('preview_end', ''))}"></video>'''
        authors = '<p class="pub-authors">' + project_authors(item) + '</p>'
        summary = f'<div class="tags" aria-label="Research topics">{tags}</div>'
        rows.append(f'''<article class="research-item" data-project-group="{e(item['group'])}" id="{e(item['id'])}">
        <a href="{e(item['url'])}" class="research-image" aria-label="Explore {e(item['name'])}">
        <img src="{e(item['image'])}" width="960" height="580" alt="{e(item['alt'])}" loading="lazy">
        {preview}</a>
        <div class="research-copy">
        <h3>{link(e(item['paper_title']), item['url'])}</h3>{authors}
        <p class="pub-venue"><em>{e(item['status'])}</em></p>{summary}
        <div class="resource-links" aria-label="{e(item['name'])} resources">{resources}</div></div></article>''')
    return '<div class="research-list' + (' compact-research' if compact else '') + '">' + '\n'.join(rows) + '</div>'

def publications(full=False):
    rows = []
    for item in DATA['publications']:
        shown_authors = item['authors'] if full else item['authors'][:5]
        authors = ', '.join('<strong>' + e(author) + '</strong>' if author == DATA['name'] else e(author) for author in shown_authors)
        if len(shown_authors) < len(item['authors']):
            authors += ', et al.'
        extras = ''
        resources = link('Paper', item.get('pdf', item['url']))
        if item.get('pdf'):
            resources += link('Publication', item['url'])
        if full:
            extras = f'''<p class="pub-details">{e(item['details'])}</p><div class="resource-links">{resources}</div>
            <details class="citation"><summary>BibTeX</summary><pre><code>{e(item['bibtex'])}</code></pre>
            <button type="button" class="copy-citation" data-copy-citation aria-live="polite" hidden>Copy BibTeX</button></details>'''
        else:
            extras = f'<div class="resource-links">{resources}</div>'
        rows.append(f'''<article class="publication" id="{e(item['id'])}"><div class="pub-year">{item['year']}</div>
        <div><h3>{link(e(item['title']), item['url'])}</h3><p class="pub-authors">{authors}</p>
        <p class="pub-venue"><em>{e(item['venue'])}</em> · {item['year']}</p>{extras}</div></article>''')
    return '<div class="publication-list">' + '\n'.join(rows) + '</div>'

def publication_cards():
    rows = []
    for item in DATA['publications']:
        authors = ', '.join('<strong>' + e(name) + '</strong>' if name == DATA['name'] else e(name) for name in item['authors'][:5])
        if len(item['authors']) > 5:
            authors += ', et al.'
        paper_url = item.get('pdf', item['url'])
        if item.get('image'):
            animation = f' data-gif-preview="{e(item["gif"])}" data-poster="{e(item["image"])}"' if item.get('gif') else ''
            media = f'''<a href="{e(paper_url)}" target="_blank" rel="noopener noreferrer" class="research-image paper-figure" aria-label="Read {e(item['title'])}">
            <img src="{e(item['image'])}" width="{e(item.get('image_width',720))}" height="{e(item.get('image_height',450))}" alt="{e(item['alt'])}" loading="lazy"{animation}></a>'''
        else:
            media = f'<div class="pub-year">{item["year"]}</div>'
        tags = ''.join(f'<span>{e(tag)}</span>' for tag in item.get('tags', []))
        resources = link('Paper', paper_url)
        if item.get('pdf'):
            resources += link('Publication', item['url'])
        media_class = '' if item.get('image') else ' paper-without-figure'
        rows.append(f'''<article class="research-item published-paper{media_class}" data-project-group="{e(item['group'])}" id="{e(item['id'])}">{media}
        <div class="research-copy"><h3>{link(e(item['title']), item['url'])}</h3><p class="pub-authors">{authors}</p>
        <p class="pub-venue"><em>{e(item['venue'])}</em> · {item['year']}</p>
        <div class="tags" aria-label="Research topics">{tags}</div>
        <div class="resource-links">{resources}</div></div></article>''')
    return '<div class="research-list publication-cards">' + '\n'.join(rows) + '</div>'

def education():
    return '<div class="entry-list">' + ''.join(f'''<article class="entry"><h3>{e(item['institution'])}</h3>
    <p>{e(item['degree'])}</p><p class="entry-date">{e(item['dates'])}</p></article>''' for item in DATA['education']) + '</div>'

def experience(full=False):
    rows = []
    items = DATA['experience'] if full else [item for item in DATA['experience'] if item['institution'] != DATA['institution']]
    for item in items:
        details = '<ul class="experience-bullets">' + ''.join('<li>' + e(text) + '</li>' for text in item['bullets']) + '</ul>' if full else '<p>' + e(item['summary']) + '</p>'
        rows.append(f'''<article class="entry"><h3>{e(item['institution'])}</h3><p>{e(item['role'])} · {e(item['location'])}</p>
        <p class="entry-date">{e(item['dates'])}</p>{details}</article>''')
    return '<div class="entry-list">' + ''.join(rows) + '</div>'

def manuscripts():
    rows = []
    for item in DATA['projects']:
        resources = link('Project & resources', item['url'])
        if item.get('paper'):
            resources += link('Paper', item['paper'])
        rows.append(f'''<article class="publication"><div class="pub-year">{e(item['name'])}</div><div>
        <h3>{link(e(item['paper_title']), item['url'])}</h3><p class="pub-authors">{project_authors(item)}</p>
        <p class="pub-venue"><em>{e(item['status'])}</em></p><div class="resource-links">{resources}</div></div></article>''')
    return '<div class="publication-list manuscript-list">' + ''.join(rows) + '</div>'

def skills():
    return '<dl class="methods">' + ''.join(f'<dt>{e(item["label"])}</dt><dd>{e(item["items"])}</dd>' for item in DATA['skills']) + '</dl>'

def news(limit=None):
    items = DATA['news'] if limit is None else DATA['news'][:limit]
    rows = []
    for item in items:
        resource = ' ' + link(e(item.get('link_label', 'Read more')), item['url']) if item.get('url') else ''
        rows.append(f'<li><time>{e(item["date"])}</time><span>{e(item["text"])}{resource}</span></li>')
    return '<ul class="news-list">' + ''.join(rows) + '</ul>'

def heading(title, description=''):
    return f'<header class="page-heading"><h1>{e(title)}</h1>' + (f'<p>{description}</p>' if description else '') + '</header>'

def section(title, content, target='', action=''):
    return '<section class="section"' + (f' id="{e(target)}"' if target else '') + f'><div class="section-heading"><h2>{e(title)}</h2>{action}</div>{content}</section>'

def home():
    topics = ' · '.join(e(topic) for topic in DATA['interests'])
    hero = f'''<section class="hero" aria-labelledby="profile-name"><div class="hero-copy">
    <h1 id="profile-name">Shuo Zhang</h1><p class="affiliation">PhD Candidate · New York University</p>
    <div class="bio"><p>I am a <strong>final-year PhD candidate</strong> in Transportation Systems at New York University (NYU). My research uses human-in-the-loop simulation to address out-of-distribution (OOD) and safety-critical scenarios in autonomous driving and road safety. Previously, I earned my master’s degree at the University of California, Los Angeles (UCLA).</p></div>
    <p class="research-keywords" aria-label="Research interests">{topics}</p>
    {profile_links()}</div>
    <figure class="hero-portrait"><img class="portrait" src="/assets/images/research/shuo-zhang.webp" width="430" height="504" alt="Shuo Zhang" fetchpriority="high"></figure></section>'''
    return (hero + section('News', news(3), 'news') + section('Selected Publications',
            projects() + '<div class="published-research">' + publication_cards() + '</div>',
            'research', '<button type="button" class="motion-toggle" data-motion-toggle hidden>Pause previews</button>'))

def project_page():
    return (heading('Research', 'Autonomous driving, human-in-the-loop systems, and HCI. Explore the papers and research projects below.')
        + '''<div class="page-body"><div class="project-filters" data-project-filters hidden role="group" aria-label="Filter projects by research area">
        <button type="button" data-filter="all" aria-pressed="true">All research</button>
        <button type="button" data-filter="interaction" aria-pressed="false">Human interaction & VR</button>
        <button type="button" data-filter="intelligence" aria-pressed="false">Driving intelligence</button></div>
        <div class="research-toolbar"><p class="filter-count" data-filter-count role="status" aria-live="polite">7 papers</p><button type="button" class="motion-toggle" data-motion-toggle hidden>Pause previews</button></div>''' + projects() + '<div class="published-research">' + publication_cards() + '</div></div>')

def publication_page():
    entries = [dict(item, title=item['paper_title'], website=item['url']) for item in DATA['projects']]
    entries += DATA['publications']
    for item in sorted(DATA.get('additional_publications', []), key=lambda item: item['position']):
        entries.insert(item['position'] - 1, item)
    rows = []
    for number, item in enumerate(entries, 1):
        # Keep the complete bibliography concise while making Shuo's author position visible.
        author_item = dict(item)
        if len(item['authors']) > 5:
            author_item.update(authors=item['authors'][:5], authors_et_al=True)
        authors = project_authors(author_item)
        if not authors.endswith('.'):
            authors += '.'
        title = e(item['title'].rstrip('.'))
        detail = e(item.get('list_venue', item.get('venue', '')))
        if item.get('year') and not item.get('list_venue'):
            detail += f" ({item['year']})"
        if item.get('status'):
            detail += (' ' if detail else '') + '(' + e(item['status']) + ')'
        resource = ''
        if item.get('website'):
            resource = ' ' + link('(Website)', item['website'])
            if item.get('paper'):
                resource += ' ' + link('(Paper)', item['paper'])
        elif item.get('url'):
            resource = ' ' + link('(Paper)', item.get('pdf', item['url']))
        rows.append(f'<li><span class="bibliography-number" aria-hidden="true">[{number}]</span><p>{authors} “{title}.” {detail}{resource}</p></li>')
    return (heading('Publications') + '<div class="page-body"><ol class="complete-publications" aria-label="Complete publication list">'
            + ''.join(rows) + '</ol></div>')

def cv_redirect():
    resume = e(DATA['resume'])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CV | Shuo Zhang</title><meta name="description" content="Shuo Zhang's original CV (PDF).">
<meta http-equiv="refresh" content="0;url={resume}">
<link rel="canonical" href="{e(DATA['url'])}{resume}"></head>
<body><main><h1>CV</h1><p><a href="{resume}">Open Shuo Zhang's original CV (PDF)</a></p></main></body></html>'''

def contact_page():
    return (heading('Get in touch', 'I welcome conversations about research and engineering opportunities, and collaborations in simulation, autonomous driving, and machine learning.')
        + '''<div class="page-body contact-grid"><section aria-labelledby="email-title"><h2 id="email-title">Email</h2>'''
        + link(e(DATA['email']), 'mailto:' + DATA['email'], 'contact-email')
        + '''<p class="contact-note">Based at New York University in New York, USA.</p><p class="contact-note">For an overview of my work, explore the project demos or view my CV.</p>'''
        + '<div class="profile-links">' + link('Explore research', '/projects/', 'button-link') + link('View CV', DATA['resume'], 'button-link')
        + '''</div></section><section aria-labelledby="elsewhere-title"><h2 id="elsewhere-title" class="visually-hidden">Elsewhere</h2><ul class="contact-links">'''
        + '<li>' + link('Google Scholar <span aria-hidden="true">↗</span>', DATA['scholar']) + '<small>Publications and citations</small></li><li>'
        + link('GitHub <span aria-hidden="true">↗</span>', DATA['github']) + '<small>Research code and open-source projects</small></li><li>'
        + link('LinkedIn <span aria-hidden="true">↗</span>', DATA['linkedin']) + '<small>Professional profile</small></li><li>'
        + link('Research projects <span aria-hidden="true">↗</span>', '/projects/') + '<small>Platforms, datasets, and demos</small></li></ul></section></div>')

def render(path, title, description, content):
    navigation = [('/', 'Home'), ('/publications/', 'Publications'), (DATA['resume'], 'CV')]
    nav = ''.join(f'<a href="{url}"' + (' aria-current="page"' if url == path else '') + f'>{label}</a>' for url, label in navigation)
    canonical = DATA['url'] + path
    schema = {'@context': 'https://schema.org', '@type': 'Person', 'name': DATA['name'], 'url': DATA['url'], 'jobTitle': DATA['role'],
        'affiliation': {'@type': 'Organization', 'name': DATA['institution']}, 'sameAs': [DATA['scholar'], DATA['github'], DATA['linkedin']], 'knowsAbout': DATA['interests']}
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="author" content="Shuo Zhang">
<meta name="robots" content="index,follow"><meta name="theme-color" content="#ffffff">
<meta name="google-site-verification" content="0Ti41fKsUuiW6AApOdysfqzf4T-JKErg_DVaoyRkRIk">
<link rel="canonical" href="{e(canonical)}"><meta property="og:type" content="profile"><meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}"><meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{DATA['url']}/assets/images/research/shuo-zhang.webp"><meta property="og:image:alt" content="Shuo Zhang">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/svg+xml" href="/assets/images/personal-favicon.svg">
<link rel="stylesheet" href="/assets/css/personal.css?v=6"><script defer src="/assets/js/personal.js?v=3"></script>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script></head>
<body><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-inner">
<a class="wordmark" href="/">Shuo Zhang</a><nav class="site-nav" aria-label="Main navigation">{nav}</nav></div></header>
<main class="wrap" id="main">{content}</main>
<footer class="site-footer"><div class="wrap footer-inner"><div>© Shuo Zhang · New York University
<div class="footer-note">Built on <a href="https://github.com/academicpages/academicpages.github.io">AcademicPages</a> · <a href="https://github.com/shuo9898-zs/shuo9898-zs.github.io">Site source</a></div></div>
<nav class="footer-links" aria-label="Footer links">{link('Email', 'mailto:' + DATA['email'])}{link('Scholar', DATA['scholar'])}{link('GitHub', DATA['github'])}</nav>
</div></footer></body></html>'''

def build():
    pages = [
        ('/', 'Shuo Zhang | ' + ' · '.join(DATA['interests']), DATA['description'], home()),
        ('/projects/', 'Research | Shuo Zhang', 'Research projects by Shuo Zhang: DuoRoad, WZDrive, and WZ-Plan. Explore simulation platforms, datasets, demos, and code.', project_page()),
        ('/publications/', 'Publications | Shuo Zhang', 'Publications by Shuo Zhang on VR simulation, eye tracking, human behavior, and roadway work-zone safety.', publication_page()),
        ('/cv/', 'CV | Shuo Zhang', 'Original CV PDF.', ''),
        ('/contact/', 'Contact | Shuo Zhang', 'Contact Shuo Zhang at New York University about research, engineering opportunities, and collaborations.', contact_page()),
    ]
    for path, title, description, content in pages:
        dest = ROOT / path.strip('/') / 'index.html'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(cv_redirect() if path == '/cv/' else render(path, title, description, content), encoding='utf-8')
    print(f'Built {len(pages)} personal pages from _data/personal.json')

if __name__ == '__main__':
    build()
