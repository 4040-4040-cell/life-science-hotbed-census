# BRIEF V2 (supersedes the row target and CSV header in BRIEF.md; all verification rules still apply)

The user wants a defensible company BASE per region, not a sample. Inclusion is rule-based. A company is IN if it
has a real site (HQ, R&D, or manufacturing) in the region AND meets ANY ONE test:
  T1 Public: exchange-listed life-science company (NASDAQ/NYSE/NYSE American) HQ'd in region, any size.
  T2 Funded private: raised >= $100M lifetime OR >= $50M since 2023-10-01 (cite the press release).
  T3 Scale: >= 100 employees at sites in the region (cite source).
  T4 Commercial: has an FDA-approved/cleared product on market.
  T5 Major site of a big pharma / tools / CDMO company (>= 100 employees or >= 100,000 SF, or a named
     manufacturing plant). Max 2 rows per company.
  T6 Anchor institution or incubator (max 8).
OUT: acquired, merged, closed, or delisted-and-wound-down as of 2026-10-28 (list exclusions in your reply).

Coverage target: everyone meeting T1 and T2 that you can find (use BioSpace list, Biocom/CLSA/MassBio/BioNC/etc.
member lists, Fierce Biotech fundraising tracker, Endpoints, company press releases, Nasdaq biotech listings by state).
Cap 160 rows. If you hit the cap, keep T1, T4, T5 first, then T2 ranked by amount raised. Say in your reply how
many more qualifying names you saw but could not add.

CSV path unchanged: /home/claude/census/<region_slug>.csv. NEW header exactly:
region,company,category,site_type,street,city,state,zip,submarket,ticker,biospace_listed,tests_met,employees,employees_source,
private_raised_total_usd_m,last_round_usd_m,last_round_date,last_round_type,funding_source_url,modality,
footprint_event_2025_26,footprint_source_url,verified,source_url,notes

- tests_met: e.g. "T1;T4"
- employees: integer only if you found a sourced number (10-K, company site, press release); else blank.
- private fields: privates only; amounts in USD millions; blank if not found. Never estimate.
- modality: e.g. small molecule, antibody, cell therapy, gene therapy, RNA, radiopharma, tools, diagnostics, CDMO.
- footprint_event_2025_26: lease signed / expansion / new plant / consolidation / sublease / layoff / site closure,
  with SF and date if stated (this is the real estate signal; prioritize finding it for the top 40 names).
- Do NOT spend effort on public-company market cap, FDA approval lists, or trial phase: those will be pulled from
  SEC EDGAR, openFDA and ClinicalTrials.gov afterward. Do give the exact ticker.
Rewrite any rows you already collected into the new header. Reply under 300 words.
