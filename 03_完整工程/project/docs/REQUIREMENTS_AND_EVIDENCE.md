# Assignment requirements and evidence

Source: supplied 2026 five-page Group Project brief, copied as data/assignment_brief.pdf. The technical task is completed against the following content requirements.

| Brief requirement | Authoritative evidence |
|---|---|
| Choose equil or chessboard | Official matsim-12.0 equil files; report sections 3-4; source manifest and byte comparison with tutorial |
| Modify input data and explain why | scenarios/capacity/network.xml; scenarios/stagger/plans.xml; combined inputs; report section 5 |
| Modify configuration and explain why | scenarios/adaptive/config_s*.xml: TimeAllocationMutator, weights and mutation settings; report sections 2 and 5 |
| Actually run the developed scenarios | 27 exit-code-zero status records and matching successful MATSim logs; full events and configurations |
| Trip information including count and departure time | Final event/native-trip agreement; analysis/*_trips.csv.gz; report sections 7-8; slides 7-10 |
| Daily plan scores | Selected-plan/scorestats agreement; score histories; report section 9; slide 11 |
| Link states | Event traversal, flow, occupancy, density and delays; 5/15-minute tables; report sections 10-12; slide 12 |
| Compare with base | Original100 reproduction separated from controlled Baseline; all five main scenarios retain the same 2,000-agent population |
| Report title, abstract, background | Report pages 1-2 |
| Introduction to MATSim mechanisms | Report section 2 |
| Base and developed scenario introduction | Report sections 3-5 |
| Results, conclusions, limitations and future work | Report sections 7-15 |
| References | Report final page; official input URLs and MATSim source/book |
| About 15 pages, <=30 excluding references, 12 pt and single spacing | Report: 17 body pages + 1 reference page; 12 pt body and tables, 14.4 pt normal leading; rendered pages visually checked |
| Presentation slides in PDF | deliverables/LSGI3213_Equil_Slides.pdf, 19 landscape pages; editable PPTX also included |
| 20-minute presentation | 19 speaker-note entries; Presentation_Script_and_QA.md timeline sums to 1,200 seconds, including chart discussion/pauses |
| Group ID and leader filename convention | Leader: ZHANG Shizhuo; group ID unconfirmed, so neutral filenames are retained. scripts/rename_submission.py makes exact Group ID_Leader_Report.pdf / Slides.pdf copies from real metadata |
| Optional contribution form | Not created because personal contributions are unknown and form is optional |
| AI acknowledgement | Report section 15 and slide 19 accurately describe assistance. The 2026 brief restricts AI to ideas/proofreading; disclosed assistance exceeds this scope and instructor acceptance remains unconfirmed |

Actual classroom delivery, group registration and Canvas upload are personal administrative actions; none is claimed to have occurred. The current deadline is 13 November 2026 before 23:59. The historical brief is retained separately.

## Scientific QA boundaries

- Event durations are matched person-by-person to MATSim native CSV, not merely compared as averages.
- Work durations are independently checked as 28,800 seconds for all 2,000 agents in the five seed-4711 main scenarios.
- Flow and traversal values on activity links 1 and 20 are missing, not zero; occupancy/density still use all applicable traffic events.
- Peak occupancy includes state carried across bin boundaries; all exported bins satisfy maximum >= time mean.
- All corridor trips cross exactly one of links 11-19.
- Extended baseline/adaptive seed-4711 runs reach iteration 200. Baseline morning time stays nearly unchanged; Adaptive score still has positive tail drift.
- Score loss under imposed staggering affects 41.2-41.6% of individuals across seeds; average improvements are not described as universal benefits.
- Report figures use final-iteration events; repeated-seed ranges are not real-population confidence intervals.
- PPTX validation checks native chart/table structure and chart/workbook values; PDF visual review checks the exported appearance. No native Microsoft PowerPoint interaction is claimed.

## November revision evidence

`data/course_zip_comparison.json` verifies all four supplied course ZIP files. Additional 2,000-person data are explicitly identified as an official repository extension. Participation sensitivity adds nine runs, with three seeds per intermediate rate; 0% and 100% reuse existing results. `scripts/validate_project.py` checks 27 completed runs, 19 slides and 1,200 seconds. Identity-dependent naming and actual instructor approval are not claimed complete.
