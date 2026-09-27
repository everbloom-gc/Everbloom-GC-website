"""Generate static team and recruitment sections from data/site.json (stdlib only)."""
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent

def text(value):
    return escape(str(value), quote=True)

def link(value):
    if urlsplit(value).scheme != 'https':
        raise ValueError('External links must use HTTPS: ' + value)
    return text(value)

def replace_section(page, name, content):
    path = ROOT / page
    html = path.read_text(encoding='utf-8')
    pattern = rf'<!-- BEGIN {name} -->.*?<!-- END {name} -->'
    result, count = re.subn(pattern, lambda _: f'<!-- BEGIN {name} -->\n{content}\n<!-- END {name} -->', html, flags=re.S)
    if count != 1:
        raise ValueError(f'Missing or duplicate {name} markers in {page}')
    path.write_text(result, encoding='utf-8')

def build():
    data = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
    ranks = json.loads((ROOT / 'ranks.json').read_text(encoding='utf-8'))
    cards = []
    ids = set()
    for team in data['teams']:
        players = []
        for p in team['players']:
            if p['id'] in ids:
                raise ValueError('Duplicate player id')
            ids.add(p['id'])
            asset = (ROOT / p['image']).resolve()
            if not asset.is_relative_to(ROOT) or not asset.is_file():
                raise ValueError('Missing/invalid image: ' + p['image'])
            rank = ranks['players'].get(p['id'], {}).get('rank', p['rank'])
            socials = ''.join(f'<a href="{link(s["url"])}" target="_blank" rel="noopener noreferrer" aria-label="{text(p["name"])} on {text(s["label"])}">{text(s["label"])}</a>' for s in p['links'])
            players.append(f'''<article class="team-player">
              <img src="{text(p['image'])}" width="300" height="360" loading="lazy" decoding="async" alt="">
              <div class="team-player-info"><p class="eyebrow">{text(p['role'])}</p><h3>{text(p['name'])}</h3>
              <p class="team-rank" id="rank-{text(p['id'])}">{text(rank)}</p><div class="team-links">{socials}</div></div>
            </article>''')
        filled_count = len(players)
        for slot in team.get('openSlots', []):
            players.append(f'<article class="team-player team-open"><div class="team-open-art" aria-hidden="true"><i class="fas fa-plus"></i></div><div class="team-player-info"><p class="eyebrow">{text(slot["role"])}</p><h3>Looking for player</h3><p class="team-rank">1 spot · EU</p><div class="team-links"><a href="join.html">See open roles</a></div></div></article>')
        count_label = f'{filled_count} players · {len(team["openSlots"])} open' if team.get('openSlots') else f'{filled_count} players · Valorant'
        cards.append(f'<section class="team-section" id="{text(team["id"])}"><div class="team-heading"><h2>{text(team["name"])}</h2><span>{count_label}</span></div><div class="team-grid">{"".join(players)}</div></section>')
    jump = '<nav class="team-jump" aria-label="Choose a team">' + ''.join(f'<a href="#{text(t["id"])}">{text(t["name"])}</a>' for t in data['teams']) + '</nav>'
    replace_section('roster.html', 'TEAMS', jump + ''.join(cards) + '<aside class="join-callout"><h2>Your next chapter starts here.</h2><p>Discover open roles and get to know our application process.</p><a class="apply-btn" href="join.html">Explore open roles</a></aside>')
    roster_path = ROOT / 'roster.html'
    roster_html = roster_path.read_text(encoding='utf-8')
    roster_html = re.sub(r'(<p\b[^>]*\bid="ranks-updated"[^>]*>)[^<]*(</p>)',
                         lambda m: m[1] + 'Last rank update: ' + text(ranks['updated']) + m[2], roster_html)
    roster_path.write_text(roster_html, encoding='utf-8')
    openings = []
    for role in data['openings']:
        if not role.get('open', True):
            continue
        requirements = ''.join(f'<li>{text(r)}</li>' for r in role['requirements'])
        openings.append(f'<article class="opening"><p class="eyebrow">{text(role["team"])}</p><h2>{text(role["title"])}</h2><p>{text(role["description"])}</p><h3>Requirements</h3><ul>{requirements}</ul><a class="apply-btn" href="{link(data["applicationUrl"])}" target="_blank" rel="noopener noreferrer">Apply via Google Forms ↗</a></article>')
    replace_section('join.html', 'OPENINGS', '<div class="openings-grid">' + (''.join(openings) or '<p>No advertised openings right now. Check back soon.</p>') + '</div>')
    replace_section('index.html', 'RECRUITMENT', '<div class="recruitment-teaser"><div><p class="eyebrow">JOIN THE BLOOM</p><h2>Find your place at Everbloom.</h2><p>Explore our advertised roles, requirements and application process.</p></div><a class="apply-btn" href="join.html">Open roles →</a></div>')
    # Keep deployment self-contained: the live host currently returns HTML for
    # missing CSS/JS paths. Maintain sources centrally but embed generated copies.
    css = (ROOT / 'enhancements.css').read_text(encoding='utf-8')
    js = (ROOT / 'enhancements.js').read_text(encoding='utf-8')
    for page in ['index.html', 'roster.html', 'join.html', 'bootcamp.html', 'legal.html']:
        path = ROOT / page
        html = path.read_text(encoding='utf-8')
        html = html.replace('<link rel="stylesheet" href="enhancements.css">', '<!-- BEGIN SHARED CSS --><!-- END SHARED CSS -->')
        html = html.replace('<script src="enhancements.js" defer></script>', '')
        if '<!-- BEGIN SHARED JS -->' not in html:
            html = html.replace('</body>', '<!-- BEGIN SHARED JS --><!-- END SHARED JS -->\n</body>')
        path.write_text(html, encoding='utf-8')
        replace_section(page, 'SHARED CSS', '<style>\n' + css + '\n</style>')
        replace_section(page, 'SHARED JS', '<script>\n' + js + '\n</script>')
    print(f'Built {len(ids)} players, {len(openings)} openings with embedded shared assets.')

if __name__ == '__main__':
    build()
