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

shutil.copy('home_template.html', 'site/index.html')
print('site/index.html (home)')
