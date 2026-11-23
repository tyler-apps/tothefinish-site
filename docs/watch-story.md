# Watch to coaches demonstration

Requested November 23: make the inner workings the main reason visitors want to follow this and eventually want their own coaching team. The homepage leads into a brief coach introduction and then the demonstration; this is still Tyler's personal setup, with no product waitlist or offer.

The watch is a CSS/HTML interpretation of Garmin epix Pro (Gen 2), based on Garmin's device overview (round screen, five controls, upper-right start/stop). It is labeled an illustration with adapted screens, not an actual Garmin app screenshot. No external runtime, autoplay video or downloaded product photo. Design structure uses the registered Apple exemplar's tangible product presentation and Linear's visible UI, with existing TTF typography/colors.

## Data

Frozen date: 2026-11-23. Brain sources: brain/health/runs/2026/2026-11-23-25174289804.json and brain/health/2026-11-17.json through 2026-11-23.json. Summary 4.03 mi, 1:02:22, average HR 110 bpm, climb 585 ft. The seven-night HRV trace uses 91, 85, 60, 86, 87, 90, 85 milliseconds, in date order. Garmin reports a seven-day average of 83 ms. Nov23 sleep 8.22 hours rounds to 8 hours and 13 minutes. These are recorded values, not new clinical conclusions. No coordinates or raw FIT files are public. JSON is the supporting selected data; the labeled example stays frozen unless deliberately revised.

Tyler's final steering: do not highlight walking. The feature now focuses on recovery trends, session demands and fueling. Prior walking evidence remains in the original replay record; it is not the homepage demonstration.

## Research and actual outcome

Last completed library review is Nov 21, 2026, per brain/coaching/research-audit-2026-11-21 and current methods. This date is not a claim of a continuous live literature scan. The monitoring method records single-low-morning HRV no longer independently changing the live plan, with trends and other inputs retained. Clinical/training study finding is separated from the coaches' chosen thresholds.

Public source links: HRV trial PMID26909534; strength economy meta-analysis PMID38165636 / PMC11052887; fuel framework PMID29453741 / PMC5889771. Internal rules: methods/running/research/build-2027/garmin-monitoring.md; methods/strength/research/runner-strength-2026-11.md; methods/nutrition/research/fuel-the-work-2026-11.md; methods/nutrition/juno-protocol.md. The Nov20 food change is also recorded in public data/progress.json board.rulings. No general performance percentage promise.

The next planned session is Nov24: 2 mi easy, 6 × 45 s uphill, 2 mi easy, including the already scheduled heart-rate test. Morning checks apply before the final day. This is a dated explanation of existing rules and recorded inputs, not a claim that tomorrow's recovery is known or that the Nov23 sleep reading caused the test to be scheduled. No automated inference establishes recovery or intent. Source: scripts/running_plan.py 2026-11-24 and the active Kai plan.

## Automation

Read-only launchctl verification Nov23: com.tylerstewart.brain.garmin-watch loaded, interval600 seconds, last exit0. It was idle between runs (not continuously running); separate garmin-ingest service was not loaded. The watcher itself calls ingest_garmin.py, build_today.py, morning_run.sync_watch and garmin_zones.sync. Recorded pipeline result Nov23 08:16:25 was ok. No watch upload/API call was triggered for website testing. This supports describing the configured automatic chain, not asserting every endpoint or future upload succeeds.

Research review is separate from this chain; pain input and food-rule changes need Tyler. Local laptop/connectivity remain dependencies. External artifact republishing and social posts are not described as part of this automatic loop.

## Interaction and maintenance

Four chapters: recording → reviewed research → specialist interpretation → next check. Native scrolling chooses the scene; anchors allow direct selection. The five current coach portraits appear together at the interpretation stage. Expanded evidence/data/automation remain normal HTML, available without JS. Reduced motion disables sticky enhancement and motion, including a live preference change. Short phone screens use a static watch to preserve reading space. Legacy #how/#research anchors are preserved.

Edit index.html between WATCH STORY markers plus assets/watch-story.css/js. Data in data/watch-story.json must stay consistent with visible values; it is intentionally a dated example rather than a live service indicator. The main builder includes these assets in cache versioning. Run node tools/test_watch_story.mjs, node tools/test_ui.mjs, python3 tools/test_seo.py and python3 tools/check_site.py after building all pages.

## Coach context before the demonstration

Tyler requested introductions before visitors see the coaches work. The compact #team section now precedes #inside, with names, existing portraits, specialties and short roles. Hero → Meet the coaches → See them work. Full profile links remain on coach names. Removed the old downstream team section and duplicate five-role strip. Existing First Light design and reveal/reduced-motion handling remain; Apple tangible lineup and Linear progressive explanation inform sequence only.

## Technology credits and partnership contact

Tyler approved factual Garmin, Anthropic and OpenAI credits plus a discreet partnership contact. #tools follows the walkthrough, using linked text names without logos or co-branding. Garmin supplies recorded workout/recovery inputs. Claude Code built the original project and remains a development tool; Codex develops/reviews the website, scripts and shared workflows. The scheduled checks remain described as local scripts/rules, not necessarily per-workout calls to both AI vendors. Sources: user's project history, Brain/scripts/TTF-WORKFLOW.md, scripts/ttf_cold_reader.py and the existing watch pipeline. Partnership contact uses existing hello@tothefinish.ai; no email sent. OpenAI brand guidance and Anthropic trademark guidance were consulted; no sponsor/endorsement relationship asserted.
