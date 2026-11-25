# Coaching product interest

Authorized November24, 2026. Shared decision and operational procedure: `../Brain/brain/social/coaching-interest.md` (relative to site root).

`tools/build_coaching_interest.py` owns `/coaching/`; `assets/coaching-interest.css` uses the existing First Light palette and type. Homepage includes a restrained invitation after the coaching demo; footer provides discovery. No newsletter form on this dedicated page. Existing scroll/reduced-motion behavior remains.

`pages/coaching-interest.json` stores only public provider configuration and verification flags, never subscriber data or credentials. Status `pending_provider_setup` renders a disabled preview with no destination. `ready` requires a separate form ID and all provider checks verified. `publish.sh` runs `check_coaching_interest.py --release` BEFORE pull/commit/push. This intentionally holds all website publication while these unpublished changes are present; finish or isolate the work before routine refreshes. Do not bypass it.

Provider setup must inspect real Kit form settings, existing rules and all broadcasts/automations that might send the Sunday letter to all subscribers. Product-only contacts must not receive the letter or its welcome. Track explicit form membership for each purpose; choosing both is valid. The optional selector uses `fields[coaching_challenge]`, with choices running_and_strength, fueling, recovery, life_and_schedule. Configure this custom field in Kit and verify its embed mapping. Leave the question optional.

The native POST leaves response/error/confirmation to Kit. `assets/join.js` emits coaching_interest_submit for this purpose; newsletter_submit stays unchanged. Neither is confirmed membership or delivered email. No email address or answer goes to analytics. No fake success or iframe confirmation. Do not submit a test signup without Tyler asking.

Validation: `python3 tools/test_coaching_interest.py`, `node tools/test_ui.mjs`, full page generators, `python3 tools/check_site.py`, `python3 tools/test_seo.py`, desktop/mobile and no-JS/native form inspection. Final public verification must check the exact native action, purpose language, enabled form, and a separate letter form on its own page. Configuration verification is not end-to-end email delivery.

## Verified provider configuration · November24

Kit form10239995 “Coaching product updates,” uid6791db9330. Published and reloaded; field name `fields[coaching_challenge]`, not required, verified from native embed. Email confirmation OFF and Kit explicitly states subscribers auto-confirm (Tyler: “I don’t want double opt in”). No confirmation email or welcome sequence is sent for this form. Native success message: “You’re on the coaching updates list. I’ll email when there’s something to report. This doesn’t add you to the Sunday letter.” The old drafted confirmation content is disabled, not an active email.

Only existing automation rule: tothefinish.ai sign-up10209840 → Welcome sequence2977232. No visual automations, no RSS feeds; Broadcasts All shows only the already-sent Nov22 letter and no pending send. Created Sunday letter · explicit opt-in segment611071: ANY subscribed to form10209840 OR Welcome sequence. This preserves the two documented original imported readers and the subsequent form signup, and excludes coaching-only membership. Future letter broadcasts must target this segment; never all subscribers. No existing subscribers were edited or emailed. Counts include unresolved tests and do not establish real audience growth.

Release config is ready from UI verification. No live signup submitted and no email-delivery test performed.
