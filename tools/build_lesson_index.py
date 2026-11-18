# Builds tools/lesson_index.json: a public-safe summary of the private lesson index
# (G:\...\VCE Physics Units 1 2 [2027]\Yr 11 Cambridge Index, built 18 Nov 2026; format in its SCHEMA.md).
# Only IDs, headings, counts and tags are copied here. No question text, answers or images:
# the index holds licensed Cambridge text and this repo is public.
# Usage: python3 tools/build_lesson_index.py <path to the index folder>   (then re-run build_year11.py)
# SHOW lists the sections whose planner card shows the lesson resources (Rocco, 18 Nov 2026: start with 1A).
import json,os,sys,glob,collections
H=os.path.dirname(os.path.abspath(__file__))
SRC=sys.argv[1] if len(sys.argv)>1 else '/home/claude/index'
SHOW=None  # None = every section (Rocco, 18 Nov 2026)
out={}
for chf in sorted(glob.glob(os.path.join(SRC,'ch*','ch*.json'))):
  ch=json.load(open(chf));d=os.path.dirname(chf)
  crit={c['id']:c for c in ch['criteria']}
  rq={q['id']:q for q in ch['review_questions']}
  for code in ch['sections']:
    p=os.path.join(d,code+'.json')
    if (SHOW and code not in SHOW) or not os.path.exists(p):continue
    s=json.load(open(p))
    tag=lambda q:{'id':q['id'],'kind':q.get('kind'),'kind2':q.get('kind2'),'size':q.get('size'),'crit':q.get('criteria',[])}
    ws=(s.get('worksheet') or {})
    allq={**{q['id']:q for q in s.get('checkins',[])},**{q['id']:q for q in s.get('section_questions',[])},**{q['id']:q for q in ws.get('questions',[])},**rq,**{w['id']:w for w in s.get('worked_examples',[])}}
    sizes=lambda L:dict(collections.Counter(q.get('size') for q in L))
    out[code]={
      'path':f"Yr 11 Cambridge Index\\{os.path.basename(d)}\\{code}.json",
      'criteria':[{'id':c,'exit':[{'id':x,'size':allq.get(x,{}).get('size')} for x in crit.get(c,{}).get('exit_candidates',[])]} for c in s.get('criteria',[])],
      'studyDesign':len(s.get('study_design',[])),
      'glossary':[g['term'] for g in s.get('glossary',[])],
      'formulas':[{'id':f['id'],'name':f.get('name')} for f in s.get('formulas',[])],
      'chunks':[{'id':c['id'],'heading':c.get('heading')} for c in s.get('chunks',[])],
      'engage':(s.get('engage') or {}).get('heading'),
      'figures':[{'id':f['id'],'label':f.get('label'),'img':f.get('img'),'important':f.get('important')} for f in s.get('figures',[])],
      'workedExamples':[{'id':w['id'],'title':w.get('title'),'steps':len(w.get('steps',[])),'crit':w.get('criteria',[])} for w in s.get('worked_examples',[])],
      'wedo':[{'crit':w.get('criteria',[]),'wedo':w.get('wedo'),'youtry':w.get('youtry',[]),'origin':w.get('origin','cambridge')} for w in s.get('wedo_plan',[])],
      'checkins':{'sets':sorted({q.get('set') for q in s.get('checkins',[])}),'n':len(s.get('checkins',[])),'sizes':sizes(s.get('checkins',[])),'items':[tag(q) for q in s.get('checkins',[])]},
      'sectionQs':{'n':len(s.get('section_questions',[])),'sizes':sizes(s.get('section_questions',[])),'items':[tag(q) for q in s.get('section_questions',[])]},
      'worksheet':{'title':ws.get('title'),'total':ws.get('total'),'n':len(ws.get('questions',[])),'items':[tag(q) for q in ws.get('questions',[])]},
      'reviewQs':sorted({r for c in s.get('criteria',[]) for r in crit.get(c,{}).get('review_qs',[])},key=lambda x:(len(x),x)),
      'skills':[k.get('heading') for k in s.get('skills',[])],
      'pracs':[p.get('title') for p in s.get('pracs',[])],
      'images':sorted({f.get('img') for f in s.get('figures',[]) if f.get('img')}|{i for L in (s.get('worked_examples',[]),s.get('section_questions',[]),ws.get('questions',[])) for q in L for i in q.get('img',[])}),
      'missingAnswers':[q['id'] for L in (s.get('checkins',[]),s.get('section_questions',[]),ws.get('questions',[])) for q in L if q.get('answer') in (None,'')],
    }
json.dump(out,open(os.path.join(H,'lesson_index.json'),'w'),indent=1,ensure_ascii=False)
print('sections',list(out))
