# tothefinish.ai

One-page site for To The Finish. Static HTML on GitHub Pages. Sign-ups post to a Google Form on the show account.

## Words on this site (the story gate)

Every word a visitor reads here is written with the Brain's `story-voice` skill, read **before** writing: `/Users/tylerstewart/Vibe_Coding/Brain/.claude/skills/story-voice/SKILL.md` (the row "Site copy" in its table says which rules bind a page). Before `tools/publish.sh`, check the visible text of every page you changed:

```
python3 ~/Vibe_Coding/Brain/scripts/voice_check.py --html index.html
```

It strips tags, scripts and form buttons and must print PASS. Reread every `?` line. Text built by `tools/*.py` or `pages/questions.json` counts: build the page, then check the built page. Links on the site itself are never tagged; links to the site from anywhere else are (`brain/social/links.md` in the Brain).
