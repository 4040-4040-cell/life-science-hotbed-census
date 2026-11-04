# Life science hotbed census

This repo holds the research data and build pipeline behind the Life Science Hotbed Maps site (https://claude.ai/artifact/UuJFneF7ycavaUyiaYXUPE).

- `census/`: the source of truth. It has one CSV per hub plus additions, the hand-classified footprint events, the Basel canton directories and campus inventories, and the research briefs that define the inclusion tests.
- `build/`: the pipeline:
  - enrichment (SEC, openFDA, ClinicalTrials.gov, geocoding)
  - scoring and reads
  - rendering (site, aerial exhibits, print sheets)
  - QA
  - logo capture, with chosen logos in `build/logos`
- `UPDATE.md`: the weekly runbook.
- `CHANGELOG.md`: what changed each run.

Caches (API responses, 10-K text, map tiles, the FDA bulk file) are regenerated and not stored here.
