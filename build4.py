import contextlib,io
with contextlib.redirect_stdout(io.StringIO()): exec(open('build3.py').read())
m['wk']=(m.ts.dt.tz_localize(None).dt.normalize()-pd.to_timedelta(m.ts.dt.dayofweek,unit='D'))
ERAS=[(e['a'],e['b']) for e in R['eras']]
mon_n=lambda a,b:len(pd.period_range(a,b,freq='M'))
def rate(a,b):
    e=m[(m.mon>=a)&(m.mon<=b)]; return e.groupby('artist').sec.sum()/3600/mon_n(a,b)
dd=m.groupby(['artist','date']).sec.sum().reset_index(); dd=dd[dd.sec>=900]
daytop=m.groupby(['artist','date','track']).sec.sum().reset_index().sort_values('sec').groupby(['artist','date']).tail(1).set_index(['artist','date']).track
R['trans']=[]
for k in range(7):
    (a0,b0),(a1,b1)=ERAS[k],ERAS[k+1]
    al=pd.concat([rate(a0,b0),rate(a1,b1)],axis=1).fillna(0); al.columns=['o','n']
    gain=(al.n-al.o).sort_values(ascending=False).index[:6]; loss=(al.o-al.n).sort_values(ascending=False).index[:6]
    bridge=al.min(axis=1).sort_values(ascending=False).index[:5]
    start=pd.Timestamp(a1+'-01')-pd.DateOffset(months=4)
    firsts=[]
    for x in gain:
        s=dd[(dd.artist==x)&(pd.to_datetime(dd.date)>=start)].sort_values('date')
        if len(s): d0=s.date.iloc[0]; firsts.append([str(d0),x,daytop.get((x,d0),''),round(s.sec.iloc[0]/60)])
    firsts.sort()
    b=pd.Timestamp(a1+'-01'); lo=pd.Timestamp(b0+'-01')+pd.offsets.MonthEnd(0)-pd.Timedelta(days=70); hi=b+pd.Timedelta(days=70)
    lo=lo-pd.to_timedelta(lo.dayofweek,unit='D'); weeks=pd.date_range(lo,hi,freq='W-MON')
    w=m[(m.wk>=lo)&(m.wk<=hi)].pivot_table(index='wk',columns='g',values='sec',aggfunc='sum').reindex(index=weeks,columns=G).fillna(0)/3600
    R['trans'].append(dict(frm=k,to=k+1,boundary=a1,weeks=[str(x.date()) for x in weeks],wg=w.round(2).values.tolist(),
        inn=[[x,round(al.o[x],2),round(al.n[x],2)] for x in gain],out=[[x,round(al.o[x],2),round(al.n[x],2)] for x in loss],
        stay=[[x,round(al.o[x],2),round(al.n[x],2)] for x in bridge],firsts=firsts))
# afterlife
R['after']=[]
for i,e in enumerate(R['eras']):
    s=[x[0] for x in e['sig']]
    f=lambda q:round(m[q&m.artist.isin(s)].sec.sum()/3600,1)
    R['after'].append(dict(art=s,bef=f(m.mon<e['a']),inn=f((m.mon>=e['a'])&(m.mon<=e['b'])),aft=f(m.mon>e['b']),
        months_after=len([mo for mo in months if mo>e['b'] and m[(m.mon==mo)].sec.sum()>3600])))
json.dump(json.loads(json.dumps(R,ensure_ascii=False,default=lambda o:o.item() if hasattr(o,'item') else str(o))),open('output/dash4.json','w'),ensure_ascii=False)
for t in R['trans']: print(t['frm']+1,'->',t['to']+1, t['weeks'][0],t['weeks'][-1],len(t['weeks']), t['firsts'])
print(R['after'])
