# Year 11 Physics lesson index: format

Purpose: Rocco picks sections (or success criteria) and HTML slides + a guided sheet build themselves.
Everything is indexed against the Cambridge **success criteria IDs** from each Chapter Checklist (e.g. `1A.4`).
This folder holds licensed Cambridge text: it is for Rocco's own teaching. Never publish it (not to the public GitHub repo).

## Folder layout
```
Index/
  SCHEMA.md            this file
  README.md            how to use it, counts, known gaps
  chNN/
    chNN.json          chapter file (criteria, review questions, summary)
    1A.json            one file per section (everything for that section)
    img/               PNG crops of important figures, graphs, diagrams, worked-example and question images
```

## Conventions
- Text is **verbatim** from the source. Maths in LaTeX inside `$...$` (KaTeX-ready): `$v = f\lambda$`, `$\text{m s}^{-1}$`.
- Never invent. If something has to be written to fill a gap, put it in a field with `"origin": "adapted"` or `"own"` (default `"cambridge"`).
- Every item has a `src`: `{"file": "<file name>", "page": <pdf page number if from the textbook>}`.
- Every question-like item has `answer` (verbatim from Suggested responses / Worksheet answers / Chapter test answers). If no answer exists: `"answer": null`.
- `criteria`: list of success-criteria IDs the item assesses or teaches (your judgement, from the Checklist wording).
- `img`: list of image paths relative to the chapter folder (e.g. `"img/1A_fig1A-1.png"`).
- IDs are stable and unique across the whole course (prefix with the section code).

## Tags (use exactly these values)
- `kind`: `recall` (define, state, name), `explain` (explain, describe, compare), `calc` (numerical), `graph` (read/draw a graph or diagram), `mc` (multiple choice; also give `kind2` with one of the others).
- `size`: `quick` (about 1 to 3 min, 1 to 2 marks), `medium` (3 to 6 min), `long` (multi-part or 4+ marks).
- `phase` (where it fits best; can be a list): `donow`, `keyidea`, `newknowledge`, `wedo`, `youtry`, `practice`, `exit`.

## Section file: `1A.json`
```json
{
  "code": "1A", "title": "The properties of waves", "chapter": 1, "unit": 1, "aos": 1,
  "study_design": ["verbatim dot point", "..."],
  "criteria": ["1A.1", "1A.2"],
  "glossary": [{"id": "1A-G1", "term": "Amplitude, A", "def": "verbatim margin definition", "src": {}}],
  "formulas": [{"id": "F1A-1", "name": "The wave equation", "latex": "\\lambda = \\frac{v}{f} = vT",
                "where": [{"sym": "\\lambda", "meaning": "Wavelength of the wave", "unit": "m"}], "criteria": [], "src": {}}],
  "engage": {"heading": "What are waves?", "text": "verbatim", "src": {}},
  "chunks": [{"id": "1A-E1", "heading": "The nature of waves", "text": "verbatim paragraph(s)", "figures": ["1A-F1"],
              "criteria": [], "src": {}}],
  "figures": [{"id": "1A-F1", "label": "Figure 1A–1", "caption": "verbatim", "img": "img/1A_fig1A-1.png",
               "important": true, "why": "one line: what it shows / why useful on a slide", "src": {}}],
  "worked_examples": [{"id": "WE1A-1", "title": "Period and frequency of a wave", "question": "verbatim",
                       "steps": ["verbatim solution line", "..."], "answer": "final answer", "img": [],
                       "criteria": [], "src": {}}],
  "checkins": [{"id": "1A-CI1.1", "set": 1, "n": 1, "question": "verbatim", "answer": "verbatim or null",
                "kind": "explain", "size": "quick", "criteria": [], "src": {}}],
  "section_questions": [{"id": "1A-SQ1", "n": "1", "question": "verbatim (stem + options for MC)",
                         "options": ["A. ...", "B. ..."], "answer": "verbatim", "marks": null,
                         "kind": "mc", "kind2": "recall", "size": "quick", "phase": ["exit","practice"],
                         "criteria": [], "img": [], "src": {}}],
  "worksheet": {"title": "Worksheet 1A–1 The properties of waves", "total": 15,
                "questions": [{"id": "WS1A-1", "n": "1", "question": "verbatim", "answer": "verbatim",
                               "marks": 2, "kind": "recall", "size": "medium",
                               "phase": ["practice"], "pair_with": null, "criteria": [], "img": [], "src": {}}]},
  "wedo_plan": [
    {"criteria": ["1A.4"], "wedo": "WE1A-1", "youtry": ["WS1A-2a"], "note": "why these pair (same skill, similar difficulty)"}
  ],
  "skills": [{"id": "1A-SK1", "heading": "Calculation questions", "text": "verbatim", "src": {}}],
  "pracs": [{"id": "P1C-1", "title": "...", "file": "file name", "aim": "verbatim aim"}],
  "notes": "anything Rocco should know (gaps, no worked examples, diagram-heavy questions, etc.)"
}
```
`wedo_plan`: one entry per teachable skill. `wedo` is a textbook worked example if one fits; otherwise a worksheet question (mark that worksheet question `phase: ["wedo"]` and the plan entry `"origin": "adapted"` because its solution steps will be written out from the answer). `youtry` = 1 or 2 worksheet questions of the same skill and similar difficulty (fall back to section questions). Everything left over in the worksheet + section questions is `practice`.

## Chapter file: `ch01.json`
```json
{
  "chapter": 1, "title": "Electromagnetic radiation", "unit": 1, "aos": 1, "sections": ["1A","1B","1C"],
  "criteria": [{"id": "1A.1", "text": "verbatim success criterion", "section": "1A",
                "review_qs": ["14","15"], "exit_candidates": ["CH1-RQ14", "1A-SQ3"]}],
  "review_questions": [{"id": "CH1-RQ1", "n": "1", "question": "verbatim", "options": [], "answer": "verbatim",
                        "marks": null, "kind": "mc", "kind2": "recall", "size": "quick",
                        "criteria": ["1A.4"], "parts": [{"n":"a","question":"...","answer":"...","size":"quick"}],
                        "img": [], "src": {}}],
  "summary": "verbatim chapter summary text (from the Summary docx), short headings kept",
  "test": {"file": "Chapter 1 Test.docx", "questions": 0, "marks": 0, "note": "not indexed question by question"},
  "notes": ""
}
```
`exit_candidates`: for each criterion, the best quick questions to use as an exit ticket (review questions first, a quick section question as fallback). For a long multi-part review question, list one part, e.g. `CH1-RQ21b`.

## Images
- Crop from the textbook PDF at 200 dpi (`pdftoppm -r 200 -f P -l P -png`, then crop with Pillow to the figure's bounding box, trim whitespace). Name: `<section>_<label>.png`, e.g. `1C_fig1C-13.png`, `1C_WE1C-2.png`, `1C_SQ7.png`.
- Images embedded in .docx files: extract from the docx `word/media/` folder and name them the same way (`1A_SQ3.png`, `1A_WS4.png`).
- Save: every figure that would help on a slide (graphs, ray diagrams, circuit diagrams, wave diagrams, tables of data, the EM spectrum), every image a question or worked example needs to make sense. Skip decorative photos.
- Check a few crops visually (Read the PNG) to make sure the box is right.
