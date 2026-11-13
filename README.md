# LSGI3213 · MATSim 交通仿真小组项目

本仓库整理 LSGI3213 Intelligent Transport Systems 小组项目的课程材料、MATSim 仿真工程、分析结果、报告与演示文件。当前已发布内容对应 **2026 年课程要求修订版**。

## 快速阅读

| 想查看的内容 | 入口 |
| --- | --- |
| 英文报告 | [报告 PDF](03_完整工程/project/deliverables/LSGI3213_Equil_Report.pdf) |
| 演示材料 | [幻灯片 PDF](03_完整工程/project/deliverables/LSGI3213_Equil_Slides.pdf) · [可编辑 PPTX](03_完整工程/project/deliverables/LSGI3213_Equil_Slides.pptx) |
| 演讲与答辩准备 | [讲稿与 Q&A](03_完整工程/project/deliverables/Presentation_Script_and_QA.md) |
| 方法、数据来源与完整复现步骤 | [工程中文说明](03_完整工程/project/README_中文.md) |
| 核对实验数值 | [主要运行汇总](03_完整工程/project/analysis/summary_by_run.csv) · [参与率敏感性](03_完整工程/project/analysis/participation_by_run.csv) |
| 查看图表 | [分析图目录](03_完整工程/project/figures/) |
| 核对课程要求 | [2026 年课程材料](01_项目要求与素材/2026最新版/) · [需求与证据](03_完整工程/project/docs/REQUIREMENTS_AND_EVIDENCE.md) |

## 研究内容

项目使用 MATSim 12.0 的官方 equil **合成示例**，比较基准、道路扩容、错峰出行、组合策略及自适应出发时间等情景，并加入 25%、50%、75% 参与率敏感性分析。

- 原始 **100 人**场景用于课程示例复现；干预效果统一以 **2,000 人**拥堵实验为基准。
- 主要情景采用 4711、42、2025 三个随机种子，另有延长迭代检查。
- 分析包括行程时间、路段运行状态、个体计划得分和参与率变化。
- 数据不是香港真实交通观测；平均行程时间改善也不代表每个个体均受益。指标定义与结论边界见工程说明。

## 仓库结构

| 路径 | 用途 |
| --- | --- |
| [`01_项目要求与素材/`](01_项目要求与素材/) | 课程要求、讨论材料与示例输入；优先参考 `2026最新版/` |
| `02_提交成果/` | 本地提交成果快捷链接；GitHub 浏览请使用上方报告和幻灯片的直接链接 |
| [`03_完整工程/project/`](03_完整工程/project/) | 完整工程：原始数据、场景、运行结果、分析、图表、源码与成果 |
| [`04_压缩备份/`](04_压缩备份/) | 历史完整工程快照，不代表当前修订版 |

工程内的 `data/` 保存来源记录与原始输入，`scenarios/` 保存运行配置，`runtime/` 保存 MATSim 运行依赖，`runs/` 保存实际仿真输出，`analysis/` 与 `figures/` 保存分析结果，`scripts/` 保存处理代码，`docs/` 与 `qa/` 保存方法和检查记录。

本地 `overleaf_draft/` 是未发布的编辑草稿，不纳入本次仓库整理；`.build/`、`.chart-data-*/` 和依赖缓存不作为发布成果跟踪。历史提交仍保留原有文件。

## 下载与复现

```bash
git clone https://github.com/Claire0712/LSGI3213-group-project.git
cd LSGI3213-group-project/03_完整工程/project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/test_events.py
python scripts/validate_project.py
```

阅读现有报告、图表和 CSV 无需重新运行仿真。完整仿真需要 Java 11 与 MATSim 12.0；分析环境及重跑顺序见[工程中文说明](03_完整工程/project/README_中文.md#复现)。幻灯片重建依赖原作者的专用构建环境，现有 PDF/PPTX 可直接查看。

## 版本与提交状态

- 课程截止：2026 年 11 月 13 日 23:59 前，Canvas；汇报时长为 20 分钟。
- 仓库已发布说明中的组长为 ZHANG Shizhuo，组号尚待确认；最终封面和提交文件名需以小组核验结果为准。
- GitHub 发布不代表已完成 Canvas 提交，也不代表本地后续草稿已同步。
- 报告和幻灯片披露了 AI 辅助。课程要求对允许的 AI 使用范围更窄，是否符合要求仍需由小组与教师确认。

## 来源与使用

MATSim 示例来源、文件哈希和比对记录见 [`data/source_manifest.json`](03_完整工程/project/data/source_manifest.json)。第三方运行依赖的许可文件保留在 [`runtime/`](03_完整工程/project/runtime/) 中。课程文件与第三方材料的权利归原权利人所有；仓库公开不额外授予这些材料的再许可权。
