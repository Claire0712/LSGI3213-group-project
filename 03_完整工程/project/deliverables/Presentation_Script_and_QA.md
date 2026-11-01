# 15-minute presentation script

English slides and script; timing includes pointing to figures and short pauses.

## Slide 1: Capacity and departure scheduling in MATSim (00:00-00:30)

This project examines two ways of reducing congestion: changing road discharge capacity and changing when people depart. We use the official equil example and execute the scenarios in MATSim 12.0. Our evidence includes actual event files, repeated runs and comparisons of trips, daily plan scores and link states. The network and population are synthetic, so the findings describe this experiment rather than a forecast for Hong Kong.

## Slide 2: Research questions (00:30-01:25)

The number of travellers does not determine congestion on its own. When they depart and how they distribute themselves over routes matter as well. We first separate a supply intervention from a timing intervention. We then combine them to see whether their benefits overlap. Finally, we let agents change departure times through a configuration change. That distinction matters: an imposed schedule represents coordination, whereas adaptive timing represents individual responses to the model scoring rules. We assess both traffic performance and daily scores, since improving one does not necessarily improve the other by the same amount.

## Slide 3: Official equil data (01:25-02:30)

The assignment permits equil or chessboard. We selected equil and downloaded the version-tagged inputs from the official MATSim repository. Five downloaded files match the corresponding tutorial files byte for byte. The Blackboard project ZIP itself was not accessed, so we distinguish those two claims. The network has nine outward alternatives and a shared return path. Red lines represent links eleven to nineteen, which receive the capacity treatment. Coordinates are synthetic and road lengths are read from XML, not measured from this drawing. The principal experiment uses the supplied two-thousand-person population with four thousand daily car trips.

## Slide 4: MATSim execution and learning (02:30-03:30)

MATSim executes individual activity plans together, so the congestion experienced by one agent depends on everyone else. The mobility simulation is queue based. Vehicles require a free-speed traversal time and then face discharge and downstream constraints. After execution, daily activity and travel experiences generate scores. In the fixed-time scenarios, BestScore has weight zero point nine and ReRoute has weight zero point one, with a five-plan memory limit. We repeat this process through iteration one hundred. The resulting mean score is informative about learning, but a flat line alone is not proof of exact network equilibrium.

## Slide 5: Five controlled scenarios (03:30-04:55)

Every main scenario keeps two thousand agents, the same home and work links, car mode and an eight-hour work activity. Capacity doubles discharge capacity on nine corridor links, without adding lanes or increasing free speed. Stagger assigns equally spaced departure times between five thirty and six thirty, preserving a six o’clock mean. Combined applies both changes. Adaptive starts with the baseline inputs but reallocates one tenth of the BestScore weight to TimeAllocationMutator. Its mutation range is thirty minutes and it does not mutate the explicit work duration. Repeated mutations can accumulate, so the final adaptive departure distribution is not restricted to the externally staggered window.

## Slide 6: Execution and independent checks (04:55-05:40)

The main experiment contains fifteen runs. Seeds are paired across scenarios, and all runs use single-thread settings to reduce unnecessary execution variability. Each final main run completes exactly four thousand trips with no stuck agents or unmatched departure and arrival events. We independently reconstruct trip durations from events and match them to every native trip-table row. Selected-plan scores are also checked against the executed-score history. The original one-hundred-person example is run separately as a reproduction check. Its different schedule structure means it is not the denominator for the policy comparisons.

## Slide 7: Morning travel time (05:40-07:05)

The baseline morning trip takes 22.05 minutes on average across the three seeds. Capacity reduces that to 18.60 minutes. Staggering reduces it to 15.00, and the combination to 15.00. The adaptive scenario gives 15.01 minutes. Trip numbers remain fixed, so these improvements come from travel experience rather than cancelling journeys. Notice the small difference between Stagger and Combined: once the departure pulse has been spread enough to remove most queues, extra capacity has little remaining delay to remove. The report also gives the ninety-fifth percentile and total daily travel hours.

## Slide 8: Realised departure patterns (07:05-08:05)

This figure uses the first trip of every person at seed forty-seven eleven. Baseline departures form a pulse around six. The staggered intervention spreads that pulse symmetrically, whereas adaptive timing emerges from learning. Capacity alone does not change the first planned departure times. The adaptive pattern is affected by the work opening time of seven and the penalties and rewards in the daily scoring system. These are realised departure events, not counts of vehicles already admitted to a full road link. The report also uses five-minute bins to show whether a coarser histogram conceals a short concentration.

## Slide 9: Travel-time distributions (08:05-09:00)

The cumulative distribution adds information hidden by an average. At a given travel time, the vertical position shows the share of morning trips completed within that duration. A curve further left generally indicates shorter trips. A near-vertical curve means that many agents experience almost the same duration. The displayed curves use two hundred and one ordered points from each two-thousand-trip distribution for clarity, while the full observations remain in the result files. Differences near the upper end identify the slower travellers, and the report pairs individual agents to examine who gains or loses.

## Slide 10: Executed scores and timing preferences (09:00-10:20)

At iteration one hundred, average executed scores across seeds are 125.92 in Baseline and 129.95 in Adaptive. The adaptive line improves more strongly because changing departure times affects activity timing as well as travel. Work opens at seven, has a latest start time of nine and closes at eighteen. Arriving early can therefore interact with the activity utility even if the trip is quick. These model-specific utility scores are not money and should not be converted into monetary benefits without a defensible welfare model. The report includes all three seed histories and a magnified late-iteration panel, and we extend selected runs to test remaining drift.

## Slide 11: Delay on the nine corridor links (10:20-11:45)

The network-wide travel comparison has a physical mechanism. This plot subtracts nominal free-speed time from full-link traversal time for each treated corridor link. The recorded traversal starts with entered-link and ends with left-link for the same vehicle. We exclude activity endpoint links from full-link speed interpretation because their traversal can be partial. The report also calculates exit flow, exact time-averaged occupancy and density. Occupancy includes moving vehicles, so it must not be called queue length. Throughput can temporarily rise as queues clear even while travel time improves. We use both fifteen-minute and five-minute bins, and leave empty traversal bins missing rather than filling them with zero.

## Slide 12: Robustness and convergence limits (11:45-12:50)

The three-seed range indicates numerical variability under these settings. It is not a confidence interval for a real population. Tail score change compares the last ten iterations with the preceding ten. A small change supports stability of that average, while continued drift, particularly in Adaptive, makes the horizon important. We also reran the baseline and adaptive cases with two hundred iterations from the same starting inputs. The extended morning-time results are baseline: 21.93 → 21.93 min; adaptive: 15.01 → 15.01 min. Longer runs can reveal continuing learning, but they cannot validate synthetic demand or the assumed schedule preferences. More observed data are needed for that.

## Slide 13: Interpretation for ITS (12:50-13:45)

Both interventions address the same queueing process, which explains why their benefits need not add. Across the three seeds, between 41.2 and 41.6 percent of agents have a lower daily score under Stagger and Combined, despite the higher mean score. This supports the warning about schedule inconvenience. The factorial interaction is Combined minus Capacity minus Stagger plus Baseline. A positive value means the joint saving is smaller than the sum of the separate savings. This is a controlled simulation comparison, not a causal estimate for an observed city. An actual ITS programme would need employer coordination or traveller incentives, measured participation and schedule constraints. Expansion would need engineering and cost assessment. The simulation provides traffic evidence but cannot establish which intervention is cost-effective, safest or most equitable.

## Slide 14: Conclusions (13:45-14:40)

The key result is that the same four thousand daily trips can produce different congestion when supply or timing changes. Capacity reduces the morning queue, while spreading departures removes much of its formation in this synthetic example. Combining them gives limited extra benefit after delays are nearly removed. Adaptive timing illustrates the importance of activity preferences and continuing learning. The project therefore satisfies the three requested analysis dimensions: trips, daily plan scores and link states. The complete inputs, code, logs and events are supplied so that another person can reproduce the analysis and examine assumptions rather than relying only on the presentation.

## Slide 15: Sources and acknowledgment (14:40-15:00)

Full references and file hashes are included in the report and project package. AI assistance covered design, implementation, analysis and writing and is disclosed explicitly. The numerical evidence comes from the saved MATSim runs. Thank you; we welcome questions about the assumptions, methods and results.

## 中文答辩提示

- 为什么不用真实香港数据？题目指定 equil/chessboard；这里选择官方 equil。它是机制实验，不是城市预测。
- 为什么 100 人和 2,000 人得分差很多？计划结构与工作时长不同，不能直接归因于人口规模；干预比较只在相同的 2,000 人需求之间进行。
- 为什么错峰之后扩容帮助很小？两种措施消除的是相同队列，错峰已接近无拥堵基准，存在收益重叠。
- 得分是否等于福利或钱？不是；它还受活动时长、到达时刻和工作开放时间影响。
- 为什么不是加车道？本实验只改 capacity，车道与长度保持不变，因此是放行能力实验。
- 是否已经收敛？查看末段得分变化与 200 次扩展运行；特别是自适应时间场景仍可能继续学习，不能声称精确均衡。
- 是否验证过数据？五个官方文件与教程一致；事件出行时间与原生 trip 表逐行匹配，全部完成且无 stuck。
- 能否直接用于政策？还需真实需求校准、参与率、成本、排放与公平性分析。
