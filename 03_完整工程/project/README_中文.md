# LSGI3213 MATSim project

本项目按照提供的 Group Project PDF 完成了公开数据获取、实际 MATSim 仿真、三类必需结果分析、英文报告及 15 分钟汇报材料。

## 先看这些文件

- `deliverables/LSGI3213_Equil_Report.pdf`：英文报告，17 页，其中正文 16 页、参考文献 1 页；正文 12 pt，单倍行距排版。
- `deliverables/LSGI3213_Equil_Slides.pdf`：15 页汇报 PDF。
- `deliverables/LSGI3213_Equil_Slides.pptx`：可编辑 PowerPoint，6 个原生图表、2 个原生表格，图表附数据工作簿，包含演讲备注。
- `deliverables/Presentation_Script_and_QA.md`：逐页英文讲稿、精确到秒的 15 分钟时间安排、中文答辩提示。
- `analysis/summary_by_run.csv`：主要实验逐运行汇总，适合检查数值。

没有提供 Group ID 和组长姓名，因此没有编造身份信息。确定后可按题目规范生成副本：

```bash
python3 scripts/rename_submission.py --group '你的组号' --leader '组长英文姓名'
```

该命令只复制 PDF/PPTX 并规范命名，不会声称完成 Blackboard 提交。题目中的组员贡献表是可选项，未编造任何人的贡献。旧日期不影响本次技术实验。

## 数据来自哪里

官方 MATSim 12.0 equil 示例：
https://github.com/matsim-org/matsim-libs/tree/matsim-12.0/examples/scenarios/equil

下载了 network.xml、facilities.xml、config.xml、plans100.xml、plans2000.xml.gz。五个文件均与本地教程附带版本逐字节相同。`data/source_manifest.json` 记录 URL、下载时间、GitHub blob SHA 和 SHA-256；`data/local_comparison.json` 记录与本地教程的比对。

这是官方**合成示例数据**，不是香港实际交通观测。没有访问 Blackboard 私有 project ZIP，因此不声称核对过该私有包。原始 100 人计划和 2,000 人计划结构不同，报告明确区分了原始示例复现和实验基准。

`data/MATSim_user_guide.pdf` 是联网下载的官方用户指南；`data/assignment_brief.pdf` 是提供的题目副本。报告、幻灯片如实披露 AI 辅助范围。

## 做了哪些实际运行

主要实验使用官方 2,000 人需求，每人两次 car 出行：

| 场景 | 改动 | 平均早晨行程，三种子均值 |
|---|---|---:|
| Baseline | 06:00 集中出发，原始网络 | 22.05 min |
| Capacity | links 11-19 的 capacity 从 1,000 加到 2,000 veh/h | 18.60 min |
| Stagger | 首次出发均匀分布于 05:30-06:30 | 15.00 min |
| Combined | 扩容 + 错峰 | 15.00 min |
| Adaptive | config 增加 0.1 权重的 TimeAllocationMutator | 15.01 min |

每个场景用 seeds 4711、42、2025，运行 iterations 0-100（含端点，即每组 101 次）。另外运行原始 100 人例子，以及 Baseline/Adaptive 各一个延长到 iteration 200 的检查：共 **18 次成功运行**。每个 2,000 人运行的最终日均完成 4,000 次出行，无 stuck；原始例子完成 201 次。

扩容平均节省约 15.7%，错峰约 32.0%。但错峰/组合下约 41.2-41.6% 的个体日计划得分下降，不能将平均时间收益解释为人人受益。自适应场景到 200 次仍有小幅得分改善，未声称已经达到严格均衡。

## 文件组织

- `data/raw/`：未改动的官方原始下载。
- `scenarios/`：可直接运行的 config、network、facilities、plans；主运行表 `run_matrix.json`。
- `runtime/`：MATSim 12.0 JAR、依赖 JAR 与原许可文件，取自教程。
- `runs/`：每次运行的原生输出目录、console log、status JSON。
- `analysis/`：出行、完整路段遍历、路段时段指标、个体得分和迭代得分；CSV.GZ 可由 pandas 直接读取。
- `figures/`：9 张分析图，保留 PNG（300 dpi）、PDF、SVG。
- `scripts/`：数据获取、场景构建、运行、分析、绘图、报告、幻灯片与校验源码。
- `docs/`：需求对应表和方法说明。
- `qa/`、`.build/`：本地检查中间文件，不是提交材料；压缩包不收录这些中间图像。

## 复现

在此 `project` 文件夹打开终端。已有结果无需重跑，即可阅读与分析。

实际运行环境：Mac arm64；Amazon Corretto Java 11.0.30；MATSim 12.0。MATSim JAR 的 Build-Jdk-Spec 是 11，虽然旧教程建议 Java 14，本机 Java 11 已成功运行。没有修改 shell profile 或系统 Java。

Python 分析/绘图使用 Python 3.11。安装依赖时建议创建独立环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/download_data.py
python scripts/test_events.py
python scripts/validate_project.py
```

通常先保留已运行的场景 XML。以下命令验证缓存输入哈希并复用已完成结果；输入或 JAR 改变时会报错，不会悄悄混用旧结果：

```bash
python scripts/run_scenarios.py
python scripts/analyze.py
python scripts/analyze_individual.py
python scripts/make_figures.py
python scripts/make_report.py
python scripts/prepare_slides.py
```

`run_scenarios.py` 默认使用 PATH 中的 java；可用 `MATSIM_JAVA=/完整路径/bin/java` 指定 Java 11。若需从头重新仿真，请先**归档**原结果（可逆），然后运行：

```bash
mv runs runs_archived
mkdir runs
python scripts/build_scenarios.py
python scripts/run_scenarios.py
python scripts/analyze.py
python scripts/extend_runs.py
python scripts/analyze_individual.py
python scripts/make_figures.py
python scripts/make_report.py
python scripts/prepare_slides.py
```

完整重跑需要若干分钟到几十分钟，取决于机器。构建会覆盖本项目生成的 scenarios 输入；若自行修改过，先保留副本。`data/raw` 不会被覆盖。不要同时启动两个写入相同运行目录的任务。

报告绘图采用 Arial。非 Mac 机器请安装 Arial，并修改 `make_report.py` 的字体路径。PowerPoint 可以直接编辑，不需要重新执行构建程序。幻灯片程序 `scripts/build_slides.mjs` 使用 Codex 内置 `@oai/artifact-tool` 和 presentation skill 校验工具；此专用构建环境不由 requirements.txt 安装。相关机器路径保留在源码中用于说明此次构建，离开本机需调整路径；**仿真、结果分析和现有 PPTX 不依赖该专用工具**。幻灯片 PDF 使用配套运行环境中的 LibreOffice 导出，并检查了最终 PDF 页面。

## 指标口径

- `mean_trip_min`：最终日全部完成出行的平均分钟数。
- `am_mean_min`：每人的第 1 次出行；主场景中是去上班。
- `am_p95_min`：每个运行内的第 95 百分位；场景汇总取三次 p95 的均值。
- `mean_score`：最终实际执行计划的平均得分，与 scorestats 的 avg. EXECUTED 相符。
- `mean_delay_s`：完整 entered-link → left-link 时间减去 length/freespeed，负值截为零。
- `exit_flow_vph`：完整路段退出数除以 5/15 分钟，再换算为每小时。
- `mean_occupancy`：以所有 link/traffic 进入退出事件精确积分的时段平均车辆数，包含移动车辆。
- `density_veh_km_lane`：平均占用数 / km / lanes。
- `max_occupancy`：时段最大车辆数，包含从前一时段延续的车辆。
- `full_link_measure=False`（links 1/20）：活动端点存在部分路段遍历，遍历和流量列设为缺失；占用与密度保留。缺失不能当成零。

主指标来自最终迭代，非 101 次迭代的时间平均。多随机种子范围反映算法不确定性，不是现实人口的置信区间。所有数值以完整精度分析；报告和幻灯片显示值有舍入，PPTX 图表数据最多保留 6 位小数。
