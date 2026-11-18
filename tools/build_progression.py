# Builds progression.html: the Years 7 to 10 physics progression into VCE Physics Units 1 and 2.
# Source: Jacaranda Science Quest 7, 8, 9, 10 (2021 editions, Victorian Curriculum 1.0) in
# VCE Physics Units 1 2 [2027]\Yr7-10 Resources (read 18 Nov 2026). Only physics subtopics are listed.
# Summaries are paraphrased for planning (the textbooks are licensed, the site is public).
# Each subtopic lists the Cambridge sections it feeds ("12:xx" = Units 3 and 4 section, "Opt x" = Unit 2 option).
# Year 12: Cambridge VCE Physics Units 3&4 (2023) contents and its curriculum grid against the 2023 to 2027 study design
# (Yr12 Resources, read 18 Nov 2026). FWD links each Units 1 and 2 section to the Units 3 and 4 sections that build on it.
# To update for Victorian Curriculum 2.0 textbooks: replace NODES and rebuild.
import os,html,json,re
H=os.path.dirname(os.path.abspath(__file__));e=html.escape
CSS=open(os.path.join(H,'planner_base.css')).read()
Y11=json.load(open(os.path.join(H,'..','data','year11.json')))
SEC={}
for u in Y11['units']:
  for a in u['aos']:
    for c in a['chapters']:
      for s in c['sections']:SEC[s['code']]=(s['title'],u['n'],a['n'],c['n'])

STRANDS=[('waves','Waves and light','#1f4fa0','1A','1C'),('heat','Heat and energy','#b4532a','2A','9C'),
 ('nuclear','Atoms and nuclear','#7a3fa0','3A','4C'),('elec','Electricity and magnetism','#2b7a3d','5A','6C'),
 ('motion','Forces and motion','#1d7a86','7A','8C'),('space','Space','#9a6b00',None,None)]
# (year, code, title, strand, own summary, feeds)
NODES=[
(7,'8.2','Forces','motion','What a force is: pushes, pulls and their effects on objects.',['8B']),
(7,'8.3','Gravity','motion','Gravity as a force; mass versus weight.',['8B','12:3A']),
(7,'8.4','Friction','motion','Friction: when it helps and when it is a problem.',['8B']),
(7,'8.5','Keeping afloat','motion','Buoyancy and surface tension.',[]),
(7,'8.6','Magnetic fields','elec','Fields around magnets; how an electromagnet works.',['12:4B']),
(7,'8.7','Electric fields','elec','Charge, charging objects, forces between charges.',['5A']),
(7,'8.8','Staying safe','motion','Helmets, seatbelts and airbags explained with forces.',['8A']),
(7,'9.2','Using levers','motion','Levers change the size, direction or speed of a force.',['8C']),
(7,'9.3','Ramps, wedges and screws','motion','Inclined planes reduce the force needed.',['9A']),
(7,'9.4','Wheels, axles and pulleys','motion','Changing the size and direction of forces.',['9A']),
(7,'9.5','Getting into gear','motion','Gears change speed and direction of rotation.',['8C']),
(7,'9.6','Compound machines','motion','Spotting simple machines inside complex ones.',[]),
(8,'10.2','Different forms of energy','heat','Forms of energy; kinetic versus potential.',['9B']),
(8,'10.3','Transforming energy','heat','Energy flow diagrams; where "lost" energy goes; efficiency idea.',['9B']),
(8,'10.4','Transferring energy','heat','Energy moved by forces, heating and waves.',['2A','9A']),
(8,'10.5','A costly escape','heat','Keeping a house warm or cool: insulation in practice.',['2A']),
(8,'10.6','Light','waves','Luminous and non-luminous sources; how light travels and interacts.',['1C']),
(8,'10.7','Light forms images','waves','Images from mirrors and lenses: reflection and refraction.',['1C']),
(8,'10.8','Seeing light','waves','The eye and vision correction.',['1C','Opt 2.8']),
(8,'10.9','Sound energy','waves','Wave model of sound; measuring the speed of sound.',['1A','Opt 2.10']),
(9,'6.2','Chemical building blocks','nuclear','Atoms, protons, neutrons, electrons; isotopes.',['3A']),
(9,'6.3','Inside the nucleus','nuclear','Radioactivity comes from unstable nuclei decaying.',['3A','3B']),
(9,'6.4','Using radioactivity','nuclear','Half-life idea and uses of radioisotopes.',['3C','3E']),
(9,'6.5','The dark side of radiation','nuclear','Health effects of radiation; reactor accidents.',['3E','4C']),
(9,'9.2','Heat transfer','heat','Heat versus temperature, absolute zero, conduction, convection, radiation.',['2A']),
(9,'9.3','Controlling heat transfer','heat','When heat flows and how to slow it.',['2A']),
(9,'9.4','Heat transfer and the planet','heat','Convection in the Earth and atmosphere; greenhouse effect.',['2B','Opt 2.1']),
(9,'9.5','Waves','waves','A wave by its nature, frequency and amplitude.',['1A']),
(9,'9.6','Energy transfer by sound','waves','Sound as a pressure wave; calculating its speed.',['1A']),
(9,'9.7','Hearing sound','waves','How the ear works and how it is damaged.',['Opt 2.10']),
(9,'9.8','Energy transfer by light','waves','Light as an EM wave; regions of the spectrum.',['1B']),
(9,'9.9','Wave behaviour of light','waves','Reflection and refraction of light.',['1C']),
(9,'9.10','Seeing the light','waves','Focusing on the retina; vision problems.',['Opt 2.8']),
(9,'9.11','Communication','waves','Radio, AM, FM and TV as uses of EM waves.',['1B']),
(9,'9.12','The Synchrotron','waves','Particle accelerators as light sources.',['1B','Opt 2.16','12:4B']),
(9,'10.2','Static electricity','elec','Charge, charging, forces between charges.',['5A']),
(9,'10.3','Electrical circuits','elec','Circuit components and symbols; voltage and current.',['5A','5B']),
(9,'10.4','Battery technology','elec','How batteries work; types of battery.',['5B']),
(9,'10.5','Series and parallel circuits','elec','Current and voltage in series and parallel.',['5C','5D']),
(9,'10.6','Measuring electricity','elec','Placing ammeters and voltmeters; circuit hazards.',['5B','6C']),
(9,'10.7','Resisting the electrons!','elec','Resistance and Ohm\'s law; ohmic or not.',['5C','6A']),
(9,'10.8','Electronics','elec','Common electronic components.',['6A']),
(9,'10.9','Electricity and magnetism','elec','Magnetic fields of magnets and electromagnets.',['12:4B']),
(9,'10.10','The motor effect','elec','Force on a current in a magnetic field.',['12:4B','12:5C']),
(9,'10.11','Generators','elec','Moving a coil in a field induces a voltage.',['12:5B','12:5C','12:5D','12:6B']),
(9,'10.12','The future of electricity','elec','Generation and electronics in the future.',['6B','12:5A']),
(10,'6.2','Observing the night sky','space','Earth\'s motion and the changing night sky.',['Opt 2.13','12:3C']),
(10,'6.3','Stars: a life story','space','Life cycle of stars; why stars differ.',['4B','Opt 2.13']),
(10,'6.4','The changing universe','space','Evidence for an expanding universe.',['Opt 2.17']),
(10,'6.5','How it all began','space','Big Bang theory and its evidence.',['Opt 2.17']),
(10,'6.6','Eyes on the universe','space','Telescopes and technology improving theories.',['Opt 2.14']),
(10,'8.2','Average speed, distance and time','motion','Average speed formula and calculations.',['7A']),
(10,'8.3','Measuring speed','motion','Devices that measure speed; speed and safety.',['7B']),
(10,'8.4','Acceleration','motion','Calculating acceleration when speeding up or slowing down.',['7B','7C']),
(10,'8.5','Newton\'s first law','motion','Forces and inertia.',['8B']),
(10,'8.6','Newton\'s second law','motion','F = ma to find acceleration.',['8B']),
(10,'8.7','Newton\'s third law','motion','Action-reaction pairs.',['8B']),
(10,'8.8','Work and energy','heat','Energy stored, transformed and transferred; work.',['9A','9B']),
(10,'8.9','Conservation of energy','heat','Energy is never created or destroyed.',['9B']),
(10,'8.10','Designing safety devices','motion','Forces and energy in safety design.',['8A','Opt 2.11']),
]

Y12=[('1A','Newton\'s laws',3,1,'motion','Newton\'s laws in one and two dimensions'),('1B','Circular motion',3,1,'motion','Horizontal, banked and vertical circles'),('1C','Projectile motion',3,1,'motion','Projectiles near Earth, air resistance'),
 ('2A','Work and energy',3,1,'heat','Work as area under F vs x; energy transformations'),('2B','Momentum and impulse',3,1,'motion','Conservation of momentum and energy in collisions'),('2C','Springs',3,1,'heat','Elastic potential energy, Hooke\'s law'),
 ('3A','Gravity and gravitational fields',3,2,'motion','Newton\'s law of gravitation, field models'),('3B','Gravitational potential energy',3,2,'heat','Energy from area under force and field graphs'),('3C','Orbiting satellites',3,2,'space','Satellites as uniform circular motion'),
 ('4A','Electric fields and forces',3,2,'elec','Coulomb\'s law, E = V/d, charges in fields'),('4B','Magnetic fields and forces',3,2,'elec','Force on currents and charges, motors, particle accelerators'),
 ('5A','Solar panels',3,3,'elec','Photovoltaic cells generating electricity'),('5B','Generating emf from changing flux',3,3,'elec','Faraday\'s and Lenz\'s laws'),('5C','DC generators',3,3,'elec','Split ring commutators'),('5D','AC generators',3,3,'elec','Slip rings and sinusoidal AC'),
 ('6A','Peak and rms AC',3,3,'elec','Peak, peak-to-peak and rms values'),('6B','Transformers',3,3,'elec','Ideal transformers and turns ratios'),('6C','Transmission losses',3,3,'elec','Reducing power loss in transmission lines'),
 ('7A','Wave-like properties of light',4,1,'waves','Diffraction and Young\'s double slit'),('7B','Particle-like properties of light',4,1,'waves','Photoelectric effect, photons'),
 ('8A','Matter as particles or waves',4,1,'waves','de Broglie wavelength, electron diffraction'),('8B','Similarities between light and matter',4,1,'waves','Spectra, energy levels, wave-particle duality'),
 ('9A','What is relativity?',4,1,'motion','Einstein\'s postulates, frames of reference'),('9B','Time dilation and length contraction',4,1,'motion','Lorentz factor calculations'),('9C','Muon decay',4,1,'motion','Evidence for relativity'),('9D','Mass and energy equivalence',4,1,'nuclear','E = mc^2 in Year 12 contexts')]
Y12D={c:(t,u,a,st,d) for c,t,u,a,st,d in Y12}
FWD={'1A':['7A'],'1B':['7A','7B'],'1C':['7A'],'3A':['9D'],'4A':['9D'],'4B':['9D'],'5A':['4A'],'5B':['4A','5A'],'5E':['6C'],
 '6A':['5A'],'6B':['6A','6C'],'7A':['1A','1C'],'7B':['1C'],'7C':['1C'],'8A':['2B'],'8B':['1A','1B'],'8C':['1A'],'9A':['2A'],'9B':['2A','3B'],'9C':['2C']}
J=lambda n:f'y{n[0]}-{n[1]}'
EDGES=[]
for n in NODES:
  for f in n[5]:EDGES.append((J(n),('12:'+f[3:]) if f.startswith('12:') else ('11:'+f if f in SEC else f)))
for a,bs in FWD.items():
  for b in bs:EDGES.append(('11:'+a,'12:'+b))
fed={}
for a,b in EDGES:fed.setdefault(b,[]).append(a)
gaps=[c for c in SEC if '11:'+c not in fed]
new12=[c for c in Y12D if '12:'+c not in fed]

def chip(f):
  if f.startswith('12:'):return f'<span class="ft y12">Y12 {e(f[3:])}</span>'
  return f'<span class="ft {"sec" if f in SEC else "oth"}">{e(f)}</span>'
def node(n):
  y,code,t,st,s,f=n
  tg=' '.join(chip(x) for x in f) or '<span class="ft none">no VCE link</span>'
  return f'<div class="nd" data-id="{J(n)}"><div class="nc">Y{y} · {e(code)}</div><div class="nt">{e(t)}</div><div class="ns">{e(s)}</div><div class="fl">{tg}</div></div>'
def secnode(c):
  k=len(fed.get('11:'+c,[]));fw=''.join(chip('12:'+x) for x in FWD.get(c,[]))
  return f'<div class="sn {"gap" if not k else ""}" data-id="11:{c}"><div class="sr"><b>{c}</b> {e(SEC[c][0])}<span>{k if k else "gap"}</span></div>{f"<div class=fl>{fw}</div>" if fw else ""}</div>'
def y12node(c):
  t,u,a,st,d=Y12D[c];k=len(fed.get('12:'+c,[]))
  return f'<div class="sn s12 {"new" if not k else ""}" data-id="12:{c}"><div class="sr"><b>{c}</b> {e(t)}<span>{"new" if not k else "U"+str(u)}</span></div><div class="ns">{e(d)}</div></div>'

body=''
order=list(SEC);o12=list(Y12D)
for key,name,col,a,b in STRANDS:
  ns=[n for n in NODES if n[3]==key]
  extra={'heat':['2A','2B','9A','9B','9C']}.get(key,order[order.index(a):order.index(b)+1] if a else [])
  vce=sorted({x for n in ns for x in n[5] if x in SEC}|set(extra),key=order.index)
  y12=set(c for c in Y12D if Y12D[c][3]==key)|{f[3:] for n in ns for f in n[5] if f.startswith('12:')}|{x for c in vce for x in FWD.get(c,[])}
  y12=sorted(y12,key=o12.index)
  oth=sorted({x for n in ns for x in n[5] if x not in SEC and not x.startswith('12:')})
  cols=''.join(f'<div class="col"><div class="ch">Year {y}</div>{"".join(node(n) for n in ns if n[0]==y) or "<div class=empty>nothing</div>"}</div>' for y in (7,8,9,10))
  cols+=f'<div class="col vce"><div class="ch">Year 11 · Units 1 and 2</div>{"".join(secnode(c) for c in vce)}{"".join(f"<div class=sn data-id=\"{e(x)}\"><div class=sr><b>{e(x)}</b> Unit 2 option</div></div>" for x in oth)}</div>'
  cols+=f'<div class="col vce y12c"><div class="ch">Year 12 · Units 3 and 4</div>{"".join(y12node(c) for c in y12) or "<div class=empty>nothing</div>"}</div>'
  body+=f'<section class="strand" style="--ac:{col}"><h2>{e(name)}</h2><div class="grid">{cols}</div></section>'

gaph=''.join(f'<li><b>{c}</b> {e(SEC[c][0])}</li>' for c in gaps)
newh=''.join(f'<li><b>{c}</b> {e(Y12D[c][0])}</li>' for c in new12)
CSSX="""main{max-width:1500px}.lead{color:var(--muted);font-size:14.5px;max-width:950px}
.strand{margin:26px 0}.strand h2{font-size:18px;margin:0 0 8px;border-left:6px solid var(--ac);padding-left:10px}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr)) minmax(0,1.1fr) minmax(0,1.1fr);gap:10px}
.col{display:flex;flex-direction:column;gap:6px;background:#fbfaf6;border:1px solid var(--line);border-radius:10px;padding:8px}
.col.vce{background:#fff;border:2px solid var(--ac)}.col.y12c{border-style:dashed}.ch{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
.nd{background:#fff;border:1px solid var(--line);border-left:4px solid var(--ac);border-radius:8px;padding:6px 8px;cursor:pointer}
.nd:hover,.sn:hover{box-shadow:0 2px 6px rgba(0,0,0,.08)}.nc{font-size:11px;color:var(--ac);font-weight:700}.nt{font-weight:600;font-size:13px}.ns{font-size:12px;color:var(--muted);margin:2px 0}
.fl{display:flex;flex-wrap:wrap;gap:3px;margin-top:2px}.ft{font-size:10.5px;border-radius:6px;padding:0 5px;background:#eef0f3;color:#555}.ft.sec{background:var(--ac);color:#fff}.ft.y12{background:#fff;color:var(--ac);border:1px dashed var(--ac)}.ft.none{background:transparent;color:#aaa}
.sn{font-size:13px;border:1px solid var(--line);border-radius:8px;padding:5px 8px;cursor:pointer}.sr{display:flex;gap:6px;align-items:baseline}.sn b{color:var(--ac)}.sr span{margin-left:auto;font-size:11px;color:var(--muted)}
.sn.gap{border-style:dashed;background:#fdf5f5}.sn.gap .sr span{color:#a32d2d;font-weight:600}.s12{background:#fbfbfd}.sn.new .sr span{color:#7a3fa0;font-weight:600}
.empty{font-size:12px;color:#aaa;font-style:italic}
.dim .nd:not(.hl),.dim .sn:not(.hl){opacity:.22}.hl{box-shadow:0 0 0 2px var(--ac)!important}.hl.me{box-shadow:0 0 0 3px var(--ink)!important}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:10px}.box{background:#fff;border:1px solid var(--line);border-left:6px solid #a32d2d;border-radius:10px;padding:10px 14px;margin:10px 0}.box.nw{border-left-color:#7a3fa0}.box ul{columns:2;margin:6px 0;padding-left:18px;font-size:13px}
.src{font-size:12px;color:var(--muted);margin-top:30px}
@media(max-width:1100px){.grid{grid-template-columns:1fr 1fr}.g2{grid-template-columns:1fr}.box ul{columns:1}}"""
JS="""const E=%s;const all=document.querySelectorAll('[data-id]');let cur=null;
const up={},dn={};E.forEach(([a,b])=>{(dn[a]=dn[a]||[]).push(b);(up[b]=up[b]||[]).push(a)});
function walk(s,m,out){(m[s]||[]).forEach(x=>{if(!out.has(x)){out.add(x);walk(x,m,out)}});return out}
function clr(){document.body.classList.remove('dim');all.forEach(x=>x.classList.remove('hl','me'));cur=null}
all.forEach(el=>el.onclick=ev=>{ev.stopPropagation();const k=el.dataset.id;if(cur===k)return clr();clr();cur=k;document.body.classList.add('dim');
 const S=new Set([k,...walk(k,up,new Set()),...walk(k,dn,new Set())]);all.forEach(x=>{if(S.has(x.dataset.id))x.classList.add('hl')});el.classList.add('me')});
document.body.onclick=clr;"""%json.dumps(EDGES)
page=f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Physics · Years 7 to 12 progression</title><style>{CSS}{CSSX}</style><script>if(window.self!==window.top){{document.documentElement.classList.add('emb')}}</script><style>.emb nav.crumb{{display:none!important}}.emb body{{background:transparent}}</style></head><body><main>
<nav class="crumb"><a href="./">Physics Planner</a> › Years 7 to 12 progression</nav>
<p class="lead">Every physics subtopic in Jacaranda Science Quest 7 to 10, sorted into strands and linked to the Cambridge Year 11 sections it prepares students for, then on to the Year 12 (Units 3 and 4) sections those build towards. <b>Click any card</b> to light up the whole chain before and after it. Year 11 cards show their Year 12 links as dashed chips.</p>
<div class="g2"><div class="box"><b>Year 11 sections with nothing from Years 7 to 10 ({len(gaps)})</b>: APK will need to be written ("own").<ul>{gaph}</ul></div>
<div class="box nw"><b>Year 12 sections that are new (nothing earlier feeds them) ({len(new12)})</b><ul>{newh}</ul></div></div>
{body}
<p class="src">Sources: Jacaranda Science Quest 7, 8, 9 and 10 (2021 editions, written for Victorian Curriculum 1.0), physics subtopics only; Cambridge VCE Physics Units 1&amp;2 and Units 3&amp;4 (2023) with their curriculum grids; VCE Physics Study Design 2023 to 2027. Summaries paraphrased for planning; links are a first pass (18 Nov 2026) to be checked. {len(NODES)} Jacaranda subtopics, {len(SEC)} Year 11 sections, {len(Y12D)} Year 12 sections. Year 12 reflects the current study design (Units 3 and 4: 2024 to 2027).</p>
</main><script>{JS}</script></body></html>"""
open(os.path.join(H,'..','progression.html'),'w').write(page)
print('edges',len(EDGES),'gaps',gaps,'new12',new12,'dashes',len(re.findall('[—–]',page)))
