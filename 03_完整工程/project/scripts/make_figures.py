"""Figures derived exclusively from saved simulation outputs."""
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.sans-serif':['Arial'],'axes.unicode_minus':False,'font.size':10,'pdf.fonttype':42,'mathtext.fontset':'custom','mathtext.rm':'Arial','mathtext.it':'Arial:italic','mathtext.bf':'Arial:bold','mathtext.default':'regular','axes.spines.top':False,'axes.spines.right':False,'legend.frameon':False})
ORDER=['baseline','capacity','stagger','combined','adaptive']
LABEL={'baseline':'Baseline','capacity':'Capacity','stagger':'Stagger','combined':'Combined','adaptive':'Adaptive'}
COL={'baseline':'#333333','capacity':'#E64B35','stagger':'#4DBBD5','combined':'#00A087','adaptive':'#3C5488'}
def save(fig,name):
    fig.tight_layout()
    for ext in ['png','pdf','svg']:fig.savefig(ROOT/'figures'/f'{name}.{ext}',dpi=300,bbox_inches='tight')
    plt.close(fig)
def read(s,k,seed=4711):return pd.read_csv(ROOT/'analysis'/f'{s}_s{seed}_{k}.csv.gz')
def main():
    summary=pd.read_csv(ROOT/'analysis/summary_by_run.csv');summary=summary[summary.scenario.isin(ORDER)]
    net=E.parse(ROOT/'data/raw/network.xml').getroot(); nodes={n.get('id'):(float(n.get('x'))/1000,float(n.get('y'))/1000) for n in net.findall('./nodes/node')}
    fig,ax=plt.subplots(figsize=(7,4.2))
    for l in net.findall('./links/link'):
        x,y=nodes[l.get('from')];xx,yy=nodes[l.get('to')];lid=int(l.get('id'));c=COL['capacity'] if 11<=lid<=19 else '#82929d'
        ax.annotate('',xy=(xx,yy),xytext=(x,y),arrowprops={'arrowstyle':'->','color':c,'lw':1.5})
        ax.text(x*.45+xx*.55,y*.45+yy*.55,str(lid),color=c,fontsize=8,bbox=dict(facecolor='white',edgecolor='none',pad=.5))
    for n,(x,y) in nodes.items():ax.scatter(x,y,s=15,c='#182e40');ax.annotate(n,(x,y),xytext=(3,3),textcoords='offset points',fontsize=8)
    ax.set(xlabel='Synthetic x coordinate (km)',ylabel='Synthetic y coordinate (km)',xlim=(-22,7),ylim=(-12,8));ax.set_aspect('equal')
    save(fig,'01_network')
    fig,axs=plt.subplots(1,2,figsize=(7,3.5))
    for ax,var,yl in zip(axs,['am_mean_min','mean_score'],['Mean morning travel time (min)','Mean executed plan score (utils)']):
        for i,s in enumerate(ORDER):
            vals=summary.loc[summary.scenario==s,var].values
            ax.scatter(i+np.linspace(-.08,.08,len(vals)),vals,color=COL[s],s=28,zorder=3)
            ax.plot([i-.2,i+.2],[vals.mean()]*2,c=COL[s],lw=2)
        ax.set_xticks(range(5),[LABEL[x] for x in ORDER],rotation=35,ha='right');ax.set_ylabel(yl);ax.grid(axis='y',alpha=.2)
    save(fig,'02_outcomes')
    fig,ax=plt.subplots(figsize=(7,3.6))
    for s in ORDER:
        t=read(s,'trips');x=np.sort(t.loc[t.trip_number==1,'travel_s']/60)
        ax.plot(x,np.arange(1,len(x)+1)/len(x),c=COL[s],label=LABEL[s])
    ax.set(xlabel='Morning travel time (min)',ylabel='Cumulative share of agents',ylim=(0,1));ax.yaxis.set_major_formatter(ticker.PercentFormatter(1));ax.legend();save(fig,'03_trip_distribution')
    fig,axs=plt.subplots(2,1,figsize=(7,5),sharex=True)
    for j,width in enumerate([900,300]):
        for s in ['baseline','stagger','adaptive']:
            t=read(s,'trips');am=t.loc[t.trip_number==1,'departure_s'];bins=np.arange(3*3600,10*3600+width,width);n,b=np.histogram(am,bins)
            axs[j].step(b[:-1]/3600,n,where='post',c=COL[s],label=LABEL[s])
        axs[j].set_ylabel(f'Departures / {width//60} min');axs[j].set_xlim(4.5,9);axs[j].grid(axis='y',alpha=.2)
    axs[0].legend();axs[1].set_xlabel('Departure time (hour of day)');save(fig,'04_departures')
    fig,axs=plt.subplots(2,1,figsize=(7,5.2))
    for s in ORDER:
        history=[read(s,'score_history',seed) for seed in [4711,42,2025]]
        arr=np.array([x['avg. EXECUTED'] for x in history]);it=history[0]['ITERATION']
        for ax in axs:ax.plot(it,arr.mean(axis=0),c=COL[s],label=LABEL[s]);ax.fill_between(it,arr.min(axis=0),arr.max(axis=0),color=COL[s],alpha=.12)
    axs[0].set(xlabel='Iteration',ylabel='Executed score (utils)',xlim=(0,100));axs[0].legend(ncol=3,fontsize=9)
    axs[1].set(xlabel='Iteration',ylabel='Executed score (utils)',xlim=(60,100));axs[1].set_ylim(summary.mean_score.min()-.2,summary.mean_score.max()+.2)
    save(fig,'05_learning')
    fig,axs=plt.subplots(1,2,figsize=(7,3.4))
    for s in ORDER:
        t=read(s,'traversals');t=t[t.link.between(11,19)];g=t.groupby('link').size().reindex(range(11,20),fill_value=0)
        axs[0].plot(g.index,g.values/2000*100,marker='o',ms=3,c=COL[s],label=LABEL[s])
        delay=t.assign(delay=(t.travel_s-5000/27.78).clip(lower=0)/60).groupby('link').delay.mean().reindex(range(11,20))
        axs[1].plot(delay.index,delay.values,marker='o',ms=3,c=COL[s])
    axs[0].set(xlabel='Corridor link ID',ylabel='Morning route share (%)');axs[0].legend(fontsize=8)
    axs[1].set(xlabel='Corridor link ID',ylabel='Mean link delay (min)');save(fig,'06_routes_links')
    fig,axs=plt.subplots(2,2,figsize=(7,5.3),sharex=True)
    for s in ['baseline','capacity','stagger','combined']:
        x=read(s,'links');x=x[(x.bin_seconds==300)&x.link.between(11,19)];g=x.groupby('bin_start_s')
        axs[0,0].plot(g.exit_flow_vph.sum().index/3600,g.exit_flow_vph.sum().values,c=COL[s],label=LABEL[s])
        axs[0,1].plot(g.mean_occupancy.sum().index/3600,g.mean_occupancy.sum().values,c=COL[s])
        l=x[x.link==12];axs[1,0].plot(l.bin_start_s/3600,l.mean_travel_s/60,c=COL[s]);axs[1,1].plot(l.bin_start_s/3600,l.density_veh_km_lane,c=COL[s])
    labs=['Corridor exit flow (veh h$^{-1}$)','Corridor mean occupancy (veh)','Link 12 travel time (min)','Link 12 density (veh km$^{-1}$ lane$^{-1}$)']
    for ax,lab in zip(axs.flat,labs):ax.set(xlim=(5.3,7.2),ylabel=lab);ax.grid(axis='y',alpha=.2)
    axs[0,0].legend(fontsize=8);axs[1,0].set_xlabel('Hour of day');axs[1,1].set_xlabel('Hour of day');save(fig,'07_link_dynamics')
    fig,axs=plt.subplots(1,2,figsize=(7,3.5),sharey=True)
    for ax,s in zip(axs,['baseline','combined']):
        x=read(s,'links');x=x[(x.bin_seconds==300)&x.link.between(11,19)&x.bin_start_s.between(19800,25200)]
        p=x.pivot(index='link',columns='bin_start_s',values='mean_delay_s')/60
        im=ax.imshow(p.values,aspect='auto',origin='lower',extent=(p.columns.min()/3600,(p.columns.max()+300)/3600,10.5,19.5),vmin=0,vmax=12,cmap='YlOrRd')
        ax.set(xlabel=f'{LABEL[s]}: hour of day',yticks=range(11,20));ax.grid(False)
    axs[0].set_ylabel('Corridor link ID');fig.colorbar(im,ax=axs.ravel().tolist(),label='Mean delay (min)',fraction=.03,pad=.04)
    # Manual spacing because the shared colourbar is outside subplot geometry.
    fig.subplots_adjust(left=.08,right=.86,bottom=.18,wspace=.13)
    for ext in ['png','pdf','svg']:fig.savefig(ROOT/'figures'/f'08_link_heatmap.{ext}',dpi=300,bbox_inches='tight')
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,3.5))
    base=read('baseline','trips').query('trip_number==1')[['person','travel_s']]
    for i,s in enumerate(ORDER[1:]):
        t=read(s,'trips').query('trip_number==1')[['person','travel_s']].merge(base,on='person',suffixes=('_s','_b'))
        delta=(t.travel_s_b-t.travel_s_s)/60
        parts=ax.violinplot(delta,positions=[i],showmedians=True,showextrema=False);parts['bodies'][0].set_facecolor(COL[s]);parts['bodies'][0].set_alpha(.6)
        ax.scatter([i]*3,np.quantile(delta,[.05,.5,.95]),s=18,c=COL[s],zorder=3)
    ax.axhline(0,c='#333333',lw=.8);ax.set_xticks(range(4),[LABEL[x] for x in ORDER[1:]]);ax.set_ylabel('Morning time saved per agent (min)');save(fig,'09_individual_changes')
if __name__=='__main__':main()
