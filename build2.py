import pandas as pd, numpy as np, json, glob, warnings; warnings.filterwarnings('ignore')
SRC="spotify_raw/Spotify Extended Streaming History"
rows=[]
for f in glob.glob(f"{SRC}/*.json"):
    for r in json.load(open(f)): r['file']='video' if 'Video' in f else 'audio'; rows.append(r)
df=pd.DataFrame(rows).drop_duplicates(['ts','spotify_track_uri','spotify_episode_uri','ms_played'])
df['ts']=pd.to_datetime(df.ts).dt.tz_convert('Asia/Jerusalem'); df=df.sort_values('ts').reset_index(drop=True)
df=df[df.spotify_track_uri.notna()|df.spotify_episode_uri.notna()].reset_index(drop=True)
df['sec']=df.ms_played/1000; df['music']=df.spotify_track_uri.notna()
df['artist']=df.master_metadata_album_artist_name; df['track']=df.master_metadata_track_name
df['date']=df.ts.dt.date; df['mon']=df.ts.dt.strftime('%Y-%m'); df['yr']=df.ts.dt.year
gap=df.ts.diff().dt.total_seconds()-df.sec.shift().fillna(0); df['sess']=(gap>30*60).cumsum()
m=df[df.music].copy(); p=df[~df.music]
H=lambda s:round(s/3600,1)
D={}
months=pd.period_range('2023-05','2026-09',freq='M').strftime('%Y-%m').tolist(); D['months']=months
# calendar
daily=df.groupby('date').agg(mu=('sec',lambda s:0),t=('sec','sum'))
dm=m.groupby('date').sec.sum(); dp=p.groupby('date').sec.sum()
days=pd.date_range('2023-05-14','2026-09-27').date
topa=m.groupby(['date','artist']).sec.sum().reset_index().sort_values('sec').groupby('date').tail(1).set_index('date').artist
D['cal']=[[str(d), round(dm.get(d,0)/60), round(dp.get(d,0)/60), topa.get(d,'')] for d in days]
# ridgeline artists by month
top=m.groupby('artist').sec.sum().sort_values(ascending=False)
pv=m.pivot_table(index='artist',columns='mon',values='sec',aggfunc='sum').reindex(columns=months).fillna(0)
D['ridge']=[dict(a=a,h=H(top[a]),v=[round(x/3600,2) for x in pv.loc[a]]) for a in top.index[:14]]
# explorer: top 400 artists monthly + top tracks
fa=m.groupby('artist').agg(first=('ts','min'),last=('ts','max'),plays=('sec',lambda s:(s>=30).sum()),skip=('sec',lambda s:round(100*(s<10).mean())))
tt=m[m.sec>=30].groupby(['artist','track']).size().reset_index(name='n').sort_values('n',ascending=False).groupby('artist').head(3)
ttd=tt.groupby('artist').apply(lambda g:[[r.track,int(r.n)] for r in g.itertuples()]).to_dict()
D['explore']=[dict(a=a,h=H(top[a]),p=int(fa.plays[a]),k=int(fa.skip[a]),f=str(fa['first'][a].date()),l=str(fa['last'][a].date()),
   v=[round(x/3600,2) for x in pv.loc[a]],t=ttd.get(a,[])) for a in top.index[:400]]
# skip anatomy: seconds before fwdbtn, bins
sk=m[m.reason_end=='fwdbtn'].sec
bins=[0,1,2,3,5,10,20,30,60,120,240,1e9]; lab=['<1s','1–2s','2–3s','3–5s','5–10s','10–20s','20–30s','30s–1m','1–2m','2–4m','4m+']
D['skipbins']=list(zip(lab,pd.cut(sk,bins,right=False).value_counts(sort=False).tolist()))
D['skipmed']=round(sk.median(),1); D['skip10']=round(100*(sk<10).mean())
g=m.groupby(['track','artist']).agg(n=('sec','size'),done=('reason_end',lambda s:(s=='trackdone').mean()),inst=('sec',lambda s:(s<10).mean()),back=('reason_start',lambda s:(s=='backbtn').sum())).reset_index()
q=g[g.n>=25]
D['loyal']=[[r.track,r.artist,int(r.n),round(100*r.done)] for r in q.sort_values('done',ascending=False).head(8).itertuples()]
D['refused']=[[r.track,r.artist,int(r.n),round(100*r.inst)] for r in q.sort_values('inst',ascending=False).head(8).itertuples()]
D['back']=[[r.track,r.artist,int(r.back)] for r in g.sort_values('back',ascending=False).head(8).itertuples()]
# how plays start per year
def startcat(r):
    return {'clickrow':'You picked it','trackdone':'Previous song ended','fwdbtn':'You skipped to it','backbtn':'You went back'}.get(r,'Other')
m['sc']=m.reason_start.map(startcat)
D['starts']={str(y):g.sc.value_counts(normalize=True).round(3).to_dict() for y,g in m.groupby('yr')}
D['shuffle']={str(y):round(100*g.shuffle.mean()) for y,g in m.groupby('yr')}
D['offline']=round(100*df.offline.fillna(False).astype(bool).mean())
# clock
hw=df.groupby([df.ts.dt.dayofweek,df.ts.dt.hour]).sec.sum()
D['heat']=[[H(hw.get((d,h),0)) for h in range(24)] for d in range(7)]
D['wday']=[round(100*x,1) for x in df.groupby(df.ts.dt.dayofweek).sec.sum().div(df.sec.sum())]
m['h']=m.ts.dt.hour
tot=m.groupby('artist').sec.sum()
D['dayparts']=[]
for lab_,(a,b) in [('Morning',(5,11)),('Afternoon',(12,17)),('Evening',(18,22)),('Late night',(23,4))]:
    sel=m[(m.h>=a)&(m.h<=b)] if a<b else m[(m.h>=a)|(m.h<=b)]
    sh=(sel.groupby('artist').sec.sum()/tot)[tot>4*3600].sort_values(ascending=False).head(4)
    D['dayparts'].append(dict(n=lab_,r=f"{a:02d}–{(b+1)%24:02d}",share=round(100*sel.sec.sum()/m.sec.sum()),a=[[k,round(100*v)] for k,v in sh.items()]))
# sessions
s=df.groupby('sess').agg(start=('ts','min'),end=('ts','max'),n=('sec','size'),sec=('sec','sum'))
D['sess']=dict(n=len(s),med=round(s.sec.median()/60),p90=round(s.sec.quantile(.9)/60))
sb=[0,5,15,30,60,120,240,1e9]; sl=['<5 min','5–15','15–30','30–60','1–2 h','2–4 h','4 h+']
D['sessbins']=list(zip(sl,pd.cut(s.sec/60,sb,right=False).value_counts(sort=False).tolist()))
L=s.sort_values('sec',ascending=False).head(3)
D['longsess']=[dict(s=str(r.start)[:16],e=str(r.end)[:16],h=round(r.sec/3600,1),n=int(r.n),a=df[df.sess==i].artist.value_counts().head(3).index.tolist()) for i,r in L.iterrows()]
op=df.groupby('sess').head(1); D['openers']=[[k[0],k[1],int(v)] for k,v in op.groupby(['track','artist']).size().sort_values(ascending=False).head(6).items()]
# streak/silence
present=pd.Series([d in set(df.date) for d in days],index=days); st=(present!=present.shift()).cumsum()
runs=pd.DataFrame({'on':present,'g':st}).groupby('g').agg(on=('on','first'),a=('on',lambda x:str(x.index.min())),b=('on',lambda x:str(x.index.max())),n=('on','size'))
D['streak']=runs[runs.on].sort_values('n').iloc[-1][['a','b','n']].tolist(); D['silence']=runs[~runs.on].sort_values('n').iloc[-1][['a','b','n']].tolist()
D['silent_days']=int((~present).sum()); D['days']=len(days)
dt=df.groupby('date').sec.sum(); D['bigday']=[str(dt.idxmax()),H(dt.max())]
# hebrew
m['heb']=m.track.fillna('').str.contains('[֐-׿]')|m.artist.fillna('').str.contains('[֐-׿]')
D['heb_share']=round(100*(m.sec*m.heb).sum()/m.sec.sum(),1)
heb_art=['Tuna','Yuval Dayan','Eviatar Banai','Tamir Bar','Hanan Ben Ari','Anna Zak','Noa Kirel','Omer Adam','Static & Ben El','Arik Einstein','Shlomo Artzi','Ravid Plotnik']
# by artist: hebrew if any hebrew track title
ha=m.groupby('artist').heb.mean(); hset=set(ha[ha>0.3].index)|set(a for a in heb_art if a in tot.index)
m['il']=m.artist.isin(hset)|m.heb
D['il_share']=round(100*(m.sec*m.il).sum()/m.sec.sum(),1)
D['il_top']=[[a,H(v)] for a,v in m[m.il].groupby('artist').sec.sum().sort_values(ascending=False).head(8).items()]
D['il_month']=[round(100*(g.sec*g.il).sum()/max(g.sec.sum(),1)) for _,g in m.groupby('mon').__iter__()] 
# practice room
pr=m[m.artist.fillna('').str.contains('Backing|Gamazda')]
D['practice']=dict(h=H(pr.sec.sum()),back=H(m[m.artist.fillna('').str.contains('Backing')].sec.sum()),gam=H(m[m.artist=='Gamazda'].sec.sum()),
  tracks=[[a,b,int(n)] for (a,b),n in m[m.artist.fillna('').str.contains('Backing')&(m.sec>=30)].groupby(['track','artist']).size().sort_values(ascending=False).head(4).items()])
# podcasts
D['pod']=dict(h=H(p.sec.sum()),eps=int(p.episode_name.nunique()),shows=int(p.episode_show_name.nunique()),
  year={str(y):H(g.sec.sum()) for y,g in p.groupby('yr')},
  top=[[k,int(v.episode_name.nunique()),H(v.sec.sum())] for k,v in sorted(p.groupby('episode_show_name'),key=lambda kv:-kv[1].sec.sum())[:7]],
  eps_top=[[a,b,H(v)] for (a,b),v in p.groupby(['episode_show_name','episode_name']).sec.sum().sort_values(ascending=False).head(5).items()])
D['monthly']=[[mo, H(m[m.mon==mo].sec.sum()), H(p[p.mon==mo].sec.sum())] for mo in months]
# dr dre
D['dre']=[H(m[(m.artist=='Dr. Dre')&(m.mon==mo)].sec.sum()) for mo in months]
D['dre_pod']=[H(p[p.episode_name.fillna('').str.contains('דרה')&(p.mon==mo)].sec.sum()) for mo in months]
# devices
D['dev']=[[mo]+[H(df[(df.mon==mo)&(df.platform==pl)].sec.sum()) for pl in ['android','ios','osx']] for mo in months]
D['ge']=[str(df[df.conn_country=='GE'].date.min()),str(df[df.conn_country=='GE'].date.max()),int((df.conn_country=='GE').sum()),df[df.conn_country=='GE'].artist.value_counts().head(3).index.tolist()]
# obsession days
od=m[m.sec>=30].groupby(['date','track','artist']).size().sort_values(ascending=False).head(6)
D['obs']=[[str(k[0]),k[1],k[2],int(v)] for k,v in od.items()]
# year cards
D['years']=[]
for y,g in m.groupby('yr'):
    pg=p[p.yr==y]; ta=g.groupby('artist').sec.sum().sort_values(ascending=False)
    tk=g[g.sec>=30].groupby(['track','artist']).size().sort_values(ascending=False)
    first=m.groupby('artist').ts.min(); new=[a for a in ta.index[:60] if first[a].year==y][:3] if y>2023 else []
    D['years'].append(dict(y=int(y),h=H(g.sec.sum()+pg.sec.sum()),art=ta.index[:5].tolist(),arth=[H(x) for x in ta.values[:5]],trk=[tk.index[0][0],tk.index[0][1],int(tk.iloc[0])],new=new,
      artists=int(g.artist.nunique()),from_=str(df[df.yr==y].date.min()),to=str(df[df.yr==y].date.max())))
D['tot']=dict(h=H(df.sec.sum()),mh=H(m.sec.sum()),ph=H(p.sec.sum()),plays=int((m.sec>=30).sum()),artists=int(m.artist.nunique()),tracks=int(m.spotify_track_uri.nunique()),attempts=len(m))
# dec 2 2024 skim
x=m[(m.ts>='2024-12-02 21:16')&(m.ts<'2024-12-02 21:28')]; D['skim']=dict(n=len(x),artists=x.artist.nunique())
D=json.loads(json.dumps(D,ensure_ascii=False,default=lambda o:o.item() if hasattr(o,'item') else str(o))); json.dump(D,open('output/dash2.json','w'),ensure_ascii=False)
print(len(json.dumps(D,ensure_ascii=False))//1024,'KB')
for k in ['skipbins','skipmed','skip10','loyal','refused','back','starts','shuffle','offline','wday','dayparts','sess','sessbins','longsess','openers','streak','silence','silent_days','bigday','heb_share','il_share','il_top','practice','pod','ge','obs','years','tot','skim']:
    print(k, json.dumps(D[k],ensure_ascii=False)[:600])
