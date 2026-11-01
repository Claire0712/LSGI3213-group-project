# LSGI3213 MATSim project execution plan

Objective: fulfil the supplied brief with traceable public equil inputs, executed scenarios, analysis of trips/scores/link states, an approximately 15-page English report (12-point body, single spacing), PDF slides for a 15-minute talk, and reproducible code.

Design: retain the official MATSim 12.0 equil network/facilities; run its 100-agent example as a source reference. Use the official 2,000-agent demand as an explicitly derived congested reference. Compare capacity doubling on links 11-19, symmetric one-hour staggered departures, their combination, and departure-time learning configured with TimeAllocationMutator. Keep scoring and other parameters consistent. Use seeds 4711, 42 and 2025, iterations 0-100, single-thread execution. Check learning traces and extend key scenarios to 200 iterations if needed. Do not equate numerical score stability with proof of equilibrium.

Alternatives considered: chessboard would add data reconstruction uncertainty; importing a real city would depart from the assigned equil/chessboard choice. Public equil best matches the brief. Synthetic data must not be described as measured Hong Kong travel.

- [x] Read all five pages of brief and inspect tutorial installation.
- [x] Download official version-tagged network, facilities, config, plans100 and plans2000; record hashes and URLs.
- [x] Build isolated scenario inputs and explicit XML change inventory; verify populations and connected routes after MATSim loading.
- [x] Execute original reference and main scenarios, recording commands, Java version, exits and logs; preserve raw events.
- [x] Extract completed/stuck trips, times, score histories, route usage and link flow/travel time/occupancy. Validate event accounting on an independent hand-computed fixture and against native trip outputs.
- [x] Compare paired seeds, departure distributions and 15/5-minute link conditions; report stochastic ranges and convergence limitations.
- [x] Make data figures with Arial and 300 dpi; retain vector originals.
- [x] Write report with every prescribed section, references, source provenance and honest AI acknowledgment.
- [x] Create PDF slides, editable deck if runtime supports it, and timed speaking notes plus Q&A guidance.
- [x] Render and inspect all final pages/slides; audit every brief requirement; package deliverables and replication instructions.

Missing group ID / leader name are administrative metadata only; use LSGI3213_Equil names pending user response. No Blackboard access, identity claims or submission is implied.
