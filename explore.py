import pandas as pd, numpy as np, json, glob, re
SRC="spotify_raw/Spotify Extended Streaming History"
rows=[]
for f in glob.glob(f"{SRC}/*.json"):
    for r in json.load(open(f)): r['file']='video' if 'Video' in f else 'audio'; rows.append(r)
df=pd.DataFrame(rows).drop_duplicates(['ts','spotify_track_uri','spotify_episode_uri','ms_played'])
df['ts']=pd.to_datetime(df.ts).dt.tz_convert('Asia/Jerusalem'); df=df.sort_values('ts').reset_index(drop=True)
df['sec']=df.ms_played/1000
m=df[df.spotify_track_uri.notna()].copy()
print(df.reason_start.value_counts(normalize=True).round(3).head(10))
print(df.reason_end.value_counts(normalize=True).round(3).head(10))
print('offline',df.offline.mean(),'incog',df.incognito_mode.mean())
print(df.groupby(df.ts.dt.year).shuffle.mean())
print('pick vs auto by year'); print(m.groupby(m.ts.dt.year).reason_start.value_counts(normalize=True).unstack().round(2)[['clickrow','trackdone','fwdbtn','backbtn','playbtn','appload','remote']] if 'remote' in m.reason_start.values else '')
heb=m.master_metadata_track_name.fillna('').str.contains('[֐-׿]')|m.master_metadata_album_artist_name.fillna('').str.contains('[֐-׿]')
m['heb']=heb
print('hebrew share time by year', m.groupby(m.ts.dt.year).apply(lambda g:(g.sec*g.heb).sum()/g.sec.sum()).round(3))
print('heb artists', m[m.heb].groupby('master_metadata_album_artist_name').sec.sum().sort_values().tail(10)/3600)
# skip timing
sk=m[m.reason_end=='fwdbtn'].sec
print('skip sec quantiles',sk.quantile([.1,.25,.5,.75,.9]).round(1).tolist(), (sk<10).mean())
# sessions
gap=df.ts.diff().dt.total_seconds() - df.sec.shift().fillna(0)
df['sess']=(gap>30*60).cumsum()
s=df.groupby('sess').agg(start=('ts','min'),end=('ts','max'),n=('sec','size'),sec=('sec','sum'))
print('sessions',len(s),'median min',s.sec.median()/60, 'longest', s.sort_values('sec').tail(3))
# daily
daily=df.groupby(df.ts.dt.date).sec.sum()
allday=pd.date_range(daily.index.min(),daily.index.max()).date
print('days total',len(allday),'days listened',len(daily))
z=pd.Series(1,index=allday).drop(daily.index,errors='ignore'); print('silent days',len(z))
# longest silence + streak
d=pd.Series(daily.index); dd=pd.to_datetime(d).diff().dt.days; print('longest gap', dd.max(), d[dd.idxmax()])
present=pd.Series([x in set(daily.index) for x in allday],index=allday)
st=(present!=present.shift()).cumsum(); runs=present.groupby(st).agg(['first','size']); print(runs[runs['first']].sort_values('size').tail(2))
# artist trajectories by quarter
m['q']=m.ts.dt.to_period('Q').astype(str)
top=m.groupby('master_metadata_album_artist_name').sec.sum().sort_values().tail(12).index
print((m[m.master_metadata_album_artist_name.isin(top)].pivot_table(index='master_metadata_album_artist_name',columns='q',values='sec',aggfunc='sum').fillna(0)/3600).round(1).to_string())
print('=== DEC 2 2024')
x=m[m.ts.dt.date==pd.Timestamp('2024-12-02').date()]; print(x[['ts','master_metadata_track_name','master_metadata_album_artist_name','reason_start','shuffle','sec']].head(25).to_string())
print('=== discovery: new artists per quarter with >=1h total ever')
fa=m.groupby('master_metadata_album_artist_name').agg(first=('ts','min'),h=('sec','sum')); fa['h']/=3600
print(fa[fa.h>=1].groupby(fa['first'].dt.to_period('Q')).size())
# completion: est duration = max sec where reason_end trackdone
dur=m[m.reason_end=='trackdone'].groupby('spotify_track_uri').sec.max()
m['dur']=m.spotify_track_uri.map(dur)
g=m.groupby(['master_metadata_track_name','master_metadata_album_artist_name']).agg(n=('sec','size'),done=('reason_end',lambda s:(s=='trackdone').mean()),instant=('sec',lambda s:(s<10).mean()),back=('reason_start',lambda s:(s=='backbtn').sum()))
print('=== loyal (n>=25)'); print(g[g.n>=25].sort_values('done').tail(10))
print('=== refused (n>=25)'); print(g[g.n>=25].sort_values('instant').tail(10))
print('=== went back for'); print(g.sort_values('back').tail(10))
m['h']=m.ts.dt.hour
for lab,(a,b) in {'morning 5-11':(5,11),'afternoon 12-17':(12,17),'evening 18-22':(18,22),'late night 23-4':(23,4)}.items():
    sel=m[(m.h>=a)&(m.h<=b)] if a<b else m[(m.h>=a)|(m.h<=b)]
    share=sel.groupby('master_metadata_album_artist_name').sec.sum()/m.groupby('master_metadata_album_artist_name').sec.sum()
    tot=m.groupby('master_metadata_album_artist_name').sec.sum()
    print(lab, round(sel.sec.sum()/m.sec.sum(),2), share[tot>4*3600].sort_values().tail(4).round(2).to_dict())
print('=== offline by month'); print(df[df.offline.fillna(False).astype(bool)].groupby(df.ts.dt.to_period('M')).sec.sum().sort_values().tail(5)/3600)
print('=== silences >=7 days'); dd2=pd.to_datetime(pd.Series(daily.index)); g2=dd2.diff().dt.days; print(pd.DataFrame({'end':dd2,'gap':g2})[g2>=7])
for dday in ['2023-09-25','2024-10-12','2025-10-02','2023-09-16','2024-10-03','2025-09-23','2026-09-21','2026-09-12']:
    print(dday, round(daily.get(pd.Timestamp(dday).date(),0)/60))
p=df[df.spotify_episode_uri.notna()]
print('=== podcast eps', p.episode_name.nunique()); print(p.groupby(p.ts.dt.year).episode_show_name.nunique())
print(p.groupby('episode_show_name').agg(eps=('episode_name','nunique'),h=('sec','sum')).sort_values('h').tail(8).assign(h=lambda d:d.h/3600))
print(p.groupby(['episode_show_name','episode_name']).sec.sum().sort_values().tail(6)/3600)
print('video music share',(m.file=='video').mean(), 'platform osx dates', df[df.platform=='osx'].ts.dt.date.unique()[:10])
print('session openers'); so=df.groupby('sess').head(1); print(so.master_metadata_track_name.value_counts().head(6))
print('weekday share', df.groupby(df.ts.dt.dayofweek).sec.sum().div(df.sec.sum()).round(3).tolist())
print('season top', m.groupby([m.ts.dt.month.isin([6,7,8]).map({True:'summer',False:'other'}),'master_metadata_track_name']).sec.sum().loc['summer'].sort_values().tail(5)/3600)
