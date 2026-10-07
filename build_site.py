"""Copy the finished pages into site/ and point their cross-links at each other. Home is static."""
import os, shutil
os.makedirs('site', exist_ok=True)
links = {
    'https://claude.ai/artifact/AoFCVRTdEmTrrKvJ2GYDCn': '/eras',        # Eight Eras
    'https://claude.ai/artifact/HiEz7vniAU1m1NCaFH7qny': '/long-play',   # The Long Play
}
for src, dst in [('output/eight_eras.html', 'site/eras.html'), ('output/the_long_play.html', 'site/long-play.html'),
                 ('output/wrapped.html', 'site/wrapped.html')]:
    html = open(src, encoding='utf-8').read()
    for a, b in links.items():
        html = html.replace(a, b)
    # the artifact host adds the document skeleton; a standalone site needs its own
    if not html.lstrip().lower().startswith('<!doctype'):
        html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                '<style>[hidden]{display:none!important}img{max-width:100%}</style>\n</head>\n<body>\n' + html + '\n</body>\n</html>\n')
    open(dst, 'w', encoding='utf-8').write(html)
    print(dst, len(html) // 1024, 'KB')

# ---- way back: a slim bar above both long pages ----
BACK = ('<style>.uw-back{display:flex;justify-content:space-between;gap:16px;padding-block:16px 0;font:500 11px/1.3 var(--mono);'
        'letter-spacing:.1em;text-transform:uppercase}.uw-back a{color:var(--muted);text-decoration:none}.uw-back a:hover{color:var(--ink)}</style>'
        '<nav class="col uw-back"><a href="/">← Unwrapped</a><a href="/wrapped">Watch the story</a></nav>\n')
for page in ['site/eras.html', 'site/long-play.html']:
    html = open(page, encoding='utf-8').read()
    if 'uw-back' not in html:
        html = html.replace('<div class="col">', BACK + '<div class="col">', 1)
    open(page, 'w', encoding='utf-8').write(html)

# ---- home: thumbnails of the two long pages, drawn from the real data ----
import json
E = json.load(open('output/dash4.json', encoding='utf-8'))
D = json.load(open('output/dash2.json', encoding='utf-8'))
GC = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948', '#B3B5AE']

def river(w=320, h=150, pad=8):
    """Genre shares per month as a 100% stacked area: the eras page's river, in miniature."""
    rows = [[v / sum(r) for v in r] for r in E['genre'] if sum(r) > 1]
    n = len(rows); x = lambda i: pad + i * (w - 2 * pad) / (n - 1)
    base = [0.0] * n; paths = []
    for g in range(len(GC)):
        top = [base[i] + rows[i][g] for i in range(n)]
        y = lambda v: pad + v * (h - 2 * pad)
        pts = [f'{x(i):.1f},{y(top[i]):.1f}' for i in range(n)] + [f'{x(i):.1f},{y(base[i]):.1f}' for i in reversed(range(n))]
        paths.append(f'<polygon points="{" ".join(pts)}" fill="{GC[g]}"/>')
        base = top
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Genre shares month by month">{"".join(paths)}</svg>'

def calendar(w=320, h=150, pad=8):
    """Every day as a cell, months across and days down: the Long Play calendar, turned on its side."""
    S = ['#E6E8E3', '#D3D9F6', '#9FAEF0', '#6478E6', '#2F45D8', '#1B2690']
    months = sorted({d[:7] for d, *_ in D['cal']}); n = len(months)
    cw = (w - 2 * pad) / n; ch = (h - 2 * pad) / 31; cells = []
    for d, mu, po, _ in D['cal']:
        t = mu + po; lvl = 0 if t == 0 else 1 if t < 15 else 2 if t < 45 else 3 if t < 90 else 4 if t < 180 else 5
        i = months.index(d[:7]); day = int(d[8:]) - 1
        cells.append(f'<rect x="{pad + i * cw:.1f}" y="{pad + day * ch:.1f}" width="{cw - 1.2:.1f}" height="{ch - 1:.1f}" rx="1" fill="{S[lvl]}"/>')
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Minutes listened, every day">{"".join(cells)}</svg>'

home = open('home_template.html', encoding='utf-8').read().replace('__ERAS_SVG__', river()).replace('__LP_SVG__', calendar())
open('site/index.html', 'w', encoding='utf-8').write(home)
print('site/index.html (home)', len(home) // 1024, 'KB')
