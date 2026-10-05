"""Condense dash2.json + dash4.json into the small data object the Unwrapped story cards read (output/wrapped.html)."""
import json

D = json.load(open('output/dash2.json', encoding='utf-8'))
E = json.load(open('output/dash4.json', encoding='utf-8'))

# hand-written for the example; uploads get theirs from Gemini
ERA_NAMES = ['Pop and festival EDM', 'Eminem moves in', 'Hip-hop summer', 'The rock turn',
             'Quieter, and instrumental', 'Deep classic rock', 'Metallica and Tuna', 'Wide open']

T = D['tot']
hours_by_hour = [round(sum(D['heat'][d][h] for d in range(7)), 1) for h in range(24)]
skips = sum(n for b, n in D['skipbins'])

W = dict(
    first=D['cal'][0][0], last=D['cal'][-1][0],
    h=T['h'], mh=T['mh'], ph=T['ph'], plays=T['plays'], attempts=T['attempts'],
    artists=T['artists'], tracks=T['tracks'],
    skips=skips, skipmed=D['skipmed'], skip10=D['skip10'],
    top=[[a['a'], a['h'], a['p'], a['f']] for a in D['explore'][:5]],
    gnames=E['gnames'],
    eras=[dict(name=ERA_NAMES[i], a=e['a'], b=e['b'], h=e['h'], g=e['g'].index(max(e['g'])), top=e['top'][0][0])
          for i, e in enumerate(E['eras'])],
    gyear=E['gyear'],
    years=[[y['y'], y['h'], y['art'][0], y['trk'][0], y['trk'][1]] for y in D['years']],
    bigday=D['bigday'], longsess=D['longsess'][0],
    streak=D['streak'], silence=D['silence'],
    obs=D['obs'][0],
    hours=hours_by_hour, wday=D['wday'],
    pod=dict(h=D['pod']['h'], eps=D['pod']['eps'], shows=D['pod']['shows'], top=D['pod']['top'][0][0]),
    tail=E['tail'],
    constants=E['constants'][:3],
)

html = open('wrapped_template.html', encoding='utf-8').read()
html = html.replace('__DATA__', json.dumps(W, ensure_ascii=False))
open('output/wrapped.html', 'w', encoding='utf-8').write(html)
print('output/wrapped.html', len(html) // 1024, 'KB')
