#!/usr/bin/env python3
"""Build the one-page chapter summary (reference book last page) for one chapter.

Usage:
  python3 make_svgs.py                      # own diagrams -> svg/ (run once, or after editing)
  python3 build.py data/ch01.json [--vendor DIR] [--out DIR] [--no-pdf]

One data file per chapter (data/chNN.json) + one template (template.html).
The data file holds named content blocks and one or more page layouts ("variants").
Each variant writes  "ChNN Summary<suffix>.html" and ".pdf", and png/<name>-<page>.png at 150 dpi.
Then it runs the checks: pages, page size, overflow, .katex-error, notation, dashes,
smallest font size, and which success criteria each variant covers.

Block types (text may hold **bold** and $maths$):
  {"sec": "1A", "name": "...", "crit": "1A.1 to 1A.6"}   section heading
  {"sub": "..."}                                          small heading
  {"pts": ["...", ...], "crit": [...]}                    dot points
  {"fm": ["$v = f\\lambda$", ...], "where": [["$v$", "wave speed (m/s)"], ...], "crit": [...]}
  {"svg": "wave", "w": 88, "cap": "..."}                  own diagram from svg/<name>.svg
  {"img": "img/x.png", "w": 70, "cap": "..."}             cropped Cambridge figure
  {"table": {"head": [...], "rows": [[...], ...]}, "note": "...", "crit": [...]}
  {"side": ["blockA", "blockB"], "cols": "1fr 40mm"}       two blocks side by side
Layout rows: {"cols": [["id", ...], ["id", ...]], "w": "1fr 1fr"} or {"full": ["id", ...]}.
"""
import argparse, base64, html, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VENDOR = "/home/claude/physics/tools/interactives/vendor"
CHROME = "/usr/bin/google-chrome"
MARGIN = "9mm 10mm 9mm 10mm"     # top right bottom left
PAGE_H_MM = 297 - 9 - 9


# ---------- maths ----------
def render_math(strings, vendor):
    if not strings:
        return []
    js = ("const k=require(process.argv[1]);let d='';process.stdin.on('data',c=>d+=c);"
          "process.stdin.on('end',()=>{const a=JSON.parse(d);"
          "console.log(JSON.stringify(a.map(s=>k.renderToString(s,{throwOnError:false,output:'html'}))));});")
    r = subprocess.run(["node", "-e", js, os.path.join(vendor, "katex.min.js")],
                       input=json.dumps(strings), capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


MATH = re.compile(r"\$(.+?)\$")


class Maths:
    def __init__(self, vendor):
        self.vendor, self.cache = vendor, {}

    def prepare(self, texts):
        bag = sorted({m.group(1) for t in texts for m in MATH.finditer(t or "")} - set(self.cache))
        for s, h in zip(bag, render_math(bag, self.vendor)):
            self.cache[s] = h

    def __call__(self, text):
        out, last = [], 0
        for m in MATH.finditer(text or ""):
            out.append(fmt(text[last:m.start()]))
            out.append(self.cache[m.group(1)])
            last = m.end()
        out.append(fmt((text or "")[last:]))
        return "".join(out)


def fmt(s):
    s = html.escape(s, quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def all_text(obj):
    """Every string in the data (for maths pre-rendering and checks)."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, list):
        for x in obj:
            yield from all_text(x)
    elif isinstance(obj, dict):
        for x in obj.values():
            yield from all_text(x)


# ---------- assets ----------
def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def font_css(vendor):
    faces = [("Inter", 400, "inter-latin-400-normal.woff2"), ("Inter", 600, "inter-latin-600-normal.woff2"),
             ("Inter", 700, "inter-latin-700-normal.woff2"),
             ("Space Grotesk", 500, "space-grotesk-latin-500-normal.woff2"),
             ("Space Grotesk", 700, "space-grotesk-latin-700-normal.woff2")]
    return "\n".join(
        f"@font-face{{font-family:'{n}';font-weight:{w};src:url(data:font/woff2;base64,{b64(os.path.join(vendor, f))}) format('woff2');}}"
        for n, w, f in faces)


def katex_css(vendor):
    css = open(os.path.join(vendor, "katex.min.css")).read()

    def face(m):
        block = m.group(0)
        f = re.search(r"url\(fonts/(KaTeX_[A-Za-z0-9-]+)\.woff2\)", block)
        if not f or not os.path.exists(os.path.join(vendor, f.group(1) + ".woff2")):
            return ""
        data = b64(os.path.join(vendor, f.group(1) + ".woff2"))
        return re.sub(r"src:[^}]*", f"src:url(data:font/woff2;base64,{data}) format(\"woff2\")", block)

    return re.sub(r"@font-face\{[^}]*\}", face, css)


# ---------- blocks ----------
def block_html(b, blocks, M):
    if isinstance(b, str):
        b = blocks[b]
    if "sec" in b:
        cr = f'<span class="cr">{fmt(b["crit"])}</span>' if b.get("crit") else ""
        return f'<div class="sec"><span class="nm">{b["sec"]} {fmt(b["name"])}</span>{cr}</div>'
    if "sub" in b:
        return f'<div class="sh">{M(b["sub"])}</div>'
    if "pts" in b:
        return '<ul class="pts">' + "".join(f"<li>{M(p)}</li>" for p in b["pts"]) + "</ul>"
    if "fm" in b:
        eqs = "".join(f"<span>{M(e)}</span>" for e in b["fm"])
        lab = f'<span class="lab">{M(b["label"])}</span>' if b.get("label") else ""
        wh = ""
        if b.get("where"):
            wh = '<div class="where">' + "".join(f'<span class="s">{M(s)}</span><span>{M(t)}</span>' for s, t in b["where"]) + "</div>"
        return f'<div class="fm"><div class="eqs">{lab}{eqs}</div>{wh}</div>'
    if "svg" in b:
        s = open(os.path.join(HERE, "svg", b["svg"] + ".svg")).read()
        cap = f'<div class="cap">{M(b["cap"])}</div>' if b.get("cap") else ""
        return f'<div class="fig" data-fig="{b["svg"]}">{s}{cap}</div>'
    if "img" in b:
        cap = f'<div class="cap">{M(b["cap"])}</div>' if b.get("cap") else ""
        return (f'<div class="fig" data-fig="{os.path.basename(b["img"])}"><img src="data:image/png;base64,{b64(os.path.join(HERE, b["img"]))}" '
                f'style="width:{b["w"]}mm" alt="">{cap}</div>')
    if "table" in b:
        t = b["table"]
        head = "<tr>" + "".join(f'<th{" class=rh" if i == 0 else ""}>{M(h)}</th>' for i, h in enumerate(t["head"])) + "</tr>"
        rows = "".join("<tr>" + "".join(f'<td{" class=rh" if i == 0 else ""}>{M(c)}</td>' for i, c in enumerate(r)) + "</tr>"
                       for r in t["rows"])
        note = f'<div class="note">{M(b["note"])}</div>' if b.get("note") else ""
        cg = "<colgroup>" + "".join(f'<col style="width:{w}">' for w in t["widths"]) + "</colgroup>" if t.get("widths") else ""
        cap = f'<div class="note">{M(b["title"])}</div>' if b.get("title") else ""
        return f'{cap}<table class="tb">{cg}{head}{rows}</table>{note}'
    if "strip" in b:
        s = b["strip"]
        n = len(s["cells"])
        cells = "".join(f'<div class="cell"><div class="cn">{M(c[0])}</div><div>{M(c[1])}</div></div>' for c in s["cells"])
        def bl(labels, cls, lab):
            out = f'<span class="lab" style="left:0">{M(lab)}</span>' if lab else ""
            for k, l in enumerate(labels, start=1):
                x = 100 * k / n
                out += f'<span class="tk" style="left:{x:.3f}%"></span><span style="left:{x:.3f}%">{M(l)}</span>'
            return f'<div class="bl {cls}">{out}</div>'
        note = f'<div class="note">{M(b["note"])}</div>' if b.get("note") else ""
        return (f'<div class="strip">{bl(s["top"], "t", s.get("toplab"))}'
                f'<div class="cells" style="grid-template-columns:repeat({n},1fr)">{cells}</div>'
                f'{bl(s["bottom"], "b", s.get("botlab"))}</div>{note}')
    if "side" in b:
        inner = "".join(f"<div>{block_html(x, blocks, M)}</div>" for x in b["side"])
        return f'<div class="side" style="grid-template-columns:{b["cols"]}">{inner}</div>'
    raise ValueError(f"unknown block {b}")


def used_ids(rows, blocks):
    out = []

    def walk(x):
        if isinstance(x, str):
            out.append(x)
            if "side" in blocks[x]:
                for y in blocks[x]["side"]:
                    walk(y)
    for r in rows:
        for col in r.get("cols", []):
            for x in col:
                walk(x)
        for x in r.get("full", []):
            walk(x)
    return out


def sheet_html(d, sheet, M, n_sheets, i):
    blocks = d["blocks"]
    out = [f'<div class="sheet" style="height:{PAGE_H_MM - 0.5}mm;display:flex;flex-direction:column">']
    if i == 0:
        out.append(f'<div class="top"><div><h1>Chapter {d["chapter"]} summary</h1>'
                   f'<div class="sub">{fmt(d["course"])}. Chapter {d["chapter"]}: {fmt(d["name"])}</div></div>'
                   f'<div class="name">Name<span></span></div></div>')
        if d.get("consts"):
            out.append('<div class="consts"><span class="ch">Values</span>' + "".join(f'<span class="c">{M(c)}</span>' for c in d["consts"]) + "</div>")
    else:
        out.append(f'<div class="top"><div><h1 style="font-size:13pt">Chapter {d["chapter"]} summary (continued)</h1></div>'
                   f'<div class="name">Name<span></span></div></div>')
    out.append('<div class="body" style="flex:1 1 auto;min-height:0">')
    for r in sheet["rows"]:
        if "full" in r:
            out.append('<div class="row full">' + "".join(block_html(x, blocks, M) for x in r["full"]) + "</div>")
        else:
            cols = "".join('<div class="col">' + "".join(block_html(x, blocks, M) for x in c) + "</div>" for c in r["cols"])
            out.append(f'<div class="row" style="grid-template-columns:{r.get("w", "1fr 1fr")}">{cols}</div>')
    out.append("</div>")
    page_no = f"Page {i + 1} of {n_sheets}" if n_sheets > 1 else ""
    out.append(f'<div class="foot"><span>{M(d["credit"])}</span><span>{page_no}</span></div>')
    out.append("</div>")
    return "\n".join(out)


def build_variant(d, v, M, template, fonts, kcss):
    body = "\n".join(sheet_html(d, s, M, len(v["sheets"]), i) for i, s in enumerate(v["sheets"]))
    return (template.replace("{{TITLE}}", html.escape(f'Chapter {d["chapter"]} summary'))
            .replace("{{FONTS}}", fonts).replace("{{KATEX_CSS}}", kcss).replace("{{MARGIN}}", MARGIN)
            .replace("{{FONT}}", v.get("font", "8.6pt")).replace("{{LH}}", v.get("lh", "1.25"))
            .replace("{{LI}}", v.get("li", "0.35mm")).replace("{{GAP}}", v.get("gap", "6mm"))
            .replace("{{ROWGAP}}", v.get("rowgap", "2.2mm")).replace("{{BODY}}", body))


# ---------- criteria coverage ----------
def coverage(d, v):
    crit_list = [c["id"] for c in json.load(open(d["index"]))["criteria"]]
    texts = {c["id"]: c["text"] for c in json.load(open(d["index"]))["criteria"]}
    where = {c: [] for c in crit_list}
    for s in v["sheets"]:
        for bid in used_ids(s["rows"], d["blocks"]):
            for c in d["blocks"][bid].get("crit", []) if isinstance(d["blocks"][bid].get("crit"), list) else []:
                where.setdefault(c, []).append(bid)
    return crit_list, texts, where


# ---------- pdf and checks ----------
def to_pdf_and_check(out, name, d):
    from playwright.sync_api import sync_playwright
    path = os.path.join(out, name + ".html")
    pdf = os.path.join(out, name + ".pdf")
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        # viewport = A4 width less the side margins, so on-screen layout matches the printed page
        pg = b.new_page(viewport={"width": round((210 - 20) / 25.4 * 96), "height": round(PAGE_H_MM / 25.4 * 96)})
        pg.goto("file://" + path)
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        pg.emulate_media(media="print")
        pg.pdf(path=pdf, prefer_css_page_size=True, print_background=True)
        res["katex_errors"] = pg.evaluate("document.querySelectorAll('.katex-error').length")
        # spare space under the lowest piece of content on each page, per column (negative = overflow)
        res["spare_mm"] = pg.evaluate("""() => [...document.querySelectorAll('.sheet .body')].map(e => {
            const bot = e.getBoundingClientRect().bottom; const mm = px => (px * 25.4 / 96).toFixed(1);
            const last = el => Math.max(...[...el.querySelectorAll('*')].filter(x => !x.closest('svg') || x.tagName==='svg').map(x => x.getBoundingClientRect().bottom));
            const rows = [...e.children]; const lastRow = rows[rows.length-1];
            const cols = lastRow.classList.contains('full') ? [lastRow] : [...lastRow.children];
            return cols.map(c => mm(bot - last(c))).join(' / '); })""")
        res["overflow"] = pg.evaluate("""() => [...document.querySelectorAll('.sheet')].map(e => e.scrollHeight - e.clientHeight)""")
        res["hclip"] = pg.evaluate("""() => [...document.querySelectorAll('.sheet *')].filter(e => !e.closest('svg') && !e.closest('.katex')
            && e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflow !== 'visible').map(e => e.className).slice(0, 10)""")
        # smallest font: ordinary text (outside KaTeX and SVG), KaTeX text, SVG text (converted to pt)
        res["fonts"] = pg.evaluate("""() => {
            const pt = px => px * 72 / 96;
            let body = 99, math = 99, mathEl = '', svgMin = 99;
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            while (walker.nextNode()) {
                const n = walker.currentNode; if (!n.textContent.replace(/[\\u200b\\s]/g,'')) continue;
                const el = n.parentElement; if (el.closest('style') || el.closest('.katex-mathml')) continue;
                if (el.closest('svg')) {
                    const t = el.closest('text') || el; const r = t.getBoundingClientRect();
                    const fs = parseFloat(getComputedStyle(el).fontSize);
                    const svg = el.closest('svg'); const sc = svg.getBoundingClientRect().width / svg.viewBox.baseVal.width;
                    svgMin = Math.min(svgMin, pt(fs * sc)); continue; }
                const fs = pt(parseFloat(getComputedStyle(el).fontSize));
                if (el.closest('.katex')) { if (fs < math) { math = fs; mathEl = n.textContent; } }
                else body = Math.min(body, fs);
            }
            return {body: body.toFixed(2), math: math.toFixed(2), mathEl, svg: svgMin.toFixed(2)};
        }""")
        res["text"] = pg.evaluate("""() => { const c = document.body.cloneNode(true);
            c.querySelectorAll('.katex-mathml, style').forEach(e => e.remove()); return c.innerText; }""")
        res["figs"] = pg.evaluate("""() => [...document.querySelectorAll('.fig')].map(f => {
            const g = f.querySelector('svg, img').getBoundingClientRect();
            return [f.dataset.fig, (g.width*25.4/96).toFixed(1), (g.height*25.4/96).toFixed(1)]; })""")
        b.close()
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    res["pages"] = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    res["size"] = re.search(r"Page size:\s+(.+)", info).group(1).strip()
    pngdir = os.path.join(out, "png")
    os.makedirs(pngdir, exist_ok=True)
    for f in os.listdir(pngdir):
        if f.startswith(name + "-"):
            os.remove(os.path.join(pngdir, f))
    subprocess.run(["pdftoppm", "-r", "150", "-png", pdf, os.path.join(pngdir, name)], check=True)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--vendor", default=DEFAULT_VENDOR)
    ap.add_argument("--out", default=HERE)
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()

    d = json.load(open(a.data))
    M = Maths(a.vendor)
    M.prepare(list(all_text(d)))
    template = open(os.path.join(HERE, "template.html")).read()
    fonts, kcss = font_css(a.vendor), katex_css(a.vendor)
    nn = f'{d["chapter"]:02d}'
    for key, v in d["variants"].items():
        name = f"Ch{nn} Summary{v.get('suffix', '')}"
        open(os.path.join(a.out, name + ".html"), "w").write(build_variant(d, v, M, template, fonts, kcss))
        print(f"\n=== {name}  ({key})")
        crit_list, texts, where = coverage(d, v)
        miss = [c for c in crit_list if not where.get(c)]
        print("criteria covered: " + f"{len(crit_list) - len(miss)} of {len(crit_list)}" + (f"  MISSING {miss}" if miss else ""))
        for c in crit_list:
            print(f"   {c:6} {', '.join(sorted(set(where[c]))) or '-'}")
        if a.no_pdf:
            continue
        r = to_pdf_and_check(a.out, name, d)
        print(f"pages={r['pages']} (want {len(v['sheets'])})  size={r['size']}  katex-error={r['katex_errors']}")
        print(f"sheet overflow px={r['overflow']}  spare mm under last row (per column)={r['spare_mm']}  h-clipped={r['hclip']}")
        print(f"smallest font: text {r['fonts']['body']} pt, maths {r['fonts']['math']} pt ('{r['fonts']['mathEl']}'), svg labels {r['fonts']['svg']} pt")
        print("figures (name, width mm, height mm): " + "; ".join(" ".join(f) for f in r["figs"]))
        t = r["text"]
        for label, pat in [("m s^-1", r"m\s*s\s*[−⁻\-–]\s*[1¹]"), ("÷", "÷"), ("em/en dash", "[—–]")]:
            hits = re.findall(pat, t)
            print(f"   {label}: {len(hits)}" + (f" {hits[:5]}" if hits else ""))


if __name__ == "__main__":
    main()
