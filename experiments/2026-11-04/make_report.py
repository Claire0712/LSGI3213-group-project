from pathlib import Path
import pandas as pd,numpy as np,json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;D=R/'results';F=R/'figures';F.mkdir(exist_ok=True)
s=pd.read_csv(D/'all_runs.csv');g=s[s.kind=='grid'];p=pd.read_csv(D/'paired_effects.csv');h=pd.read_csv(D/'adaptive_score_histories.csv');c=pd.read_csv(D/'adaptive_checkpoints.csv');st=pd.read_csv(D/'adaptive_stability.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
colors=['#355c9a','#d88924','#238b73']
fig,ax=plt.subplots(figsize=(8,5))
for w,col in zip([0,30,60],colors):
 a=g[g.spread_minutes==w].groupby('capacity_factor').am_mean_min.agg(['mean','min','max']);ax.plot(a.index,a['mean'],'o-',color=col,label=f'{w}-minute departure window');ax.fill_between(a.index,a['min'],a['max'],color=col,alpha=.18)
ax.axhline(15,color='#555',ls='--',lw=1,label='Approximate free-flow floor');ax.set(xlabel='Corridor capacity multiplier',ylabel='Mean morning trip (minutes)',xticks=[1,1.5,2]);ax.legend(frameon=False);ax.set_title('Capacity benefit depends on departure concentration');fig.text(.12,.01,'Means of 3 paired seeds; bands show seed min-max, not confidence intervals.',fontsize=9);fig.tight_layout(rect=(0,.04,1,1));fig.savefig(F/'capacity_sensitivity.png',dpi=200);plt.close(fig)
fig,(a,b)=plt.subplots(1,2,figsize=(11,4.7))
for (seed,x),col in zip(h.groupby('seed'),colors):
 a.plot(x.iloc[:,0],x['avg. EXECUTED'],lw=1.4,label=str(seed),color=col);b.plot(x.iloc[:,0],x['avg. EXECUTED'],lw=1.4,color=col)
a.set(xlabel='Iteration',ylabel='Mean executed-plan score (utils)',title='Adaptive learning through 500 iterations');a.legend(title='Seed',frameon=False);b.set(xlabel='Iteration',ylabel='Score (utils)',title='Tail: iterations 350-500',xlim=(350,500));tail=h[h.iloc[:,0]>=350]['avg. EXECUTED'];b.set_ylim(tail.min()-.02,tail.max()+.02);fig.tight_layout();fig.savefig(F/'adaptive_convergence.png',dpi=200);plt.close(fig)
fig,(a,b)=plt.subplots(1,2,figsize=(11,4.7))
for factor,col in zip([1,1.5,2],colors):
 x=g[g.capacity_factor==factor].groupby('spread_minutes').agg(score=('mean_score','mean'),losers=('score_losers_pct','mean'))
 a.plot(x.index,x.score,'o-',label=f'{factor:g}x capacity',color=col);b.plot(x.index,x.losers,'o-',color=col)
a.set(xlabel='Departure window (minutes)',ylabel='Mean plan score (utils)',xticks=[0,30,60],title='Average utility');a.legend(frameon=False);b.set(xlabel='Departure window (minutes)',ylabel='Agents with lower score (%)',xticks=[0,30,60],title='Losses relative to simultaneous baseline');fig.tight_layout();fig.savefig(F/'utility_distribution.png',dpi=200);plt.close(fig)
agg=g.groupby(['capacity_factor','spread_minutes']).mean(numeric_only=True)
lines=['# 补充交通实验结果（独立分支）','', '日期：2026-11-04。此实验新增结果位于独立分支，未合并至 main。','', '## 实际运行与核验','', '- 3 档容量 × 3 档出发窗口 × 3 个配对随机种子，共 27 个网格实验记录。复用 12 个已核验原运行，新增 15 个运行；均采用迭代 0–100。','- 另外将自适应场景用三个种子分别从头运行到迭代 500，新增运行合计 18 次。','- 每次最终日均有 2,000 人、4,000 次完成出行，stuck 为 0。逐人逐次核对事件与原生出行表，并核对实际执行计划得分、正常结束日志及输入哈希。','- 运行使用 MATSim 12.0、Java 14.0.2、每个仿真单线程。复用原结果使用 Java 11；此前两个独立重跑的最终事件与原始结果完全一致。','', '## 1. 容量和出发窗口的相互影响','', '下表为三个种子的均值，单位为早晨平均行程分钟。出发窗口中心固定在 06:00。','', '| 容量 | 同时出发 | 分散 30 分钟 | 分散 60 分钟 |','|---|---:|---:|---:|']
for factor in [1,1.5,2]:lines.append(f'| {factor:g} 倍 | '+ ' | '.join(f'{agg.loc[(factor,w),"am_mean_min"]:.4f}' for w in [0,30,60])+' |')
lines+=['','![容量敏感性](figures/capacity_sensitivity.png)','','双倍容量相对同一出发窗口下的原容量，按种子配对比较：','','| 已有出发窗口 | 平均节省（秒） | 三种子范围（秒） | 平均节省比例 |','|---|---:|---:|---:|']
for w in [0,30,60]:
 x=p[(p.comparison=='capacity_vs_1x_same_spread')&(p.capacity_factor==2)&(p.spread_minutes==w)]
 lines.append(f'| {w} 分钟 | {x.minutes_saved.mean()*60:.3f} | {x.minutes_saved.min()*60:.3f}–{x.minutes_saved.max()*60:.3f} | {x.pct_saved.mean():.3f}% |')
lines += ['', f'在原容量下，30 分钟窗口的平均行程为 {agg.loc[(1,30),"am_mean_min"]:.4f} 分钟，60 分钟窗口为 {agg.loc[(1,60),"am_mean_min"]:.4f} 分钟，两者仅差 {(agg.loc[(1,30),"am_mean_min"]-agg.loc[(1,60),"am_mean_min"])*60:.3f} 秒；30 分钟窗口的平均日计划得分高出 {agg.loc[(1,30),"mean_score"]-agg.loc[(1,60),"mean_score"]:.5f} utils。这只支持本次受测组合中的比较，不能宣称 30 分钟是全局最优窗口。']
lines+=['','这些结果说明，扩容收益取决于原来是否存在明显拥堵。不能把“同时出发”基准下的收益百分比套用于已经分散出发的交通。分散基准是敏感性假设，没有真实观测数据支持其现实代表性。','','## 2. 组合方案为何收益有限','','| 设置（原容量，除最后一行） | 平均行程（分钟） | 走廊完整遍历平均延误（秒） | 走廊峰值车辆数（种子均值） |','|---|---:|---:|---:|']
for factor,w in [(1,0),(1,30),(1,60),(2,60)]:
 x=agg.loc[(factor,w)];lines.append(f'| 容量 {factor:g} 倍 / 窗口 {w} 分钟 | {x.am_mean_min:.4f} | {x.corridor_mean_delay_min*60:.4f} | {x.corridor_peak_vehicles:.1f} |')
ff=g.am_route_freeflow_min.mean();lines += ['',f'原生输出的早晨行驶距离为 25,000 米，道路自由流速度为 27.78 米/秒，对应约 {ff:.4f} 分钟；离散仿真中的无拥堵出行约为 15 分钟。该距离采用 MATSim 原生出行距离，避免把活动端点整段道路重复计入。走廊延误仅使用 links 11–19 的完整 entered-link→left-link 遍历。接近自由流时间后，继续增加容量很难再缩短行程。','','## 3. 平均收益与个体得分','','![效用与个体差异](figures/utility_distribution.png)','','| 原容量下的窗口 | 平均日计划得分 | 相对同时出发基准的得分下降人数占比 |','|---|---:|---:|']
for w in [0,30,60]:
 x=agg.loc[(1,w)];lines.append(f'| {w} 分钟 | {x.mean_score:.5f} | {x.score_losers_pct:.2f}% |')
lines+=['','完整个体结果见 `results/individual_outcomes.csv.gz`；按 15 分钟出发时段划分的结果见 `results/departure_group_outcomes.csv`。','工作设施 07:00 开放；preopening_gap_min 是到达至开放之间的时间差，不能解释成原生 wait_time，也不能据此断言得分损失完全由等待造成。得分同时受家庭活动时长、工作活动评分等因素影响。当前分组是描述性分析，不是因果机制拆分。','','## 4. 自适应场景是否已稳定','','![收敛过程](figures/adaptive_convergence.png)','','| 种子 | 100 次得分 | 200 次得分 | 500 次得分 | 最后两段 50 次均值之差 | ≤0.05 utils 筛查 |','|---|---:|---:|---:|---:|---|']
for seed in [4711,42,2025]:
 x=c[c.seed==seed].set_index('iteration');v=st[st.seed==seed].iloc[0];lines.append(f'| {seed} | {x.loc[100,"mean_score"]:.5f} | {x.loc[200,"mean_score"]:.5f} | {x.loc[500,"mean_score"]:.5f} | {v.mean_change:.5f} | {"通过" if v.passes_descriptive_005_screen else "未通过"} |')
lines+=['','阈值在新结果完成前设定：比较迭代 451–500 与 401–450 的平均执行得分，绝对差不超过 0.05 utils。它只是明确标注的描述性稳定性检查，不是正式均衡检验。完整尾部范围、斜率及 100/200/300/400/500 次的出发时间与行程指标均保存在 CSV 中。',f'本次通过该筛查的种子为 {int(st.passes_descriptive_005_screen.sum())}/3；应结合完整曲线解释，不能只因跑到 500 就宣称达到严格均衡。','新长运行的前 101 次得分与对应原始自适应运行一致（绝对容差 1e-9），支持此次延长没有改变前期轨迹。','','## 5. 如何复现','','需要原工程的 `project` 文件夹及 Java；Python 需要 numpy、pandas、matplotlib。源工程路径应含 runtime、scenarios 和 runs。','','```bash','python run_extension.py --source /path/to/project --workers 3','python validate_design.py --source /path/to/project','python analyze_extension.py --source /path/to/project','python make_report.py','```','','`run_extension.py` 拒绝覆盖已有但未核验的运行。重跑前请将本补充包中的 runs 文件夹改名归档；原工程无需改动。脚本会在本补充目录中生成输入与输出。发布包保存脚本、输入、结果、图表和精简原生证据；运行引擎使用原工程提供的 runtime。为减少体积，精简证据保留最终事件/出行/计划/得分及自适应检查点出行表，未收录每次迭代的全部重复文件。复用运行的原始事件仍在原工程内。','','## 6. 实验边界','','- 三个种子用于观察算法随机性；范围不是现实人口的置信区间，也没有进行显著性宣称。','- 人口需求保持 2,000 人，未测试需求增长、方式选择、真实路网、扩容成本或实施可行性。','- 出发窗口按原有个人顺序分配，没有增加随机分配时段的实验；个体得失也受该分配方式影响。','- 容量变化不改变车道数或道路存储空间；结果不能直接当作真实道路拓宽评估。','- 本次已检查网络容量和时间窗口交互，但没有对评分参数或设施开放时间做因果分解。','- 技术结果可复现并不自动证明实验假设适合某个真实城市。','']
(R/'README.md').write_text('\n'.join(lines))
print('Wrote report and 3 figures')
