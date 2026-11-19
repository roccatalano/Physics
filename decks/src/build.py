# Builds three self-contained lesson files (fonts, KaTeX, engine and interactives all inside each file).
import os,re,base64,sys
H=os.path.dirname(os.path.abspath(__file__));V=sys.argv[1]  # folder holding the fonts and KaTeX
b64=lambda f:base64.b64encode(open(os.path.join(V,f),'rb').read()).decode()
FONTS=''.join(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b64(f)}) format('woff2')}}" for fam,w,f in [('Inter',400,'inter-latin-400-normal.woff2'),('Inter',600,'inter-latin-600-normal.woff2'),('Inter',700,'inter-latin-700-normal.woff2'),('Space Grotesk',500,'space-grotesk-latin-500-normal.woff2'),('Space Grotesk',700,'space-grotesk-latin-700-normal.woff2')])
kcss=re.sub(r'@font-face\{[^}]*\}','',open(os.path.join(V,'katex.min.css')).read())+''.join(f"@font-face{{font-family:'{f[:-6].rsplit('-',1)[0]}';font-style:{'italic' if 'Italic' in f else 'normal'};font-weight:{'bold' if 'Bold' in f else 'normal'};src:url(data:font/woff2;base64,{b64(f)}) format('woff2')}}" for f in os.listdir(V) if f.startswith('KaTeX_'))
FONTS+="@font-face{font-family:'Patrick Hand';src:url(data:font/woff2;base64,"+base64.b64encode(open(os.path.join(H,'patrick-hand-latin-400-normal.woff2'),'rb').read()).decode()+") format('woff2')}"
FONTS+="@font-face{font-family:'Kalam';font-weight:700;src:url(data:font/woff2;base64,"+base64.b64encode(open(os.path.join(H,'kalam-latin-700-normal.woff2'),'rb').read()).decode()+") format('woff2')}"
rd=lambda f:open(os.path.join(H,f),encoding='utf-8').read()
os.makedirs(os.path.join(H,'out'),exist_ok=True)
for src,name in [(a,b) for a,b in [('l1.html','Lesson 1 - 1A The properties of waves'),('l2.html','Lesson 2 - 1B Electromagnetic waves'),('l3.html',"Lesson 3 - 1C Refraction and Snell's law")] if len(sys.argv)<3 or a in sys.argv[2:]]:
  body=rd(src);cfg,body=re.match(r'(<script>.*?</script>)(.*)',body,re.S).groups()
  page=f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{name}</title>
<style>{FONTS}{kcss}{rd('engine.css')}</style></head><body><div id="stage">{body}</div>
<script>{open(os.path.join(V,'katex.min.js')).read()}</script>{cfg}<script>{rd('engine.js')}</script><script>{rd('sims.js')}
init();</script></body></html>"""
  open(os.path.join(H,'out',name+'.html'),'w',encoding='utf-8').write(page);print(name,len(page)//1024,'KB')
