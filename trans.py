import contextlib,io
with contextlib.redirect_stdout(io.StringIO()): exec(open('build3.py').read())
import numpy as np
ERAS=[(e['a'],e['b']) for e in R['eras']]
m['wk']=(m.ts.dt.tz_localize(None).dt.normalize()-pd.to_timedelta(m.ts.dt.dayofweek,unit='D'))
mon_n=lambda a,b:len(pd.period_range(a,b,freq='M'))
def rate(a,b):  # hours per month per artist in era
    e=m[(m.mon>=a)&(m.mon<=b)]; return e.groupby('artist').sec.sum()/3600/mon_n(a,b)
for k in range(7):
    (a0,b0),(a1,b1)=ERAS[k],ERAS[k+1]
    r0,r1=rate(a0,b0),rate(a1,b1); al=pd.concat([r0,r1],axis=1).fillna(0); al.columns=['old','new']
    gain=(al.new-al.old).sort_values(ascending=False); loss=(al.old-al.new).sort_values(ascending=False)
    bridge=al.min(axis=1).sort_values(ascending=False)
    print(f'\n===== {k+1}->{k+2}: {b0} | {a1}')
    print(' IN ', [(x,round(al.old[x],2),round(al.new[x],2)) for x in gain.index[:7]])
    print(' OUT', [(x,round(al.old[x],2),round(al.new[x],2)) for x in loss.index[:7]])
    print(' STAY', [(x,round(bridge[x],2)) for x in bridge.index[:5]])
    # first serious day of incoming (>=15 min/day), searching from 4 months before boundary
    start=pd.Timestamp(a1+'-01')-pd.DateOffset(months=4)
    dd=m.groupby(['artist','date']).sec.sum().reset_index(); dd=dd[dd.sec>=900]
    for x in gain.index[:6]:
        s=dd[(dd.artist==x)&(pd.to_datetime(dd.date)>=start)].date
        print('   first serious', x, s.min() if len(s) else None)
    # weekly genre share window
    lo=pd.Timestamp(a1+'-01')-pd.Timedelta(days=63); hi=pd.Timestamp(a1+'-01')+pd.Timedelta(days=63)
    w=m[(m.wk>=lo)&(m.wk<=hi)].pivot_table(index='wk',columns='g',values='sec',aggfunc='sum').fillna(0)
    print((w.div(w.sum(1),axis=0)*100).round(0).astype(int).assign(h=(w.sum(1)/3600).round(1)).to_string())
