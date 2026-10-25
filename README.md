# Student employment analysis

Open **index.html** to begin. Each HTML visualization contains its own data and libraries and works offline. The navigation links work when the folder structure is preserved. Individual HTML files can also be copied and opened independently.

## Main findings
- The source contains 1,613 students and 1,689 appointment records concerning 931 students. The other 682 students have no career record in the supplied file; this does not establish unemployment.
- Academic/education accounts for 495 appointments (29.3%), government/public administration for 330 (19.5%), industry/manufacturing/extraction for 209 (12.4%), and military/defense for 186 (11.0%). People can appear in several sectors.
- The United States accounts for 849 appointments (50.3%) and China for 815 (48.3%). These counts include past and current appointments.
- There are 710 current, 969 past and 10 unknown-status appointments. “Current” refers to the historical source, not the present day.
- Career-record coverage differs by gender: 108/312 female students (34.6%) and 823/1,301 male students (63.3%). Differences in documentation coverage must be considered when comparing their recorded jobs; these are not employment rates.
- Only 488/1,613 students have a birth year. Education years are available for 1,496 students. Birth-cohort comparisons are therefore particularly incomplete.
- 1,056/1,689 appointments (62.5%) have valid coordinates. Of these, 1,044 have at least one mapped education stop. Geographic patterns describe the observed subset.
- The employer projection contains 760 known employers and 986 employer pairs linked by shared students. The Sankey includes 330 students with both known past and current employers.

## Files and workflow

- `student_careers.ipynb`: executed notebook containing the complete Python analysis, explanatory notes and results. Run all cells from this folder to rebuild exports.
- `workflow.py`: the same analysis as a plain Python script. Run `python workflow.py` from this folder.
- `render_html.py` and `assets/app.js`: HTML generation and transparent browser-side filtering, centrality, aggregation and chart logic.
- `data/`: exact copies of the three analysis inputs and the supplied birth-locality lookup. Their SHA-256 hashes are recorded in `tables/source_manifest.csv`.
- `tables/`: UTF-8 CSVs, including the synthetic student list, joined appointments, statistical breakdowns, graph nodes/edges, flows, missingness and mapping audits.
- `maps/`: city map, US/China choropleths and birth–education–work association map.
- `networks/`: individual–employer network and employer projection.
- `sankey/`: direct past–current employer diagram.
- `validation.json`: data reconciliation checks. `filter_validation.json`: browser-logic checks on pure data functions.

To reproduce, use Python 3.12, install `requirements.txt`, open the notebook in Jupyter and run all cells. Alternatively run `python workflow.py`. The original CSVs are already included; replace files in `data/` to analyze an updated source, keeping the same schema. Assets are bundled so rebuilding does not require downloading map boundaries or JavaScript libraries. `python static_maps.py` regenerates the optional static choropleth figure when matplotlib is installed.

## Data definitions and counting rules

The main file uses semicolon delimiters; education uses commas; career and the supplied birthplace lookup use semicolons. Blank trailing columns are removed. Text is trimmed, while substantive categories remain unchanged. Source files are retained verbatim. `NameID` is the person key and `record_id` is the appointment key. No appointment rows are deduplicated. Identical student–employer relationships are deduplicated only for graph construction.

The synthetic student list contains one row per main-file NameID. `birth_year` comes from main; `study_start` and `study_end` are the minimum and maximum nonmissing education `Year`. A student with one recorded year has equal bounds. Those bounds do not establish continuous attendance, enrolment dates, graduation dates or degree duration. Education values are retained as lists. Main-file gender is authoritative; education gender conflicts are audited separately (none were found). No date or gender is inferred.

Counts report appointment rows, distinct students and distinct known employer labels within each cell. Unknown categories are retained. A person can have multiple jobs, education institutions, degrees or disciplines, so totals of subgroup student counts can exceed the number of distinct students. Multi-valued education backgrounds are exploded only for those comparison tables; their category totals overlap. Employer identity follows `Institution_normalized` at the parent-institution level, not department or branch. Unknown employer rows remain in descriptive counts but cannot identify a common institution for networks or Sankey employer links.

Decades are floor(year/10)×10. Static CSV tables include separate and combined status/gender/birth/study-start strata and separate study-end strata. Arbitrary year ranges are available in every interactive view. Study-span filtering uses interval overlap: first recorded year ≤ upper bound AND last recorded year ≥ lower bound. Unknown periods are included by default and can be excluded. This overlap is a cohort selection rule, not evidence of attendance throughout the interval.

## Filters

Expand a filter, search its choices and use checkboxes. Choices within a field combine with OR; fields combine with AND. Select All restores a field; Clear selects none and therefore produces no matches. Click Apply filters after changing choices or periods. Reset restores defaults. Multiple countries, provinces, sectors, levels and professional groups can be selected concurrently. Education level (educ.Level), discipline, education-country and birth-province filters select individuals through their recorded background and retain that person's matching appointments. Different educational background filters can match different education records for the same person.

Graph and Sankey employer filters restrict matching appointment rows. Selecting several employers retains only those employers and their matching student relationships. Networks can be panned/zoomed, nodes dragged, searched and clicked. Tables, matching appointments, graph nodes/edges, route rows and direct Sankey links can be downloaded with the current filters.

## Maps and location limitations

City circles use supplied workplace coordinates. Records with invalid or missing coordinates remain in tables but are omitted from point maps. Coordinates for the same country/province/city label are averaged; circle area, not radius, is proportional to appointment count. City CSVs include unknown locations, while the interactive geography download contains mapped city groups only. The map shows offline country outlines and no online basemap tiles.

US and China choropleths count known province/state labels even when point coordinates are missing. They use independent linear color scales, explicitly labelled maxima, and zero as white. Unmatched regions and missing province values are exported. Only explicit US corrections are applied: Chicago → Illinois, Pittsburgh → Pennsylvania, Southern California/South California → California. Original values are preserved in `province_source`. A US record labelled Hubei remains unmatched rather than being guessed. USA is standardized to United States for analysis; original country values remain in the raw CSV.

Modern geographic boundaries provide reference outlines for historical records. Historical province assignments (for example Hebei or Jiangsu encompassing places now in separate municipalities) are retained, so the choropleths must not be interpreted as a reconstruction of historical administrative boundaries. Boundary datasets reflect their publishers' conventions, including disputed areas, and are not an assertion about sovereignty.

Birthplace coordinates are matched to the supplied chinese_cities_with_coordinates.csv using province plus Chinese or romanized town labels. Unicode, case and punctuation are normalized; province context is required. Decimal commas are parsed as decimal points. All 919 recorded birth localities match; 694 students have no birth town and remain without birth coordinates. Seven matched entries are explicitly marked province-level proxies in the lookup and are labelled as such. Other coordinates are locality reference points from the file, not verified residential addresses. Original Notes, lookup row IDs, matching status and precision labels are retained in birthplace_geocodes.csv and route exports; notes appear in map tooltips. Ambiguous, missing or invalid-coordinate matches are never guessed. Education coordinates prefer revised latitude/longitude, then fall back to original coordinates. Invalid pairs are omitted.

Flow maps link each matching appointment to every distinct mapped education institution/location recorded for the individual. Repeated same-school/location records are collapsed. Each appointment has total education-to-work weight one, divided equally among mapped education stops; the same shares are used for mapped birth-to-education links. A missing birth point does not suppress education-to-work links. These are birthplace–education–work associations, not observed journeys or a confirmed temporal itinerary. No succession among education stops is inferred.

## Networks and communities

The bipartite graph contains individuals and known employer labels, with one edge per distinct person–employer affiliation. Degree is the count of distinct neighbors. Bipartite centrality is degree divided by the size of the opposite partition. Thus students and employers have different denominators. Centrality is recalculated after appointment filters, before node thresholds; displayed measures and exports use this graph. Centrality thresholds can remove neighbors and leave isolates in the displayed graph.

In the employer projection, two employers are linked if one or more individuals have recorded affiliations with both. Edge weight is the number of distinct shared individuals; duplicate appointments cannot inflate it. Degree counts distinct employer neighbors, centrality is degree/(number of employers−1), and strength is the sum of edge weights. The all-data CSV exports include strength. Shared individuals may connect past–past, current–current or past–current affiliations; these edges do not imply a dated move. The status filter restricts affiliations before projection.

Communities are computed using NetworkX weighted greedy modularity on the full-data employer projection. IDs are ordered by community size, then label, for reproducibility. Isolated employers are included and may form singleton communities. Communities remain fixed across interactive filters for comparable labels; degree and centrality recalculate after appointment filters. Degree/community node thresholds then create the displayed induced graph. Exports retain pre-threshold metrics, and tooltips label them accordingly. The layout uses a fixed random seed, then supports manual exploration.

## Sankey

The diagram directly links Past employer → Current employer, with no student or cohort stage. Only individuals retaining at least one known employer in both statuses after the active appointment filters qualify. Country, sector, position level, gender, education level and period filters rebuild the pair counts from surviving records. Unknown-status records do not create past/current links. Filters apply on both sides, so a person can disappear if one side no longer survives.

Each past/current employer pair is counted by its distinct bridging NameIDs. For a person with P distinct past employers and C distinct current employers, each of their P×C employer pairs receives one contribution. Duplicate appointment rows never increase their count for the same pair. Link width and hover text show the integer number of distinct bridging individuals; hover text and CSV exports also provide IDs and names. The per-person bridge table makes these contributions auditable. Counts across links are not additive unique-person totals, because one person may bridge multiple employer pairs. Node totals are sums of link counts (bridge participations), not unique people per employer.

The default shows all employers. Optional top-15/top-30 views group other employers on each side. Grouped link counts use the union of bridging people within each displayed pair, so the same person is counted once even if several original employer pairs collapse into Other. The individual stage and cohort-stage control have been removed. Appointment dates are unavailable; these are historical status-based affiliations rather than verified successive job changes.

## Validation and known limits

The workflow asserts unique main and appointment IDs, full matching of career/education IDs to main, a many-to-one career join with unchanged row count, status count reconciliation, route-weight reconciliation and projection edge counts. Pure-data JavaScript checks independently compare filter results and graph computations against Python exports, including multiple selections, unknown periods, empty selections, repeated affiliations and direct Sankey distinct-person counts and identities.

The local browser preview was blocked by the application's URL security policy. HTML syntax, bundled scripts, data reconciliation and filter logic have been checked, but visual browser rendering and interactive browser downloads were not verified in this session. Open index.html in a standard browser to inspect the outputs. Mapping audits and unknown categories should be reviewed before drawing population-wide conclusions. No statistical significance or causal effect is claimed.

## Geographic and software sources

- US states: [PublicaMundi MappingAPI GeoJSON](https://github.com/PublicaMundi/MappingAPI/blob/master/data/geojson/us-states.json).
- Chinese provincial reference outlines: [longwosion/geojson-map-china](https://github.com/longwosion/geojson-map-china/blob/master/china.json).
- Country reference outlines: [Natural Earth 1:110m](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson), public domain.
- Leaflet 1.9.4, vis-network 9.1.9 and Plotly.js 2.35.2. Source links and licenses are bundled in assets. Geographic assets were downloaded on 25 October 2026; their SHA-256 hashes are recorded in tables/asset_manifest.csv.

Recorded educational qualifications may have been obtained before or after a particular appointment; without appointment dates, their temporal relationship cannot be established. The background comparisons are descriptive associations.

To repeat the independent browser-logic checks: run python validate_filters.py, then node validate_filters.cjs. These require Node.js in addition to the Python requirements.


## Career-only package revision

All education filters now use educ.Level rather than raw Degree. Values are preserved exactly, including Doctor and Doctorate as separate recorded categories. Unknown selects students with no recorded Level. When a person has multiple recorded levels, any selected level can match. Raw Degree values remain in the synthetic list and CSV tables as reference data; an Education level count dimension and related tables have been added. Position level remains a separate employment filter.

Past/current Sankey links now connect employers directly, with distinct bridging NameIDs and names in tooltips and exports. Birth-origin flows now use the supplied town lookup, with seven explicit province proxies labelled rather than silently treated as towns. Birth-coordinate matching and missingness are audited in birthplace_geocodes.csv, unmapped_birth_towns.csv, ambiguous_birth_towns.csv and birthplace_validation.json. The original lookup file is included under data/ and hashed in source_manifest.csv. Run python validate_birthplaces.py to repeat the geocoding checks. The separate education–career package is unchanged.


## Direct-link Sankey and network tooltip revision

The Sankey now has only past and current employer stages, with integer distinct-person counts rebuilt after filtering. tables/sankey_links.csv contains direct pair counts and identities; tables/sankey_individual_bridges.csv contains one row per person and employer pair. Individual IDs and names remain available in link hover text and downloads. Both network views now construct node and edge tooltips with real text elements, so HTML line-break tags are not printed literally and institution names containing special characters remain readable.


## Network controls and filter label

Both career-only networks now offer a 0.25×–2× physics pace slider and Pause/Resume. Pace and paused state persist across filters, and retained nodes reuse their positions. Settled layouts may be stationary with physics enabled. These controls affect layout only. The education filter label is Education level in both packages.
