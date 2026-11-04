# BRIEF V3 (for new and relaunched regions). Read BRIEF.md for verification rules and BRIEF_V2.md for the
# inclusion tests T1 to T6 and column meanings. This file changes three things:

1. TWO NEW COLUMNS appended at the end of the header: website,country
   - website: the company's own homepage URL (https://...), verified by fetching it (curl -sL -o /dev/null -w "%{http_code}"
     from Bash is fine and does not use search budget). For big-company sites use the parent homepage.
   - country: US or UK.
   Full header:
   region,company,category,site_type,street,city,state,zip,submarket,ticker,biospace_listed,tests_met,employees,employees_source,private_raised_total_usd_m,last_round_usd_m,last_round_date,last_round_type,funding_source_url,modality,footprint_event_2025_26,footprint_source_url,verified,source_url,notes,website,country

2. SEARCH BUDGET. WebSearch is capped at 200 calls per turn SHARED across all agents. Your personal cap is stated in
   your prompt. Count your searches and stop searching at the cap. Prefer non-search sources first: SEC EDGAR APIs
   via curl (https://www.sec.gov/files/company_tickers.json, https://data.sec.gov/submissions/CIK##########.json has
   business address and state; use User-Agent "WCLS research chad.urie@urieinvestments.com"), company websites via
   WebFetch or curl, trade association member directories via WebFetch, BioSpace hub page via WebFetch.
   WebFetch does not count against the search cap.

3. Write the CSV with python csv module to /home/claude/census/<region_slug>.csv. Save progress to the file every
   20 rows so work is not lost if you are interrupted.
Reply under 250 words: row count, by category, verified=N count, qualifying names seen but not added.
