# Physics planner: handoff (18 Nov 2026)

Start a new chat with: "Read HANDOFF.md and CLAUDE.md in roccatalano/Physics and carry on."

## Where things are
- Repo: `roccatalano/Physics` (public, renamed from 11PHY). Live site: https://roccatalano.github.io/Physics/
- Rules for Claude: `CLAUDE.md` (Cambridge first, calendar, planning rules, slide style). Also in the project doc `claude/11phy-planner-instructions.md`.
- Planner: `index.html` + `data/years.json` + `data/year11.json`. Never edit JSON by hand: run `python3 tools/build_year11.py`.
- Other pages (shown as tabs inside Year 11): `analysis.html` (Cambridge course, `tools/build_analysis.py`), `pearson.html` (Pearson cross-map, `tools/build_pearson_page.py`), `studydesign.html` (`tools/build_studydesign.py`).
- Drive links: `tools/drive_ids.json` (354 Cambridge files), `tools/pearson_drive_ids.json` (158 Pearson files). Mapping rules in `tools/pearson_map.py`. Links only open for people with shared-drive access.
- Check pages locally: `python3 -m http.server 8897` in the repo, then a playwright screenshot.

## Done
- Year 7 to 12 tabs (only Year 11 started), 12MAG look.
- Year 11 sub-tabs: Course plan, Cambridge course, Pearson cross-map, Study design.
- Course plan: AoS detail bars, chapter cards with badges, section cards nested (collapsed with Cambridge/Pearson counts; open to show grouped links). Cambridge links blue, Pearson orange.
- All Cambridge files linked; all 158 Pearson files mapped onto Cambridge sections, chapters, AoS or course (pirated Pearson textbook PDF excluded, never link it).
- 2027 calendar and planning rules agreed (see CLAUDE.md): Unit 1 about 48 lessons, Unit 2 about 46.
- Study design deep dive (prac hours: Unit 1 15 h, Unit 2 10 h + 7 h investigation).
- Verdict so far: Cambridge is the stronger base; Pearson is a top-up (6 sections have no Pearson extras: 3A, 3D, 4A, 6B, 6C, 9A).

* Years 7 to 10 tabs merged into one **Progression** tab: 60 Jacaranda physics subtopics in 6 strands, linked to Cambridge sections (click a card to highlight links). Gaps with no feeder: 3D, 4A, 5E, 9C.

## Next
1. Year-by-year tabs (e.g. 2027 overview calendar like 12MAG).
2. Lay out Unit 1 lessons on the calendar.
3. Then slides and guided sheets per lesson from Cambridge.
4. Later: Years 7 to 10 (need those SCIENCE folders connected). Later still: move to Google Sites / Apps Script.

## Open questions for Rocco
- Cambridge/Pearson groups inside section cards: start open or folded?
- One chapter test per chapter, or per AoS (lesson budget is tight: about 21 theory lessons for 21 sections)?
- SACs in the SAC free periods or in class?
- 79-minute lessons confirmed?
- Which pracs (Unit 1 needs 12 prac lessons; Cambridge has 14)?
- Is the lesson shape still right?
- Step Up (from 19 Nov): start Ch 1 or an intro?
- Unit 2 worked examples not yet indexed.

## Indexing plan (agreed in discussion, 18 Nov)
* Goal: pick sections (or success criteria) and the HTML slides and guided sheet build themselves from an index.
* Index everything by Cambridge success criteria IDs (e.g. 1A.4).
* We do / You try: textbook worked examples first, then worksheet questions (tagged calc/explain/recall); the rest of the worksheet + section questions are practice (12MAG style).
* APK: from the Progression tab links.
* Do now: generator from check-in questions, indexed by section (tag recall/calc).
* Exit tickets: review questions matched to success criteria (start from the Chapter Checklist links), tagged quick/long.
