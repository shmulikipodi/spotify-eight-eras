import contextlib,io
with contextlib.redirect_stdout(io.StringIO()): exec(open('build3.py').read())
def wk(a,b):
    x=m[(m.date>=pd.Timestamp(a).date())&(m.date<=pd.Timestamp(b).date())]
    print(a,b,round(x.sec.sum()/3600,1),'h', x.groupby('artist').sec.sum().nlargest(6).div(3600).round(1).to_dict())
wk('2024-06-24','2024-06-30'); wk('2025-12-15','2025-12-21'); wk('2024-09-30','2024-10-06'); wk('2025-06-23','2025-07-06'); wk('2026-06-22','2026-07-05')
# daily genre around rock flip
for a,b in [('2024-10-26','2024-11-12'),('2025-07-15','2025-08-14')]:
    x=m[(m.date>=pd.Timestamp(a).date())&(m.date<=pd.Timestamp(b).date())]
    d=x.pivot_table(index='date',columns='g',values='sec',aggfunc='sum').fillna(0)
    t=d.sum(1); r=(d.div(t,axis=0)*100).round(0).astype(int); r['min']=(t/60).round(0)
    r['top']=x.groupby(['date','artist']).sec.sum().reset_index().sort_values('sec').groupby('date').tail(1).set_index('date').artist
    print(r.to_string())
# afterlife of each era's signature (top 5 by hours with >=50% lifetime in era)
for i,e in enumerate(R['eras']):
    s=[x[0] for x in e['sig']]
    aft=m[(m.artist.isin(s))&(m.mon>e['b'])].sec.sum()/3600; inn=m[(m.artist.isin(s))&(m.mon>=e['a'])&(m.mon<=e['b'])].sec.sum()/3600
    bef=m[(m.artist.isin(s))&(m.mon<e['a'])].sec.sum()/3600
    print(i+1, s, 'before',round(bef,1),'in',round(inn,1),'after',round(aft,1))
