exec(open('build2.py').read().split("D={}")[0])
exec(open('tags.py').read())
import numpy as np
months=pd.period_range('2023-05','2026-09',freq='M').strftime('%Y-%m').tolist()
rank=m.groupby('artist').sec.sum().sort_values(ascending=False)
top400=rank.index[:400]
GEN={a:t[0] for a,t in zip(top400,T)}; DEC={a:t[1] for a,t in zip(top400,T)}
heb=m.groupby('artist').apply(lambda g:(g.track.fillna('')+g.artist.fillna('')).str.contains('[֐-׿]').mean())
def g_of(a):
    if a in GEN: return GEN[a]
    return 'I' if heb.get(a,0)>0.3 else 'U'
m['g']=m.artist.map(g_of); m['dec']=m.artist.map(DEC)
G=['P','E','H','I','A','C','M','N','O']  # stack order; U folded into O for display, kept separately
print('coverage tagged',round(100*m[m.g!='U'].sec.sum()/m.sec.sum(),1))
gm=m.pivot_table(index='mon',columns='g',values='sec',aggfunc='sum').reindex(months).fillna(0)/3600
print((gm.div(gm.sum(1),axis=0)*100).fillna(0).round(0).astype(int).to_string())
# by quarter genre share
m['q']=m.ts.dt.to_period('Q').astype(str)
gq=m.pivot_table(index='q',columns='g',values='sec',aggfunc='sum').fillna(0); print((gq.div(gq.sum(1),axis=0)*100).round(0).astype(int).to_string())
# decade
dv={'5':1955,'6':1965,'7':1975,'8':1985,'9':1995,'0':2005,'1':2015,'2':2022}
m['yr_']=m.dec.map(dv)
x=m[m.yr_.notna()]; print('avg decade by quarter', x.groupby('q').apply(lambda g:np.average(g.yr_,weights=g.sec)).round(0).to_dict())
# diversity / novelty
first_track=m.groupby('spotify_track_uri').ts.min(); m['ft']=m.spotify_track_uri.map(first_track)
m['newtrack']=(m.ts-m.ft).dt.days<30
first_art=m.groupby('artist').ts.min(); m['fa']=m.artist.map(first_art); m['newart']=(m.ts-m.fa).dt.days<30
def stats(g):
    a=g.groupby('artist').sec.sum(); p=a/a.sum(); ent=np.exp(-(p*np.log(p)).sum())
    return pd.Series(dict(h=g.sec.sum()/3600,arts=(g.groupby('artist').sec.max()>=30).sum(),eff=ent,top5=a.nlargest(5).sum()/a.sum(),newtr=(g.sec*g.newtrack).sum()/g.sec.sum(),newart=(g.sec*g.newart).sum()/g.sec.sum()))
st=m.groupby('mon').apply(stats).reindex(months); print(st.round(2).to_string())
