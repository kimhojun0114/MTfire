"""분석 그래프(PNG)를 만듭니다. 결과는 figures/ 폴더에 저장됩니다.
실행: python analysis/02_make_figures.py  (먼저 01_prepare_data.py 실행)
한글 글꼴(Noto Sans CJK)이 필요합니다. 없으면 FONT 경로를 바꿔 주세요."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
FONT="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.font_manager as fm
fm.fontManager.addfont(FONT)
plt.rcParams.update({'font.family':'Noto Sans CJK JP','axes.unicode_minus':False,'figure.dpi':150,
 'axes.spines.top':False,'axes.spines.right':False})
L=pd.read_csv(ROOT/'data'/'fire_long.csv'); O=str(ROOT/'figures')+'/'
order=L.groupby('원인').건수.sum().sort_values(ascending=False).index.tolist()
cols=dict(zip(order,['#c0392b','#95a5a6','#e67e22','#f1c40f','#8e44ad','#2c3e50','#16a085','#3498db']))
src='출처: 산림청 「산불통계」 (KOSIS), 2006–2025'

# 1 연도별 원인별 누적
Y=L.pivot_table(index='연도',columns='원인',values='건수',aggfunc='sum').fillna(0)[order]
fig,ax=plt.subplots(figsize=(12,6)); b=np.zeros(len(Y))
for c in order: ax.bar(Y.index,Y[c],bottom=b,color=cols[c],label=c); b+=Y[c].values
for x,t in zip(Y.index,b): ax.text(x,t+8,int(t),ha='center',fontsize=8)
ax.axhline(b.mean(),ls='--',c='k',lw=1); ax.text(2005.35,b.mean()+8,f'20년 평균 {b.mean():.0f}건',fontsize=9)
ax.set_title('연도별 산불 발생건수 (원인별 누적)',fontsize=15,weight='bold'); ax.set_ylabel('건수')
ax.set_xticks(Y.index); ax.legend(ncol=4,frameon=False,loc='upper left'); fig.text(0.99,0.01,src,ha='right',fontsize=8,c='gray')
fig.tight_layout(); fig.savefig(O+'01_yearly_by_cause.png'); plt.close()

# 2 월별 분포
M=L.groupby('월').건수.sum(); pct=M/M.sum()*100
fig,ax=plt.subplots(figsize=(11,5.5))
c=['#c0392b' if m in (2,3,4) else '#bdc3c7' for m in M.index]
ax.bar([f'{m}월' for m in M.index],M.values,color=c)
for i,(v,p) in enumerate(zip(M.values,pct.values)): ax.text(i,v+30,f'{p:.1f}%',ha='center',fontsize=9)
ax.set_title(f'월별 산불 발생건수 (20년 합계) — 2~4월에 {pct[[2,3,4]].sum():.1f}% 집중',fontsize=15,weight='bold')
ax.set_ylabel('건수'); fig.text(0.99,0.01,src,ha='right',fontsize=8,c='gray')
fig.tight_layout(); fig.savefig(O+'02_monthly_distribution.png'); plt.close()

# 3 월x원인 히트맵 (원인별 행 정규화: 각 원인이 어느 달에 몰리는가)
P=L.pivot_table(index='원인',columns='월',values='건수',aggfunc='sum').fillna(0).loc[order]
Pn=P.div(P.sum(1),axis=0)*100
fig,ax=plt.subplots(figsize=(12,5.5)); im=ax.imshow(Pn,cmap='YlOrRd',aspect='auto')
ax.set_xticks(range(12),[f'{m}월' for m in range(1,13)]); ax.set_yticks(range(len(order)),[f'{o} ({int(P.loc[o].sum())})' for o in order])
for i in range(len(order)):
  for j in range(12): v=Pn.iat[i,j]; ax.text(j,i,f'{v:.0f}',ha='center',va='center',fontsize=8,c='white' if v>20 else 'black')
fig.colorbar(im,label='해당 원인 내 비율 (%)'); ax.set_title('원인별 월간 발생 비율 히트맵 (각 행 합 = 100%)',fontsize=15,weight='bold')
fig.text(0.99,0.01,src,ha='right',fontsize=8,c='gray'); fig.tight_layout(); fig.savefig(O+'03_cause_month_heatmap.png'); plt.close()

# 4 원인별 비중
T=L.groupby('원인').건수.sum()[order]
fig,ax=plt.subplots(figsize=(8,8))
w,_,at=ax.pie(T,labels=[f'{k}\n{v:,}건' for k,v in T.items()],colors=[cols[k] for k in order],autopct='%1.1f%%',
  pctdistance=0.8,startangle=90,counterclock=False,wedgeprops=dict(width=0.4,edgecolor='white'))
for a in at: a.set_fontsize(9)
ax.text(0,0,f'총 {T.sum():,}건',ha='center',va='center',fontsize=16,weight='bold')
ax.set_title('산불 원인별 비중 (2006–2025 누적)',fontsize=15,weight='bold'); fig.text(0.99,0.01,src,ha='right',fontsize=8,c='gray')
fig.tight_layout(); fig.savefig(O+'04_cause_share.png'); plt.close()

# 5 전기 vs 후기 비교
a=Y.loc[2006:2015].mean(); bb=Y.loc[2016:2025].mean(); ch=(bb-a)/a*100
fig,ax=plt.subplots(figsize=(11,6)); x=np.arange(len(order)); w=0.38
ax.bar(x-w/2,a,w,label='2006–2015 연평균',color='#95a5a6'); ax.bar(x+w/2,bb,w,label='2016–2025 연평균',color='#c0392b')
for i,c in enumerate(order):
  ax.text(i,max(a[c],bb[c])+4,f'{ch[c]:+.0f}%',ha='center',fontsize=10,weight='bold',c='#c0392b' if ch[c]>0 else '#2980b9')
ax.set_xticks(x,order); ax.set_ylabel('연평균 건수'); ax.legend(frameon=False)
ax.set_title('원인별 연평균 발생건수 변화: 전기(2006–15) vs 후기(2016–25)',fontsize=15,weight='bold')
fig.text(0.99,0.01,src,ha='right',fontsize=8,c='gray'); fig.tight_layout(); fig.savefig(O+'05_cause_change_periods.png'); plt.close()

# 6 연도x월 히트맵
YM=L.pivot_table(index='연도',columns='월',values='건수',aggfunc='sum')
fig,ax=plt.subplots(figsize=(11,8)); im=ax.imshow(YM,cmap='Reds',aspect='auto')
ax.set_xticks(range(12),[f'{m}월' for m in range(1,13)]); ax.set_yticks(range(len(YM)),YM.index)
for i in range(len(YM)):
  for j in range(12): v=YM.iat[i,j]; ax.text(j,i,int(v),ha='center',va='center',fontsize=7,c='white' if v>120 else 'black')
fig.colorbar(im,label='건수'); ax.set_title('연도 × 월 산불 발생건수',fontsize=15,weight='bold')
fig.text(0.99,0.01,src,ha='right',fontsize=8,c='gray'); fig.tight_layout(); fig.savefig(O+'06_year_month_heatmap.png'); plt.close()
print(ch.round(1).to_string()); print(a.round(1).to_string()); print(bb.round(1).to_string())
print(YM.idxmax(axis=1).value_counts())
