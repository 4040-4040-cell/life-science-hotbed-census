# Form D candidate screen (judgment task)
Input: /home/claude/census/formd_candidates_<part>.csv. Each row is a private company that filed SEC Form D (industry Biotechnology or
Pharmaceuticals) and sold >= $10M of securities since Jan 1 2023, with its latest Form D business address. Today is 2026-10-28.

For EVERY row decide, and write /home/claude/census/formd_screen_<part>.csv with columns:
cik,name,status,status_note,website,category,modality,site_type,keep
- status: active | acquired | merged | closed | renamed | public_now | unknown. Use your knowledge, then check the company website with
  curl from Bash (curl -sIL -m 12 URL; look at final URL after redirects: a redirect to another company's domain usually means acquired).
  WebSearch is capped (cap given in your prompt; shared 200 per turn across all agents); spend it only on the largest-raise rows where status is unclear.
- status_note: max 12 words (e.g. "acquired by Novartis Oct 2025", "now named X", "site redirects to Biogen").
- website: verified homepage URL (http status < 400, or 403/429 bot wall acceptable), else blank.
- category: Biopharma | Tools & Diagnostics | CDMO/CRO | OUT (OUT = medical device, digital health, consumer, veterinary-only,
  cannabis, holding vehicle, SPAC, fund, or not life science).
- modality: short (small molecule, antibody, cell therapy, gene therapy, RNA, radiopharma, platform/AI, tools, diagnostics, CDMO...).
- site_type: HQ (default).
- keep: Y if status in (active, renamed, unknown) and category != OUT; else N.
Do not invent anything; unknown is acceptable. Save progress every 40 rows. Reply under 150 words with counts by status and keep.
