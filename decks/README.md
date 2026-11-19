# Chapter decks

This folder holds the source for the chapter slide decks (one deck per chapter, for example
Chapter 1 = sections 1A, 1B and 1C). The build script joins the pieces into **one HTML file**
that works offline: fonts, maths and labs are all inside it.

## What is where

| Path | What it is |
|---|---|
| `src/engine.js`, `src/engine.css` | How every deck looks and behaves (modes, reveals, timers, contents page, reference pages, printing). Shared by all chapters. |
| `src/sims.js` | The labs (interactives). |
| `src/build.py` | Builds a deck. |
| `src/*.woff2` | Two handwriting fonts (Patrick Hand, Kalam). |
| `src/chapter1/chapter.json` | Chapter 1 settings: title, unit, "On your desk" line, and the list of section files in teaching order. |
| `src/chapter1/1a.html` | Section 1A: its slides and its reference book page. |
| `test/` | A small test deck (a dummy section with two pages). Only for checking the engine. Not for class. |
| `out/` | Built decks appear here. Not saved in git. |

## Build a deck

From the repo folder, run:

```
python3 decks/src/build.py tools/interactives/vendor decks/src/chapter1/chapter.json
```

The deck appears as `decks/out/Chapter 1 deck.html`. Open it in Chrome.

The build stops with a "PROBLEM" line if a reference book slide points at a page or part that does
not exist, or if the section text has an em or en dash, "m s⁻¹" or "÷".

## Using the deck

- **PageDown / clicker**: next reveal, then next slide. **PageUp**: back.
- **Contents** is slide 2. Click a line to jump there, or type a slide number then **G**. Press **C** to come back to the contents.
- Close the file and open it again: it goes back to the last slide shown.
- **P** prints the reference pages of the section you are in, one A4 sheet each. **Shift+P** prints every page in the chapter. **F** is full screen.

## Add a section (for example 1B)

1. Copy `src/chapter1/1a.html` to `src/chapter1/1b.html` and replace the slides and pages.
2. The first line names the section:
   `<script type="application/json">{"code":"1B","title":"Electromagnetic waves"}</script>`
   Add `"desk":"On your desk: ..."` there if this section needs a different list.
3. Add `"1b.html"` to the `sections` list in `src/chapter1/chapter.json`, in teaching order.
4. Build again.

The engine makes the section's title slide and its lines on the contents slide for you.

## Section file format

- Slides: `<section class="slide" data-mode="watch|board|lab|book|practise" data-do="instruction" data-t="seconds">`.
  Anything with class `st` appears one click at a time.
- Loops: put `data-loop="Short name"` on the first slide of each loop. Other contents entries
  (worked example, coursework) use `data-part="Name"`.
- Reference pages: one `<div class="pagesrc">` per A4 page, in order. Each holds `<div class="col L">`
  and `<div class="col R">`, and each part of the page is a `<div class="bk" data-b="1">` (the number is
  the stage). A page after the first can set its own top line with `data-title="..."`.
- Reference book slides: `data-mode="book" data-page="2" data-b="3"` shows page 2 with part 3 new,
  earlier parts faded and later parts hidden. `data-page` can be left out for page 1. `data-b="0"` is the
  blank page; `class="slide pageslide"` with `data-b="99"` shows the finished page to check against.
- Each column holds at most 35 ruled lines. If a section needs more, give it another page.
