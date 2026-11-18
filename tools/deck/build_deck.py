# Builds a lesson deck (and its Do now half-sheet) from a lesson recipe + the lesson index (data/index).
# Usage: python3 tools/deck/build_deck.py lessons/specs/<name>.json
# Recipe: {"name","title","unit","aos","aos_name","lesson","sections":[..],"slides":[{"type":..., ...}, ...]}
# Slide types (each may set "phase" and "min"; the first slide of a phase sets that phase's timer):
#   title · donow{items:[ids], labels:[..]} · goals{criteria:[ids]} · keyideas{glossary:[ids], formulas:[ids]}
#   apk{items:[{from, text, q, a}]} (own wording, marked own) · new{chunk, figure, points:[..]} · figure{figure}
#   interactive{id} · wedo{item, kib} · youtry{item, kib} · practice{rows:[[what, questions]]}
#   exit{items:[{crit, q}]} · prac{title, aim}
# Look: tools/deck/deck.css (+ interactives' ix.css fonts/KaTeX), behaviour: deck.js, background: interactives ix.js by AoS.
import os,re,json,sys,glob,base64,html,subprocess
H=os.path.dirname(os.path.abspath(__file__));R=os.path.join(H,'..','..');IXD=os.path.join(H,'..','interactives')
e=html.escape
sys.path.insert(0,IXD)
V=os.path.join(IXD,'vendor');b64=lambda p:base64.b64encode(open(p,'rb').read()).decode()
FONTS=''.join(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b64(os.path.join(V,f))}) format('woff2')}}"
 for fam,w,f in [('Inter',400,'inter-latin-400-normal.woff2'),('Inter',600,'inter-latin-600-normal.woff2'),('Inter',700,'inter-latin-700-normal.woff2'),('Space Grotesk',500,'space-grotesk-latin-500-normal.woff2'),('Space Grotesk',700,'space-grotesk-latin-700-normal.woff2')])
kcss=re.sub(r'@font-face\{[^}]*\}','',open(os.path.join(V,'katex.min.css')).read())+''.join(f"@font-face{{font-family:'{f[:-6].rsplit('-',1)[0]}';font-style:{'italic' if 'Italic' in f else 'normal'};font-weight:{'bold' if 'Bold' in f else 'normal'};src:url(data:font/woff2;base64,{b64(os.path.join(V,f))}) format('woff2')}}" for f in os.listdir(V) if f.startswith('KaTeX_'))
# ---------- index lookup
IDX={};CRIT={};SEC={};CHAP={}
for chf in glob.glob(os.path.join(R,'data','index','ch*','ch*.json')):
  ch=json.load(open(chf));d=os.path.dirname(chf);CHAP[ch['chapter']]=ch
  for c in ch['criteria']:CRIT[c['id']]=c
  for q in ch['review_questions']:
    IDX[q['id']]=dict(q,_dir=d,_kind='review')
    for p in q.get('parts',[]) or []:IDX[q['id']+p['n']]=dict(p,id=q['id']+p['n'],_parent=q,_dir=d,_kind='review',src=q.get('src',{}))
  for code in ch['sections']:
    p=os.path.join(d,code+'.json')
    if not os.path.exists(p):continue
    s=json.load(open(p));SEC[code]=s;s['_dir']=d
    for k in ['glossary','formulas','chunks','figures','worked_examples','checkins','section_questions','skills','resources']:
      for it in s.get(k,[]):IDX[it['id']]=dict(it,_dir=d,_kind=k,_sec=code)
    for it in (s.get('worksheet') or {}).get('questions',[]):IDX[it['id']]=dict(it,_dir=d,_kind='worksheet',_sec=code,_ws=s['worksheet'].get('title'))
def get(i):
  if i not in IDX:raise SystemExit(f'Not in the index: {i}')
  return IDX[i]
def img(it,rel):
  p=os.path.join(it['_dir'],rel)
  if not os.path.exists(p):return ''
  ext='jpeg' if p.lower().endswith(('jpg','jpeg')) else 'png'
  return f'<img src="data:image/{ext};base64,{b64(p)}">'
def srcline(it):
  s=it.get('src') or {};f=s.get('file','');pg=s.get('page')
  f=re.sub(r'^Physics12_Ch0?(\d+)\.pdf$',r'Cambridge VCE Physics Units 1&2, Chapter \1',f)
  return e(f)+(f', p. {pg}' if pg else '')
# ---------- KaTeX pre-render: collect every $...$ and render in one node call
MATH=[]
def m(t):
  t=t or ''
  def rep(x):
    MATH.append(html.unescape(x.group(1)));return f'\x00M{len(MATH)-1}\x00'
  t=e(t).replace('\n','<br>')
  return re.sub(r'\$([^$]+)\$',rep,t)
def render_math(page):
  if not MATH:return page
  js="const k=require(process.argv[1]);const m=JSON.parse(require('fs').readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(m.map(x=>{try{return k.renderToString(x,{throwOnError:false})}catch(e){return x}})))"
  r=json.loads(subprocess.run(['node','-e',js,os.path.join(V,'katex.min.js')],input=json.dumps(MATH),capture_output=True,text=True,check=True).stdout)
  return re.sub('\x00M(\\d+)\x00',lambda x:r[int(x.group(1))],page)
# ---------- working lines: split an answer/solution into one-click lines
def lines(s):
  out=[]
  for part in re.split(r';\s+|\n',s or ''):
    part=part.strip()
    if not part:continue
    # a = b = c  ->  "a = b", "= c" (only outside $...$ splits are not attempted; split inside one $..$ block)
    mm=re.fullmatch(r'(.*?)\$([^$]*)\$(.*)',part)
    if mm and mm.group(2).count('=')>=2 and not mm.group(3).strip(' .'):
      bits=[b.strip() for b in mm.group(2).split('=')]
      out.append(mm.group(1)+'$'+bits[0]+' = '+bits[1]+'$')
      out+=['$= '+b+'$' for b in bits[2:]]
    else:out.append(part)
  return out
def worklines(ls,final_bold=True):
  h=''
  for k,l in enumerate(ls):
    isText=not l.startswith('$') and not l.startswith('=')
    cls='st wl'+(' txt' if isText and '$' not in l[:3] else '')
    body=m(l)
    if final_bold and k==len(ls)-1:body=f'<b>{body}</b>'
    h+=f'<div class="{cls}">{body}</div>'
  return h
# ---------- slide pieces
AC={1:'#7dd3fc',2:'#fbb040',3:'#4ade80',4:'#a78bfa',5:'#2dd4bf',6:'#facc15'}
def bar(code,title,small='',sec=''):
  return f'<div class="bar"><span class="code">{e(code)}</span><span class="sep"></span><h2>{e(title)}{f"<small>{e(small)}</small>" if small else ""}</h2><span class="sec">{e(sec)}</span><span class="timer"></span></div>'
def foot(src,n,own=False):
  return f'<div class="foot"><span>{src}{" · <span class=own>Own wording</span>" if own else ""}</span><span>{n}</span></div>'
def kibox(fid):
  if not fid:return ''
  f=get(fid)
  if f['_kind']=='formulas':return f'<div class="kib"><span class="kt">Key idea · {e(f.get("name",""))}</span>{m("$"+f["latex"]+"$")}</div>'
  if f['_kind']=='glossary':return f'<div class="kib"><span class="kt">Key idea</span><b>{m(f["term"])}</b>: {m(f["def"])}</div>'
  return ''
def build(spec):
  global MATH;MATH=[]
  code=' + '.join(spec['sections']);secname=SEC[spec['sections'][0]]['title'] if spec['sections'][0] in SEC else ''
  slides=[];n=0;phases=[];seen=set()
  for sd in spec['slides']:
    n+=1;t=sd['type'];ph=sd.get('phase',{'title':'','donow':'Do now','goals':'Learning goals','keyideas':'Key ideas','apk':'APK','new':'New knowledge','figure':'New knowledge','interactive':'New knowledge','video':'New knowledge','wedo':'We do','youtry':'We do','practice':'Independent practice','exit':'Exit ticket','prac':'Prac'}[t])
    mn=sd.get('min')
    if ph and ph not in seen and mn:phases.append((ph,mn));seen.add(ph)
    mn=mn or dict(phases).get(ph)
    attrs=f'data-phase="{e(ph)}" data-min="{mn or ""}" data-sid="{e(sd.get("_sid",sd.get("id","")))}" data-type="{t}"';src='';own=False;body=''
    if t=='title':
      body=None;slides.append(('title',sd));continue
    if t=='donow':
      rows='';labels=sd.get('labels',['Last lesson','Last week','Last term'])
      for k,i in enumerate(sd['items']):
        q=get(i);rows+=f'<div class="qrow"><div class="card" style="--c:{["#7dd3fc","#fbb040","#f472b6"][k%3]}"><div class="lbl">{e(labels[k] if k<len(labels) else "")} · {e(q.get("_sec",""))}</div><div class="q">{m(q["question"])}</div></div><div class="sol st">{m(q.get("answer") or "")}</div></div>'
      body=bar(code,'Do now','',secname)+f'<div class="rows">{rows}</div>';src='Cambridge VCE Physics Units 1&2, check-in questions'
    elif t=='goals':
      cols=['#7dd3fc','#fbb040','#f472b6']
      g=''.join(f'<div class="card goal" style="--c:{cols[k%3]}"><span class="n">{k+1}</span><div>{m(CRIT[c]["text"])}<small>{e(c)}</small></div></div>' for k,c in enumerate(sd['criteria']))
      body=bar(code,'Learning goals','By the end of today I can',secname)+f'<div class="goals">{g}</div>';src='Cambridge VCE Physics Units 1&2, Chapter checklist'
    elif t=='keyideas':
      gl=''.join(f'<div><span><b>{m(get(i)["term"])}</b>: {m(get(i)["def"])}</span></div>' for i in sd.get('glossary',[]))
      fm=''
      for i in sd.get('formulas',[]):
        f=get(i);wh=''.join(f'<span>{m("$"+w["sym"]+"$")}</span><span>{e(w["meaning"])} ({m("$\\mathrm{"+w["unit"].replace(" ","\\,")+"}$") if w.get("unit") else ""})</span>' for w in f.get('where',[]))
        fm+=f'<div><div class="lbl">{e(f.get("name",""))}</div><div class="fm">{m("$"+f["latex"]+"$")}</div><div class="where">{wh}</div></div>'
      body=bar(code,'Key ideas','',secname)+f'<div class="grid g2"><div class="card kd" style="--c:#7dd3fc"><h3>Definitions</h3>{gl}</div><div class="card kd" style="--c:#fbb040"><h3>Formulas</h3>{fm}</div></div>';src='Cambridge VCE Physics Units 1&2, '+code+' glossary and formula boxes'
    elif t=='apk':
      cells=''.join(f'<div class="card" style="--c:{["#7dd3fc","#fbb040","#f472b6","#4ade80"][k%4]}"><div class="lbl">{e(a["from"])}</div><div class="q">{m(a["text"])}</div>{f"<div class=q style=margin-top:10px><b>{m(a['q'])}</b></div>" if a.get("q") else ""}{f"<div class=\"sol st\" style=margin-top:10px>{m(a['a'])}</div>" if a.get("a") else ""}</div>' for k,a in enumerate(sd['items']))
      body=bar(code,'APK','What you already know',secname)+f'<div class="grid g{min(2,len(sd["items"]))}">{cells}</div>';src='Progression: Jacaranda Science Quest 7 to 10';own=True
    elif t in ('new','figure'):
      fig=''
      if sd.get('figure'):
        f=get(sd['figure']);fig=f'<div class="fig">{img(f,f["img"])}<div class="cap">{e(f.get("label",""))} {e(f.get("caption",""))}</div></div>'
      txt=''
      if sd.get('points'):txt='<div class="txt"><ul>'+''.join(f'<li class="st">{m(p)}</li>' for p in sd['points'])+'</ul></div>'
      elif sd.get('chunk'):
        c=get(sd['chunk']);flat=' '.join(p.strip() for p in c['text'].split('\n') if p.strip())
        sents=re.split(r'(?<=[.!?])\s+(?=[A-Z•])',flat)[sd.get('from',0):sd.get('from',0)+sd.get('sentences',4)]
        txt='<div class="txt">'+''.join(f'<p class="st">{m(x.lstrip("• "))}</p>' for x in sents)+'</div>'
      head=sd.get('heading') or (get(sd['chunk']).get('heading') if sd.get('chunk') else (get(sd['figure']).get('label') if sd.get('figure') else ''))
      lay='g2' if fig and txt else ''
      body=bar(code,'New knowledge',head,secname)+f'<div class="grid {lay}">{f"<div class=card style=--c:#7dd3fc>{txt}</div>" if txt else ""}{fig}</div>'
      src=srcline(get(sd['chunk'])) if sd.get('chunk') else (srcline(get(sd['figure'])) if sd.get('figure') else '');own=bool(sd.get('points'))
    elif t=='video':
      v=get(sd['item']);st=f'&start={v["start"]}' if v.get('start') else ''
      body=bar(code,'New knowledge',sd.get('heading') or 'Video',secname)+f'<div class="vid"><div class="vt">{m(v["title"])}{" · "+e(v["duration"]) if v.get("duration") else ""}</div><iframe class="ixf" data-yt="{e(v["yt"])}" data-q="rel=0{st}" allow="autoplay; encrypted-media; fullscreen; picture-in-picture" allowfullscreen></iframe><div class="vn">Needs the internet. If it will not play here: <a href="{e(v["url"])}" target="_blank" rel="noopener">open on YouTube</a></div></div>'
      src='Cambridge VCE Physics Units 1&amp;2, Chapter '+code[0]+' curated internet resources'
    elif t=='interactive':
      body=bar(code,'New knowledge',sd.get('heading',''),secname)+f'<iframe class="ixf" data-src="{e(sd["id"])}.html?bare" allow="fullscreen"></iframe>';src='Interactive by teacher'
    elif t in ('wedo','youtry'):
      it=get(sd['item']);we=it['_kind']=='worked_examples';label=('We do' if t=='wedo' else 'You try')
      title=it.get('title') or ((it.get('_ws') or 'Worksheet') if it['_kind']=='worksheet' else ('Section '+it.get('_sec','')+' questions' if it['_kind']=='section_questions' else 'Review questions'))+' Q'+str(it.get('n',''))
      steps=it['steps'] if we else lines(it.get('answer') or '')
      opts=''.join(f'<div class="opt">{m(o)}</div>' for o in (it.get('options') or []))
      fig=''.join(f'<div class="fig">{img(it,p)}</div>' for p in (sd.get('img') or ([] if we else it.get('img',[])))[:1])
      body=(bar(code,label,title,secname)+
        f'<div class="grid" style="grid-template-columns:1.05fr 1fr"><div style="display:flex;flex-direction:column;gap:14px"><div class="card" style="--c:{"#fbb040" if t=="wedo" else "#94a3c8"}"><div class="q">{m(it["question"])}</div>{f'<div class="opts">{opts}</div>' if opts else ''}</div>{kibox(sd.get("kib"))}{fig}</div>'
        f'<div class="card" style="--c:#4ade80;display:flex;flex-direction:column"><h3>Working</h3><div class="work{' c2' if len(steps)>9 else ''}">{worklines(steps)}</div>{"<div class=ans st style=margin-top:auto>"+m(it.get("answer",""))+"</div>" if we and it.get("answer") else ""}</div></div>')
      src=srcline(it)+(', '+e(it['id']) if not we else ', Worked example '+e(it['id'][2:]))+('' if we else '. Working from the worksheet answers.')
      own=bool(sd.get('adapted'))
    elif t=='practice':
      rows=''.join(f'<tr><td>{m(a)}</td><td>{m(b)}</td></tr>' for a,b in sd['rows'])
      body=bar(code,'Independent practice','',secname)+f'<div class="card" style="--c:#7dd3fc"><table class="pr"><tr><th>Resource</th><th>Questions</th></tr>{rows}</table></div><div class="lead">{m(sd.get("note","Work on your own. Check your answers when you finish each set."))}</div>'
      src='Cambridge VCE Physics Units 1&2, '+code
    elif t=='exit':
      rows=''
      for k,x in enumerate(sd['items']):
        q=get(x['q']);qt=q.get('question','');
        if q.get('_parent'):qt=q['_parent'].get('question','')+' '+qt
        rows+=f'<div class="qrow"><div class="card" style="--c:{["#7dd3fc","#fbb040","#f472b6"][k%3]}"><div class="ican"><span>{m(CRIT[x["crit"]]["text"])}</span></div><div class="q" style="font-size:18px">{m(qt)}</div><div class="rag"><i></i><i></i><i></i></div></div><div class="sol st">{m(q.get("answer") or "")}</div></div>'
      body=bar(code,'Exit ticket','',secname)+f'<div class="rows">{rows}</div>';src='Cambridge VCE Physics Units 1&2, Chapter review questions'
    elif t=='prac':
      body=bar(code,'Prac',sd['title'],secname)+f'<div class="card" style="--c:#4ade80"><h3>Aim</h3><div class="lead">{m(sd.get("aim",""))}</div></div>';src=e(sd.get('file',''))
    slides.append((t,f'<section class="slide" {attrs}>{body}{foot(src,n,own)}</section>'))
  total=sum(x for _,x in phases)
  seq=''.join(f'<div><span>{e(p)}</span><span>{x} min</span></div>' for p,x in phases)+f'<div><span>Total</span><span>{total} min</span></div>'
  out=[]
  for t,x in slides:
    if t=='title':
      if not phases:continue
      tags=f'<div class="tags"><span style="--k:#7dd3fc">Unit {spec["unit"]}</span><span style="--k:#fbb040">AoS {spec["aos"]}: {e(spec.get("aos_name",""))}</span><span style="--k:#f472b6">Lesson {spec["lesson"]}</span></div>'
      out.append(f'<section class="slide title" data-phase="" data-min="">{tags}<h1>{e(spec["title"])}</h1><div class="sub">{e(code)} · Cambridge VCE Physics Units 1&amp;2</div><div class="seq"><h3>Lesson sequence</h3>{seq}</div>{foot("",1)}</section>')
    else:out.append(x)
  ch=int(re.match(r'\d+',spec['sections'][0]).group(0));bg={1:'waves',2:'waves',3:'nuclear',4:'nuclear',5:'circuit',6:'circuit'}.get(ch,'motion')
  ac=AC.get(int(spec['aos']) if spec['unit']==1 else 3+int(spec['aos']),'#7dd3fc')
  ixjs=open(os.path.join(IXD,'ix.js')).read()
  page=f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(code+' · '+spec['title'])}</title>
<style>{FONTS}{kcss}{open(os.path.join(H,'deck.css')).read()}</style></head><body data-bg="{bg}"><div id="stage" style="--ac:{ac}"><svg id="bg" viewBox="0 0 1280 720"></svg>{''.join(out)}<div class="help">click / → next line · ← back · F full screen</div></div>
<script>{ixjs}</script><script>{open(os.path.join(H,'deck.js')).read()}</script></body></html>"""
  page=render_math(page)
  return page,total
def donow_sheet(spec):
  global MATH
  d=[s for s in spec['slides'] if s['type']=='donow']
  if not d:return None
  MATH=[];labels=d[0].get('labels',['Last lesson','Last week','Last term'])
  qs=''.join(f'<div class="dq"><b>{k+1}.</b> <span class="dl">{e(labels[k] if k<len(labels) else "")}</span><div>{m(get(i)["question"])}</div><div class="sp"></div></div>' for k,i in enumerate(d[0]['items']))
  half=f'<div class="half"><div class="hd"><b>Do now</b><span>{e(" + ".join(spec["sections"]))} · Lesson {spec["lesson"]}</span><span>Name: ______________________</span></div>{qs}</div>'
  page=f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Do now · {e(spec['title'])}</title><style>{FONTS}{kcss}
@page{{size:A4;margin:10mm}}body{{font-family:Inter,sans-serif;color:#000;margin:0}}.pg{{width:190mm;height:277mm;display:flex;flex-direction:column}}
.half{{height:50%;padding:4mm 2mm;display:flex;flex-direction:column;gap:2mm}}.half+.half{{border-top:1.5px dashed #000}}
.hd{{display:flex;gap:10mm;align-items:baseline;border-bottom:2px solid #000;padding-bottom:2mm;font-size:11pt}}.hd b{{font:700 15pt 'Space Grotesk'}}.hd span:last-child{{margin-left:auto}}
.dq{{flex:1;font-size:11pt;line-height:1.4;display:flex;flex-direction:column}}.dl{{font-size:8.5pt;text-transform:uppercase;letter-spacing:.05em;color:#555;margin-left:2mm}}.sp{{flex:1;border-bottom:1px solid #bbb}}
</style></head><body><div class="pg">{half}{half}</div></body></html>"""
  return render_math(page)
if __name__=='__main__':
  sp=sys.argv[1];spec=json.load(open(sp))
  outdir=os.path.join(R,'lessons');os.makedirs(outdir,exist_ok=True)
  page,total=build(spec);fn=os.path.join(outdir,spec['name']+'.html');open(fn,'w').write(page)
  print(fn,len(page)//1024,'KB · phases total',total,'min')
  dn=donow_sheet(spec)
  if dn:open(os.path.join(outdir,spec['name']+' do now.html'),'w').write(dn);print('do now sheet written')

# ---------- guided sheet: black and white, double-sided A4, follows the slides, cut-off exit ticket strip
BLANK_WAVE='''<svg viewBox="0 0 640 190" style="width:100%;height:44mm"><line x1="20" y1="95" x2="620" y2="95" stroke="#000" stroke-dasharray="5 5" stroke-width="1.2"/>
<path d="M20 95 C 70 15, 120 15, 170 95 S 270 175, 320 95 S 420 15, 470 95 S 570 175, 620 95" fill="none" stroke="#000" stroke-width="2.5"/>
<path d="M560 30 L610 30" stroke="#000" stroke-width="1.5" marker-end="url(#ah)"/><defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z"/></marker></defs>
<text x="585" y="22" font-size="13" text-anchor="middle" font-family="Inter">direction of wave</text></svg>'''
def guided_sheet(spec):
  global MATH;MATH=[]
  code=' + '.join(spec['sections']);secname=SEC[spec['sections'][0]]['title'] if spec['sections'][0] in SEC else ''
  L=lambda n,h=8:''.join(f'<div class="ln" style="height:{h}mm"></div>' for _ in range(n))
  box=lambda t,inner,cls='':f'<section class="bx {cls}"><h3>{t}</h3>{inner}</section>'
  parts=[];exitp=''
  for sd in spec['slides']:
    t=sd['type']
    if t=='donow':
      parts.append(box('Do now',''.join(f'<div class="q"><b>{k+1}.</b> {m(get(i)["question"])}</div>{L(1,6)}' for k,i in enumerate(sd['items']))))
    elif t=='goals':
      parts.append(box('Learning goals: by the end of today I can',''.join(f'<div class="tk"><span>{m(CRIT[c]["text"])}</span></div>' for c in sd['criteria'])))
    elif t=='keyideas':
      d=''.join(f'<div class="kd"><span class="gap"></span><span>{m(get(i)["def"])}</span></div>' for i in sd.get('glossary',[]))
      f=''
      for i in sd.get('formulas',[]):
        fo=get(i);us=' &nbsp; '.join(f'{m("$"+w["sym"]+"$")} <span class="gap s"></span>' for w in fo.get('where',[]))
        f+=f'<div class="fm"><b>{e(fo.get("name",""))}:</b> &nbsp; {m("$"+fo["latex"].split("=")[0].strip()+"$")} = <span class="gap s"></span> = <span class="gap s"></span><span class="us">Units: &nbsp; {us}</span></div>'
      parts.append(box('Key ideas',f'<div class="sub">Write the term for each definition</div>{d}{f}'))
    elif t=='apk':
      parts.append(box('APK: what you already know',''.join(f'<div class="q">{m(a["q"])}</div>{L(1,7)}' for a in sd['items'] if a.get('q'))))
    elif t in ('new','figure'):
      if sd.get('sheet')=='skip':continue
      if sd.get('sheet_figure')=='blank-wave':
        parts.append(box('New knowledge: label the wave','<div class="sub">Label: crest, trough, amplitude (A), wavelength (λ), neutral position</div>'+BLANK_WAVE,'own'))
      elif t=='new' and sd.get('sheet_notes',True):
        parts.append(box('New knowledge: '+e(sd.get('heading') or (get(sd['chunk']).get('heading') if sd.get('chunk') else '')),L(sd.get('lines',4))))
    elif t in ('wedo','youtry'):
      it=get(sd['item']);we=it['_kind']=='worked_examples'
      title=('We do: ' if t=='wedo' else 'You try: ')+(it.get('title') or (it.get('_ws') or 'Worksheet')+' Q'+it.get('n',''))
      parts.append(box(title,f'<div class="q">{m(it["question"])}</div><div class="work" style="height:{sd.get("space",64)}mm"></div>'))
    elif t=='practice':
      parts.append(box('Independent practice',''.join(f'<div class="tk"><span>{m(a)}: {m(b)}</span></div>' for a,b in sd['rows'])))
    elif t=='exit':
      rows=''
      for k,x in enumerate(sd['items']):
        q=get(x['q']);qt=(q['_parent'].get('question','')+' ' if q.get('_parent') else '')+q.get('question','')
        rows+=f'<div class="ex"><div class="exq"><b>{k+1}.</b> {m(qt)}{L(1,7)}</div><div class="rag"><i></i><i></i><i></i><small>{e(x["crit"])}</small></div></div>'
      exitp=f'<div class="cut">✂ cut here and hand in</div><section class="bx exit"><h3>Exit ticket · {e(code)} · Name: ______________________</h3>{rows}</section>'
  sheetcss="""@page{size:A4;margin:11mm 12mm}*{box-sizing:border-box}body{font-family:Inter,sans-serif;color:#000;margin:0;font-size:10pt;line-height:1.35}
.hd{display:flex;align-items:baseline;gap:5mm;white-space:nowrap;border-bottom:2.5px solid #000;padding-bottom:2mm;margin-bottom:3mm}.hd b{font:700 15pt 'Space Grotesk'}.hd span{font-size:9.5pt}.hd .nm{margin-left:auto}
.bx{border:1.5px solid #000;border-radius:3mm;padding:2mm 3.5mm;margin-bottom:2.5mm;break-inside:avoid}.bx h3{font:700 9pt Inter;letter-spacing:.06em;text-transform:uppercase;margin:0 0 1.5mm;border-bottom:1px solid #000;padding-bottom:1mm}
.q{margin:1.2mm 0}.ln{border-bottom:1px solid #999}.sub{font-size:8.5pt;color:#333;margin-bottom:1mm}
.tk{display:flex;gap:2.5mm;align-items:flex-start;margin:1mm 0}.tk:before{content:"";flex:none;width:3.6mm;height:3.6mm;border:1.3px solid #000;margin-top:.5mm}
.two{display:grid;grid-template-columns:1.55fr 1fr;gap:5mm}.kd{display:grid;grid-template-columns:30mm 1fr;gap:3mm;margin:1.2mm 0;align-items:end;font-size:9.5pt}.gap{flex:none;width:27mm;border-bottom:1.3px solid #000;height:5mm;display:inline-block}.gap.s{width:12mm;vertical-align:-1mm}
.fm{font-size:10.5pt;margin:2.5mm 0 1mm;white-space:nowrap;display:flex;align-items:baseline;gap:1.5mm;border-top:1px dashed #777;padding-top:2mm}.fm .us{margin-left:auto;font-size:9.5pt}.wt{width:100%;border-collapse:collapse;font-size:9pt}.wt th,.wt td{border:1px solid #000;padding:1mm 2mm;text-align:left}.wt td.bl{width:20mm}
.work{border:1px dashed #777;border-radius:2mm;margin-top:1.5mm}
.cut{border-top:1.5px dashed #000;text-align:center;font-size:8pt;margin:2mm 0;padding-top:1mm}
.ex{display:grid;grid-template-columns:1fr 26mm;gap:3mm;margin:1mm 0}.rag{display:flex;gap:1.5mm;align-items:center}.rag i{width:5.5mm;height:5.5mm;border:1.5px solid #000;border-radius:50%}.rag small{font-size:7pt;margin-left:1mm}
.own h3:after{content:" (own)";font-weight:400;text-transform:none;letter-spacing:0}
.pb{break-before:page}"""
  split=[i for i,p in enumerate(parts) if p.startswith('<section class="bx "><h3>We do')]
  k=split[0] if split else len(parts)
  head=f'<div class="hd"><b>{e(code)} {e(secname)}</b><span>Unit {spec["unit"]} · AoS {spec["aos"]} · Lesson {spec["lesson"]}</span><span class="nm">Name: ____________________ Date: __________</span></div>'
  page=f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{e(code)} guided sheet</title><style>{FONTS}{kcss}{sheetcss}</style></head><body>
{head}{''.join(parts[:k])}<div class="pb"></div>{''.join(parts[k:])}{exitp}</body></html>"""
  return render_math(page)
if __name__=='__main__':
  gs=guided_sheet(spec);open(os.path.join(outdir,spec['name']+' guided sheet.html'),'w').write(gs);print('guided sheet written')
