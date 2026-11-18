# Builds analysis.html: how the Cambridge VCE Physics 1&2 resources are meant to be used.
# Data: tools/cambridge_unit1_sections.json (inventory of the shared drive + textbook chapter PDFs, 18 Nov 2026)
import json,html,os
H=os.path.dirname(os.path.abspath(__file__));S=json.load(open(os.path.join(H,'cambridge_unit1_sections.json')))
e=html.escape
CH={'1':('Electromagnetic radiation',44,'AoS 1: Light and heat',28),'2':('Thermal energy',34,'AoS 1: Light and heat',22),'3':('Nuclear radiation',68,'AoS 2: Energy from the nucleus',25),'4':('Nuclear energy',48,'AoS 2: Energy from the nucleus',30),'5':('Electricity',94,'AoS 3: Electricity',58),'6':('Using electricity',56,'AoS 3: Electricity',44)}
tot=dict(sec=len(S),ci=sum(v['checkin'] for v in S.values()),we=sum(len(v.get('we',[])) for v in S.values()),ws=sum(len(v['ws']) for v in S.values()),pr=sum(len(v['prac']) for v in S.values()),pp=sum(v['ppt'] for v in S.values()),pg=sum(c[1] for c in CH.values()))
def fix(s):return s.replace('–','-').replace('—','-')
rows=''
for c,(name,pg,aos,tm) in CH.items():
  secs=[(k,v) for k,v in S.items() if k[0]==c]
  rows+=f'<tr class="chrow"><td colspan="7"><b>Chapter {c}: {name}</b> <span class="mut">{aos} · {pg} textbook pages · chapter test out of {tm}</span></td></tr>'
  for k,v in secs:
    we='<br>'.join(e(fix(w)) for w in v.get('we',[])) or '<span class="none">none</span>'
    pr='<br>'.join(e(fix(p)) for p in v['prac']) or '<span class="none">none</span>'
    ws=str(len(v['ws'])) if v['ws'] else '<span class="none">0</span>'
    rows+=f'<tr><td><b>{k}</b> {e(v["name"])}</td><td class="n">{v["checkin"]}</td><td>{we}</td><td class="n">{ws}</td><td>{pr}</td><td class="n">{v["ppt"]}</td><td class="n">1</td></tr>'
CARDS=[
 ('#1f4fa0','Check-in questions','Section','Short sets of 3 to 4 questions placed straight after each chunk of theory inside a section, so a section has one to five sets.','Cambridge calls these formative assessment: a quick check that the chunk just taught has landed before moving on.',f'{tot["ci"]} sets across Unit 1, each its own Word file. Answers are in "Chapter N Suggested responses" (TEACHER ONLY).','Natural fit for checking understanding mid-lesson, or as retrieval questions later. Short and low-stakes.'),
 ('#b4532a','Worked examples','Section','Boxed, fully solved problems in the textbook, placed right after the theory they apply.','Model how to solve the section\'s calculation and reasoning problems before students try them.',f'{tot["we"]} in Unit 1, inside the chapter PDFs only (no separate files). Four sections have none: 1B, 3D, 4C and 6C.','The backbone of an "I do / we do" step. Sections without them are mostly descriptive.'),
 ('#b03a7a','Skills boxes','Section','One per section, near the end. Exam technique for the question types in that section, each with a video in the Interactive Textbook.','Advice on how to answer and prepare for questions, especially in exams.','In the chapter PDFs. The videos are online only.','Short teacher talk or a slide before practice. Good exam-habit building from Unit 1.'),
 ('#2b7a3d','Section questions','Section','A set of multiple-choice and short-answer questions at the end of each section.','Cambridge calls these summative for the section, with full answers in the digital resources.','21 files (one per section). Answers in "Chapter N Suggested responses".','The main independent practice and homework set for a section.'),
 ('#7a3fa0','Worksheets','Section','Printable extra practice for a section, usually marked out of about 15, with matching, calculation and short-answer items.','Extra questions and activities, and in some cases extra content. Editable copies are in the teacher resources.',f'{tot["ws"]} in Unit 1 (none for 3B). Answers in TEACHER ONLY.','Extension, consolidation, a relief-teacher lesson, or targeted re-teaching after a weak check-in.'),
 ('#a32d2d','Practicals','Section','A prelab (introduction, aim, prelab questions) followed by the practical (aim, materials, safety notes, method, results, discussion questions with marks).','Downloadable, editable and printable practical investigations linked to their section.',f'{tot["pr"]} in Unit 1, clustered in Ch 3 (4), Ch 5 (3) and Ch 6 (3). Ch 4 has one, a simulation. There are no worksheet-style answers for pracs on the drive.','These are the obvious source for logbook pracs. Unit 1 needs at least 15 h of practical work, so the 14 need checking against timing.'),
 ('#1d7a86','PowerPoint figures','Section','Single-figure or table slide shows taken from the book (e.g. Figure 1B-3, Table 3B-1).','Animated versions of key charts and diagrams for teachers to project.',f'{tot["pp"]} in Unit 1 section folders plus one in the Ch 4 review folder.','Drop-in visuals for slides. They are not lesson decks.'),
 ('#9a6b00','Chapter review','Chapter','Four parts: a summary task, a checklist of success criteria, then multiple-choice and short-answer review questions.','Students write their own summary notes (Cambridge provides a model summary). The checklist lists the chapter\'s learning objectives as success criteria, each linked to the review questions that test it, so students tick off what they can do.','6 checklists, 6 summaries (model answers), 6 review question sets (Ch 1 has 36 questions), 6 curated internet resource lists.','A built-in end-of-chapter revision lesson, and a ready-made success-criteria list. The links between criteria and questions make it easy to target weak spots.'),
 ('#c2410c','Chapter tests','Chapter','One editable test per chapter in TEACHER ONLY, multiple choice then short answer, with worked answers at the end of the same file.','Editable and printable chapter tests with answers, in the teacher resources.','Totals vary a lot: Ch 1 /28, Ch 2 /22, Ch 3 /25, Ch 4 /30, Ch 5 /58, Ch 6 /44.','Fits a topic test or CFAT after each chapter. The longer ones would need trimming to fit a single lesson.'),
 ('#5f5e5a','Unit revision and practice exam','Unit / course','A Unit 1 revision exercise (24 questions, with suggested responses), the textbook\'s revision pages, and a Units 1&2 practice exam (reading 15 min, writing 95 min, Section A 20 MC, Section B 28 short answer, 83 marks) with answers.','End-of-unit revision. The practice exam was made by Cambridge\'s exam generator from VCAA questions.','Course-wide folder and Unit 1 Revision folder.','Semester exam preparation. Check the practice exam\'s topic coverage first (see Flags).'),
]
cards=''.join(f'<div class="rc" style="--c:{c}"><div class="lvl">{lv}</div><h3>{e(t)}</h3><p><b>What it is.</b> {e(w)}</p><p><b>What Cambridge says it is for.</b> {e(y)}</p><p><b>On the drive.</b> {e(d)}</p><p class="use"><b>Planning note.</b> {e(u)}</p></div>' for c,t,lv,w,y,d,u in CARDS)
FLOW=[('Study Design + glossary','Each section opens with its dot points and key terms'),('Engage','Not assessed: real-world hook'),('Explain','The assessable content, with concept videos'),('Check-ins','After each chunk of theory'),('Worked examples','Fully solved, after the theory'),('Skills','Exam technique + video'),('Section questions','MC + short answer to finish')]
flow='<div class="flow">'+'<div class="arr">→</div>'.join(f'<div class="fc"><b>{e(a)}</b><span>{e(b)}</span></div>' for a,b in FLOW)+'</div>'
CFLOW=[('Chapter opener','Learning objectives table and concept map'),('Sections','2 to 5 per chapter, each as above, with worksheets and pracs alongside'),('Chapter review','Summary, checklist, MC + short-answer review'),('Chapter test','Teacher-only, editable, with answers')]
cflow='<div class="flow f4">'+'<div class="arr">→</div>'.join(f'<div class="fc"><b>{e(a)}</b><span>{e(b)}</span></div>' for a,b in CFLOW)+'</div>'
FLAGS=[
 ('Online only, not on the drive','The Interactive Textbook videos (concept and skills videos), the "Scorcher" key-term quizzes, the Years 9 and 10 prior-knowledge quiz, Cambridge\'s teaching programs, teacher notes, the question bank and test generator, and extra assessment tasks all live in the Online Teaching Suite. None are in the shared drive folders. The teaching programs would be worth downloading if the school has access.'),
 ('Gaps in the section files','3B has no worksheet. 1B, 3D, 4C and 6C have no worked examples. Ch 4 has a single practical and it is a simulation.'),
 ('Chapter tests are uneven','Totals run from 22 to 58 marks. Ch 5 (58) and Ch 6 (44) are too long for one lesson as written.'),
 ('Practice exam scope','It was generated from VCAA questions. At least one item (DC motor torque) looks like content outside the 2023 Units 1&2 study design. Check every question before using it as a semester exam.'),
 ('Corrections','Course-wide\\Updates_Feb2023.pdf lists errata for the first print, e.g. 1A Check-in Set 2 Q2 should ask for the wave equation with T as the subject. Apply these before using the affected items.'),
 ('Odd files','Course-wide holds Physics12_book.pdf (64 MB, looks like a different book) and the Unit 2 investigation folders only contain placeholder README files.'),
 ('Answers','Check-ins and section questions: "Chapter N Suggested responses". Worksheets: separate answer files. Chapter tests: answers inside the test file. All in TEACHER ONLY folders. Ch 2\'s suggested responses is a PDF, not a Word file.'),
]
flags=''.join(f'<div class="flag"><b>{e(a)}</b><p>{e(b)}</p></div>' for a,b in FLAGS)
stats=[('6','chapters'),(tot['sec'],'sections'),(tot['pg'],'textbook pages'),(tot['ci'],'check-in sets'),(tot['we'],'worked examples'),(tot['ws'],'worksheets'),(tot['pr'],'practicals'),('6','chapter tests')]
st=''.join(f'<div class="st"><b>{a}</b><span>{b}</span></div>' for a,b in stats)
IMP=[('Lesson unit','Cambridge is organised by section, not by lesson. Sections vary from about 2 to 15 pages and 0 to 7 worked examples, so some sections fit one lesson and others need two or three.'),
 ('Inside a lesson','The textbook\'s own rhythm is teach a chunk, check-in, teach, check-in, worked example, practise. That maps closely onto explain, check, model, practise.'),
 ('End of a section','Section questions are the natural independent practice or homework. Worksheets add depth where needed.'),
 ('End of a chapter','The review is a ready-made revision lesson, the checklist is a ready-made set of success criteria, and the chapter test is a ready-made CFAT or topic test.'),
 ('Pracs','14 practicals sit inside their sections. Whether they run as a weekly prac lesson or inside the section is a timetabling choice, not something Cambridge prescribes.'),
 ('Still open','Where do-nows, APK and exit tickets come from? Cambridge\'s check-ins and section questions can supply them, but it does not label anything as a do-now or exit ticket.')]
imp=''.join(f'<div class="rc" style="--c:#1f4fa0"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a,b in IMP)
CSS="""
*{box-sizing:border-box;margin:0;padding:0}body{background:#f6f5f1;color:#1f1e1c;font:15px/1.55 system-ui,'Segoe UI',sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:40px 28px 80px}a{color:#1f4fa0}
h1,h2,h3{font-family:system-ui,'Segoe UI',sans-serif;letter-spacing:-.01em;color:#1f1e1c}h1{font-size:28px;line-height:1.15}h2{font-size:28px;margin:46px 0 14px}h3{font-size:19px;margin-bottom:8px;color:var(--c,#1f1e1c)}
.tags{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}.tags span{font:700 13px system-ui;border:2px solid var(--k);color:var(--k);border-radius:99px;padding:5px 14px}
.lead{color:#6b6a65;font-size:18px;max-width:820px;margin-top:12px}.mut{color:#6b6a65;font-weight:400}
.stats{display:grid;grid-template-columns:repeat(8,1fr);gap:10px;margin-top:28px}.st{background:#fff;border:1px solid #e2e0d8;border-radius:14px;padding:14px;text-align:center}.st b{display:block;font:700 28px system-ui;color:#1f4fa0}.st span{font-size:12px;color:#6b6a65}
.flow{display:grid;grid-template-columns:repeat(7,1fr 24px);grid-template-columns:1fr 24px 1fr 24px 1fr 24px 1fr 24px 1fr 24px 1fr 24px 1fr;align-items:stretch;gap:0}.flow.f4{grid-template-columns:1fr 24px 1fr 24px 1fr 24px 1fr}
.fc{background:#fff;border:1px solid #e2e0d8;border-top:4px solid #1f4fa0;border-radius:12px;padding:12px}.fc b{display:block;font-size:14px;color:#1f1e1c;margin-bottom:4px}.fc span{font-size:12.5px;color:#6b6a65}.arr{display:grid;place-items:center;color:#9a988f;font-size:20px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.rc{background:#fff;border:1px solid #e2e0d8;border-left:6px solid var(--c);border-radius:14px;padding:18px 20px}.rc p{font-size:13.5px;margin:6px 0;color:#1f1e1c}.rc .use{color:#8a5a00}.lvl{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#6b6a65;margin-bottom:2px}
table{width:100%;border-collapse:collapse;font-size:13.5px;background:#fff;border:1px solid #e2e0d8;border-radius:14px;overflow:hidden}th{background:#fbfaf6;color:#6b6a65;text-align:left;padding:10px;font-size:12px;text-transform:uppercase;letter-spacing:.06em}td{padding:8px 10px;border-top:1px solid #e2e0d8;vertical-align:top}td.n{text-align:center}.chrow td{background:#eef3fb;padding:10px}.none{color:#a32d2d}
.flag{background:#fff;border:1px solid #e2e0d8;border-left:6px solid #a32d2d;border-radius:14px;padding:14px 18px;margin-bottom:10px}.flag p{font-size:13.5px;color:#1f1e1c;margin-top:4px}
.src{font-size:12px;color:#6b6a65;margin-top:40px}nav{margin-bottom:26px;font-size:14px}"""
page=f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Physics · How the Cambridge resources are meant to be used</title><style>{CSS}</style><script>if(window.self!==window.top){{document.documentElement.classList.add('emb')}}</script><style>.emb .top,.emb nav,.emb nav.crumb{{display:none!important}}.emb body{{background:transparent}}.emb main,.emb .wrap{{padding-top:4px}}</style></head><body><div class="wrap">
<nav><a href="./">Physics Planner</a> › Cambridge resources</nav>
<div class="tags"><span style="--k:#1f4fa0">Unit 1</span><span style="--k:#b4532a">Cambridge VCE Physics 1&amp;2</span><span style="--k:#b03a7a">Analysis</span></div>
<h1>How the Cambridge resources are meant to be used</h1>
<p class="lead">What Cambridge provides for Unit 1, how its pieces fit together, what Cambridge says each one is for, and what that means for planning. Based on the textbook's "How to use this resource" overview, the six Unit 1 chapter PDFs and every file in the Cambridge Resources folder on the shared drive.</p>
<div class="stats">{st}</div>
<h2>The design: one section</h2><p class="mut" style="margin-bottom:14px">Every section follows the same pattern. Check-ins are spread through the theory, not left to the end.</p>{flow}
<h2>The design: one chapter</h2>{cflow}
<p class="mut" style="margin-top:12px">Learning objectives at the start of each chapter come straight from the study design. They return at the end as the checklist's success criteria, each linked to the review questions that assess it. Units close with a revision exercise; the course closes with a practice exam.</p>
<h2>Every resource type</h2><div class="grid">{cards}</div>
<h2>Unit 1, section by section</h2>
<table><tr><th>Section</th><th>Check-in sets</th><th>Worked examples (textbook)</th><th>Worksheets</th><th>Practicals</th><th>PowerPoints</th><th>Section Qs</th></tr>{rows}</table>
<h2>What this means for planning</h2><div class="grid">{imp}</div>
<h2>Flags</h2>{flags}
<p class="src">Sources: Cambridge Senior Science VCE Physics Units 1&amp;2, textbook front matter ("Overview: How to use this resource"), Unit 1 chapter PDFs, Curriculum grid, Updates Feb 2023, and the Cambridge Resources folder (359 files) on the shared drive, inventoried 18 Nov 2026. Counts of worked examples are taken from the chapter PDFs. These are licensed school resources: this page describes them and does not reproduce them.</p>
</div></body></html>"""
open(os.path.join(H,'..','analysis.html'),'w').write(page)
import re;print('dashes',len(re.findall('[—–]',page)))
