import contextlib,io
with contextlib.redirect_stdout(io.StringIO()): exec(open('build3.py').read())
m['wk']=(m.ts.dt.tz_localize(None).dt.normalize()-pd.to_timedelta(m.ts.dt.dayofweek,unit='D'))
r=m[m.ts>='2026-06-20']
for w,g in r.groupby('wk'):
    a=g.groupby('artist').sec.sum().sort_values(ascending=False)/3600
    rk=list(a.index).index('Metallica')+1 if 'Metallica' in a.index else None
    ti=a.get('Tame Impala',0)
    print(str(w.date()), round(g.sec.sum()/3600,1),'h | top5', [(x,round(v,1)) for x,v in a.head(5).items()], '| Metallica #',rk, round(a.get('Metallica',0),1),'| Tame',round(ti,1))
t=m[m.artist=='Tame Impala']; print('TAME first',t.ts.min(),'total',round(t.sec.sum()/3600,1),'h')
print(t.groupby(t.mon).sec.sum().div(3600).round(2).to_dict())
print(t[t.sec>=30].groupby('track').size().sort_values(ascending=False).head(8))
td=t.groupby('date').sec.sum().div(60).round(0); print(td[td>10].to_dict())
# Metallica monthly rank
for mo in months[-8:]:
    a=m[m.mon==mo].groupby('artist').sec.sum().sort_values(ascending=False)
    if len(a): print(mo, 'Metallica rank', list(a.index).index('Metallica')+1 if 'Metallica' in a.index else '-', 'top3',list(a.index[:3]))
# late Sept genre & new artists
l=m[m.ts>='2026-09-01']; print(l.groupby('g').sec.sum().div(l.sec.sum()).round(2).to_dict())
fa=m.groupby('artist').ts.min(); new=l.groupby('artist').sec.sum().loc[lambda s: s.index.map(lambda x: fa[x]>=pd.Timestamp('2026-08-01',tz='Asia/Jerusalem'))].sort_values(ascending=False).head(10)/3600
print('new since Aug', new.round(2).to_dict())
