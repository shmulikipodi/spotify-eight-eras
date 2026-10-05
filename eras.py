exec(open('trends.py').read().split("print('coverage")[0])
import numpy as np
gm=m.pivot_table(index='mon',columns='g',values='sec',aggfunc='sum').reindex(months).fillna(0)
valid=[mo for mo in months if gm.loc[mo].sum()>3600]
X=gm.loc[valid].div(gm.loc[valid].sum(1),axis=0).values
# artist vectors too
am=m.pivot_table(index='mon',columns='artist',values='sec',aggfunc='sum').reindex(valid).fillna(0)
A=np.sqrt(am.div(am.sum(1),axis=0).values)
F=np.hstack([X*1.0, A*0.7])
n=len(valid)
def cost(i,j):
    s=F[i:j]; return ((s-s.mean(0))**2).sum()
C=[[cost(i,j) if j>i else 0 for j in range(n+1)] for i in range(n+1)]
best={}
for k in range(1,11):
    dp=np.full((k+1,n+1),np.inf); bk=np.zeros((k+1,n+1),int); dp[0][0]=0
    for kk in range(1,k+1):
        for j in range(1,n+1):
            for i in range(kk-1,j):
                if j-i<2 and not (j==n or i==0): pass
                v=dp[kk-1][i]+C[i][j]
                if v<dp[kk][j]: dp[kk][j]=v; bk[kk][j]=i
    cuts=[]; j=n
    for kk in range(k,0,-1): i=bk[kk][j]; cuts.append((i,j)); j=i
    cuts=cuts[::-1]; best[k]=(dp[k][n],cuts)
    print(k, round(dp[k][n],2), [valid[a]+'→'+valid[b-1] for a,b in cuts])
