# BRIEF BASEL (11th hub). Read /home/claude/census/BRIEF.md for verification rules and BRIEF_V3.md for header/search rules.

REGION = Basel trinational life-science cluster, region value "Basel", region_slug "basel", country column CH, FR or DE.
Geography: Basel-Stadt; Basel-Landschaft (Allschwil, Muttenz/Schweizerhalle, Pratteln, Liestal, Reinach, Aesch, Arlesheim,
Münchenstein, Birsfelden, Bubendorf, Sissach); Aargau Fricktal (Kaiseraugst, Rheinfelden, Stein AG, Möhlin, Frick, Sisseln);
Solothurn north (Dornach, Breitenbach); Jura (Delémont, Courroux); Alsace (Saint-Louis, Huningue, Hégenheim); South Baden
(Grenzach-Wyhlen, Lörrach, Weil am Rhein, Rheinfelden-Baden). Nothing in Zurich, Zug, Bern, Lausanne or Geneva.

Inclusion: real site in region AND any one test (amounts converted to USD millions at the rate on the announcement date; state
the original currency and amount in notes):
  T1 Public: listed life-science company (SIX, NASDAQ, NYSE, Euronext, Xetra) headquartered in region.
  T2 Funded private: >= $100M lifetime OR >= $50M since 2023-10-01 (cite press release).
  T3 >= 100 employees at sites in region (cite).
  T4 Approved product (Swissmedic, EMA or FDA) on market.
  T5 Major site of a big pharma / tools / CDMO / medtech company (named plant, >= 100 staff or >= 10,000 m2). Max 2 rows/company.
  T6 Anchor institution, park or incubator (max 8: e.g. University of Basel Biozentrum, ETH Zurich D-BSSE Basel, Swiss TPH,
     FMI, University Hospital Basel, Switzerland Innovation Park Basel Area Main Campus, Rosental Mitte, Campus Klybeck / Stücki).
  T7 Funded young private: >= $10M disclosed equity financing since 2023-01-01 (cite; startupticker.ch, company PR).
OUT: acquired/merged/closed/delisted as of 2026-11-02 (list in reply). Life science only: biopharma, tools, diagnostics,
CDMO/API, medtech with lab or manufacturing. Not pure agrochemicals or specialty chemicals unless a pharma CDMO business line.

Columns: standard header from BRIEF_V3 (ends website,country). state = canton code (BS, BL, AG, SO, JU) or Haut-Rhin / Baden-Württemberg.
zip = Swiss 4-digit / French / German postcode. Street addresses matter: we geocode to the building. Use Handelsregister/Zefix
address, company contact page or campus resident page. Campus residents at Hegenheimermattweg 167A etc: give that address and
put "Main Campus resident" in notes. submarket: use one of Novartis Campus / St. Johann, Klybeck / Rosental, Roche Wettstein /
Grenzacherstrasse, Basel Central (SBB / Aeschen / Picassoplatz), Basel Gundeli / Dreispitz, Allschwil / Bachgraben, Schweizerhalle /
Muttenz / Pratteln, Birs Valley (Reinach, Aesch, Dornach, Arlesheim, Münchenstein), Fricktal (Kaiseraugst, Rheinfelden, Stein, Sisseln),
Upper Basel-Landschaft (Liestal, Bubendorf, Sissach), Alsace (Saint-Louis, Huningue), South Baden (Grenzach, Lörrach, Weil), Jura.
employees: sourced integer for region-level staff if stated, else company-wide only if the company is region-only; else blank.
footprint_event_2025_26: lease, expansion, new building, consolidation, sublease, layoff, closure, with m2 and date. This is the CRE signal:
prioritise it for the top 40 names (Roche Bau 2/52, Novartis campus moves and Klybeck sale, Lonza, Bachem Sisseln, Idorsia
downsizing, J&J Allschwil, BMS Klybeck, Main Campus leases, Rosental Mitte, Stücki Park, Dreispitz, etc.).
Seed list (verify each, keep if it qualifies): /home/claude/census/basel_work/v6_seed.csv (from a parallel dataset; addresses may be
incomplete and some sites may be stale; re-verify every row, do not copy without checking).
Never estimate. Blank beats a guess. Save progress every 20 rows.
