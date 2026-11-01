# Figure choices from the actual data

Profile: 16 primary summary rows: 5 scenarios with 3 paired seeds and 1 original-data reference. Main runs have 2,000 identified people and 4,000 trips each; link states use 23 links x 5/15-minute bins, with synthetic node coordinates available. Extended runs are separate sensitivity evidence. No filtering of people is applied.

Computed comparison: Baseline AM mean 22.052 min; Capacity 18.599; Stagger 15.002; Combined 15.000; Adaptive 15.011. Main score means range 125.920-129.949. Adaptive has approximately +0.245 utils of late-iteration drift at iteration 100. These support separate performance, timing and learning figures rather than a single index.

- Orientation: directed synthetic network, with treatment links coloured; coordinates provide topology context and not measured distance or a city basemap.
- Scenario outcomes: three seed points plus a mean mark, retaining stochastic variation; mean bars alone would hide replication variability. Presentation uses a zero-based bar with the range table on another slide.
- Individual trip distribution: ECDF and paired-change violin; no distribution is inferred from a bar of means.
- Departure patterns: both 15- and 5-minute bins are retained. Count heights depend on bin width and are labelled accordingly.
- Learning: full history plus late-iteration inset, with all five main scenarios sharing a score scale. Original100 scores are excluded from the inset range because that population's plans differ.
- Route use and link delay: common link-ID axis. Missing routes are not imputed as zero travel time.
- Link dynamics: matched time axes for flow, occupancy, travel time and density; separate units and no dual axis.
- Link-by-time matrix: shared sequential delay scale across Baseline and Combined; missing cells remain white.

Rejected: pie charts (poor for small scenario differences); 3D plots (distortion); a real basemap (synthetic coordinates); score-to-money conversion (unsupported); population confidence intervals (only algorithmic seed variation). Colours are consistent across figures. Quantitative charts and tables are editable in the PPTX; full-precision analysis remains in CSV, while displayed chart data is rounded to six decimals.
