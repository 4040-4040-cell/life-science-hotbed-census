# Weekly update runbook: Life Science Hotbed Maps

Live site: https://claude.ai/artifact/UuJFneF7ycavaUyiaYXUPE (artifact slug e1f40db8-a4c7-48cb-84be-83b638148455, shared publicly).
Mode: approve before publish. A weekly run builds and checks everything, then stops and asks for approval. It never publishes on its own.

## 0. Set up the workspace (5 minutes)
- Clone this repo to /home/claude/hotbed. Then: `ln -sfn /home/claude/hotbed/build /home/claude/build; ln -sfn /home/claude/hotbed/census /home/claude/census`. The scripts use those absolute paths.
- `pip install --break-system-packages pillow pypdf pytesseract cairosvg python-pptx` if missing. Playwright and Chromium are preinstalled.
- `sh build/fetch_bulk.sh` gets the openFDA Drugs@FDA bulk file.
- SEC EDGAR needs a declared User-Agent. The scripts default to `WCLS research chad.urie@urieinvestments.com` (approved by the user, Nov 4, 2026). Override with `WCLS_UA` if needed.
- Rebuild the caches the first time (they are not in git): `cd build && python3 build.py` (all regions, about 60 to 90 minutes cold), then `python3 prefetch_aerial.py` after the first render.

## 1. Collect the week's changes (research)
Search only sources dated since the last run (see CHANGELOG.md for the date). Never use or cite CBRE. Never estimate. Blank beats a guess.
For each hub (Biotech Beach, Biotech Bay, Genetown, Pharm Country, BioCapital, Bio NC, BioMidwest, Seattle, Colorado, UK, Basel, plus the Basel-Stadt and Basel-Landschaft canton files):
- Footprint events: leases, expansions, new buildings, groundbreakings, subleases, layoffs, site closures, plant sales. Write the event into the company row (`footprint_event_2025_26`, `footprint_source_url`) and add one hand-classified line to `census/footprint_class.csv` (dir +1 expansion, -1 contraction, 0 neutral; sf_change if stated; event_month; short label; reason).
- Membership: acquisitions, mergers, liquidations, delistings, renames, relocations. Remove or rename rows and log the reason in CHANGELOG.md.
- New qualifying companies (tests T1 to T7 in census/BRIEF_V2.md, BRIEF_FORMD.md, BRIEF_BASEL.md; T8 for the Basel canton directories): add rows to `census/<slug>_addN.csv` with a verified operating street address.
- Basel space: update `census/basel_campus_bs.csv` and `basel_campus_bl.csv` (status, delivery year, available m2, anchor tenants) with each size on its published basis.

## 2. Rebuild
```
cd /home/claude/census && python3 tools/make_basel_detail.py
cd /home/claude/build
python3 build.py            # re-enrich: SEC cash, 10-K, FDA, ClinicalTrials.gov, geocoding
python3 logo_items.py && python3 logos_pw.py logo_items_new.json; python3 logos_static_run.py logo_items_new.json; python3 choose.py   # only for new companies
python3 render.py           # site/index.html and site/data/*.js (about 20 minutes)
python3 export.py           # census CSV
python3 print_pdfs.py compare,biotech-beach,biotech-bay,genetown,pharm-country,biocapital,bio-nc,biomidwest,seattle,colorado,uk,basel,basel-city,basel-land
```

## 3. Check (all must pass)
- `python3 qa.py`: there must be no out_of_bbox rows and no HQ appearing in more than one region. Review every new fda_check and emp_jump.
- Every print PDF must be exactly 1 page (pypdf page count).
- Render and look at every changed market sheet. Leader lines must reach their zones, and there must be no clipping or overflow.
- No banned wording, no em dash, no CBRE in served text.
- Compare each hub's compare-table numbers with last week's. Explain any move over 10% in the changelog.

## 4. Changelog and approval
Write CHANGELOG.md for this week: date, companies added and removed (with reasons), new footprint events by hub, read changes (new expansion candidates and contraction risks), compare-table deltas, open issues. Commit to a branch `update-YYYY-MM-DD`, then send the user the changelog and the one-page PDFs for any market that changed. Ask for approval to publish.

## 5. Publish (only after the user approves)
Publish with publish_files to the slug above, base_version from get_artifact, shared_live "public", artifact_title "Life Science Hotbed Maps". Publish `index.html` plus only the `data/*.js` files that changed. Merge the branch to main. Update the project doc claude/hotbed-census-summary.md.

## Standing rules
- Each site counts in its own canton or hub. Fricktal, Alsace and South Baden stay in the Basel hub only.
- Major sites of outside companies get the Site tier and are not scored.
- "No trigger" means no signal was found, not that a company is stable.
- JLL research figures supplied by the user may be shown with their source.
- Imagery: Esri World Imagery. Confirm JLL's ArcGIS license before client distribution.
