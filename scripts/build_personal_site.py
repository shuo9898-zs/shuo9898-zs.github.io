"""Build personal pages from verified profile data, using only the standard library."""
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / '_data/personal.json').read_text(encoding='utf-8'))

def e(value):
    return escape(str(value), quote=True)

def link(label, url, css=''):
    attrs = ' target="_blank" rel="noopener noreferrer"' if url.startswith('https://') else ''
    return f'<a href="{e(url)}"{attrs} class="{e(css)}">{label}</a>'

def profile_links():
    return '<div class="profile-links">' + ''.join([
        link('Email', 'mailto:' + DATA['email'], 'button-link primary'),
        link('Google Scholar', DATA['scholar'], 'button-link'),
        link('GitHub', DATA['github'], 'button-link'),
        link('CV <span aria-hidden="true">↗</span>', '/cv/', 'button-link'),
    ]) + '</div>'

def projects():
    rows = []
    for item in DATA['projects']:
        resources = ''.join(link(e(ref['label']), ref['url']) for ref in item['links'])
        tags = ''.join(f'<span>{e(tag)}</span>' for tag in item['tags'])
        rows.append(f'''<article class="research-item" data-project-group="{e(item['group'])}" id="{e(item['id'])}">
        <a href="{e(item['url'])}" class="research-image" aria-label="Explore {e(item['name'])}">
        <img src="{e(item['image'])}" width="960" height="580" alt="{e(item['alt'])}" loading="lazy">
        <span class="research-image-label" aria-hidden="true">View project ↗</span></a>
        <div class="research-copy"><div class="project-name">{e(item['name'])}</div>
        <h3>{link(e(item['title']), item['url'])}</h3><p>{e(item['description'])}</p>
        <div class="tags" aria-label="Research topics">{tags}</div>
        <div class="resource-links" aria-label="{e(item['name'])} resources">{resources}</div></div></article>''')
    return '<div class="research-list">' + '\n'.join(rows) + '</div>'

def publications(full=False):
    rows = []
    for item in DATA['publications']:
        authors = ', '.join('<strong>' + e(author) + '</strong>' if author == DATA['name'] else e(author) for author in item['authors'])
        extras = ''
        if full:
            resources = link('Publisher / DOI', item['url'])
            if item.get('pdf'):
                resources += link('Open PDF', item['pdf'])
            extras = f'''<p class="pub-details">{e(item['details'])}</p><div class="resource-links">{resources}</div>
            <details class="citation"><summary>BibTeX</summary><pre><code>{e(item['bibtex'])}</code></pre>
            <button type="button" class="copy-citation" data-copy-citation aria-live="polite" hidden>Copy BibTeX</button></details>'''
        rows.append(f'''<article class="publication" id="{e(item['id'])}"><div class="pub-year">{item['year']}</div>
        <div><h3>{link(e(item['title']), item['url'])}</h3><p class="pub-authors">{authors}</p>
        <p class="pub-venue"><em>{e(item['venue'])}</em> · {e(item['type'])}</p>{extras}</div></article>''')
    return '<div class="publication-list">' + '\n'.join(rows) + '</div>'

def education():
    return '<div class="entry-list">' + ''.join(f'''<article class="entry"><h3>{e(item['institution'])}</h3>
    <p>{e(item['degree'])}</p><p class="entry-date">{e(item['dates'])}</p></article>''' for item in DATA['education']) + '</div>'

def experience():
    return '<div class="entry-list">' + ''.join(f'''<article class="entry"><h3>{e(item['institution'])}</h3>
    <p>{e(item['role'])}</p><p class="entry-date">{e(item['dates'])}</p></article>''' for item in DATA['experience']) + '</div>'

def news(limit=None):
    items = DATA['news'] if limit is None else DATA['news'][:limit]
    return '<ul class="news-list">' + ''.join(f'<li><time>{e(item["date"])}</time><span>{e(item["text"])}</span></li>' for item in items) + '</ul>'

def heading(title, description=''):
    return f'<header class="page-heading"><h1>{e(title)}</h1>' + (f'<p>{description}</p>' if description else '') + '</header>'

def section(title, content, target='', action=''):
    return '<section class="section"' + (f' id="{e(target)}"' if target else '') + f'><div class="section-heading"><h2>{e(title)}</h2>{action}</div>{content}</section>'

def home():
    topics = ''.join(f'<span>{e(topic)}</span>' for topic in DATA['interests'])
    hero = f'''<section class="hero" aria-labelledby="profile-name"><div class="hero-copy">
    <p class="eyebrow">Human interaction · Simulation · Intelligent driving</p>
    <h1 id="profile-name">Shuo Zhang</h1><p class="affiliation">PhD Candidate · New York University</p>
    <div class="bio"><p>I build <strong>human-in-the-loop driving simulations</strong> to study how people interact with vehicles and each other in complex road environments.</p>
    <p>My work spans <strong>research and system development</strong>: building VR interfaces and simulation tools, connecting multimodal data streams, and studying behavior, trajectory prediction, and autonomous driving policies.</p></div>
    {profile_links()}<p class="opportunity">Interested in research and engineering opportunities in HCI, autonomous driving, robotics, and applied machine learning.</p>
    <div class="interests" aria-label="Research interests">{topics}</div></div>
    <figure class="hero-portrait"><img class="portrait" src="/assets/images/research/shuo-zhang.webp" width="430" height="504" alt="Shuo Zhang" fetchpriority="high">
    <figcaption class="portrait-caption">New York University<br>New York, USA</figcaption></figure></section>'''
    return (hero + section('Selected research', projects(), 'research', link('All projects <span aria-hidden="true">↗</span>', '/projects/'))
        + section('Selected publications', publications(), 'publications', link('Publications & citations <span aria-hidden="true">↗</span>', '/publications/'))
        + section('News & highlights', news(3), 'news')
        + '<div class="section two-columns"><section><div class="section-heading"><h2>Education</h2></div>' + education()
        + '</section><section><div class="section-heading"><h2>Industry experience</h2></div>' + experience() + '</section></div>')

def project_page():
    return (heading('Research projects', 'I build simulation platforms, collect multimodal human data, and study learning-based approaches to autonomous driving.')
        + '''<div class="page-body"><div class="project-filters" data-project-filters hidden role="group" aria-label="Filter projects by research area">
        <button type="button" data-filter="all" aria-pressed="true">All projects</button>
        <button type="button" data-filter="interaction" aria-pressed="false">Human interaction & VR</button>
        <button type="button" data-filter="intelligence" aria-pressed="false">Driving intelligence</button></div>
        <p class="filter-count" data-filter-count role="status" aria-live="polite">3 projects</p>''' + projects() + '</div>')

def publication_page():
    return (heading('Publications', 'Published work on immersive simulation, human behavior, and road safety. ' + link('Google Scholar <span aria-hidden="true">↗</span>', DATA['scholar']))
        + '<div class="page-body">' + section('Peer-reviewed papers', publications(True))
        + section('Current research', '<p class="section-intro">For ongoing work, project demos, and available manuscripts, see '
        + link('DuoRoad', '/duoroad/') + ', ' + link('WZDrive', '/wzdrive/') + ', and ' + link('WZ-Plan', '/wz-plan/') + '.</p>') + '</div>')

def cv_page():
    rows = ''.join(f'<article class="cv-project"><h3>{link(e(item["name"]), item["url"])}</h3><p>{e(item["description"])}</p></article>' for item in DATA['projects'])
    return ('''<header class="page-heading cv-header"><div><h1>Shuo Zhang</h1><p>Curriculum vitae · PhD Candidate, New York University</p>
        <div class="cv-meta">''' + link(e(DATA['email']), 'mailto:' + DATA['email']) + ' · New York, USA<br>' + link('shuo9898-zs.github.io', DATA['url'])
        + '''</div></div><button type="button" class="print-button" data-print-cv>Print / Save PDF</button></header><div class="page-body">'''
        + section('Research interests', '<p class="cv-summary">Human–computer interaction; VR-based driving simulation; multimodal human and vehicle sensing; autonomous driving; imitation learning and motion planning.</p>')
        + section('Education', education()) + section('Industry experience', experience()) + section('Selected research projects', rows)
        + section('Publications', publications()) + section('Methods & tools', '''<dl class="methods">
        <dt>Simulation</dt><dd>CARLA, Unreal Engine, SUMO, virtual reality, human-in-the-loop experiments</dd>
        <dt>Sensing & behavior</dt><dd>Eye tracking, biometric signals, RGB cameras, LiDAR, vehicle trajectories</dd>
        <dt>Learning & analysis</dt><dd>Trajectory prediction, reinforcement learning, imitation learning, multimodal data analysis</dd></dl>''')
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
        + link('Research projects <span aria-hidden="true">↗</span>', '/projects/') + '<small>Platforms, datasets, and demos</small></li></ul></section></div>')

def render(path, title, description, content):
    navigation = [('/', 'About'), ('/projects/', 'Research'), ('/publications/', 'Publications'), ('/cv/', 'CV'), ('/contact/', 'Contact')]
    nav = ''.join(f'<a href="{url}"' + (' aria-current="page"' if url == path else '') + f'>{label}</a>' for url, label in navigation)
    canonical = DATA['url'] + path
    schema = {'@context': 'https://schema.org', '@type': 'Person', 'name': DATA['name'], 'url': DATA['url'], 'jobTitle': DATA['role'],
        'affiliation': {'@type': 'Organization', 'name': DATA['institution']}, 'sameAs': [DATA['scholar'], DATA['github']], 'knowsAbout': DATA['interests']}
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="author" content="Shuo Zhang">
<meta name="robots" content="index,follow"><meta name="theme-color" content="#ffffff">
<meta name="google-site-verification" content="0Ti41fKsUuiW6AApOdysfqzf4T-JKErg_DVaoyRkRIk">
<link rel="canonical" href="{e(canonical)}"><meta property="og:type" content="profile"><meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}"><meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{DATA['url']}/assets/images/research/shuo-zhang.webp"><meta property="og:image:alt" content="Shuo Zhang">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/svg+xml" href="/assets/images/personal-favicon.svg">
<link rel="stylesheet" href="/assets/css/personal.css?v=1"><script defer src="/assets/js/personal.js?v=1"></script>
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
