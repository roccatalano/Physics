# Extracts the Cambridge practicals (aim, materials, safety, method, sections) into data/pracs.json.
# Usage: python3 tools/extract_pracs.py <folder holding the unzipped Cambridge topic folders>
# Source: the 23 "Practical <code>–n <title>.docx" files (Cambridge VCE Physics Units 1&2). Text kept verbatim.
import sys,os,re,json,glob,subprocess
SRC=sys.argv[1];H=os.path.dirname(os.path.abspath(__file__))
out=[]
for f in sorted(glob.glob(os.path.join(SRC,'**','*Practical *.docx'),recursive=True)):
  b=os.path.basename(f);m=re.match(r'(\d[A-E]) Practical (\d[A-E])[–-](\d+) (.*)\.docx',b)
  if not m:continue
  sec,_,n,title=m.groups()
  t=subprocess.run(['pandoc','-t','plain','--wrap=none',f],capture_output=True,text=True).stdout
  L=[l.rstrip() for l in t.split('\n')]
  heads=['Prelab','Introduction','Questions','Aim','Materials','Safety notes','Safety','Method','Results','Analysis','Discussion','Conclusion','Evaluation','Extension']
  secs={};cur=None
  for l in L:
    s=l.strip()
    if not s or re.match(r'^(Name|Teacher|Date):',s) or s.startswith('[') or set(s)<=set('+-=| '):continue
    h=next((x for x in heads if s.lower()==x.lower() or s.lower().startswith(x.lower()+' ') and len(s)<40),None)
    if h and len(s)<40:cur=h;secs.setdefault(cur,[]);continue
    if cur:secs[cur].append(s)
  clean=lambda xs:[re.sub(r'^(-|\d+\.)\s+','',x) for x in xs if not x.startswith('|')]
  method=[x for x in secs.get('Method',[]) if re.match(r'^\d+\.\s',x)]
  out.append({'id':f'P{sec}-{n}','section':sec,'n':int(n),'title':title.replace('–','-'),'file':b,
    'aim':' '.join(secs.get('Aim',[])[:3]),'materials':clean([x for x in secs.get('Materials',[]) if x.startswith('-')]),
    'safety':' '.join(secs.get('Safety notes',secs.get('Safety',[]))),
    'method':[re.sub(r'^\d+\.\s+','',x) for x in method],
    'prelab':clean(secs.get('Questions',[]))[:6],
    'has':[h for h in ['Prelab','Results','Analysis','Discussion','Conclusion','Evaluation','Extension'] if h in secs]})
json.dump(out,open(os.path.join(H,'..','data','pracs.json'),'w'),indent=1,ensure_ascii=False)
print(len(out));[print(p['id'],p['title'][:40],len(p['materials']),len(p['method']),bool(p['aim']),bool(p['safety']),p['has']) for p in out]
