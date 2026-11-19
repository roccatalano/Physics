#!/usr/bin/env python3
"""Build the "I can do this" checklist for one chapter.

Usage:
  python3 build.py data/ch02.json [--vendor DIR] [--out DIR] [--no-pdf]

One data file per chapter (data/chNN.json) + one template (template.html).
Writes, for chapter NN:
  checklist-chNN-compact.html / .pdf   student copy, aims for one double-sided sheet
  checklist-chNN-roomy.html   / .pdf   student copy, more answer space
  checklist-chNN-answers.html / .pdf   teacher answers
  png/<name>-<page>.png                every page, for checking
Then runs the checks (page count, .katex-error, notation, dashes, rows split).

Data file fields per row: id, text, kind (mc | tf | short | prac), src, question,
optional stem, question2, options + opt_cols (1, 2 or 4), img + img_mm,
lines / lines_roomy (short), prac (prac name, may be empty), answer (teacher page).
Maths in $...$ is pre-rendered with KaTeX (node) so the HTML needs no script.
"""
import argparse, base64, html, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VENDOR = "/home/claude/physics/tools/interactives/vendor"
CHROME = "/usr/bin/google-chrome"

VARIANTS = {
    # compact: aims for one double-sided sheet; long MC options go two across
    "compact": {"line": "6.2mm", "pad": "0.7mm", "lines_key": "lines", "cols": "minmax(0,1fr) 11mm",
                "opt_min": 2, "font": "8.6pt", "lh": "1.25", "sec_break": False, "layout": "stacked"},
    # roomy: more writing space, options as Cambridge set them (one per line)
    "roomy":   {"line": "8mm",   "pad": "2.2mm", "lines_key": "lines_roomy", "cols": "52mm minmax(0,1fr) 12mm",
                "opt_min": 1, "font": "9.2pt", "lh": "1.32", "sec_break": True, "layout": "columns"},
}


# ---------- maths ----------
def render_math(strings, vendor):
    """Render a list of TeX strings with KaTeX in node. Returns list of HTML."""
    if not strings:
        return []
    js = (
        "const k=require(process.argv[1]);let d='';process.stdin.on('data',c=>d+=c);"
        "process.stdin.on('end',()=>{const a=JSON.parse(d);"
        "console.log(JSON.stringify(a.map(s=>k.renderToString(s,{throwOnError:false,output:'html'}))));});"
    )
    r = subprocess.run(["node", "-e", js, os.path.join(vendor, "katex.min.js")],
                       input=json.dumps(strings), capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


class Maths:
    def __init__(self, vendor):
        self.vendor, self.cache = vendor, {}

    def collect(self, text, bag):
        for m in re.finditer(r"\$(.+?)\$", text or ""):
            bag.add(m.group(1))

    def prepare(self, bag):
        todo = sorted(s for s in bag if s not in self.cache)
        for s, h in zip(todo, render_math(todo, self.vendor)):
            self.cache[s] = h

    def __call__(self, text):
        """Text with $..$ maths and <br> allowed; everything else escaped."""
        if text is None:
            return ""
        out, last = [], 0
        for m in re.finditer(r"\$(.+?)\$", text):
            out.append(esc(text[last:m.start()]))
            out.append(self.cache[m.group(1)])
            last = m.end()
        out.append(esc(text[last:]))
        return "".join(out)


def esc(s):
    return html.escape(s, quote=False).replace("&lt;br&gt;", "<br>")


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
            return ""  # font not shipped: drop the face (unused here)
        data = b64(os.path.join(vendor, f.group(1) + ".woff2"))
        return re.sub(r"src:[^}]*", f"src:url(data:font/woff2;base64,{data}) format(\"woff2\")", block)

    return re.sub(r"@font-face\{[^}]*\}", face, css)


def img_tag(row, base_dir, v):
    p = os.path.join(base_dir, row["img"])
    mm = row.get("img_mm_roomy" if v["layout"] == "columns" else "img_mm", row.get("img_mm", 60))
    return (f'<div class="qimg"><img src="data:image/png;base64,{b64(p)}" '
            f'style="width:{mm}mm" alt=""></div>')


# ---------- student copy ----------
def student_body(d, variant, M, base_dir):
    v = VARIANTS[variant]
    stacked = v["layout"] == "stacked"
    out = [f'<div class="top {v["layout"]}"><div><h1>{esc(d["title"])}</h1>'
           f'<div class="sub">{esc(d["course"])}. Chapter {d["chapter"]}: {esc(d["subtitle"])}</div></div>'
           f'<div class="name">Name<span></span></div></div>'
           f'<p class="how">' + "Answer the question. Tick the box when you can do it without help." + '</p>']
    for sec in d["sections"]:
        rows = [r for r in d["rows"] if r["id"].startswith(sec["code"] + ".")]
        brk = ' brk' if v["sec_break"] and sec is not d["sections"][0] else ''
        out.append(f'<div class="sec{brk}"><div class="sec-h"><div class="nm">{sec["code"]} {esc(sec["name"])}' + ('' if stacked else '<span class="ican">I can</span>') + '</div>'
                   + (f'<div class="lab tk">Done</div></div>' if stacked else f'<div class="lab">Show me</div><div class="lab tk">Done</div></div>'))
        # first column label sits under the section name: "I can"
        for r in rows:
            out.append(row_html(r, v, d, M, base_dir))
        out.append("</div>")
    return "\n".join(out)


def row_html(r, v, d, M, base_dir):
    crit = f'<div class="crit"><b>{r["id"]}</b>{M(r["text"])}</div>'
    if r["kind"] == "prac":
        name = f'<div class="pn">{esc(r["prac"])}</div>' if r.get("prac") else ""
        q = f'<div class="q prac">{name}<div>{esc(d["prac_text"])}</div></div>'
    else:
        main = []
        if r.get("stem"):
            main.append(f'<div class="stem">{M(r["stem"])}</div>')
        n = r.get(v["lines_key"], r.get("lines", 2))
        inline = r["kind"] == "tf" or (r["kind"] == "short" and n == 1 and r.get("inline"))
        if inline:
            # one-line answers sit on the same line as the question
            tail = '<span class="tf">T&nbsp;&nbsp;F</span>' if r["kind"] == "tf" else '<span class="iline"></span>'
            main.append(f'<div class="inl"><span>{M(r["question"])}</span>{tail}</div>')
        else:
            main.append(f'<div>{M(r["question"])}</div>')
        if r.get("question2"):
            main.append(f'<div style="margin-top:0.8mm">{M(r["question2"])}</div>')
        if r["kind"] == "mc":
            cols = max(r.get("opt_cols", 1), v["opt_min"])
            opts = "".join(f'<div class="opt"><span class="L">{"ABCD"[i]}</span><span>{M(o)}</span></div>'
                           for i, o in enumerate(r["options"]))
            main.append(f'<div class="opts c{cols}">{opts}</div>')
        elif r["kind"] == "short" and not inline:
            main.append('<div class="lines">' + "<div></div>" * n + "</div>")
        img = img_tag(r, base_dir, v) if r.get("img") else ""
        q = f'<div class="q"><div class="qwrap"><div class="qmain">{"".join(main)}</div>{img}</div></div>'
    if v["layout"] == "stacked":
        return (f'<div class="row" data-id="{r["id"]}"><div class="stk">{crit}{q}</div>'
                f'<div class="tick"><div class="box"></div></div></div>')
    return f'<div class="row" data-id="{r["id"]}">{crit}{q}<div class="tick"><div class="box"></div></div></div>'


def lower_first(s):
    # "Recognise wave motion" -> "recognise wave motion" after "I can:"
    return s[:1].lower() + s[1:] if s[:1].isupper() and not s[1:2].isupper() else s


# ---------- teacher copy ----------
def teacher_body(d, M):
    out = [f'<div class="top"><div><h1>{esc(d["title"])}: answers</h1>'
           f'<div class="sub">Teacher copy. {esc(d["course"])}. Chapter {d["chapter"]}: {esc(d["subtitle"])}</div></div></div>',
           '<table class="ans"><thead><tr><th>Criterion</th><th>Question</th><th>Answer</th></tr></thead><tbody>']
    for sec in d["sections"]:
        out.append(f'<tr class="secrow"><td colspan="3">{sec["code"]} {esc(sec["name"])}</td></tr>')
        for r in d["rows"]:
            if not r["id"].startswith(sec["code"] + "."):
                continue
            if r["kind"] == "prac":
                pr = esc(r["prac"]) if r.get("prac") else "No Cambridge prac in the index"
                out.append(f'<tr><td class="c">{r["id"]}</td><td class="s">Prac</td><td>{pr}. Tick when written up in the log book.</td></tr>')
            else:
                out.append(f'<tr><td class="c">{r["id"]}</td><td class="s">{esc(r["src"])}</td><td>{M(r["answer"])}</td></tr>')
    out.append("</tbody></table>")
    n = d["chapter"]
    out.append(f'<p class="foot">Questions: Cambridge VCE Physics Units 1&amp;2, Chapter {n} review questions, section questions and check-ins. '
               f'Answers checked against the Chapter {n} Suggested responses.</p>')
    return "\n".join(out)


# ---------- build ----------
def fill(template, title, body, fonts, kcss, v):
    return (template.replace("{{TITLE}}", esc(title)).replace("{{FONTS}}", fonts).replace("{{KATEX_CSS}}", kcss)
            .replace("{{COLS}}", v["cols"]).replace("{{PAD}}", v["pad"]).replace("{{LINE}}", v["line"]).replace("{{FONT}}", v["font"]).replace("{{LH}}", v["lh"])
            .replace("{{BODY}}", body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--vendor", default=DEFAULT_VENDOR)
    ap.add_argument("--out", default=HERE)
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()

    d = json.load(open(a.data))
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(a.data)))  # img/ paths are relative to the project folder
    M = Maths(a.vendor)
    bag = set()
    for r in d["rows"]:
        for k in ("text", "stem", "question", "question2", "answer"):
            M.collect(r.get(k), bag)
        for o in r.get("options", []):
            M.collect(o, bag)
    M.prepare(bag)

    template = open(os.path.join(HERE, "template.html")).read()
    fonts, kcss = font_css(a.vendor), katex_css(a.vendor)
    nn = f'{d["chapter"]:02d}'
    built = []
    for variant in VARIANTS:
        name = f"checklist-ch{nn}-{variant}"
        page = fill(template, d["title"], student_body(d, variant, M, base_dir), fonts, kcss, VARIANTS[variant])
        open(os.path.join(a.out, name + ".html"), "w").write(page)
        built.append(name)
    name = f"checklist-ch{nn}-answers"
    page = fill(template, d["title"] + ": answers", teacher_body(d, M), fonts, kcss, VARIANTS["compact"])
    open(os.path.join(a.out, name + ".html"), "w").write(page)
    built.append(name)

    if not a.no_pdf:
        to_pdf(a.out, built)
        check(a.out, built, d)


def to_pdf(out, names):
    from playwright.sync_api import sync_playwright
    os.makedirs(os.path.join(out, "png"), exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page()
        for n in names:
            pg.goto("file://" + os.path.join(out, n + ".html"))
            pg.wait_for_load_state("networkidle")
            pg.evaluate("document.fonts.ready")
            pg.pdf(path=os.path.join(out, n + ".pdf"), format="A4", prefer_css_page_size=True,
                   display_header_footer=True, header_template="<span></span>",
                   footer_template='<div style="font-size:7pt;width:100%;text-align:right;margin-right:12mm;font-family:sans-serif">'
                                   '<span class="pageNumber"></span> of <span class="totalPages"></span></div>',
                   margin={"top": "11mm", "bottom": "12mm", "left": "12mm", "right": "12mm"})
        b.close()
    for n in names:
        for f in os.listdir(os.path.join(out, "png")):
            if f.startswith(n + "-"):
                os.remove(os.path.join(out, "png", f))
        subprocess.run(["pdftoppm", "-r", "110", "-png", os.path.join(out, n + ".pdf"),
                        os.path.join(out, "png", n)], check=True)


def check(out, names, d):
    from playwright.sync_api import sync_playwright
    print("\nCHECKS")
    own_pat = [("m s⁻¹", re.compile(r"m\s*s\s*[−⁻\-–]\s*[1¹]")), ("÷", re.compile("÷")),
               ("em/en dash", re.compile("[—–]"))]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page()
        for n in names:
            pg.goto("file://" + os.path.join(out, n + ".html"))
            pg.emulate_media(media="print")
            errs = pg.evaluate("document.querySelectorAll('.katex-error').length")
            # visible text of our own wording: everything except question and option text
            own = pg.evaluate("""() => { const c = document.body.cloneNode(true);
                c.querySelectorAll('.q:not(.prac) .qmain, .ans td:nth-child(3) .katex-mathml, .katex-mathml').forEach(e => e.remove());
                return c.innerText; }""")
            allt = pg.evaluate("document.body.innerText")
            pages = subprocess.run(["pdfinfo", os.path.join(out, n + ".pdf")], capture_output=True, text=True).stdout
            pages = re.search(r"Pages:\s+(\d+)", pages).group(1)
            print(f"{n}: pages={pages} katex-error={errs}")
            for label, pat in own_pat:
                hits = pat.findall(own)
                if hits:
                    print(f"   OWN WORDING has {label}: {hits}")
                if pat.findall(allt) and not hits:
                    print(f"   (Cambridge text has {label}; see decisions)")
        b.close()
    # rows split across pages: each row's pdf text must sit on a single page
    for n in names[:2]:
        pdf = os.path.join(out, n + ".pdf")
        npages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
        where = {}
        for i in range(1, npages + 1):
            t = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "-layout", pdf, "-"], capture_output=True, text=True).stdout
            for r in d["rows"]:
                if re.search(r"(?<![\d.])" + re.escape(r["id"]) + r"(?!\d)", t):
                    where.setdefault(r["id"], []).append(i)
        miss = [r["id"] for r in d["rows"] if r["id"] not in where]
        multi = {k: v for k, v in where.items() if len(v) > 1}
        print(f"{n}: rows per page " + ", ".join(f"p{i}={sum(1 for v in where.values() if i in v)}" for i in range(1, npages + 1))
              + (f"  MISSING {miss}" if miss else "") + (f"  code seen on >1 page {multi}" if multi else ""))


if __name__ == "__main__":
    main()
