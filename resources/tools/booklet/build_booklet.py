#!/usr/bin/env python3
"""Build a printable chapter practice booklet from Cambridge worksheet .docx files.

Usage:
    python3 build_booklet.py            # builds the chapter set in CHAPTER below
    python3 build_booklet.py --keep     # also keeps the intermediate files in build/

To reuse for another chapter, copy the CHAPTER dict, change the paths, titles
and corrections, and run again. Everything is written beside this script.

What it does
 1. Copies each worksheet .docx to a temp folder and makes one layout fix that
    LibreOffice needs (see fix_header): the banner picture in Cambridge's header
    is set to push the header text below it. Word does this; LibreOffice ignores
    it and prints "Chapter N ..." on top of the red "Physics" logo. Content is
    not touched.
 2. Converts each copy to PDF with LibreOffice, using a private fontconfig that
    maps "Times New Roman Bold" (named in Cambridge's list numbering) to
    Liberation Serif Bold. Needs the libreoffice-math package or Word equations
    (x signs, degree signs, fractions) silently disappear.
 3. Makes the cover, contents, corrections and notes pages with reportlab.
 4. Puts the pages in order so every worksheet starts on an odd (right-hand)
    page, pads the end to a multiple of 4, stamps "Booklet page N" under
    Cambridge's footer on every page, and sets every page box to exact A4.
 5. Checks: A4 size, page count, contents numbers against the real pages, no
    overlap between the page number and any text on the page, no em or en
    dashes in our own wording. Writes page-map.md and PNG renders.

Licensed Cambridge content: output is for the school's shared drive only.
Do not commit the PDF, the PNGs or the worksheets to any git repo.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pdfplumber
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- chapter set
CHAPTER = {
    "course": "Year 11 Physics",
    "unit": "VCE Physics Unit 1",
    "chapter": "Chapter 2 Thermal energy and electromagnetic radiation",
    "output": "Ch02 Practice booklet.pdf",
    "source_note": ("Worksheets from Cambridge Senior Science Physics VCE Units 1&2. "
                    "© Cambridge University Press & Assessment 2023."),
    "worksheets": [
        {"code": "2A", "title": "Worksheet 2A Thermal energy",
         "docx": "/home/claude/cambridge2/2A Thermal energy/2A Worksheet 2A–1 Thermal energy.docx"},
        {"code": "2B", "title": "Worksheet 2B Thermal energy and electromagnetic radiation",
         "docx": "/home/claude/cambridge2/2B Global warming/2B Worksheet 2B–1 Thermal energy and electromagnetic.docx"},
    ],
    # Genuine errors in the worksheet QUESTIONS only, as (where, correction).
    # Leave empty for a ruled page where students write corrections given in class.
    "corrections": [
        ("Page 7, 2A Q9b", "Delete \"at\": the steam condenses to water at 100°C."),
        ("Page 9, 2B Q1 f", "Read H₂O (the letter O), not H₂0."),
    ],
    "pad_to": 4,  # 4 = whole sheets folded for a stapled booklet; 2 = just double-sided
    # One line for page-map.md about anything the question finder could misread.
    "map_note": ("Q1 of both worksheets is a matching table: its i, ii, iii ... and a to n are "
                 "terms and descriptions, not parts. Worksheet 2A Q7 starts at the foot of page 6 "
                 "and its writing space runs onto the top of page 7."),
}

# ---------------------------------------------------------------- page layout
A4_W, A4_H = 595.2756, 841.8898          # exactly 210 x 297 mm in points
NUM_BASELINE = 7.5 * mm                   # booklet number baseline from bottom edge
NUM_SIZE = 9
LIBERATION = "/usr/share/fonts/truetype/liberation"
pdfmetrics.registerFont(TTFont("LSans", f"{LIBERATION}/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LSansB", f"{LIBERATION}/LiberationSans-Bold.ttf"))

FONTS_CONF = """<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
  <match target="pattern">
    <test name="family"><string>Times New Roman Bold</string></test>
    <edit name="family" mode="assign" binding="strong"><string>Liberation Serif</string></edit>
    <edit name="weight" mode="assign" binding="strong"><const>bold</const></edit>
  </match>
</fontconfig>
"""


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------- 1. docx fix
def fix_header(xml, header_dist_twips):
    """Emulate Word's text wrap under a full-width banner anchored in the header.

    Cambridge anchors the banner to the first header paragraph with a negative
    offset (so it starts at the page top) and square wrap. Word pushes the
    header text below the picture. LibreOffice does not, so we pin the picture
    to the page at the same spot and give the first paragraph enough space
    before it to clear the picture, which is where Word puts it.
    Returns (new_xml, note)."""
    m = re.search(r'<wp:anchor\b.*?</wp:anchor>', xml, re.S)
    if not m:
        return xml, "no anchored picture in header"
    anchor = m.group(0)
    if "wrapSquare" not in anchor and "wrapTopAndBottom" not in anchor:
        return xml, "header picture does not wrap text"
    pv = re.search(r'<wp:positionV relativeFrom="paragraph">\s*<wp:posOffset>(-?\d+)</wp:posOffset>', anchor)
    ext = re.search(r'<wp:extent cx="\d+" cy="(\d+)"', anchor)
    if not pv or not ext:
        return xml, "header picture not positioned from paragraph"
    off, cy = int(pv.group(1)), int(ext.group(1))
    top_emu = header_dist_twips * 635 + off               # picture top from page top
    clear_twips = round((top_emu + cy) / 635) - header_dist_twips
    if clear_twips <= 0:
        return xml, "picture does not reach the header text"
    new_anchor = anchor.replace(pv.group(0),
                                f'<wp:positionV relativeFrom="page"><wp:posOffset>{top_emu}</wp:posOffset>')
    xml = xml.replace(anchor, new_anchor)
    # Word keeps the empty anchor paragraph where it is (it is hidden behind the
    # picture) and starts the next paragraph below the picture. So the space goes
    # on the paragraph after the anchor: picture bottom minus the anchor line.
    paras = list(re.finditer(r'<w:p\b[^>]*>.*?</w:p>', xml, re.S))
    ia = next(i for i, p in enumerate(paras) if "<wp:anchor" in p.group(0))
    if ia + 1 >= len(paras):
        return xml, "no header text after the picture"
    nxt = paras[ia + 1]
    anchor_line = 276  # one empty line of the Header style: 12 pt Times New Roman, 13.8 pt
    clear_twips -= anchor_line
    ptxt = nxt.group(0)
    if "<w:spacing" in ptxt:
        return xml, "header text paragraph already has spacing; left as is"
    if "<w:pPr>" in ptxt:
        ptxt2 = ptxt.replace("<w:pPr>", f'<w:pPr><w:spacing w:before="{clear_twips}"/>', 1)
    else:
        ptxt2 = re.sub(r'(<w:p\b[^>]*>)', rf'\1<w:pPr><w:spacing w:before="{clear_twips}"/></w:pPr>', ptxt, 1)
    xml = xml[:nxt.start()] + ptxt2 + xml[nxt.end():]
    return xml, f"header text moved below banner ({clear_twips} twips space before)"


def prepare_docx(src, dst):
    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf8")
    hd = re.search(r'<w:pgMar[^>]*w:header="(\d+)"', doc)
    header_dist = int(hd.group(1)) if hd else 708
    word_pages = None
    try:
        app = zin.read("docProps/app.xml").decode("utf8")
        mp = re.search(r"<Pages>(\d+)</Pages>", app)
        word_pages = int(mp.group(1)) if mp else None
    except KeyError:
        pass
    notes = []
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            data = zin.read(it.filename)
            if re.fullmatch(r"word/header\d*\.xml", it.filename):
                new, note = fix_header(data.decode("utf8"), header_dist)
                notes.append(f"{it.filename}: {note}")
                data = new.encode("utf8")
            zout.writestr(it, data)
    return word_pages, notes


def convert(docx, outdir, tmp):
    env = dict(os.environ, FONTCONFIG_FILE=str(tmp / "fonts.conf"))
    cmd = ["soffice", f"-env:UserInstallation=file://{tmp}/lo_profile", "--headless",
           "--convert-to", "pdf", "--outdir", str(outdir), str(docx)]
    subprocess.run(cmd, env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = outdir / (Path(docx).stem + ".pdf")
    if not pdf.exists():
        sys.exit(f"LibreOffice did not produce {pdf}")
    return pdf


# ---------------------------------------------------------------- 3. our pages
def new_canvas(path):
    c = canvas.Canvas(str(path), pagesize=(A4_W, A4_H), initialFontName="LSans", initialFontSize=10)
    c.setTitle("")
    return c


def draw_cover(path, ch):
    c = new_canvas(path)
    x = 25 * mm
    c.setFont("LSans", 14)
    c.drawString(x, A4_H - 40 * mm, ch["course"])
    c.drawString(x, A4_H - 47 * mm, ch["unit"])
    c.setLineWidth(1.5)
    c.line(x, A4_H - 55 * mm, A4_W - x, A4_H - 55 * mm)
    size = 30
    while pdfmetrics.stringWidth(ch["chapter"], "LSansB", size) > A4_W - 2 * x:
        size -= 1
    c.setFont("LSansB", size)
    c.drawString(x, A4_H - 80 * mm, ch["chapter"])
    c.setFont("LSansB", 22)
    c.drawString(x, A4_H - 95 * mm, "Practice booklet")
    c.setFont("LSans", 14)
    c.setLineWidth(0.8)
    for i, label in enumerate(["Name", "Class"]):
        y = A4_H - 135 * mm - i * 20 * mm
        c.drawString(x, y, label)
        c.line(x + 18 * mm, y - 1.5, A4_W - x, y - 1.5)
    c.setFont("LSans", 9)
    c.drawString(x, 22 * mm, ch["source_note"])
    c.showPage()
    c.save()


def draw_contents(path, ch, rows):
    c = new_canvas(path)
    x, right = 25 * mm, A4_W - 25 * mm
    c.setFont("LSansB", 22)
    c.drawString(x, A4_H - 35 * mm, "Contents")
    c.setFont("LSans", 10)
    c.drawRightString(right, A4_H - 50 * mm, "Page")
    c.setFont("LSans", 13)
    y = A4_H - 60 * mm
    for title, page in rows:
        c.drawString(x, y, title)
        c.drawRightString(right, y, str(page))
        tw = pdfmetrics.stringWidth(title, "LSans", 13)
        c.setDash(1, 3)
        c.setLineWidth(0.5)
        c.line(x + tw + 3 * mm, y + 1, right - 10 * mm, y + 1)
        c.setDash()
        y -= 11 * mm
    c.showPage()
    c.save()


def ruled(c, top, bottom, x0, x1, gap=8 * mm, width=0.4):
    c.setLineWidth(width)
    c.setStrokeGray(0.55)
    y = top
    last = top
    while y >= bottom:
        c.line(x0, y, x1, y)
        last = y
        y -= gap
    c.setStrokeGray(0)
    return last


def draw_corrections(path, corrections):
    c = new_canvas(path)
    x, right = 25 * mm, A4_W - 25 * mm
    c.setFont("LSansB", 22)
    c.drawString(x, A4_H - 35 * mm, "Corrections")
    c.setFont("LSans", 12)
    y = A4_H - 50 * mm
    if corrections:
        for where, text in corrections:
            c.setFont("LSansB", 12)
            c.drawString(x, y, where)
            c.setFont("LSans", 12)
            c.drawString(x + 45 * mm, y, text)
            y -= 9 * mm
        y -= 6 * mm
        c.drawString(x, y, "More corrections from class:")
        y -= 8 * mm
    else:
        c.drawString(x, y, "Write any corrections your teacher gives you here.")
        y -= 14 * mm
    # three columns: page, question, correction
    col_q, col_c = x + 22 * mm, x + 44 * mm
    c.setFont("LSansB", 11)
    c.drawString(x, y, "Page")
    c.drawString(col_q, y, "Question")
    c.drawString(col_c, y, "Correction")
    y -= 4 * mm
    last = ruled(c, y, 25 * mm, x, right)
    c.setLineWidth(0.4)
    c.setStrokeGray(0.55)
    c.line(col_q - 3 * mm, y, col_q - 3 * mm, last)
    c.line(col_c - 3 * mm, y, col_c - 3 * mm, last)
    c.setStrokeGray(0)
    c.showPage()
    c.save()


def draw_notes(path):
    c = new_canvas(path)
    x, right = 25 * mm, A4_W - 25 * mm
    c.setFont("LSansB", 16)
    c.drawString(x, A4_H - 30 * mm, "Notes")
    ruled(c, A4_H - 42 * mm, 25 * mm, x, right)
    c.showPage()
    c.save()


def number_overlay(path, n):
    c = new_canvas(path)
    c.setFont("LSans", NUM_SIZE)
    c.drawCentredString(A4_W / 2, NUM_BASELINE, f"Booklet page {n}")
    c.showPage()
    c.save()
    w = pdfmetrics.stringWidth(f"Booklet page {n}", "LSans", NUM_SIZE)
    # bbox in pdfplumber coordinates (top-down), with a 4 pt safety margin
    return (A4_W / 2 - w / 2 - 4, A4_H - NUM_BASELINE - NUM_SIZE - 4,
            A4_W / 2 + w / 2 + 4, A4_H - NUM_BASELINE + 3 + 4)


# ---------------------------------------------------------------- helpers
def to_exact_a4(page):
    """LibreOffice writes Word's A4 (11906 x 16838 twips) as 595.30 x 841.89 pt,
    0.01 mm wider than A4. Scale to exactly 210 x 297 mm."""
    w, h = float(page.mediabox.width), float(page.mediabox.height)
    if abs(w - A4_W) > 0.001 or abs(h - A4_H) > 0.001:
        if abs(w - A4_W) > 3 or abs(h - A4_H) > 3:
            sys.exit(f"Page is not A4: {w} x {h} pt")
        page.add_transformation(Transformation().scale(A4_W / w, A4_H / h))
    box = RectangleObject([0, 0, A4_W, A4_H])
    page.mediabox = box
    page.cropbox = box
    page.trimbox = box
    page.bleedbox = box
    page.artbox = box
    return page


def text_boxes(pdf_path, pageno):
    with pdfplumber.open(pdf_path) as pdf:
        p = pdf.pages[pageno]
        return [(w["x0"], w["top"], w["x1"], w["bottom"], w["text"]) for w in p.extract_words()]


def page_is_empty(pdf_path, pageno, header_bottom=90, footer_top=790):
    """True if a worksheet page has no words and no pictures between the running
    header and the footer."""
    with pdfplumber.open(pdf_path) as pdf:
        p = pdf.pages[pageno]
        words = [w for w in p.extract_words() if header_bottom < w["top"] < footer_top]
        pics = [im for im in p.images if im["bottom"] > header_bottom and im["top"] < footer_top]
        rects = [r for r in p.rects + p.lines if r["top"] > header_bottom and r["bottom"] < footer_top]
        return not words and not pics and not rects


def question_marks(pdf_path):
    """Find question numbers and part letters on each page of a worksheet PDF.
    Question numbers sit at the left margin; parts are a lone letter just inside."""
    found = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, p in enumerate(pdf.pages):
            words = p.extract_words(extra_attrs=["fontname"])
            lines = {}
            for w in words:
                lines.setdefault(round(w["top"]), []).append(w)
            for top in sorted(lines):
                ws = sorted(lines[top], key=lambda w: w["x0"])
                first = ws[0]
                # a question number may sit alone on its line when part a starts below it
                if 70 <= first["x0"] <= 76 and re.fullmatch(r"\d{1,2}", first["text"]) and top < 780:
                    found.append((i, "Q", first["text"]))
                elif 85 <= first["x0"] <= 125 and re.fullmatch(r"[a-h]", first["text"]):
                    found.append((i, "part", first["text"]))
    return found


# ---------------------------------------------------------------- main build
def main():
    keep = "--keep" in sys.argv
    ch = CHAPTER
    out_pdf = HERE / ch["output"]
    tmp = Path(tempfile.mkdtemp(prefix="booklet_"))
    (tmp / "fonts.conf").write_text(FONTS_CONF)
    build = tmp / "build"
    build.mkdir()
    png_dir = HERE / "png"
    if png_dir.exists():
        for f in png_dir.glob("*.png"):
            f.unlink()
    png_dir.mkdir(exist_ok=True)

    if not shutil.which("soffice"):
        sys.exit("soffice not found")
    if not list(Path("/usr/lib/libreoffice/program").glob("libsmlo.so")):
        sys.exit("LibreOffice Math is missing (apt-get install libreoffice-math); "
                 "Word equations would drop out of the worksheets.")

    # 1-2. worksheets to PDF
    for ws in ch["worksheets"]:
        dst = build / (ws["code"] + ".docx")
        ws["word_pages"], notes = prepare_docx(ws["docx"], dst)
        ws["pdf"] = convert(dst, build, tmp)
        total = len(PdfReader(ws["pdf"]).pages)
        ws["keep"] = list(range(total))
        # A trailing page holding only empty paragraphs (LibreOffice lays lines out a
        # few points taller than Word) is dropped; it has no content.
        while len(ws["keep"]) > 1 and page_is_empty(ws["pdf"], ws["keep"][-1]):
            dropped = ws["keep"].pop()
            log(f"  {ws['code']}: dropped empty trailing page {dropped + 1}")
        ws["n"] = len(ws["keep"])
        log(f"{ws['code']}: {total} pages from LibreOffice, {ws['n']} used "
            f"(Word saved it as {ws['word_pages']}); " + "; ".join(notes))
        if ws["word_pages"] and ws["word_pages"] != ws["n"]:
            log(f"  WARNING: page count differs from Word for {ws['code']}")

    # 4. plan
    plan = [("cover", None), ("contents", None), ("corrections", None)]
    for ws in ch["worksheets"]:
        if len(plan) % 2 == 1:          # next page would be even: pad
            plan.append(("notes", None))
        ws["start"] = len(plan) + 1
        for k in ws["keep"]:
            plan.append(("ws", (ws, k)))
        ws["end"] = len(plan)
    while len(plan) % ch.get("pad_to", 2):
        plan.append(("notes", None))
    corr_page = 3
    rows = [("Corrections", corr_page)] + [(ws["title"], ws["start"]) for ws in ch["worksheets"]]

    # 3. our pages
    draw_cover(build / "cover.pdf", ch)
    draw_contents(build / "contents.pdf", ch, rows)
    draw_corrections(build / "corrections.pdf", ch["corrections"])
    draw_notes(build / "notes.pdf")

    writer = PdfWriter()
    clash = []
    for idx, (kind, data) in enumerate(plan, start=1):
        if kind == "ws":
            ws, k = data
            src_pdf, src_page = ws["pdf"], k
        else:
            src_pdf, src_page = build / f"{kind}.pdf", 0
        page = PdfReader(src_pdf).pages[src_page]
        page = to_exact_a4(page)
        num_pdf = build / f"num{idx}.pdf"
        nb = number_overlay(num_pdf, idx)
        # collision check against everything already on the source page
        for (x0, t, x1, b, txt) in text_boxes(src_pdf, src_page):
            if x0 < nb[2] and x1 > nb[0] and t < nb[3] and b > nb[1]:
                clash.append((idx, txt))
        page.merge_page(PdfReader(num_pdf).pages[0])
        writer.add_page(page)
    writer.add_metadata({"/Title": f"{ch['chapter']} Practice booklet"})
    with open(out_pdf, "wb") as f:
        writer.write(f)

    # 5. checks
    problems = []
    r = PdfReader(out_pdf)
    if len(r.pages) != len(plan):
        problems.append("page count mismatch")
    if len(r.pages) % 2:
        problems.append("odd page count")
    for i, p in enumerate(r.pages, 1):
        w, h = float(p.mediabox.width), float(p.mediabox.height)
        if abs(w / mm - 210) > 0.005 or abs(h / mm - 297) > 0.005:
            problems.append(f"page {i} is {w / mm:.3f} x {h / mm:.3f} mm")
    if clash:
        problems.append(f"page number overlaps text: {clash}")
    with pdfplumber.open(out_pdf) as pdf:
        for ws in ch["worksheets"]:
            t = pdf.pages[ws["start"] - 1].extract_text() or ""
            if f"Worksheet {ws['code']}" not in t:
                problems.append(f"contents says {ws['code']} starts on {ws['start']} but that page does not show it")
            if ws["start"] % 2 == 0:
                problems.append(f"{ws['code']} starts on an even page")
        for i, pg in enumerate(pdf.pages, 1):
            t = pg.extract_text() or ""
            if f"Booklet page {i}" not in t:
                problems.append(f"page {i} number missing")
    ours = [ch["course"], ch["unit"], ch["chapter"], ch["source_note"], "Practice booklet", "Contents",
            "Corrections", "Notes", "Write any corrections your teacher gives you here.",
            "More corrections from class:", "Booklet page"] + [t for t, _ in rows] \
        + [a + b for a, b in ch["corrections"]]
    for s in ours:
        if "–" in s or "—" in s:
            problems.append(f"dash in our text: {s}")

    # page map
    lines = [f"# {ch['chapter']} practice booklet: page map", "",
             f"File: `{ch['output']}`, {len(plan)} pages, A4, print double-sided.", "",
             "Each page shows \"Booklet page N\" at the bottom centre. The small number at the "
             "bottom right is Cambridge's own worksheet page number; ignore it when pointing students "
             "to a page. " + ch.get("map_note", ""), "",
             "| Booklet page | Content |", "|---|---|"]
    for idx, (kind, data) in enumerate(plan, 1):
        if kind == "ws":
            ws, k = data
            lines.append(f"| {idx} | {ws['title']}, page {k + 1} of {ws['n']} |")
        else:
            lines.append(f"| {idx} | {kind.capitalize()} |")
    for ws in ch["worksheets"]:
        lines += ["", f"## {ws['title']}", "", f"Booklet pages {ws['start']} to {ws['end']}.", "",
                  "| Question | Booklet page | Parts (page) |", "|---|---|---|"]
        q, parts, rowsq = None, [], []
        for (pi, kind, label) in question_marks(ws["pdf"]):
            if pi not in ws["keep"]:
                continue
            bp = ws["start"] + ws["keep"].index(pi)
            if kind == "Q":
                if q:
                    rowsq.append((q, parts))
                q, parts = (label, bp), []
            elif q:
                parts.append((label, bp))
        if q:
            rowsq.append((q, parts))
        for (label, bp), parts in rowsq:
            pages_q = sorted({bp} | {p for _, p in parts})
            pt = ", ".join(f"{a} ({p})" for a, p in parts) or ""
            span = str(bp) if len(pages_q) == 1 else f"{pages_q[0]} to {pages_q[-1]}"
            lines.append(f"| Q{label} | {span} | {pt} |")
    (HERE / "page-map.md").write_text("\n".join(lines) + "\n")

    # renders
    subprocess.run(["pdftoppm", "-r", "110", "-png", str(out_pdf), str(png_dir / "page")], check=True)

    if keep:
        kd = HERE / "build"
        if kd.exists():
            shutil.rmtree(kd)
        shutil.copytree(build, kd)
    shutil.rmtree(tmp, ignore_errors=True)

    log(f"\nWrote {out_pdf} ({len(plan)} pages)")
    for idx, (kind, data) in enumerate(plan, 1):
        log(f"  {idx:2d}  " + (f"{data[0]['title']} p{data[1] + 1}" if kind == "ws" else kind))
    log("Contents: " + "; ".join(f"{t} {p}" for t, p in rows))
    if problems:
        log("PROBLEMS:\n  " + "\n  ".join(problems))
        sys.exit(1)
    log("All checks passed.")


if __name__ == "__main__":
    main()
