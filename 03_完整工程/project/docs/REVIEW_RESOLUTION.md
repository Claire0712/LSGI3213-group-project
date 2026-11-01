# Independent review resolution

A separate reviewer inspected scenario generation, event accounting and report interpretation.

1. Peak occupancy across bin boundaries: fixed by carrying the pre-event state into every intersected bin. Regenerated all 18 analysis files. Validation checks maximum >= mean in every row.
2. Activity-link flow interpretation: links 1 and 20 now have missing traversal/flow columns, while event-integrated occupancy and density remain. Corridor figures use links 11-19. This scope is documented in report Section 6 and README.
3. Individual score losses: independently recalculated paired-person scores for all three seeds. Stagger and Combined each show 41.2-41.6% score losers. Added the result to the report and presentation.
4. Eight-hour work duration: reviewer and project validator independently checked actstart/actend events for every person in the five seed-4711 main scenarios. All 10,000 work activities last 28,800 s.
5. No other substantive errors found in headline results or scenario controls. Remaining limitations are stated in the report rather than treated as validation failures.

Visual QA additionally corrected an inset range that included the separate original100 reference, an unsupported font glyph, unused-link missing observations, and chart-export defaults. Portable chart normalization explicitly disables scatter smoothing, removes empty axis titles and places axes at minima; it changes no numeric observations.
