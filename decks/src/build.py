# Builds one self-contained chapter deck (fonts, KaTeX, engine and labs all inside one HTML file).
#   python3 build.py <vendor folder> <chapter.json> [output folder]
# The vendor folder holds Inter, Space Grotesk and KaTeX (tools/interactives/vendor in the repo).
# chapter.json lists the section files in teaching order; see decks/README.md for the format.
import os,re,json,base64,sys
H=os.path.dirname(os.path.abspath(__file__))
if len(sys.argv)<3:sys.exit(__doc__ or 'usage: python3 build.py <vendor folder> <chapter.json> [output folder]')
V,CJ=sys.argv[1],os.path.abspath(sys.argv[2]);OUT=os.path.abspath(sys.argv[3]) if len(sys.argv)>3 else os.path.join(H,'..','out')
b64=lambda p:base64.b64encode(open(p,'rb').read()).decode()
FONTS=''.join(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b64(os.path.join(V,f))}) format('woff2')}}" for fam,w,f in [('Inter',400,'inter-latin-400-normal.woff2'),('Inter',600,'inter-latin-600-normal.woff2'),('Inter',700,'inter-latin-700-normal.woff2'),('Space Grotesk',500,'space-grotesk-latin-500-normal.woff2'),('Space Grotesk',700,'space-grotesk-latin-700-normal.woff2')])
kcss=re.sub(r'@font-face\{[^}]*\}','',open(os.path.join(V,'katex.min.css')).read())+''.join(f"@font-face{{font-family:'{f[:-6].rsplit('-',1)[0]}';font-style:{'italic' if 'Italic' in f else 'normal'};font-weight:{'bold' if 'Bold' in f else 'normal'};src:url(data:font/woff2;base64,{b64(os.path.join(V,f))}) format('woff2')}}" for f in sorted(os.listdir(V)) if f.startswith('KaTeX_'))
FONTS+="@font-face{font-family:'Patrick Hand';src:url(data:font/woff2;base64,"+b64(os.path.join(H,'patrick-hand-latin-400-normal.woff2'))+") format('woff2')}"
FONTS+="@font-face{font-family:'Kalam';font-weight:700;src:url(data:font/woff2;base64,"+b64(os.path.join(H,'kalam-latin-700-normal.woff2'))+") format('woff2')}"
rd=lambda p:open(p,encoding='utf-8').read()

ch=json.load(open(CJ,encoding='utf-8'));meta=[];body=[];problems=[]
for f in ch['sections']:
  src=rd(os.path.join(os.path.dirname(CJ),f))
  m=re.match(r'\s*<script type="application/json">(.*?)</script>(.*)',src,re.S)
  if not m:sys.exit(f'{f}: must start with <script type="application/json">{{"code":...,"title":...}}</script>')
  sec=json.loads(m.group(1));html=m.group(2);meta.append(sec)
  # checks: every book slide points at a page that exists and a stage that exists on it
  pages=re.findall(r'<div class="pagesrc"[^>]*>',html);parts=re.split(r'<div class="pagesrc"[^>]*>',html)[1:]
  stages=[set(int(b) for b in re.findall(r'class="bk"[^>]*data-b="(\d+)"',p)) for p in parts]
  for tag in re.findall(r'<section class="slide[^"]*"[^>]*data-mode="book"[^>]*>',html):
    pg=int((re.search(r'data-page="(\d+)"',tag) or [0,1])[1]);b=int(re.search(r'data-b="(\d+)"',tag)[1])
    if pg>len(pages):problems.append(f'{sec["code"]}: book slide asks for page {pg}, section has {len(pages)}')
    elif b not in (0,99) and b not in stages[pg-1]:problems.append(f'{sec["code"]}: page {pg} has no part with data-b="{b}"')
  # students' text: no em or en dashes, m/s not m s^-1, fractions not the divide sign
  txt=html  # tags too: data-do and data-loop text is shown to students
  for bad,why in [('—','em dash'),('–','en dash'),('÷','divide sign'),('m s⁻¹','m s⁻¹ (write m/s)'),('m s^{-1}','m s^{-1} (write m/s)')]:
    if bad in txt:problems.append(f'{sec["code"]}: {why} in the text')
  body.append(f'<div class="sec" data-sec="{sec["code"]}">{html}</div>')
for p in problems:print('PROBLEM',p)
if problems:sys.exit(1)
cfg='<script>const CHAPTER='+json.dumps({k:v for k,v in ch.items() if k!='sections'}|{'sections':meta},ensure_ascii=False).replace('</','<\\/')+';</script>'
name=ch.get('file',f"Chapter {ch['code']} deck")
page=f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Chapter {ch['code']} {ch['title']}</title>
<style>{FONTS}{kcss}{rd(os.path.join(H,'engine.css'))}</style></head><body><div id="stage">{''.join(body)}</div>
<script>{rd(os.path.join(V,'katex.min.js'))}</script>{cfg}<script>{rd(os.path.join(H,'engine.js'))}</script><script>{rd(os.path.join(H,'sims.js'))}
init();</script></body></html>"""
os.makedirs(OUT,exist_ok=True);out=os.path.join(OUT,name+'.html')
open(out,'w',encoding='utf-8').write(page);print(os.path.normpath(out),len(page)//1024,'KB,',len(meta),'sections')
