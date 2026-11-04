# Supplemental MATSim experiment design

This study is isolated on `experiment/sensitivity-2026-11-04`. It adds experiments without merging into main or replacing the original results.

## Questions

1. Does capacity expansion still help when departures are already spread over 30 minutes?
2. How do capacity multipliers 1, 1.5 and 2 interact with departure windows 0, 30 and 60 minutes?
3. Why does combining capacity and staggering add little benefit in the original experiment?
4. Do adaptive-timing scores stabilize by iteration 500, and which departure groups lose plan utility?

## Design fixed before inspecting the new outcomes

- 3 x 3 grid, paired seeds 4711, 42 and 2025: 27 grid records.
- Reuse 12 verified original grid runs; execute 15 missing grid runs through iterations 0-100 inclusive.
- Execute adaptive timing through iterations 0-500 inclusive for all three seeds, starting from the original inputs.
- Keep 2,000 agents, facilities, work duration, scoring, routing strategies and thread counts fixed. Capacity changes only links 11-19.
- Departure windows use the original deterministic person-order midpoint quantiles centered on 06:00. A dispersed baseline is hypothetical, not calibrated observed traffic.
- Compare final-day AM mean and p95, plan scores, score-loser share, full corridor traversal delay, corridor occupancy peak and 5-minute exit flow.
- Independently match event-derived trips to MATSim native trip output and selected-plan scores to score histories.
- Adaptive checkpoints: 100, 200, 300, 400 and 500. Descriptive stability screen: absolute executed-score mean difference between iterations 451-500 and 401-450 at most 0.05 utils. This is an explicitly chosen diagnostic, not proof of equilibrium. Also report trajectories, ranges, slopes and departure/travel changes.
- Report paired seed effects and ranges; three seeds do not support strong statistical or real-world generalization.
- Pre-opening gap is max(07:00 minus work arrival, 0). It is a descriptive timing measure, not MATSim native waiting time or a causal decomposition of score losses.

## Reproducibility

The completed package will include scripts, input scenarios, raw run evidence, result tables, figures and file hashes. The original project supplies MATSim 12.0 and its runtime libraries. This machine uses Java 14.0.2; original saved runs used Java 11. The earlier independent baseline and capacity reruns reproduced final event files exactly across these environments.
