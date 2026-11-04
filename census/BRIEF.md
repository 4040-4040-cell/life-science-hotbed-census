# Census brief (shared by all 7 region agents)

Goal: a curated, verified census of life-science company SITES in one BioSpace "hotbed" region, for a
commercial real estate advisor (life-science lab/manufacturing real estate). Will be geocoded and plotted.

## Who to include (target 60 to 90 rows for your region; quality over count)
1. Every company listed on the region's BioSpace hub page (fetch it; click-through lists only show names).
   Mark these biospace_listed=Y. Keep only if they actually have a site in the region.
2. All publicly traded biotech / biopharma / life-science tools / diagnostics companies HEADQUARTERED in the region
   that are material (prioritize by market cap / headcount).
3. Large pharma and tools companies with a MAJOR R&D or manufacturing site in the region (one row per site,
   max 2 sites per company; site_type = R&D or Manufacturing).
4. Top private biotechs HQ'd in the region (well-funded, raised >= $100M lifetime or notable recent rounds).
5. CDMOs/CROs with significant regional facilities.
6. Up to 8 anchor research institutions / incubators (universities, research institutes, major incubators like
   JLABS, LabCentral, BioLabs) with category = Institution.

## Verification rules (strict)
- Street address must come from a current source: company website contact/locations page, latest SEC 10-K/10-Q
  cover page, or a press release dated 2025-2026. Record the URL in source_url.
- If a company moved HQ in 2025-2026, use the new address. If acquired/defunct as of Oct 2026, EXCLUDE it
  (note exclusions in a separate list at the bottom of your reply, not in the CSV).
- If you cannot verify a street address, you may still include the row with address blank and city filled,
  verified=N. Never invent a street address or suite number.
- Use WebSearch/WebFetch. Do not guess from memory without checking.

## Output
Write CSV to /home/claude/census/<region_slug>.csv with header exactly:
region,company,category,site_type,street,city,state,zip,submarket,ticker,biospace_listed,verified,source_url,notes
- category one of: Biopharma, Big Pharma, Tools & Diagnostics, CDMO/CRO, Institution
- site_type one of: HQ, R&D, Manufacturing, Campus
- submarket: the standard CRE life-science submarket name (e.g. Torrey Pines, UTC, Sorrento Mesa, South San Francisco,
  Kendall Square, Seaport, Research Triangle Park, Rockville/I-270, etc.). Use your judgment from the address.
- ticker blank if private. Quote fields containing commas (use python csv module to write).
Reply with: row count, count by category, count verified=N, BioSpace names excluded and why, and any data caveats.
Keep the reply under 300 words. Do not paste the CSV in the reply.
