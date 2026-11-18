# Builds pearson.html: the Pearson to Cambridge cross-map for Year 11 (Cambridge is the backbone).
import json,os,html,re,sys
H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,H);import pearson_map as PMOD
e=html.escape;D=json.load(open(os.path.join(H,'..','data','year11.json')))
src=open(os.path.join(H,'build_studydesign.py')).read();CSS=open(os.path.join(H,'planner_base.css')).read()+re.search(r'CSS=open\(os.path.join\(H,\'planner_base.css\'\)\).read\(\)\+"""(.*?)"""',src,re.S).group(1)
EMB="<script>if(window.self!==window.top){document.documentElement.classList.add('emb')}</script><style>.emb .top,.emb nav.crumb{display:none!important}.emb body{background:transparent}</style>"
secs=[(u,a,c,s) for u in D['units'] for a in u['aos'] for c in a['chapters'] for s in c['sections']]
def cnt(fs,lab):return sum(1 for f in fs if f['label']==lab)
rows=''
for u,a,c,s in secs:
  P=s['pearson'];ps=[k for k,(cs,_) in PMOD.PSEC.items() if s['code'] in cs]
  pch=[f'Ch {n}' for n,cs in PMOD.PCH.items() if s['code'] in cs]
  rows+=f"<tr><td><b>{s['code']}</b> {e(s['title'])}</td><td>{', '.join(ps) if ps else ', '.join(pch)}</td><td>{cnt(P,'Practical (SAB SPARKlab)') or ''}</td><td>{cnt(P,'Online experiment') or ''}</td><td>{cnt(P,'Video') or ''}</td><td>{'<span class=warn>no section extras</span>' if not P else ''}</td></tr>"
psec=''.join(f"<tr><td>{k}</td><td>{e(t)}</td><td>{', '.join(cs)}</td></tr>" for k,(cs,t) in PMOD.PSEC.items())
pch=''.join(f"<tr><td>Ch {n}</td><td>{e(PMOD.PCHN[n])}</td><td>{', '.join(cs)}</td></tr>" for n,cs in PMOD.PCH.items())
R=PMOD.build();tot=sum(len(v) for v in R['sec'].values())
ADDS=[('Pracs (SAB SPARKlabs)','23 practical activities, PA01 to PA23, with teacher notes, solutions and risk assessments per AoS. They overlap Cambridge\'s pracs in places (e.g. series and parallel circuits, specific heat) and add new ones: speed of light, G-M tube, OPAL reactor, Van de Graaff, reaction timer, g at Earth\'s surface, momentum and energy conservation.'),
 ('Online experiments','22 online experiments, many with teacher notes and risk assessments: data analysis tasks, research topics and simple at-home or in-class experiments. Useful as prac alternatives or homework.'),
 ('Videos','14 short videos already on the drive, each mapped to a Cambridge section.'),
 ('Fully worked solutions','Per chapter, per AoS review and per unit. Teacher only.'),
 ('SAB answers','Worksheet and exam-question solutions for each AoS. Students do not have the SAB, so these answer questions students cannot see.'),
 ('Unit 2 options','Pearson adds three options Cambridge does not cover: 2.2 fusion vs fission, 2.5 forces on the human body, 2.12 AC to DC. It also has its own versions of 2.10, 2.11 and 2.15.'),
 ('Unit 2 investigation','Logbook template, poster template, sample logbook and poster, student checklist, assessment rubric and teacher notes. Cambridge has nothing here, so this fills a real gap.'),
 ('Course-wide','Formula and data sheet, a Units 1 and 2 practice exam with a mapping document and answers, sample teaching plans for both units, risk assessment templates, and lists of all pracs and videos.')]
adds='<div class="g2">'+''.join(f'<div class="box" style="--ac:#b4532a"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a,b in ADDS)+'</div>'
none=[f"{s['code']} {s['title']}" for u,a,c,s in secs if not s['pearson']]
page=f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Physics · Pearson cross-map</title><style>{CSS}</style>{EMB}</head><body><div class="top"><header><h1>Physics Planner</h1></header></div><main>
<nav class="crumb"><a href="./">Physics Planner</a> › Year 11 › Pearson cross-map</nav>
<div class="unit">Pearson resources, mapped onto the Cambridge course</div>
<p class="lead">Cambridge sets the order and the sections. Every Pearson Heinemann Physics 11 (5E) resource on the shared drive is attached to the Cambridge section, chapter or AoS it supports, and appears in orange on the Course plan cards. The unofficial textbook PDF in the Pearson folder is not linked.</p>
<div class="stats"><div class="st"><b>158</b><span>Pearson files on the drive</span></div><div class="st"><b>{tot}</b><span>attached to a Cambridge section</span></div><div class="st"><b>{len(secs)-len(none)}/{len(secs)}</b><span>Cambridge sections with Pearson extras</span></div><div class="st"><b>3</b><span>extra Unit 2 options</span></div><div class="st"><b>0</b><span>files left unmapped</span></div></div>
<h2>What Pearson adds</h2>{adds}
<h2>Cambridge section by section</h2><table class="t"><tr><th>Cambridge section</th><th>Pearson equivalent</th><th>Pearson pracs</th><th>Online experiments</th><th>Videos</th><th></th></tr>{rows}</table>
<h2>Pearson Unit 1 sections → Cambridge</h2><table class="t"><tr><th>Pearson</th><th>Topic</th><th>Cambridge</th></tr>{psec}</table>
<h2>Pearson chapters → Cambridge</h2><table class="t"><tr><th>Pearson</th><th>Chapter</th><th>Cambridge</th></tr>{pch}</table>
<h2>Flags</h2><div class="flag"><b>No Pearson extras:</b> {e(', '.join(none)) or 'none'}. These have no Pearson pracs, online experiments or videos; Pearson's chapter solutions still apply.</div>
<div class="flag"><b>SAB items:</b> students do not have the Pearson Skills and Assessment Book, so SAB worksheets and exam questions can only be used if we copy them for class.</div>
<div class="flag"><b>Topic labels:</b> Pearson section topics here are short descriptions for mapping, not Pearson's exact section titles.</div>
<p class="src">Built from the Pearson Resources and Cambridge Resources folders on the shared drive (Google Drive), 18 Nov 2026. Mapping rules: tools/pearson_map.py.</p></main></body></html>"""
open(os.path.join(H,'..','pearson.html'),'w').write(page);print('dashes',len(re.findall('[—–]',page)),'none',none)
