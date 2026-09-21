"""3D 그래프(PNG)를 만듭니다: 월×연도 곡면, 월×원인 3D 막대.
실행: python analysis/03_make_3d_figures.py"""
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
import json, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.font_manager as fm
from matplotlib import cm, colors
fm.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams.update({'font.family':'Noto Sans CJK JP','axes.unicode_minus':False})
c=json.load(open(ROOT/'data'/'cube.json')); O=str(ROOT/'figures')+'/'
# cube.json → 월×연도 합계(ym), 원인×월 합계(cm)
d={'years':c['years'],'causes':c['causes'],
   'ym':[[sum(m) for m in y] for y in c['v']],
   'cm':[[sum(c['v'][yi][m][ci] for yi in range(len(c['years']))) for m in range(12)] for ci in range(len(c['causes']))]}
fire=colors.LinearSegmentedColormap.from_list('f',['#fdf3c4','#f9d27a','#f08a3c','#d2402a','#6e1414'])
# A
Z=np.array(d['ym']); yrs=np.array(d['years'])
fig=plt.figure(figsize=(12,8.5)); ax=fig.add_subplot(111,projection='3d')
xs,ys=np.meshgrid(np.arange(1,13),np.arange(len(yrs)))
ax.plot_surface(xs,ys,Z,cmap=fire,rstride=1,cstride=1,linewidth=0.3,edgecolor='#00000030',antialiased=True)
ax.contourf(xs,ys,Z,zdir='z',offset=0,cmap=fire,alpha=0.5)
z=Z.ravel()
ax.set_xticks(range(1,13)); ax.set_xticklabels([f'{m}월' for m in range(1,13)],fontsize=8)
ax.set_yticks(range(0,20,2)); ax.set_yticklabels(yrs[::2],fontsize=8)
ax.set_zlabel('발생건수',labelpad=12); ax.view_init(elev=30,azim=-60); ax.set_box_aspect((1.3,1.5,0.7))
ax.set_title('월 × 연도별 산불 발생건수 (3D)',fontsize=15,weight='bold',pad=0)
sm=cm.ScalarMappable(cmap=fire,norm=colors.Normalize(0,z.max())); fig.colorbar(sm,ax=ax,shrink=0.5,pad=0.08,label='건수')
fig.text(0.98,0.02,'출처: 산림청 「산불통계」 (KOSIS), 2006–2025',ha='right',fontsize=8,c='gray')
fig.savefig(O+'07_3d_month_year.png',dpi=150,bbox_inches='tight'); plt.close()
# B
C=np.array(d['cm']); cc=['#c0392b','#8f9a92','#e67e22','#d4ac0d','#8e44ad','#2c3e50','#16a085','#3498db']
fig=plt.figure(figsize=(12,8.5)); ax=fig.add_subplot(111,projection='3d')
n=len(d['causes'])
for ci in range(n):
  yp=n-1-ci; m=C[ci]>0; xm=np.arange(1,13)[m]
  ax.bar3d(xm-0.31,np.full(len(xm),yp)-0.31,0,0.62,0.62,C[ci][m],color=cc[ci],shade=True,edgecolor='none')
ax.set_xticks(range(1,13)); ax.set_xticklabels([f'{m}월' for m in range(1,13)],fontsize=8)
ax.set_yticks(range(n)); ax.set_yticklabels(d['causes'][::-1],fontsize=8)
ax.set_zlabel('발생건수 (20년 누적)'); ax.view_init(elev=26,azim=-58); ax.set_box_aspect((1.4,1.1,0.7))
ax.set_title('월 × 원인별 산불 발생건수 (3D)',fontsize=15,weight='bold',pad=0)
fig.text(0.98,0.02,'출처: 산림청 「산불통계」 (KOSIS), 2006–2025',ha='right',fontsize=8,c='gray')
fig.savefig(O+'08_3d_month_cause.png',dpi=150,bbox_inches='tight'); plt.close()
