# Builds the Physics interactives: tools/interactives/src/<id>.html  ->  interactives/<id>.html (one self-contained,
# offline file each: fonts and KaTeX embedded, $...$ maths pre-rendered with KaTeX via node) + interactives/index.html.
# Each source file starts with a JSON header in <!-- --> (id, section, title, criteria, blurb), then the body HTML,
# then <script> for its own JS. Shared look and helpers: ix.css, ix.js. Embed in a slide with an iframe; add ?bare
# to hide the title, context line and footer.
# Usage: python3 tools/interactives/build.py
import os,re,json,base64,subprocess,glob,html
H=os.path.dirname(os.path.abspath(__file__));V=os.path.join(H,'vendor');OUT=os.path.join(H,'..','..','interactives')
b64=lambda f:base64.b64encode(open(os.path.join(V,f),'rb').read()).decode()
FONTS=''.join(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b64(f)}) format('woff2')}}"
 for fam,w,f in [('Inter',400,'inter-latin-400-normal.woff2'),('Inter',600,'inter-latin-600-normal.woff2'),('Inter',700,'inter-latin-700-normal.woff2'),
                 ('Space Grotesk',500,'space-grotesk-latin-500-normal.woff2'),('Space Grotesk',700,'space-grotesk-latin-700-normal.woff2')])
kcss=open(os.path.join(V,'katex.min.css')).read()
kfonts=[f for f in os.listdir(V) if f.startswith('KaTeX_')]
kcss=re.sub(r'@font-face\{[^}]*\}','',kcss)+''.join(f"@font-face{{font-family:'{f[:-6].rsplit('-',1)[0]}';font-style:{'italic' if 'Italic' in f else 'normal'};font-weight:{'bold' if 'Bold' in f else 'normal'};src:url(data:font/woff2;base64,{b64(f)}) format('woff2')}}" for f in kfonts)
CSS=open(os.path.join(H,'ix.css')).read();JS=open(os.path.join(H,'ix.js')).read()
def katex(src):
  parts=re.split(r'(\$[^$]+\$)',src);maths=[p[1:-1] for p in parts if p.startswith('$') and p.endswith('$') and len(p)>2]
  if not maths:return src
  js="const k=require(process.argv[1]);const m=JSON.parse(require('fs').readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(m.map(x=>k.renderToString(x,{throwOnError:true}))))"
  r=json.loads(subprocess.run(['node','-e',js,os.path.join(V,'katex.min.js')],input=json.dumps(maths),capture_output=True,text=True,check=True).stdout)
  it=iter(r);return ''.join(next(it) if p.startswith('$') and p.endswith('$') and len(p)>2 else p for p in parts)
os.makedirs(OUT,exist_ok=True);meta=[]
for f in sorted(glob.glob(os.path.join(H,'src','*.html'))):
  s=open(f).read();m=re.match(r'\s*<!--(.*?)-->',s,re.S);M=json.loads(m.group(1));s=s[m.end():]
  body,_,script=s.partition('<script>');script=script.rsplit('</script>',1)[0]
  body=katex(body)
  page=f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(M['section']+' · '+M['title'])}</title>
<style>{FONTS}{kcss}{CSS}</style></head><body><div id="stage"><svg id="bg" viewBox="0 0 1280 720"></svg><div class="tools"></div>
<div class="ix" style="--c:{M.get('colour','#7dd3fc')}"><div class="head"><div><div class="label">{html.escape(M['section'])} · Interactive</div><h1>{html.escape(M['title'])}</h1></div></div>
{body}</div><div class="foot"><span>{html.escape(M.get('source',''))}</span><span>Interactive by teacher</span></div></div>
<script>{JS}</script><script>{script}</script></body></html>"""
  open(os.path.join(OUT,M['id']+'.html'),'w').write(page);meta.append(M)
  print(M['id'],len(page)//1024,'KB')
json.dump(meta,open(os.path.join(OUT,'interactives.json'),'w'),indent=1,ensure_ascii=False)
cards=''.join(f'<a class="g" href="{m["id"]}.html" style="--c:{m.get("colour","#7dd3fc")}"><span>{html.escape(m["section"])} · {html.escape(", ".join(m.get("criteria",[])))}</span><b>{html.escape(m["title"])}</b><i>{html.escape(m.get("blurb",""))}</i></a>' for m in meta)
open(os.path.join(OUT,'index.html'),'w').write(f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Physics interactives</title><style>{FONTS}
body{{margin:0;background:#0d1330;color:#eef2ff;font-family:Inter,sans-serif;padding:40px}}h1{{font:700 40px 'Space Grotesk'}}p{{color:#a5b4d8;max-width:900px}}
.gr{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px;margin-top:24px}}.g{{background:#1a2150;border-left:7px solid var(--c);border-radius:16px;padding:16px 20px;color:inherit;text-decoration:none;display:flex;flex-direction:column;gap:6px}}.g:hover{{outline:2px solid var(--c)}}.g span{{font-size:13px;color:var(--c);font-weight:700;text-transform:uppercase;letter-spacing:.05em}}.g b{{font:700 22px 'Space Grotesk'}}.g i{{font-style:normal;color:#a5b4d8;font-size:15px}}code{{color:#fbb040}}</style></head><body>
<h1>Physics interactives</h1><p>Each one works offline and fills a 16:9 slide. Embed it in a deck with <code>&lt;iframe src="interactives/ID.html?bare"&gt;</code> (<code>?bare</code> hides the title, context line and footer). Space = pause, F = full screen.</p><div class="gr">{cards}</div></body></html>""")
