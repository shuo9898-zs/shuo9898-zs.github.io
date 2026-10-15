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
        summary = '' if compact else f'<p>{e(item["description"])}</p><div class="tags" aria-label="Research topics">{tags}</div>'
        identity = '' if compact else f'<div class="project-name">{e(item["name"])}</div>'
        rows.append(f'''<article class="research-item" data-project-group="{e(item['group'])}" id="{e(item['id'])}">
        <a href="{e(item['url'])}" class="research-image" aria-label="Explore {e(item['name'])}">
        <img src="{e(item['image'])}" width="960" height="580" alt="{e(item['alt'])}" loading="lazy">
        {preview}</a>
        <div class="research-copy">{identity}
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
        <p class="pub-venue"><em>{e(item['venue'])}</em> · {e(item['type'])}</p>{extras}</div></article>''')
    return '<div class="publication-list">' + '\n'.join(rows) + '</div>'

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
        rows.append(f'''<article class="publication"><div class="pub-year">{e(item['name'])}</div><div>
        <h3>{link(e(item['paper_title']), item['url'])}</h3><p class="pub-authors">{project_authors(item)}</p>
        <p class="pub-venue"><em>{e(item['status'])}</em></p><div class="resource-links">{link('Project & resources', item['url'])}</div></div></article>''')
    return '<div class="publication-list manuscript-list">' + ''.join(rows) + '</div>'

def skills():
    return '<dl class="methods">' + ''.join(f'<dt>{e(item["label"])}</dt><dd>{e(item["items"])}</dd>' for item in DATA['skills']) + '</dl>'

def news(limit=None):
    items = DATA['news'] if limit is None else DATA['news'][:limit]
    return '<ul class="news-list">' + ''.join(f'<li><time>{e(item["date"])}</time><span>{e(item["text"])}</span></li>' for item in items) + '</ul>'

def heading(title, description=''):
    return f'<header class="page-heading"><h1>{e(title)}</h1>' + (f'<p>{description}</p>' if description else '') + '</header>'

def section(title, content, target='', action=''):
    return '<section class="section"' + (f' id="{e(target)}"' if target else '') + f'><div class="section-heading"><h2>{e(title)}</h2>{action}</div>{content}</section>'

def home():
    hero = f'''<section class="hero" aria-labelledby="profile-name"><div class="hero-copy">
    <h1 id="profile-name">Shuo Zhang</h1><p class="affiliation">PhD Candidate · New York University</p><p class="graduation">{e(DATA['graduation'])}</p>
    <div class="bio"><p>My research connects <strong>human-in-the-loop simulation</strong>, multimodal sensing, and autonomous driving. I build VR–CARLA platforms to study driver–worker interactions and use human driving data to develop trajectory prediction and motion planning methods.</p>
    <p>My engineering experience spans simulation systems, VR interfaces, data collection pipelines, and LiDAR diagnostics. I am interested in research and engineering opportunities in autonomous driving, robotics, HCI, and applied machine learning.</p></div>
    {profile_links()}</div>
    <figure class="hero-portrait"><img class="portrait" src="/assets/images/research/shuo-zhang.webp" width="430" height="504" alt="Shuo Zhang" fetchpriority="high">
    <figcaption class="portrait-caption">New York University<br>New York, USA</figcaption></figure></section>'''
    return (hero + section('Research & publications',
            '<div class="research-toolbar"><p>Manuscripts, ongoing work, and published papers.</p><button type="button" class="motion-toggle" data-motion-toggle hidden>Pause previews</button></div>'
            + projects(True) + '<div class="published-research">' + publications() + '</div>',
            'research', link('Full publication list <span aria-hidden="true">↗</span>', '/publications/'))
        + section('News & highlights', news(3), 'news')
        + '<div class="section two-columns"><section><div class="section-heading"><h2>Education</h2></div>' + education()
        + '</section><section><div class="section-heading"><h2>Industry experience</h2></div>' + experience() + '</section></div>')

def project_page():
    return (heading('Research projects', 'I build simulation platforms, collect multimodal human data, and study learning-based approaches to autonomous driving.')
        + '''<div class="page-body"><div class="project-filters" data-project-filters hidden role="group" aria-label="Filter projects by research area">
        <button type="button" data-filter="all" aria-pressed="true">All projects</button>
        <button type="button" data-filter="interaction" aria-pressed="false">Human interaction & VR</button>
        <button type="button" data-filter="intelligence" aria-pressed="false">Driving intelligence</button></div>
        <div class="research-toolbar"><p class="filter-count" data-filter-count role="status" aria-live="polite">3 projects</p><button type="button" class="motion-toggle" data-motion-toggle hidden>Pause previews</button></div>''' + projects() + '</div>')

def publication_page():
    return (heading('Publications', 'Manuscripts and published work on immersive simulation, human behavior, and autonomous driving. ' + link('Google Scholar <span aria-hidden="true">↗</span>', DATA['scholar']))
        + '<div class="page-body">' + section('Manuscripts & ongoing work', manuscripts())
        + section('Peer-reviewed papers', publications(True)) + '</div>')

def cv_page():
    rows = ''.join(f'<article class="cv-project"><h3>{link(e(item["name"]), item["url"])}</h3><p>{e(item["description"])}</p></article>' for item in DATA['projects'])
    return ('''<header class="page-heading cv-header"><div><h1>Shuo Zhang</h1><p>Curriculum vitae · PhD Candidate, New York University</p>
        <div class="cv-meta">''' + link(e(DATA['email']), 'mailto:' + DATA['email']) + ' · New York, USA<br>' + link('shuo9898-zs.github.io', DATA['url'])
        + '''</div></div><div class="cv-actions">''' + link('Download CV (PDF)', DATA['resume'], 'button-link primary')
        + '''<button type="button" class="print-button" data-print-cv>Print this page</button></div></header><div class="page-body">'''
        + section('Research interests', '<p class="cv-summary">Human–computer interaction; VR-based driving simulation; multimodal human and vehicle sensing; autonomous driving; imitation learning and motion planning.</p>')
        + section('Education', education()) + section('Research & industry experience', experience(True)) + section('Selected research projects', rows)
        + section('Manuscripts & ongoing work', manuscripts()) + section('Published papers', publications()) + section('Technical skills', skills())
        + section('Presentations & recognition', news()) + '</div>')

def contact_page():
    return (heading('Get in touch', 'I welcome conversations about research and engineering opportunities, and collaborations in simulation, autonomous driving, and machine learning.')
        + '''<div class="page-body contact-grid"><section aria-labelledby="email-title"><h2 id="email-title">Email</h2>'''
        + link(e(DATA['email']), 'mailto:' + DATA['email'], 'contact-email')
        + '''<p class="contact-note">Based at New York University in New York, USA.</p><p class="contact-note">For an overview of my work, explore the project demos or view my CV.</p>'''
        + '<div class="profile-links">' + link('Explore research', '/projects/', 'button-link') + link('View CV', '/cv/', 'button-link')
        + '''</div></section><section aria-labelledby="elsewhere-title"><h2 id="elsewhere-title" class="visually-hidden">Elsewhere</h2><ul class="contact-links">'''
        + '<li>' + link('Google Scholar <span aria-hidden="true">↗</span>', DATA['scholar']) + '<small>Publications and citations</small></li><li>'
        + link('GitHub <span aria-hidden="true">↗</span>', DATA['github']) + '<small>Research code and open-source projects</small></li><li>'
        + link('LinkedIn <span aria-hidden="true">↗</span>', DATA['linkedin']) + '<small>Professional profile</small></li><li>'
        + link('Research projects <span aria-hidden="true">↗</span>', '/projects/') + '<small>Platforms, datasets, and demos</small></li></ul></section></div>')

def render(path, title, description, content):
    navigation = [('/', 'About'), ('/projects/', 'Research'), ('/publications/', 'Publications'), ('/cv/', 'CV'), ('/contact/', 'Contact')]
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
<link rel="stylesheet" href="/assets/css/personal.css?v=3"><script defer src="/assets/js/personal.js?v=2"></script>
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
        ('/', 'Shuo Zhang | Human-in-the-loop Simulation & Autonomous Driving', DATA['description'], home()),
        ('/projects/', 'Research | Shuo Zhang', 'Research projects by Shuo Zhang: DuoRoad, WZDrive, and WZ-Plan. Explore simulation platforms, datasets, demos, and code.', project_page()),
        ('/publications/', 'Publications | Shuo Zhang', 'Publications by Shuo Zhang on VR simulation, eye tracking, human behavior, and roadway work-zone safety.', publication_page()),
        ('/cv/', 'CV | Shuo Zhang', 'Curriculum vitae of Shuo Zhang, PhD candidate at New York University. Education, industry experience, research, and publications.', cv_page()),
        ('/contact/', 'Contact | Shuo Zhang', 'Contact Shuo Zhang at New York University about research, engineering opportunities, and collaborations.', contact_page()),
    ]
    for path, title, description, content in pages:
        dest = ROOT / path.strip('/') / 'index.html'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(path, title, description, content), encoding='utf-8')
    print(f'Built {len(pages)} personal pages from _data/personal.json')

if __name__ == '__main__':
    build()
