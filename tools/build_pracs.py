# Builds pracs.html: the Year 11 Pracs tab. Two big cards: Cambridge (23 pracs from data/pracs.json, made by
# tools/extract_pracs.py) and Pearson (SAB SPARKlab pracs, Online experiments, teacher notes, solutions and risk
# assessments, placed on Cambridge sections by tools/pearson_map.py). Every file is a Google Drive link.
import os,json,re,html
H=os.path.dirname(os.path.abspath(__file__));e=html.escape
import sys;sys.path.insert(0,H);import pearson_map
CSS=open(os.path.join(H,'planner_base.css')).read()
P=json.load(open(os.path.join(H,'..','data','pracs.json')))
DI=json.load(open(os.path.join(H,'drive_ids.json')))
IX=[m for m in json.load(open(os.path.join(H,'..','interactives','interactives.json'))) if m.get('year',11)==11]
PM=pearson_map.build()
DR=lambda i:f'https://drive.google.com/file/d/{i}/view'
SECT={};Y=json.load(open(os.path.join(H,'..','data','year11.json')))
for u in Y['units']:
  for a in u['aos']:
    for c in a['chapters']:
      for s in c['sections']:SECT[s['code']]=(u['n'],a['n'],a['title'],c['n'],c['title'],s['title'])
AOSC={(1,1):'#1f4fa0',(1,2):'#b4532a',(1,3):'#2b7a3d',(2,1):'#7a3fa0'}
def cid(p):
  k=next((k for k in DI if k.startswith(f"{p['section']} Practical {p['section']}–{p['n']}") or k.startswith(f"{p['section']} Practical {p['section']}-{p['n']}")),None)
  return DI.get(k)
def link(i,t,cls='dl'):return f'<a class="{cls}" href="{DR(i)}" target="_blank" rel="noopener">{e(t)}</a>' if i else f'<span class="dl off">{e(t)}</span>'
# ---------- Cambridge
camb='';last=None
for p in sorted(P,key=lambda p:(SECT[p['section']][0],SECT[p['section']][1],p['section'],p['n'])):
  u,a,an,cn,ct,st=SECT[p['section']]
  if (u,a)!=last:camb+=f'<div class="aosh" style="--ac:{AOSC[(u,a)]}">Unit {u} · AoS {a} · {e(an)}</div>';last=(u,a)
  pe=[x for x in PM['sec'].get(p['section'],[]) if x['label'] in ('Practical (SAB SPARKlab)','Online experiment')]
  ix=[m for m in IX if m['section']==p['section']]
  det=''
  if p['aim']:det+=f'<div class="row"><i>Aim</i><span>{e(re.split(r"\s*Pre-?lab questions",p["aim"])[0])}</span></div>'
  if p['materials']:det+=f'<div class="row"><i>Materials</i><span><ul>{"".join(f"<li>{e(x)}</li>" for x in p["materials"])}</ul></span></div>'
  if p['safety']:det+=f'<div class="row"><i>Safety</i><span>{e(p["safety"])}</span></div>'
  if p['method']:det+=f'<div class="row"><i>Method</i><span><ol>{"".join(f"<li>{e(x)}</li>" for x in p["method"])}</ol></span></div>'
  if p['prelab']:det+=f'<div class="row"><i>Prelab questions</i><span><ol>{"".join(f"<li>{e(x)}</li>" for x in p["prelab"])}</ol></span></div>'
  det+=f'<div class="row"><i>Sections in the doc</i><span>{e(", ".join(["Aim","Materials" if p["materials"] else "","Method" if p["method"] else ""]+p["has"]).replace(", ,",","))}</span></div>'
  if pe:det+=f'<div class="row"><i>Pearson for the same section</i><span>{" ".join(link(x["id"],x["ref"]+" "+re.sub(r"^(OE|PA)?\s*[\d.]+\s*","",x["name"].split(" ",1)[-1]),"dl pe") for x in pe)}</span></div>'
  if ix:det+=f'<div class="row"><i>Interactives</i><span>{" ".join(f"<a class=dl href=interactives/{m[chr(105)+chr(100)]}.html target=_blank>{e(m[chr(116)+chr(105)+chr(116)+chr(108)+chr(101)])}</a>" for m in ix)}</span></div>'
  camb+=f'''<details class="pr" style="--ac:{AOSC[(u,a)]}"><summary><b>{e(p["section"])}–{p["n"]}</b> {e(p["title"])}<span class="meta">{e(p["section"])} {e(st)} · {len(p["materials"])} materials · {len(p["method"])} steps</span>{link(cid(p),"Open (Word)")}</summary><div class="body">{det}</div></details>'''
# ---------- Pearson
pear='';last=None
pas=[];oes={}
for s,L in PM['sec'].items():
  for x in L:
    if x['ref'].startswith('PA'):pas.append((x['ref'],s,x))
    elif x['ref'].startswith('OE'):oes.setdefault(x['ref'],{'sec':s,'files':[]})['files'].append(x)
pa={}
for ref,s,x in pas:pa.setdefault(ref,{'sec':s,'files':[]})['files'].append(x)
def secsort(s):return (SECT[s][0],SECT[s][1],s)
rows=''
for ref in sorted(pa):
  d=pa[ref];main=[x for x in d['files'] if x['label'].startswith('Practical')];risk=[x for x in d['files'] if 'Risk' in x['label']]
  nm=main[0]['name'].split(' ',1)[1] if main else ref
  rows+=f'<tr><td><b>{e(ref)}</b></td><td>{e(nm)}</td><td>{e(d["sec"])} {e(SECT[d["sec"]][5])}</td><td>{" ".join(link(x["id"],"SPARKlab file","dl pe") for x in main)} {" ".join(link(x["id"],"Risk assessment","dl pe") for x in risk)}</td></tr>'
oerows=''
for ref in sorted(oes,key=lambda r:[int(x) for x in r[3:].split('.')]):
  d=oes[ref];st=[x for x in d['files'] if x['label']=='Online experiment'];tn=[x for x in d['files'] if x['label']=='Teacher notes'];rk=[x for x in d['files'] if x['label']=='Risk assessment']
  nm=re.sub(r'^(OE|Online experiment) \d+\.\d+\.\d+\s*','',st[0]['name']) if st else ref
  oerows+=f'<tr><td><b>{e(ref)}</b></td><td>{e(nm)}</td><td>{e(d["sec"])} {e(SECT[d["sec"]][5])}</td><td>{" ".join(link(x["id"],"Student","dl pe") for x in st)} {" ".join(link(x["id"],"Teacher notes","dl pe") for x in tn)} {" ".join(link(x["id"],"Risk assessment","dl pe") for x in rk)}</td></tr>'
aosrows=''
for (u,a),L in sorted(PM['aos'].items()):
  L=[x for x in L if re.search('prac|risk',x['label']+x['name'],re.I)]
  if L:aosrows+=f'<tr><td><b>Unit {u} AoS {a}</b></td><td colspan="3">{" ".join(link(x["id"],x["name"],"dl pe") for x in L)}</td></tr>'
crs=[x for x in PM['course'] if re.search('prac|risk|experiment',x['name'],re.I)]
pear=f'''<h3 class="sub">SAB SPARKlab practical activities ({len(pa)})</h3><p class="lead">Data-logging pracs (open the .spklab file in PASCO SPARKvue). Placed on the Cambridge section they fit.</p>
<table class="t"><tr><th>Prac</th><th>Title</th><th>Cambridge section</th><th>Files</th></tr>{rows}</table>
<h3 class="sub">Online experiments ({len(oes)})</h3><p class="lead">Pearson's simulations, data analysis and research tasks, with teacher notes and risk assessments where Pearson provides them.</p>
<table class="t"><tr><th>OE</th><th>Title</th><th>Cambridge section</th><th>Files</th></tr>{oerows}</table>
<h3 class="sub">Teacher notes, solutions and risk assessments by AoS</h3><table class="t">{aosrows}</table>
<h3 class="sub">Course-wide</h3><p>{" ".join(link(x["id"],x["name"],"dl pe") for x in crs)}</p>'''
SD='<div class="sd"><div><b>Unit 1</b> at least <b>15 h</b> of practical work (12 lessons of 79 min). Cambridge has 14 Unit 1 pracs.</div><div><b>Unit 2</b> at least <b>10 h</b> across AoS 1 and 2 (8 lessons; Cambridge Ch 7 to 9 has 9 pracs) plus at least <b>7 h</b> for the AoS 3 investigation (6 lessons).</div><div>Pracs get their own lesson (decided 18 Nov). Which pracs: still to decide.</div></div>'
X="""main{max-width:1200px}.lead{color:var(--muted);font-size:14px;margin:4px 0 10px}
.big{background:#fff;border:1px solid var(--line);border-top:8px solid var(--bc);border-radius:14px;padding:16px 20px;margin:18px 0}
.big>h2{margin:0 0 4px;font-size:24px;color:var(--bc)}
.aosh{font-weight:700;margin:16px 0 6px;padding-left:10px;border-left:6px solid var(--ac)}
details.pr{border:1px solid var(--line);border-left:6px solid var(--ac);border-radius:10px;margin:6px 0;background:#fcfcfa}
details.pr>summary{cursor:pointer;padding:9px 12px;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;list-style:none}
details.pr>summary b{color:var(--ac)}.meta{color:var(--muted);font-size:12.5px;margin-left:auto}
details.pr .body{padding:4px 14px 12px}.row{display:grid;grid-template-columns:150px 1fr;gap:10px;padding:6px 0;border-top:1px dashed var(--line);font-size:13.5px}.row i{font-style:normal;color:var(--muted);font-weight:600}
.row ul,.row ol{margin:0;padding-left:20px}
.dl{display:inline-block;font-size:12px;color:#1d4596;text-decoration:none;border:1px solid #b9c9ee;border-radius:6px;padding:1px 7px;margin:1px 3px 1px 0;font-weight:600;background:#fff}.dl.pe{color:#9a4a1c;border-color:#efc4a3}.dl.off{color:#999;border-color:#ddd}
table.t{width:100%;border-collapse:collapse;font-size:13.5px;margin-bottom:8px}table.t th{text-align:left;font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);padding:6px 8px;border-bottom:1.5px solid var(--line)}table.t td{padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}
h3.sub{font-size:16px;margin:18px 0 2px}.sd{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.sd div{background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 12px;font-size:13.5px}
.ctl{display:flex;gap:8px;margin:6px 0}.ctl button{font:inherit;font-size:12.5px;border:1px solid var(--line);background:#fff;border-radius:8px;padding:4px 10px;cursor:pointer}"""
page=f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Physics · Year 11 pracs</title><style>{CSS}{X}</style>
<script>if(window.self!==window.top){{document.documentElement.classList.add('emb')}}</script><style>.emb body{{background:transparent}}</style></head><body><main>
<p class="lead">Every Year 11 practical on the drive, Cambridge and Pearson, with its details and files. Click a Cambridge prac to see its aim, materials, safety notes, method and prelab questions. Files open from the shared drive.</p>
{SD}
<section class="big" style="--bc:#1f4fa0"><h2>Cambridge · {len(P)} pracs</h2><p class="lead">From each section's Practical file (text as written by Cambridge). Pearson pracs for the same section and our interactives are listed inside each one.</p>
<div class="ctl"><button onclick="document.querySelectorAll('details.pr').forEach(d=>d.open=true)">Open all</button><button onclick="document.querySelectorAll('details.pr').forEach(d=>d.open=false)">Close all</button></div>{camb}</section>
<section class="big" style="--bc:#b4532a"><h2>Pearson · {len(pa)} SPARKlab pracs, {len(oes)} online experiments</h2>{pear}</section>
<p class="lead" style="margin-top:20px">Built by tools/build_pracs.py from data/pracs.json (Cambridge, extracted by tools/extract_pracs.py) and the Pearson cross-map.</p></main></body></html>"""
open(os.path.join(H,'..','pracs.html'),'w').write(page);print('pracs.html',len(P),'cambridge',len(pa),'PA',len(oes),'OE')
