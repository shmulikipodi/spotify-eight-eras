import contextlib,io
with contextlib.redirect_stdout(io.StringIO()): exec(open('trends.py').read())
import numpy as np
m.loc[m.g=='U','g']='O'
GN={'P':'Pop','E':'Electronic & dance','H':'Hip-hop & R&B','I':'Israeli','A':'Alternative & modern rock','C':'Classic rock','M':'Hard rock & metal','N':'Instrumental & classical','O':'Everything else'}
G=['P','E','H','I','A','C','M','N','O']
R={}
R['months']=months; R['gnames']=[GN[g] for g in G]; R['gkeys']=G
gm=m.pivot_table(index='mon',columns='g',values='sec',aggfunc='sum').reindex(index=months,columns=G).fillna(0)/3600
R['genre']=gm.round(2).values.tolist()
R['podh']=[round(p[p.mon==mo].sec.sum()/3600,1) for mo in months]
# decades
dv={'5':'60s & before','6':'60s & before','7':'70s','8':'80s','9':'90s','0':'2000s','1':'2010s','2':'2020s'}
DK=['60s & before','70s','80s','90s','2000s','2010s','2020s']
m['dk']=m.dec.map(dv)
dm=m[m.dk.notna()].pivot_table(index='mon',columns='dk',values='sec',aggfunc='sum').reindex(index=months,columns=DK).fillna(0)/3600
R['dkeys']=DK; R['decade']=dm.round(2).values.tolist()
yrs={'5':1958,'6':1965,'7':1975,'8':1985,'9':1995,'0':2005,'1':2015,'2':2022}; m['yv']=m.dec.map(yrs)
R['avgyear']=[ (round(float(np.average(g.yv,weights=g.sec)),1) if g.sec.sum()>3600 else None) for mo in months for g in [m[(m.mon==mo)&m.yv.notna()]]]
# diversity & novelty
st=m.groupby('mon').apply(stats).reindex(months)
R['eff']=[None if pd.isna(v) or st.h[i]<1 else round(v) for i,v in enumerate(st.eff)]
R['arts']=[None if pd.isna(v) or st.h[i]<1 else int(v) for i,v in enumerate(st.arts)]
R['top5']=[None if pd.isna(v) or st.h[i]<1 else round(100*v) for i,v in enumerate(st.top5)]
R['newtr']=[None if (i<3 or pd.isna(v) or st.h[i]<1) else round(100*v) for i,v in enumerate(st.newtr)]
R['musich']=[round(v,1) if not pd.isna(v) else 0 for v in st.h]
# eras
ERAS=[('2023-05','2024-01'),('2024-02','2024-06'),('2024-07','2024-10'),('2024-11','2025-02'),('2025-03','2025-07'),('2025-08','2025-10'),('2025-11','2026-03'),('2026-06','2026-09')]
life=m.groupby('artist').sec.sum()
R['eras']=[]
for a,b in ERAS:
    e=m[(m.mon>=a)&(m.mon<=b)]; tot=e.sec.sum()
    gs=e.groupby('g').sec.sum().reindex(G).fillna(0)/tot
    ah=e.groupby('artist').sec.sum().sort_values(ascending=False)
    sig=[(x,round(ah[x]/3600,1),round(100*ah[x]/life[x])) for x in ah.index[:40] if ah[x]>=1800 and ah[x]/life[x]>=0.5][:5]
    tk=e[e.sec>=30].groupby(['track','artist']).size().sort_values(ascending=False).head(3)
    first=m.groupby('artist').ts.min()
    newa=[x for x in ah.index[:80] if a<=first[x].strftime('%Y-%m')<=b and ah[x]>=1800][:5] if a>'2023-08' else []
    yv=e[e.yv.notna()]
    R['eras'].append(dict(a=a,b=b,h=round(tot/3600),g=[round(100*v) for v in gs],top=[[x,round(ah[x]/3600,1)] for x in ah.index[:6]],sig=sig,
       trk=[[k[0],k[1],int(v)] for k,v in tk.items()],new=newa,yr=round(float(np.average(yv.yv,weights=yv.sec))),eff=round(stats(e).eff)))
# similarity matrix on artist vectors
valid=[mo for mo in months if gm.loc[mo].sum()>1]
am=m.pivot_table(index='mon',columns='artist',values='sec',aggfunc='sum').reindex(valid).fillna(0)
A=np.sqrt(am.div(am.sum(1),axis=0).values); A=A/np.linalg.norm(A,axis=1,keepdims=True)
S=A@A.T; R['simm']=valid; R['sim']=np.round(S,2).tolist()
R['turn']=[None]+[round(float(1-S[i,i-1]),2) for i in range(1,len(valid))]
# lifelines: artists >=2h
big=life[life>=2*3600].sort_values(ascending=False)
pv=m[m.artist.isin(big.index)].pivot_table(index='artist',columns='mon',values='sec',aggfunc='sum').reindex(columns=months).fillna(0)/3600
R['life']=[dict(a=x,g=m[m.artist==x].g.iloc[0],h=round(big[x]/3600,1),v=[round(v,2) for v in pv.loc[x]]) for x in big.index]
# constants: in how many eras ≥30 min
cnt={}
for a,b in ERAS:
    e=m[(m.mon>=a)&(m.mon<=b)].groupby('artist').sec.sum()
    for x in e[e>=1800].index: cnt[x]=cnt.get(x,0)+1
R['constants']=[[x,c,round(life[x]/3600,1)] for x,c in sorted(cnt.items(),key=lambda kv:(-kv[1],-life[kv[0]])) if c>=6]
# long tail
r=life.sort_values(ascending=False); tot=r.sum()
R['tail']=dict(n=len(r),top10=round(100*r.head(10).sum()/tot),top100=round(100*r.head(100).sum()/tot),top400=round(100*r.head(400).sum()/tot),
  under5=int((r<300).sum()),under5share=round(100*r[r<300].sum()/tot,1),once=int((m.groupby('artist').size()==1).sum()))
# genre totals + top artists
R['gtot']=[[GN[g],round(m[m.g==g].sec.sum()/3600),int(m[m.g==g].artist.nunique()),[[x,round(v/3600,1)] for x,v in m[m.g==g].groupby('artist').sec.sum().nlargest(6).items()]] for g in G]
R['gyear']={str(y):[round(100*v) for v in (g.groupby('g').sec.sum().reindex(G).fillna(0)/g.sec.sum())] for y,g in m.groupby('yr')}
R['tot']=dict(h=round(df.sec.sum()/3600),mh=round(m.sec.sum()/3600),arts=int(m.artist.nunique()),tracks=int(m.spotify_track_uri.nunique()),coverage=round(100*m[m.artist.isin(top400)].sec.sum()/m.sec.sum(),1))
R=json.loads(json.dumps(R,ensure_ascii=False,default=lambda o:o.item() if hasattr(o,'item') else str(o)))
json.dump(R,open('output/dash3.json','w'),ensure_ascii=False)
print(len(json.dumps(R,ensure_ascii=False))//1024,'KB', len(R['life']),'lifelines')
for e in R['eras']: print(e['a'],e['b'],e['h'],'h yr',e['yr'],'eff',e['eff'],dict(zip(G,e['g'])),'\n  top',e['top'][:4],'\n  sig',e['sig'],'\n  new',e['new'],'\n  trk',e['trk'][:2])
print(R['constants']); print(R['tail']); print(R['gyear'])
print('turn',dict(zip(valid,R['turn'])))
