import pandas as pd, glob, json, os
SRC="/Users/msphh/data_con/spotify_raw/Spotify Extended Streaming History"
OUT="/Users/msphh/data_con/output"
rows=[]
for f in glob.glob(f"{SRC}/*.json"):
    for r in json.load(open(f)):
        r['file_type']='Video' if 'Video' in f else 'Audio'; rows.append(r)
df=pd.DataFrame(rows)
df=df.drop_duplicates(['ts','spotify_track_uri','spotify_episode_uri','ms_played'])
df['ts']=pd.to_datetime(df.ts).dt.tz_convert('Asia/Jerusalem')
df=df.sort_values('ts')
df['kind']=df.spotify_track_uri.notna().map({True:'Music',False:None})
df.loc[df.spotify_episode_uri.notna(),'kind']='Podcast'
df=df[df.kind.notna()].copy()
df['minutes']=df.ms_played/60000
df['title']=df.master_metadata_track_name.fillna(df.episode_name)
df['artist']=df.master_metadata_album_artist_name.fillna(df.episode_show_name)
df['album']=df.master_metadata_album_album_name
df['date']=df.ts.dt.date; df['year']=df.ts.dt.year; df['month']=df.ts.dt.strftime('%Y-%m')
df['hour']=df.ts.dt.hour; df['weekday']=df.ts.dt.day_name()
df['counted']=df.ms_played>=30000   # Spotify counts a "stream" at 30s
m=df[df.kind=='Music']; p=df[df.kind=='Podcast']

def top(d,keys,n=None):
    g=d.groupby(keys).agg(minutes=('minutes','sum'),plays=('counted','sum'),
        attempts=('minutes','size'),skips=('skipped','sum'),first=('ts','min'),last=('ts','max')).reset_index()
    g['hours']=(g.minutes/60).round(1); g=g.sort_values('minutes',ascending=False)
    return g.head(n) if n else g

# ---------- Excel ----------
plays=df[['ts','kind','title','artist','album','minutes','platform','shuffle','skipped','reason_start','reason_end','offline','conn_country','file_type']].copy()
plays['ts']=plays.ts.dt.tz_localize(None); plays['minutes']=plays.minutes.round(2)
plays.columns=['Date & time (Israel)','Type','Track / Episode','Artist / Show','Album','Minutes played','Device','Shuffle','Skipped','How it started','How it ended','Offline','Country','Source file']
def clean(g,cols,names):
    g=g.copy(); g['first']=g['first'].dt.date; g['last']=g['last'].dt.date
    g['skip %']=(100*g.skips/g.attempts).round(0)
    g=g[cols+['hours','plays','skip %','first','last']]; g.columns=names+['Hours','Plays (30s+)','Skip %','First played','Last played']; return g
artists=clean(top(m,'artist'),['artist'],['Artist'])
tracks=clean(top(m,['title','artist']),['title','artist'],['Track','Artist'])
albums=clean(top(m,['album','artist']),['album','artist'],['Album','Artist'])
shows=clean(top(p,'artist'),['artist'],['Podcast'])
monthly=df.pivot_table(index='month',columns='kind',values='minutes',aggfunc='sum').fillna(0).div(60).round(1).reset_index()
monthly.columns.name=None; monthly=monthly.rename(columns={'month':'Month','Music':'Music hours','Podcast':'Podcast hours'})
yr=[]
for y,g in m.groupby('year'):
    t=top(g,'artist',10).reset_index(drop=True); tt=top(g,['title','artist'],10).reset_index(drop=True)
    for i in range(10):
        yr.append({'Year':y,'Rank':i+1,'Artist':t.artist[i] if i<len(t) else '','Artist hours':t.hours[i] if i<len(t) else '',
                   'Track':tt.title[i] if i<len(tt) else '','Track by':tt.artist[i] if i<len(tt) else '','Track plays':tt.plays[i] if i<len(tt) else ''})
summary=pd.DataFrame([
 ('First record',str(df.ts.min().date())),('Last record',str(df.ts.max().date())),
 ('Total hours',round(df.minutes.sum()/60,1)),('Music hours',round(m.minutes.sum()/60,1)),('Podcast hours',round(p.minutes.sum()/60,1)),
 ('Music plays (30s+)',int(m.counted.sum())),('Different artists',m.artist.nunique()),('Different tracks',m.spotify_track_uri.nunique()),
 ('Skip rate (music)',f"{100*m.skipped.mean():.0f}%"),('Shuffle on (music)',f"{100*m.shuffle.mean():.0f}%")],columns=['Stat','Value'])
with pd.ExcelWriter(f"{OUT}/Spotify_History_Organized.xlsx",engine='openpyxl') as w:
    for name,d in [('Summary',summary),('Top Artists',artists),('Top Tracks',tracks),('Top Albums',albums),('Podcasts',shows),('Top 10 by Year',pd.DataFrame(yr)),('Monthly',monthly),('All Plays',plays)]:
        d.to_excel(w,sheet_name=name,index=False)
        ws=w.sheets[name]; ws.freeze_panes='A2'; ws.auto_filter.ref=ws.dimensions
        for col in ws.columns:
            L=max(len(str(c.value)) if c.value is not None else 0 for c in col[:300]); ws.column_dimensions[col[0].column_letter].width=min(max(10,L+2),45)
        for c in ws[1]: c.font=c.font.copy(bold=True)
plays.to_csv(f"{OUT}/all_plays_clean.csv",index=False)

# ---------- dashboard JSON ----------
def lst(g,keys): return [dict(n=r[keys[0]],a=(r[keys[1]] if len(keys)>1 else None),h=round(r.minutes/60,1),p=int(r.plays),s=round(100*r.skips/max(r.attempts,1)),f=str(r['first'].date())) for _,r in g.iterrows()]
D={'range':[str(df.ts.min().date()),str(df.ts.max().date())]}
D['years']={}
for y in ['all']+sorted(m.year.unique().tolist()):
    mm=m if y=='all' else m[m.year==y]; pp=p if y=='all' else p[p.year==y]; dd=df if y=='all' else df[df.year==y]
    hw=dd.groupby([dd.ts.dt.dayofweek,'hour']).minutes.sum()
    daily=dd.groupby('date').minutes.sum()
    D['years'][str(y)]=dict(
      music_h=round(mm.minutes.sum()/60),pod_h=round(pp.minutes.sum()/60),plays=int(mm.counted.sum()),
      artists=int(mm.artist.nunique()),tracks=int(mm.spotify_track_uri.nunique()),
      skip=round(100*mm.skipped.mean()),shuffle=round(100*mm.shuffle.mean()),
      days=int(daily.size),avg_day=round(daily.mean()),
      top_day=[str(daily.idxmax()),round(daily.max()/60,1)],
      top_artists=lst(top(mm,'artist',25),['artist']),
      top_tracks=lst(top(mm,['title','artist'],25),['title','artist']),
      top_albums=lst(top(mm,['album','artist'],15),['album','artist']),
      shows=lst(top(pp,'artist',10),['artist']),
      heat=[[round(hw.get((d,h),0)/60,1) for h in range(24)] for d in range(7)],
      platform={k:round(v/60) for k,v in dd.groupby('platform').minutes.sum().items() if v>60},
    )
mo=df.pivot_table(index='month',columns='kind',values='minutes',aggfunc='sum').fillna(0)
D['monthly']=[dict(m=i,music=round(r.Music/60,1),pod=round(r.Podcast/60,1)) for i,r in mo.iterrows()]
# repeat obsessions: most plays of one track in a single day
td=m[m.counted].groupby(['date','title','artist']).size().sort_values(ascending=False).head(8)
D['obsessions']=[dict(d=str(k[0]),t=k[1],a=k[2],n=int(v)) for k,v in td.items()]
# most-played artist per month
ma=m.groupby(['month','artist']).minutes.sum().reset_index().sort_values('minutes').groupby('month').tail(1).sort_values('month')
D['artist_of_month']=[dict(m=r.month,a=r.artist,h=round(r.minutes/60,1)) for _,r in ma.iterrows()]
json.dump(D,open(f"{OUT}/dash.json",'w'),ensure_ascii=False)
print(summary.to_string()); print(json.dumps(D['years']['all']['top_tracks'][:10],ensure_ascii=False)); print(D['obsessions'][:5]); print(D['years']['all']['platform'])
print({y:(v['music_h'],v['pod_h'],v['top_artists'][0]['n']) for y,v in D['years'].items()}); print(os.path.getsize(f"{OUT}/dash.json"))
