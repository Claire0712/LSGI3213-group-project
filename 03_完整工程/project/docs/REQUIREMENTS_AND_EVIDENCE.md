# Assignment requirements and evidence

Source: supplied five-page Group Project brief, copied as data/assignment_brief.pdf. The technical task is completed against the following content requirements.

| Brief requirement | Authoritative evidence |
|---|---|
| Choose equil or chessboard | Official matsim-12.0 equil files; report sections 3-4; source manifest and byte comparison with tutorial |
| Modify input data and explain why | scenarios/capacity/network.xml; scenarios/stagger/plans.xml; combined inputs; report section 5 |
| Modify configuration and explain why | scenarios/adaptive/config_s*.xml: TimeAllocationMutator, weights and mutation settings; report sections 2 and 5 |
| Actually run the developed scenarios | 18 exit-code-zero status records and matching successful MATSim logs; full events and configurations |
| Trip information including count and departure time | Final event/native-trip agreement; analysis/*_trips.csv.gz; report sections 7-8; slides 6-9 |
| Daily plan scores | Selected-plan/scorestats agreement; score histories; report section 9; slide 10 |
| Link states | Event traversal, flow, occupancy, density and delays; 5/15-minute tables; report sections 10-12; slide 11 |
| Compare with base | Original100 reproduction separated from controlled Baseline; all five main scenarios retain the same 2,000-agent population |
| Report title, abstract, background | Report pages 1-2 |
| Introduction to MATSim mechanisms | Report section 2 |
| Base and developed scenario introduction | Report sections 3-5 |
| Results, conclusions, limitations and future work | Report sections 7-15 |
| References | Report final page; official input URLs and MATSim source/book |
| About 15 pages, <=30 excluding references, 12 pt and single spacing | Report: 16 body pages + 1 reference page; 12 pt body and tables, 14.4 pt normal leading; rendered pages visually checked |
| Presentation slides in PDF | deliverables/LSGI3213_Equil_Slides.pdf, 15 landscape pages; editable PPTX also included |
| 15-minute presentation | 15 speaker-note entries; Presentation_Script_and_QA.md timeline sums to 900 seconds, including chart discussion/pauses |
| Group ID and leader filename convention | Identity not supplied; neutral names used. scripts/rename_submission.py makes exact Group ID_Leader_Report.pdf / Slides.pdf copies from real metadata |
| Optional contribution form | Not created because personal contributions are unknown and form is optional |
| AI acknowledgement | Report section 15 and slide 15 accurately describe assistance. User instructed proceeding regardless of the old brief's scope restriction |

Actual classroom delivery, group registration and Blackboard upload are personal administrative actions; none is claimed to have occurred. The November 2025 dates belong to the supplied historical brief.

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
