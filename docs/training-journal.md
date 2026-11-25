# Public training journal

Approved November 24, 2026. `/training/` is a dated, four-week record of completed runs and reported strength work, with a compact homepage preview after progress. It does not release the held explainer or restart replays.

## Source and update path

Brain `scripts/site_training.py` reads recorded Garmin JSON and `brain/lifting/lift-log.md`, exporting only date, public numeric workout fields, known movement names and reviewed editorial annotations to `data/training.json`. Raw names/IDs, precise times, coordinates, streams, private notes and recovery data are excluded. Assumed or prescribed sets are excluded. Unknown movement names require review before adding to the exporter allowlist. Missing data never means completion or a missed workout. Weekly planned miles come from the active running calendar; they are distinct from recorded miles.

Public coaching summaries live in Brain `brain/social/training-notes.json`. These are Tyler's summaries, not verbatim quotes or automatic new AI calls. Guarded expected values invalidate a note if its source changes. The initial Nov24 feature follows the verified hill-test source and unchanged 120 bpm easy limit; the six 45-second efforts exclude the longer test climb. Summaries keep their dates as new sessions arrive.

Existing Codex growth check-ins (09:00/17:00 Pacific) and the Sunday site refresh run the export, then the existing guarded publisher. These schedules depend on the Mac and connections; this is not an instant or continuously live feed. Use the shared edit lock and preserve unrelated site changes. New public wording must pass review; numeric refresh does not create editorial notes.

## Build and design

`tools/build_pages.py` calls `tools/build_training.py`, adds the journal to the sitemap and versions assets. The page is server-rendered HTML. `assets/training.js` progressively enhances filters and refreshes the homepage preview from JSON; no JavaScript leaves a dated readable preview and the full journal. `assets/training.css` keeps First Light, the site's display font, warm ink surfaces, hairline divisions and sparse orange. Shared motion reveals entries and animates the effort chart, respecting reduced-motion changes. Native details and keyboard-operable filters expose session data.

Build using `PYTHONDONTWRITEBYTECODE=1 python3 tools/build_pages.py` plus the existing remaining generators. Run `check_site.py`, `test_seo.py`, UI/watch checks and Brain `test_site_training.py`. Verify mobile/desktop, filtering, details, no-script content and dated homepage preview. No test newsletter submission. `publish.sh --numbers-only` allows training data/generated pages; its homepage guard permits only known generated number/date changes, never prose changes.
