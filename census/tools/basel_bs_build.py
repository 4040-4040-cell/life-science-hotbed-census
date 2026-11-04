import csv

OUT = "/home/claude/census/basel_campus_bs.csv"
H = ["canton","campus","building","street","zip","city","owner_developer","use_type","status",
     "year_delivered_or_due","size_m2","size_basis","lab_share_or_note","anchor_tenants","other_tenants",
     "available_m2","availability_note","footprint_event_2025_26","source_url","second_source_url","notes"]

R = []
def row(**k):
    d = {h: "" for h in H}
    d["canton"] = "BS"; d["city"] = "Basel"
    d.update(k)
    for key in k:
        assert key in H, key
    R.append(d)
    if len(R) % 20 == 0:
        save()

def save():
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=H)
        w.writeheader()
        w.writerows(R)

# ---------------- Novartis Campus (St. Johann) ----------------
row(campus="Novartis Campus (St. Johann)", building="Campus (site level)", street="Lichtstrasse 35", zip="4056",
    owner_developer="Novartis AG", use_type="HQ, R&D labs, offices (multi-building campus)", status="operating",
    lab_share_or_note="Open to third-party life-science companies since 2021; facility and leasing management by ISS Facility Services AG (brochure)",
    anchor_tenants="Novartis",
    other_tenants="FMI (Fabrikstrasse 24); Switzerland Innovation Park Basel Area site (residents incl. CSL Behring, Jura Bio, InsightsMD); Ultragenyx Europe, FoRx Therapeutics, Vaderis Therapeutics (Building WSJ-350) registered at Lichtstrasse 35",
    footprint_event_2025_26="Sep 2 2026: Novartis ends small-scale biologics production in Kleinbasel as leases expire; cell-bank, analytical and technical development labs relocate to the Novartis Campus by end 2027 (up to 130 jobs cut)",
    source_url="https://campus.novartis.com/en/rent-and-work-novartis-campus",
    second_source_url="https://www.switzerland-innovation.com/locations/park-basel-area/site-novartis-campus",
    notes="Breakthrough Properties project on campus NOT verified: btprop.com portfolio lists no Basel asset (checked 2026-11-04). Tenant addresses for Ultragenyx/FoRx/Vaderis from census basel.csv (Zefix/company pages)")
row(campus="Novartis Campus (St. Johann)", building="Building 210", street="Lichtstrasse 35 (campus)", zip="4056",
    owner_developer="Novartis AG", use_type="office (multi-tenant)", status="for lease",
    size_m2="723", size_basis="floor plate per floor (ca.); 17 floors",
    lab_share_or_note="Office only; max floor sub-division ca. 360 m2; ceiling 2.8 m; floor loading 500 kg; fit-out 'as is'",
    availability_note="Marketed to third-party life-science tenants (2026 brochure); vacant area not stated",
    source_url="https://campus.novartis.com/sites/campus_com/files/novartis-campus-brochure_final_2026.pdf",
    second_source_url="https://campus.novartis.com/en/rent-and-work-novartis-campus/your-office-building-210",
    notes="Web page shows average floor size 720 m2 and ceiling 2.8 m; brochure gives 17 floors and ca. 723 m2 floor plate")
row(campus="Novartis Campus (St. Johann)", building="FMI research building", street="Fabrikstrasse 24", zip="4056",
    owner_developer="Novartis AG (converted a former production building for FMI)", use_type="academic/institute R&D labs", status="operating",
    year_delivered_or_due="2024", anchor_tenants="Friedrich Miescher Institute for Biomedical Research (FMI), about 330 staff",
    lab_share_or_note="FMI moved from Rosental site in spring 2024; opening celebrated Aug 23 2024",
    source_url="https://novartis.com/sites/novartis_ch/files/novartis-nachbarschafts-newsletter-oktober-2024.pdf",
    second_source_url="https://www.fmi.ch/about/contact/",
    notes="Floor area not published in sources found")
row(campus="Novartis Campus (St. Johann)", building="Biologics early technical development centre", street="Lichtstrasse 35 (campus)", zip="4056",
    owner_developer="Novartis AG", use_type="R&D labs (biologics technical development)", status="planned",
    year_delivered_or_due="2026 (target set in 2022)",
    lab_share_or_note="About CHF 100M investment announced Sep 12 2022 to replace an existing facility in the Klybeck area by 2026",
    anchor_tenants="Novartis",
    footprint_event_2025_26="Sep 2 2026: Novartis calls the Kleinbasel relocation the next step toward the new biologics technical development centre on campus",
    source_url="https://www.novartis.com/ch-de/news/media-releases/novartis-investiert-rund-chf-100-millionen-ein-neues-zentrum-fuer-biologikaentwicklung-auf-dem-novartis-campus-basel",
    second_source_url="https://www.swissinfo.ch/eng/pharma-supply-chains/novartis-is-cutting-up-to-130-jobs-in-basel/91994515",
    notes="Completion status and building number not confirmed in any source found; status 'planned' is the conservative reading")
row(campus="Novartis Kleinbasel (leased sites, Klybeck area)", building="Novartis Kleinbasel biologics operations (leased buildings)", zip="4057",
    owner_developer="Third-party landlords (not named)", use_type="biologics small-scale production and labs", status="vacating",
    year_delivered_or_due="end 2027",
    lab_share_or_note="Small-scale biologics production halted; cell-bank, analytical and technical development labs move to Novartis Campus",
    anchor_tenants="Novartis",
    footprint_event_2025_26="Sep 2 2026: up to 130 jobs cut by end 2027 because individual Kleinbasel leases expire",
    source_url="https://www.swissinfo.ch/eng/pharma-supply-chains/novartis-is-cutting-up-to-130-jobs-in-basel/91994515",
    second_source_url="https://www.cash.ch/news/novartis-streicht-bis-zu-130-stellen-in-basel-965515",
    notes="Buildings not named in release. Rhystadt (Jun 18 2024) reported Novartis using additional space in WKL-686 on the Klybeck site during the final phase of a construction project (https://www.rhystadt.ch/wp-content/uploads/2024/07/Medienmitteilung_Rhystadt_Entwicklung_240612.pdf)")

# ---------------- Roche Basel site ----------------
ROCHE_ST = "Grenzacherstrasse 124"
row(campus="Roche Basel site (Wettstein)", building="Building 1 (Bau 1)", street=ROCHE_ST, zip="4058",
    owner_developer="F. Hoffmann-La Roche AG", use_type="office", status="operating", year_delivered_or_due="2015",
    size_m2="74200", size_basis="total floor space", lab_share_or_note="Office tower, 41 floors, 178 m; about 2,000 workers; CHF 550M",
    anchor_tenants="Roche",
    source_url="https://www.swissinfo.ch/eng/society/high-flyer_switzerland-s-tallest-building-officially-opened/41669088",
    notes="Inaugurated Sep 18 2015. Owner-occupied; street = Roche Zefix registered address for the site")
row(campus="Roche Basel site (Wettstein)", building="Building 2 (Bau 2)", street=ROCHE_ST, zip="4058",
    owner_developer="F. Hoffmann-La Roche AG", use_type="office", status="operating", year_delivered_or_due="2022",
    size_m2="83000", size_basis="floorspace", lab_share_or_note="Office tower, 50 floors, 205 m; about 3,200 workplaces; CHF 550M",
    anchor_tenants="Roche",
    source_url="https://www.roche.ch/en/media-switzerland/informationen/med-ch-2022-09-02",
    notes="Inaugurated Sep 2 2022; consolidated Roche staff from other Basel locations")
row(campus="Roche Basel site (Wettstein)", building="pRED Center (Building 6 lab tower, second lab tower, office building, convention center)", street=ROCHE_ST, zip="4058",
    owner_developer="F. Hoffmann-La Roche AG", use_type="R&D labs and offices", status="operating", year_delivered_or_due="2024",
    lab_share_or_note="Two high-rise lab buildings (114 m, 72 m) plus office building and convention center; 33 lab/office floors; 150 labs; about 1,000 lab and office workplaces; space for about 1,800 researchers; CHF 1.2B",
    anchor_tenants="Roche Pharma Research and Early Development (pRED)",
    source_url="https://www.roche.com/media/releases/med-cor-2024-09-10",
    second_source_url="https://www.roche.ch/en/media-switzerland/informationen/med-ch-2025-10-29",
    notes="Opened Sep 10 2024. Floor area not stated. Roche Oct 2025 release calls Building 6 'the research and development center that opened last year'. 'Bau 98' from the brief not found in any Roche source")
row(campus="Roche Basel site (Wettstein)", building="Building 12 (Bau 12)", street=ROCHE_ST, zip="4058",
    owner_developer="F. Hoffmann-La Roche AG", use_type="R&D labs and offices", status="under construction", year_delivered_or_due="Q4 2029",
    size_m2="32200", size_basis="building area", lab_share_or_note="15 floors, 72 m; about 450 workplaces; consolidates early R&D functions; CHF 500M; Herzog & de Meuron",
    anchor_tenants="Roche",
    footprint_event_2025_26="Oct 29 2025: groundbreaking of Building 12",
    source_url="https://www.roche.ch/en/media-switzerland/informationen/med-ch-2025-10-29",
    second_source_url="https://www.roche.ch/en/stories/groundbreaking-building12")
row(campus="Roche Basel site (Wettstein)", building="Building 51 Synthetic Molecules Factory (with Building 50 modernisation)", street=ROCHE_ST, zip="4058",
    owner_developer="F. Hoffmann-La Roche AG", use_type="process development and production (synthetic molecules)", status="under construction", year_delivered_or_due="2030",
    lab_share_or_note="CHF 790M across new Building 51 and modernised Building 50; about 200 jobs",
    anchor_tenants="Roche",
    footprint_event_2025_26="Sep 2026: foundation stone laid for Building 51",
    source_url="https://www.s-ge.com/invest/en/articles/news/roche-investing-790-million-swiss-francs-basel",
    notes="Floor area not stated in source")

# ---------------- Klybeck: Rhystadt (Neues Klybeck) ----------------
row(campus="Klybeck: Rhystadt (Neues Klybeck)", building="Rhystadt Klybeck site (site level)", street="Klybeckstrasse 191", zip="4057",
    owner_developer="Rhystadt AG (subsidiary of Central Real Estate Holding AG; Swiss pension funds and insurers); bought from Novartis 2019",
    use_type="mixed industrial site in transformation: labs, offices, studios", status="operating",
    size_m2="160000", size_basis="site area", lab_share_or_note="More than 40 buildings on six plots; about 2,000 people work on site (neuesklybeck.ch)",
    anchor_tenants="Monte Rosa Therapeutics (WKL-136)",
    other_tenants="LifeMine Therapeutics (about 3,900 m2, 2022); Bright Peak Therapeutics (2022); Mycrobez (WKL-136 labs, WKL-675 production); Sintares (WKL-136); Wesemann/RPG Kunststoff/LABCO (lab fit-out); KV Basel school (WKL-147); Novartis (WKL-686, interim)",
    footprint_event_2025_26="Jun 15 2026: Rhystadt launches 'Neues Klybeck' leasing brand; zoning plan to be published early 2027; housing possible from end 2028",
    source_url="https://www.rhystadt.ch/wp-content/uploads/2026/06/Medienmitteilung_Rhystadt-AG-lanciert-Neues-Klybeck.pdf",
    second_source_url="https://www.rhystadt.ch/wp-content/uploads/2022/05/220523_Medienmitteilung_LifeMine-zieht-auf-Areal-der-Rhystadt-AG.pdf",
    notes="Leasing contact on neuesklybeck.ch object pages: JLL (Max Koller). LifeMine and Bright Peak occupancy is as of May 2022; current status not re-verified")
row(campus="Klybeck: Rhystadt (Neues Klybeck)", building="WKL-136", street="Klybeckstrasse 191", zip="4057",
    owner_developer="Rhystadt AG", use_type="lab and office", status="for lease", year_delivered_or_due="mid-1980s (built for Ciba)",
    lab_share_or_note="Functionally fitted lab and office space on six floors; ceiling height 3.2 m; asking rent CHF 220/m2 p.a.",
    anchor_tenants="Monte Rosa Therapeutics (44,685 sq ft office and lab; lease extended Mar 2026 to Jun 30 2028)",
    other_tenants="Mycrobez; Sintares AG (since May 2025, R&D and admin); Rhystadt AG offices",
    available_m2="2600", availability_note="Stated 'rund 2,600 m2' on 1st and 2nd floors, units from 90 m2; listed units 1,590 m2 office/lab (1st floor), 173 m2 office and 696 m2 lab (2nd floor); available immediately",
    footprint_event_2025_26="Mar 2026: Monte Rosa extends Klybeckstrasse 191 lease from Jun 30 2027 to Jun 30 2028 (SEC 10-Q)",
    source_url="https://neuesklybeck.ch/de/objekte/gebaeude-136",
    second_source_url="https://www.sec.gov/Archives/edgar/data/1826457/000119312526336711/glue-20260630.htm",
    notes="Monte Rosa space: 21,422 sq ft from Mar 2021, increased to 44,685 sq ft in Apr 2023; landlord named in 10-Q is Wincasa AG. Brief's 'Monte Rosa until 2027' is superseded by the Mar 2026 extension")
row(campus="Klybeck: Rhystadt (Neues Klybeck)", building="WKL-135", street="Klybeckstrasse 191 (site address)", zip="4057",
    owner_developer="Rhystadt AG; architect Herzog & de Meuron", use_type="multi-tenant lab (refurbishment and extension)", status="planned",
    year_delivered_or_due="mid-2028",
    lab_share_or_note="1980s Ciba lab building, out of use since 2023; gutted to concrete frame, side extension plus three added storeys in timber; lettable from 200 m2 units or by floor from 2,250 m2; LEED Gold targeted",
    footprint_event_2025_26="Mar 31 2025: building permit application filed",
    source_url="https://www.rhystadt.ch/wp-content/uploads/2025/03/250331_Medienmitteilung_Baugesuch.pdf",
    second_source_url="https://www.rhystadt.ch/wp-content/uploads/2025/05/250505_Medienmitteilung_Sintares.pdf",
    notes="Total floor area not stated. Permit grant and construction start not confirmed in sources found. Sources do not state whether WKL-135 is the same project as FLOW")
row(campus="Klybeck: Rhystadt (Neues Klybeck)", building="FLOW", street="Klybeck site (Rhystadt part)", zip="4057",
    owner_developer="Rhystadt AG", use_type="lab and office (life sciences)", status="planned",
    year_delivered_or_due="end 2029",
    size_m2="19000", size_basis="lab and office space (approx., 'rund')",
    lab_share_or_note="Targets life-science companies; marketed under Neues Klybeck",
    availability_note="Pre-leasing via neuesklybeck.ch",
    footprint_event_2025_26="Jun 15 2026: FLOW announced as first Neues Klybeck commercial project, ready from end 2029",
    source_url="https://www.rhystadt.ch/wp-content/uploads/2026/06/Medienmitteilung_Rhystadt-AG-lanciert-Neues-Klybeck.pdf",
    second_source_url="https://www.immo-invest.ch/en/klybeck-wird-schon-vor-dem-wohnstart-vermarktet/",
    notes="Brief described a '19,000 sqm lab building opening mid-2028'; sources give 19,000 m2 for FLOW with end-2029 occupancy, and mid-2028 for WKL-135 (size not stated). Treated as two rows; possible overlap unresolved")
row(campus="Klybeck: Rhystadt (Neues Klybeck)", building="WKL-132", street="Klybeckstrasse 191", zip="4057",
    owner_developer="Rhystadt AG", use_type="office", status="for lease",
    lab_share_or_note="Office only; newest building on the Rhystadt part; ca. 1,000 m2 per floor; asking rent CHF 200/m2 p.a.",
    available_m2="4168", availability_note="Floors 3 to 6, 1,042 m2 each, fully fitted, available immediately",
    source_url="https://neuesklybeck.ch/de/objekte/gebaeude-132",
    second_source_url="https://www.rhystadt.ch/wp-content/uploads/2024/07/Medienmitteilung_Rhystadt_Entwicklung_240612.pdf",
    notes="Included because marketed inside the Klybeck life-science cluster; no lab")

# ---------------- Klybeck: Swiss Life (Campus Klybeck) ----------------
row(campus="Klybeck: Swiss Life (Campus Klybeck)", building="Campus Klybeck (site level)", street="Klybeckstrasse 141", zip="4057",
    owner_developer="Swiss Life (acquired former BASF part of Klybeck in 2019); Swiss Life Asset Management AG",
    use_type="mixed: offices, labs, commercial", status="operating",
    lab_share_or_note="K-25, K-141 and K-410 offer about 15,400 m2 office, commercial and lab space",
    anchor_tenants="BASF Schweiz AG; IOB (K-420)",
    other_tenants="Walter Klybeck (co-working and labs); The 5th Floor (K-141 co-working); Swiss Life Asset Managers; Bricks; Apleona (K-25 from Nov 2026); Praxis im Klybeck (since Mar 2026); fair fashion factory",
    available_m2="15400", availability_note="Stated 'rund 15,400 m2' ready across K-25 (4,300), K-141 (8,048), K-410 (3,100) as of Sep 17 2026",
    footprint_event_2025_26="Nov 26 2025: klybeckplus Richtprojekt published by Swiss Life, Rhystadt and Canton Basel-Stadt",
    source_url="https://www.campus-klybeck.ch/de/2026/09/17/diese-flaechen-sind-heute-schon-im-klybeck-verfuegbar/",
    second_source_url="https://www.campus-klybeck.ch/de/2025/11/27/medienmitteilung-zum-richtprojekt-klybeckplus-veroeffentlicht/",
    notes="K-141 is the listed former BASF HQ (over 100 tenants, mostly non-life-science); not given its own row")
row(campus="Klybeck: Swiss Life (Campus Klybeck)", building="K-410", street="Klybeckstrasse 206", zip="4057",
    owner_developer="Swiss Life; lab operator Walter Klybeck", use_type="lab and office (shared and private labs)", status="under construction",
    year_delivered_or_due="2026",
    size_m2="3100", size_basis="total area (UG to 6th floor), lab and office",
    lab_share_or_note="Refurbishment of existing building into flexible shared and private lab space for life sciences",
    available_m2="3100", availability_note="Listed as available lab and office space (Sep 2026); renovation 'in vollem Gange'",
    footprint_event_2025_26="2026: Walter Klybeck fitting out K-410 labs",
    source_url="https://www.campus-klybeck.ch/de/2026/09/17/diese-flaechen-sind-heute-schon-im-klybeck-verfuegbar/",
    second_source_url="https://www.campus-klybeck.ch/de")
row(campus="Klybeck: Swiss Life (Campus Klybeck)", building="K-420", zip="4057",
    owner_developer="Swiss Life", use_type="institute R&D labs", status="operating",
    anchor_tenants="IOB, Institute of Molecular and Clinical Ophthalmology Basel",
    lab_share_or_note="Campus map lists K-420 as 'Labor' occupied by IOB",
    source_url="https://www.campus-klybeck.ch/de",
    second_source_url="https://www.srf.ch/news/baumschutz-statt-forschung-alte-baeume-stehen-neuem-augen-forschungszentrum-im-weg",
    notes="SRF (Mar 2019) reported IOB renting on the Klybeck site as a provisional solution after a planned new building at the eye clinic fell through. Street number and area not published")
row(campus="Klybeck: Swiss Life (Campus Klybeck)", building="K-25", street="Klybeckstrasse 161", zip="4057",
    owner_developer="Swiss Life", use_type="office, storage, commercial (co-working and lab provider on site)", status="for lease",
    size_m2="4300", size_basis="total area (UG to 5th floor)",
    lab_share_or_note="Refurbished historic building, DGNB Gold; Walter Klybeck offices in operation since Mar 2025",
    anchor_tenants="BASF Schweiz AG; Walter Klybeck",
    other_tenants="Praxis im Klybeck (Mar 2026); Apleona Schweiz AG (from Nov 2026)",
    availability_note="Listed among 15,400 m2 available across K-25, K-141, K-410; vacancy within K-25 not separated",
    source_url="https://www.campus-klybeck.ch/de/2026/09/17/diese-flaechen-sind-heute-schon-im-klybeck-verfuegbar/")
row(campus="Klybeck (klybeckplus)", building="klybeckplus transformation area (whole Klybeck)", zip="4057",
    owner_developer="Planning partners Canton Basel-Stadt, Rhystadt AG, Swiss Life", use_type="mixed-use district plan (incl. life-science commercial)", status="planned",
    year_delivered_or_due="2040",
    lab_share_or_note="Space for 8,500 residents and 7,500 jobs by 2040",
    footprint_event_2025_26="Nov 26 2025: Richtprojekt published; zoning plan public early 2027 (Neues Klybeck FAQ)",
    source_url="https://www.rhystadt.ch",
    second_source_url="https://www.campus-klybeck.ch/de/2025/11/27/medienmitteilung-zum-richtprojekt-klybeckplus-veroeffentlicht/")

# ---------------- Rosental Mitte ----------------
RM = "Rosental Mitte (Canton Basel-Stadt)"
RMO = "Canton Basel-Stadt (Immobilien Basel-Stadt)"
row(campus=RM, building="Rosental Mitte (site level)", street="Mattenstrasse 22", zip="4058",
    owner_developer=RMO, use_type="research and lab district in transformation", status="operating",
    lab_share_or_note="Former Geigy/chemical-industry research site; phased opening and conversion to mixed district",
    anchor_tenants="Universität Basel; Syngenta Crop Protection",
    other_tenants="Celonic AG; Pattern BioSciences; Solvias; SpiroChem; Ten23 health; Elanco Tiergesundheit; BASF Schweiz; Clear Solutions Laboratories; GeneusChem; Therapeomic; cryoWrite; Agrexis; Westhive; others",
    footprint_event_2025_26="May 26 2026: Government Council submits CHF 149.37M (gross) spending request for University Chemistry fit-out in Haus 6",
    source_url="https://rosentalmitte.ch/de/rosental-mitte/firmenverzeichnis",
    second_source_url="https://rosentalmitte.ch/de/mieten",
    notes="All leasing listings use Mattenstrasse 22, 4058 Basel")
row(campus=RM, building="RO-1055", street="Mattenstrasse 22", zip="4058",
    owner_developer=RMO, use_type="office, lab and storage (multi-tenant)", status="for lease", year_delivered_or_due="1959",
    lab_share_or_note="2 basements, ground plus 7 floors; renovation ongoing; freight lift 4,000 kg for chemicals; central compressed air, vacuum, demineralised water; floor load up to 2,000 kg/m2",
    other_tenants="Solvias AG; Therapeomic AG; cryoWrite AG; Agrexis AG; GALVITA AG; Superabsorbent Technologies AG; TÜV SÜD Schweiz AG; Ayron Energy; Filtertec; MAPEI Suisse; Apleona; Veolia; Sunrise; Schachenmann; Selmoni",
    availability_note="Offices 30 to 2,700 m2 and storage 50 to 350 m2 offered (ranges; no single vacancy figure); rent on request",
    source_url="https://rosentalmitte.ch/de/mieten/RO-1055",
    second_source_url="https://rosentalmitte.ch/de/rosental-mitte/firmenverzeichnis")
row(campus=RM, building="RO-1059", street="Mattenstrasse 22", zip="4058",
    owner_developer=RMO, use_type="lab and office (biology BSL1/2 and chemistry labs)", status="for lease", year_delivered_or_due="1988 (renovated 2021)",
    lab_share_or_note="2 basements plus 8 floors; biology labs 50 to 75 m2 per lab (BSL1/2), chemistry labs 75 m2 with 6 to 8 fume hoods; shared lab equipment room; chemicals exchange run by BASF",
    anchor_tenants="Universität Basel; BASF Schweiz AG",
    other_tenants="Idemitsu OLED Materials Europe; Clear Solutions Laboratories; GeneusChem; AUE BS environmental lab; HTP HiTech Photopolymere; Jay Chemical; Metafuels; SAMSON Controls; IWB",
    availability_note="Biology labs 75 to 1,300 m2, chemistry labs 50 to 250 m2, lab ancillary 10 to 300 m2, offices 15 to 1,000 m2, storage 10 to 500 m2 offered (ranges); rent on request",
    source_url="https://rosentalmitte.ch/de/mieten/RO-1059",
    second_source_url="https://rosentalmitte.ch/de/rosental-mitte/firmenverzeichnis")
row(campus=RM, building="Building 1060", street="Mattenstrasse 22", zip="4058",
    owner_developer=RMO, use_type="lab (biomanufacturing and R&D)", status="operating",
    anchor_tenants="Celonic AG", other_tenants="Pattern BioSciences AG; Universität Basel",
    source_url="https://rosentalmitte.ch/de/rosental-mitte/firmenverzeichnis",
    notes="Building assignment from site company directory; area not published. Celonic is the brief's 'Celonic site'")
row(campus=RM, building="Building 1047 / 1047a", street="Mattenstrasse 22", zip="4058",
    owner_developer=RMO, use_type="lab and office", status="operating",
    anchor_tenants="SpiroChem AG (1047)", other_tenants="Apleona Schweiz AG (1047a)",
    source_url="https://rosentalmitte.ch/de/rosental-mitte/firmenverzeichnis",
    second_source_url="https://rosentalmitte.ch",
    notes="SpiroChem (chemistry CRO) quoted on rosentalmitte.ch as growing on site")
row(campus=RM, building="Building 1094", street="Mattenstrasse 22", zip="4058",
    owner_developer=RMO, use_type="lab (pharma development services)", status="operating",
    anchor_tenants="Ten23 health AG",
    source_url="https://rosentalmitte.ch/de/rosental-mitte/firmenverzeichnis")
row(campus=RM, building="Buildings 1095 and 1096", street="Mattenstrasse 22", zip="4058",
    owner_developer=RMO, use_type="university labs and offices", status="operating",
    anchor_tenants="Universität Basel", other_tenants="SWISSFM AG (1095)",
    source_url="https://rosentalmitte.ch/de/rosental-mitte/firmenverzeichnis",
    notes="University also in 1059 and 1060")
row(campus=RM, building="Building 1032", street="Mattenstrasse 24A (Elanco registered address)", zip="4058",
    owner_developer=RMO, use_type="office and services", status="operating",
    anchor_tenants="Elanco Tiergesundheit AG", other_tenants="Sanacare AG; Physio 23 GmbH",
    source_url="https://rosentalmitte.ch/de/rosental-mitte/firmenverzeichnis",
    second_source_url="https://bs.chregister.ch/cr-portal/auszug/auszug.xhtml?uid=CHE-206.040.619",
    notes="Street from Zefix for Elanco Europe GmbH (census basel.csv); building-to-street mapping not confirmed by site owner")
row(campus=RM, building="Buildings 1004, 1006, 1007, 1008", street="Mattenstrasse 22", zip="4058",
    owner_developer=RMO, use_type="lab and office (agrochemical R&D)", status="operating",
    anchor_tenants="Syngenta Crop Protection AG (1004, 1006, 1007)", other_tenants="SV (Schweiz) AG (1006, 1008)",
    source_url="https://rosentalmitte.ch/de/rosental-mitte/firmenverzeichnis",
    notes="Crop science, not human life science; kept because it occupies competing lab stock")
row(campus=RM, building="Haus 6 (lab new build)", zip="4058",
    owner_developer=RMO + "; tenant fit-out for University of Basel", use_type="lab and office (university chemistry plus third parties)", status="under construction",
    year_delivered_or_due="ca. Q2 2033",
    size_m2="33461", size_basis="gross floor area (Geschossfläche, SIA 416)",
    lab_share_or_note="Rental area 15,954 m2 (SBFI basis): University 12,177 m2, third parties 3,777 m2. University main usable area ca. 9,700 m2 (lab 6,579 m2). Typical floor ca. 2,700 m2 with ca. 1,500 m2 lab per floor; 7 storeys above ground, 4 basements; 167 parking spaces let to third parties. Construction cost CHF 254.3M (Apr 2025 price basis)",
    anchor_tenants="University of Basel, Department of Chemistry",
    availability_note="3,777 m2 earmarked for third-party tenants (no letting status published)",
    footprint_event_2025_26="Jul 2 2025: building permit filed. May 26 2026: Government Council requests CHF 149.37M gross (CHF 127.37M net) for university fit-out; Haus 6 becomes permanent Chemistry site",
    source_url="https://grosserrat.bs.ch/dokumente/100412/000000412700.pdf",
    second_source_url="https://www.bs.ch/regierungsratsbeschluesse/P260523",
    notes="Excavation and soil remediation under way, to finish Q3 2028; completion and occupancy ca. Q2 2033 (Jan 2026 schedule). unigeschichte.unibas.ch still says occupancy from 2029 (older). Brief's '13,150 m2 with 10,000 m2 for Chemistry' does not match the Ratschlag figures; Ratschlag used")
row(campus="University of Basel (Spiegelhof / St. Johann)", building="St. Johanns-Ring 19 (current Department of Chemistry)", street="St. Johanns-Ring 19", zip="4056",
    owner_developer="Canton Basel-Stadt (university building)", use_type="university chemistry labs", status="vacating",
    year_delivered_or_due="ca. 2033 (on Haus 6 occupancy)",
    lab_share_or_note="1950s building past its useful life; houses most Chemistry labs; replacement on Baufeld 4 rejected in 2023 evaluation",
    anchor_tenants="University of Basel, Department of Chemistry",
    source_url="https://www.bs.ch/api/government-resolutions/document/c44f233e125b44378fa817b6336a1439-332/3/Dokument",
    second_source_url="https://grosserrat.bs.ch/dokumente/100412/000000412700.pdf",
    notes="Future use of the building not stated")

# ---------------- Stücki Park ----------------
SP = "Stücki Park (Swiss Prime Site)"
SPO = "Swiss Prime Site Immobilien AG"
row(campus=SP, building="Stücki Business Park (site level)", street="Hochbergerstrasse 60", zip="4057",
    owner_developer=SPO, use_type="lab and office business park with retail/leisure park", status="operating",
    size_m2="60000", size_basis="office and lab space after expansion (from 27,000 m2)",
    lab_share_or_note="About 4,000 jobs on site after Stücki Park II; offices 59 to 810 m2 marketed; property management Wincasa AG",
    anchor_tenants="Lonza; Medartis; Boehringer Ingelheim / NBE-Therapeutics",
    other_tenants="Superlab Suisse; Skyhawk Therapeutics; BioVersys; Anaveon; TECregen; Bottmedical",
    footprint_event_2025_26="Apr 3 2025: Boehringer Ingelheim opened NBE ADC R&D centre (1,826 m2, CHF 27M) at Hochbergerstrasse 60i",
    source_url="https://sps.swiss/en/group/investors/company-reports/2022/stories/stuecki-park/story",
    second_source_url="https://www.stueckipark.ch/de/business-park-basel/")
row(campus=SP, building="Stücki Park II (four 'finger' buildings)", street="Hochbergerstrasse 60", zip="4057",
    owner_developer=SPO + "; Blaser Architekten", use_type="lab and office", status="operating",
    year_delivered_or_due="2024", size_m2="28000", size_basis="usable floor space",
    lab_share_or_note="Three lab/research buildings and one office building on shared 3-level basement; SGNI (DGNB) Gold; about 1,700 added jobs",
    anchor_tenants="Superlab Suisse",
    source_url="https://sps.swiss/en/stories/story-detail/stuecki-park-ii-a-piece-more-laboratory",
    second_source_url="https://sps.swiss/en/group/investors/company-reports/2022/stories/stuecki-park/story",
    notes="SPS 2022 report describes the expansion as four new buildings, first two (8,000 m2 each) completed end 2020 (one let to Lonza), two more due end 2024. SPS Dec 2024 story gives 28,000 m2 usable for 'Stücki Park II', construction 2020 to 2023. Whether the 2020 buildings are inside the 28,000 m2 is not stated; do not add the Lonza row to this total")
row(campus=SP, building="Lonza building (first expansion building)", street="Hochbergerstrasse 60", zip="4057",
    owner_developer=SPO, use_type="lab and office (QC, bioanalytics, drug product services)", status="operating",
    year_delivered_or_due="2020", size_m2="8000", size_basis="surface area (per SPS 2022 report)",
    anchor_tenants="Lonza (Drug Product Services)",
    lab_share_or_note="Lonza completed a 6,000 m2 QC and bioanalytics lab and office expansion at its Basel DPS site in Oct 2024 (census basel.csv, pharmasource)",
    source_url="https://sps.swiss/en/group/investors/company-reports/2022/stories/stuecki-park/story",
    second_source_url="https://pharmasource.global/content/news/cdmo-news/lonza-completes-6000m%C2%B2-expansion-for-qc-and-bioanalytics-in-basel/",
    notes="Brief mentions 'Lonza two buildings of 8,000 m2 each'; SPS 2022 says two 8,000 m2 buildings, one occupied by Lonza and one fitted as flexible offices/meeting rooms. Building letter not published")
row(campus=SP, building="Tech Park Basel (linear building, 2011)", street="Hochbergerstrasse 60C (tenant registered address)", zip="4057",
    owner_developer=SPO + " (building); park opened by Canton Basel-Stadt", use_type="startup labs and offices", status="operating",
    year_delivered_or_due="2011",
    lab_share_or_note="Technology park for life sciences, nanotech, ICT and cleantech startups; long linear building also houses Lonza and Medartis (SPS)",
    other_tenants="BioVersys; Anaveon; TECregen (all registered at Hochbergerstrasse 60C)",
    available_m2="522", availability_note="Hochbergerstrasse 60C level 6: 522 m2 fully fitted office at CHF 230/m2 (stueckipark.ch, Nov 2026)",
    source_url="https://sps.swiss/en/group/investors/company-reports/2022/stories/stuecki-park/story",
    second_source_url="https://www.stueckipark.ch/de/gewerbeflaechen-mieten/labor-mieten/",
    notes="Mapping of 60C to the Tech Park building rests on census tenant notes (Technologiepark Basel); techparkbasel.ch did not load")
row(campus=SP, building="Superlab Suisse Basel (lab-as-a-service)", street="Hochbergerstrasse 60", zip="4057",
    owner_developer=SPO + "; operator Superlab Suisse", use_type="turnkey BSL1/2 labs (lab-as-a-service)", status="operating",
    year_delivered_or_due="2024", size_m2="4770", size_basis="lab space (over 4,770 m2)",
    anchor_tenants="Skyhawk Therapeutics (early tenant)",
    lab_share_or_note="Opened Jul 12 2024 in Stücki Park II",
    source_url="https://startupticker.ch/en/news/superlab-suisse-opens-5000-square-meters-lab-space-in-basel",
    second_source_url="https://www.stueckipark.ch",
    notes="Exact building letter not published; Skyhawk Europe registered at Hochbergerstrasse 60i (Zefix)")
row(campus=SP, building="Hochbergerstrasse 60A", street="Hochbergerstrasse 60A", zip="4057",
    owner_developer=SPO, use_type="lab and office", status="for lease",
    available_m2="901", availability_note="Level 7: 901 m2 BSL2 fully fitted lab at CHF 590/m2 net; occupancy by agreement",
    source_url="https://www.stueckipark.ch/de/gewerbeflaechen-mieten/labor-mieten/")
row(campus=SP, building="Hochbergerstrasse 60B", street="Hochbergerstrasse 60B", zip="4057",
    owner_developer=SPO, use_type="lab and office", status="for lease",
    anchor_tenants="Boehringer Ingelheim (Schweiz) GmbH (registered address)",
    availability_note="Listed units: level 1+2 399 m2 lab in shell at CHF 160; level 4 415 m2 fitted office at CHF 230; level 5 396 m2 fitted office at CHF 240 (no total stated)",
    source_url="https://www.stueckipark.ch/de/gewerbeflaechen-mieten/labor-mieten/",
    second_source_url="https://bs.chregister.ch/cr-portal/auszug/auszug.xhtml?uid=CHE-153.827.725",
    notes="BI registration at 60B per census basel.csv notes")
row(campus=SP, building="Hochbergerstrasse 60E", street="Hochbergerstrasse 60E", zip="4057",
    owner_developer=SPO, use_type="HQ office and production-related operations (medtech)", status="operating",
    anchor_tenants="Medartis Holding AG (HQ)",
    source_url="https://www.medartis.com/contact")
row(campus=SP, building="Hochbergerstrasse 60i (NBE ADC R&D centre)", street="Hochbergerstrasse 60i", zip="4057",
    owner_developer=SPO, use_type="R&D lab and office (ADC)", status="operating", year_delivered_or_due="2025",
    size_m2="1826", size_basis="lab and office (tenant premises)",
    anchor_tenants="Boehringer Ingelheim / NBE-Therapeutics AG", other_tenants="Skyhawk Therapeutics Europe GmbH (registered address)",
    footprint_event_2025_26="Apr 3 2025: NBE ADC R&D centre opened, CHF 27M",
    source_url="https://www.boehringer-ingelheim.com/science-innovation/human-health-innovation/new-nbe-therapeutics-antibody-drug-conjugate-rd-center",
    second_source_url="https://bs.chregister.ch/cr-portal/auszug/auszug.xhtml?uid=CHE-153.827.725")

# ---------------- University / institutes ----------------
row(campus="Schällemätteli Life Sciences Campus (University of Basel)", building="Biozentrum new building", street="Spitalstrasse 41", zip="4056",
    owner_developer="Cantons Basel-Stadt and Basel-Landschaft (joint project) for University of Basel; Ilg Santer Architekten", use_type="academic R&D labs, lecture halls", status="operating",
    year_delivered_or_due="2021", size_m2="23400", size_basis="floorspace",
    lab_share_or_note="16 above-ground and 3 basement levels, 72 m; 32 to 40 research groups, about 400 scientists; lecture space for 900 students; planned budget CHF 340M with overruns of about CHF 100M",
    anchor_tenants="Biozentrum, University of Basel", other_tenants="University of Basel IT Services",
    source_url="https://www.unibas.ch/en/News-Events/News/Uni-Info/Official-opening-of-the-new-Biozentrum-building.html",
    second_source_url="https://unigeschichte.unibas.ch/en/first-menu/behausungen-und-orte/bauboom-20/life-science-campus-20",
    notes="Completed Sep 2021 per unigeschichte. Brief's 'CHF 430m+' not stated as such in sources: CHF 340M budget plus about CHF 100M overrun")
row(campus="Schällemätteli Life Sciences Campus (University of Basel)", building="ETH Zurich D-BSSE BSS building", street="Klingelbergstrasse 48", zip="4056",
    owner_developer="ETH Zurich; contractor Implenia", use_type="academic R&D labs (biosystems)", status="operating",
    year_delivered_or_due="2023", size_m2="36000", size_basis="floor area",
    lab_share_or_note="18,900 m2 main usable space",
    anchor_tenants="ETH Zurich Department of Biosystems Science and Engineering (D-BSSE)",
    source_url="https://implenia.com/en/references/detail/ref/neubau-bss-des-departements-fuer-biosysteme-basel/",
    second_source_url="https://implenia.com/referenzen/detail/ref/neubau-bss-des-departements-fuer-biosysteme-basel/pdf",
    notes="Completion May 2023 per census basel.csv (Implenia)")
row(campus="Schällemätteli Life Sciences Campus (University of Basel)", building="Department of Biomedicine (DBM) new building", zip="4056",
    owner_developer="University of Basel (developer); Burckhardt+Partner; contractor Implenia", use_type="academic biomedical R&D labs", status="under construction",
    year_delivered_or_due="2028 (building) / 2031 (operational)",
    lab_share_or_note="Two basements and nine upper floors on the site of the old Biozentrum; CHF 365M; about 70 research groups, 900 staff, up to 200 students (unigeschichte) / about 700 researchers from 2030/2031 (Keystone-SDA)",
    anchor_tenants="University of Basel, Department of Biomedicine",
    footprint_event_2025_26="May 23 2025: foundation stone laid",
    source_url="https://www.swissinfo.ch/eng/healthcare-innovation/foundation-stone-laid-for-new-%e2%82%ac365-million-building-for-biomedicine-in-basel/89405105",
    second_source_url="https://unigeschichte.unibas.ch/en/first-menu/behausungen-und-orte/bauboom-20/life-science-campus-20/neubau-biomedizin",
    notes="Consolidates DBM from five sites (Mattenstrasse 28, Pestalozzistrasse 20, Petersplatz 10, Klingelbergstrasse 50, ZLF), which will be vacated; cantonal loan guarantee raised from CHF 106M to 182.5M in 2023. Floor area not found. Street not stated in sources")
row(campus="University Hospital Basel (Campus Gesundheit)", building="Klinikum 2 replacement, stage 1", street="Petersgraben 4 (hospital address)", zip="4031",
    owner_developer="Universitätsspital Basel", use_type="hospital with clinical research", status="under construction",
    year_delivered_or_due="2033",
    lab_share_or_note="Groundbreaking Jan 22 2024; stage 2 planned 2035 to 2042; Klinikum 3 new build dropped after Claraspital takeover",
    anchor_tenants="Universitätsspital Basel",
    source_url="https://www.bs.ch/schwerpunkte/arealentwicklungen-im-kanton-basel-stadt/universitaetsspital-basel-campus-gesundheit",
    second_source_url="https://unispital-basel.ch/dam/jcr:17c5bf46-2605-436e-8fcb-f1bdb2ead8bd/240507%20Neubau%20Klinikum%202.pdf",
    notes="Floor area and research-lab share not stated")

# ---------------- CBD offices used by life-science companies ----------------
row(campus="Basel SBB / Elsässertor", building="Elsässertor", street="Centralbahnstrasse 4", zip="4051",
    use_type="office (pharma HQ)", status="vacating", year_delivered_or_due="Jan 2028",
    anchor_tenants="Sandoz Group AG (global HQ)",
    footprint_event_2025_26="Jun 30 2026: Sandoz to consolidate global HQ (Elsässertor) and Swiss HQ (Rotkreuz) into Helvetia Campus east tower from Jan 2028",
    source_url="https://www.zug4you.ch/en/news/news-articles/a/sandoz-to-leave-canton-zug",
    second_source_url="https://bs.chregister.ch/cr-portal/auszug/auszug.xhtml?uid=CHE-433.164.136",
    notes="Owner not identified in sources used. Sandoz Basel HQ lease was up for renewal (zug4you)")
row(campus="St. Alban / Helvetia Campus", building="Helvetia Campus east tower", street="St. Alban-Anlage", zip="4052",
    owner_developer="Helvetia Baloise; Herzog & de Meuron (campus design)", use_type="office (pharma HQ)", status="planned",
    year_delivered_or_due="Jan 2028 (Sandoz occupancy)",
    anchor_tenants="Sandoz Group AG (long-term lease with renewal options)",
    lab_share_or_note="Existing Helvetia tower; Helvetia staff move out to Baloise Park, Aeschengraben, by spring 2027",
    footprint_event_2025_26="Jun 30 2026: Sandoz signs long-term lease for east tower",
    source_url="https://www.zug4you.ch/en/news/news-articles/a/sandoz-to-leave-canton-zug",
    second_source_url="https://www.moneycab.com/?p=1030499",
    notes="Street number and tower area not stated; zug4you places the campus at St. Alban-Graben/St. Alban-Anlage. Sandoz has about 420 Swiss employees")
row(campus="Basel SBB / Peter Merian", building="Peter Merian-Weg 12", street="Peter Merian-Weg 12", zip="4002",
    use_type="office (medtech HQ)", status="operating",
    anchor_tenants="Straumann Holding AG / Institut Straumann AG",
    footprint_event_2025_26="Straumann named anchor of planned Medtech Innovation Hub Baselland in Arlesheim (BL), bundling 760 employees; canton funding 2026 to 2029 (article undated)",
    source_url="https://bs.chregister.ch/cr-portal/auszug/auszug.xhtml?uid=CHE-101.673.828",
    second_source_url="https://www.technik-und-wissen.ch/uptownbasel-waechst-weiter-jetzt-mit-medtech-hub-und-straumann.html",
    notes="Whether Peter Merian-Weg 12 is vacated is not stated")
row(campus="Basel SBB / Peter Merian", building="Peter Merian-Weg 10", street="Peter Merian-Weg 10", zip="4052",
    use_type="office", status="operating", anchor_tenants="Moderna Switzerland GmbH",
    source_url="https://bs.chregister.ch/cr-portal/auszug/auszug.xhtml?uid=CHE-344.522.989")
row(campus="Basel SBB / Peter Merian", building="Peter Merian-Strasse 84", street="Peter Merian-Strasse 84", zip="4052",
    use_type="office (pharma/consumer health hub)", status="operating", anchor_tenants="Bayer Consumer Care AG (Bayer Basel hub)",
    lab_share_or_note="Basel workforce about 1,000 (Bayer/Fierce 2024)",
    source_url="https://www.bayer.com/en/switzerland/about-us/sites/basel",
    second_source_url="https://bs.chregister.ch/cr-portal/auszug/auszug.xhtml?uid=CHE-107.359.454")
row(campus="Basel SBB / Peter Merian", building="Peter Merian-Strasse 90", street="Peter Merian-Strasse 90", zip="4052",
    use_type="office", status="operating", anchor_tenants="Pierre Fabre Pharma SA",
    source_url="https://bs.chregister.ch/cr-portal/auszug/auszug.xhtml?uid=CHE-105.969.179")
row(campus="Aeschen / Grosspeter", building="Grosspeteranlage 29", street="Grosspeteranlage 29", zip="4052",
    use_type="office (multi-tenant)", status="operating",
    anchor_tenants="Regeneron Switzerland GmbH", other_tenants="Dr. Reddy's Laboratories SA; Camlog Biotechnologies GmbH",
    source_url="https://bs.chregister.ch/cr-portal/auszug/auszug.xhtml?uid=CHE-426.698.987",
    second_source_url="https://bs.chregister.ch/cr-portal/auszug/auszug.xhtml?uid=CHE-113.571.287")
row(campus="Aeschen / Grosspeter", building="Aeschenplatz 6", street="Aeschenplatz 6", zip="4052",
    use_type="office (biotech HQ)", status="operating", anchor_tenants="Windward Bio",
    source_url="https://windwardbio.com/contact")
row(campus="Aeschen / Grosspeter", building="Aeschenvorstadt 36", street="Aeschenvorstadt 36", zip="4051",
    use_type="office (biotech)", status="operating",
    anchor_tenants="Ironwood Pharmaceuticals GmbH (former VectivBio)", other_tenants="Granite Bio",
    source_url="https://bs.chregister.ch/cr-portal/auszug/auszug.xhtml?uid=CHE-434.388.253",
    second_source_url="https://www.granitebio.com/contact")
row(campus="Aeschen / Grosspeter", building="Aeschengraben 27", street="Aeschengraben 27", zip="4051",
    use_type="office (biopharma HQ)", status="operating", anchor_tenants="BeOne Medicines (21st floor)",
    source_url="https://data.sec.gov/submissions/CIK0001651308.json")
row(campus="Old Town", building="Barfüsserplatz 3", street="Barfüsserplatz 3", zip="4051",
    use_type="office (biotech)", status="operating",
    anchor_tenants="Acadia Pharmaceuticals GmbH", other_tenants="Noema Pharma",
    source_url="https://bs.chregister.ch/cr-portal/auszug/auszug.xhtml?uid=CHE-435.458.844",
    second_source_url="https://www.zefix.admin.ch/en/search/entity/list/firm/1444973")
row(campus="Old Town", building="Erasmushaus", street="Bäumleingasse 18", zip="4051",
    use_type="office (shared address for biotech)", status="operating",
    anchor_tenants="Nouscom", other_tenants="Nuclidium",
    source_url="https://www.zefix.admin.ch/en/search/entity/list/firm/1210307",
    second_source_url="https://www.zefix.admin.ch/en/search/entity/list/firm/1298847",
    notes="Census notes describe Bäumleingasse 18 as a shared registered address; Nouscom main R&D in Rome")
row(campus="Kleinbasel (Rosental / Erlenmatt)", building="Hammerstrasse 44", street="Hammerstrasse 44", zip="4058",
    use_type="pharma R&D (registered purpose)", status="operating", anchor_tenants="BioNTech Switzerland GmbH",
    source_url="https://bs.chregister.ch/cr-portal/auszug/auszug.xhtml?uid=CHE-189.526.416",
    notes="Site size not found")

save()
print(len(R), "rows written to", OUT)
