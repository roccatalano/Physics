# Builds data/year11.json for the Physics planner from the Cambridge VCE Physics 1&2 file inventory.
# Inputs: tools/cambridge_inventory.json (file list of the Cambridge Resources folder on G:, 18 Nov 2026)
#         tools/cambridge_unit1_sections.json (worked examples read from the Unit 1 chapter PDFs)
import json,re,os,collections
H=os.path.dirname(os.path.abspath(__file__))
INV=json.load(open(os.path.join(H,'cambridge_inventory.json')))
IDS=json.load(open(os.path.join(H,'drive_ids.json')))  # file name -> Google Drive file id (Cambridge Resources folder, 18 Nov 2026)
LABEL={'checkin':'Check-in','sq':'Section questions','ws':'Worksheet','wsans':'Worksheet answers','prac':'Practical','ppt':'PowerPoint','test':'Chapter test','resp':'Suggested responses','review':'Review questions','checklist':'Checklist','summary':'Model summary','links':'Internet resources','book':'Textbook chapter','other':'Other'}
def fl(names):
  out=[]
  for n in sorted(names):
    b=n.split('/')[-1];k=kind(b)
    out.append({'kind':k,'label':LABEL[k],'name':b.rsplit('.',1)[0].replace('–','-'),'ext':b.rsplit('.',1)[-1],'id':IDS.get(b)})
  return out
U1=json.load(open(os.path.join(H,'cambridge_unit1_sections.json')))
ROOT='G:\\Shared drives\\1. EKC CURRICULUM\\1. KLA Folders\\SCIENCE\\VCE Physics\\VCE Physics Units 1 2 [2027]\\Cambridge Resources\\'
TESTS={1:28,2:22,3:25,4:30,5:58,6:44}
AOS={'U1 AoS1 Light and heat':(1,1,'How are light and heat explained?'),'U1 AoS2 Nuclear':(1,2,'How is energy from the nucleus utilised?'),'U1 AoS3 Electricity':(1,3,'How can electricity be used to transfer energy?'),
     'U2 AoS1 Motion':(2,1,'How is motion understood?'),'U2 AoS2 Options':(2,2,'Options: How does physics inform contemporary issues and applications in society?'),'U2 AoS3 Investigation':(2,3,'How do physicists undertake investigations?')}
UNITS={1:'How is energy useful to society?',2:'How does physics help us to understand the world?'}
def kind(b):
  for k,p in [('checkin','Check-in Set'),('sq','Section questions'),('wsans','Answers'),('ws','Worksheet'),('prac','Practical'),('ppt','PowerPoint'),('test','Chapter \\d+ Test'),('resp','Suggested responses'),('review','Review questions'),('checklist','Checklist'),('summary','Summary'),('links','Curated internet'),('book','Textbook chapter')]:
    if re.search(p,b):return k
  return 'other'
units={}
tree=collections.OrderedDict()
for e in INV:
  p=e['name'].split('/')
  if p[0] not in('Unit 1','Unit 2') or len(p)<3 or p[1] not in AOS: continue
  u,a,_=AOS[p[1]];tree.setdefault(p[1],collections.OrderedDict())
  if len(p)>=4 and re.match(r'Ch\d\d ',p[2]):
    ch=tree[p[1]].setdefault(p[2],{'files':[],'secs':collections.OrderedDict()})
    if re.match(r'\d[A-Z] ',p[3]):
      ch['secs'].setdefault(p[3],[]).append(e['name'])
    else: ch['files'].append(e['name'])
  elif len(p)>=3:
    tree[p[1]].setdefault('_other',{'files':[],'secs':{}})['files'].append(e['name'])
out={'year':11,'title':'Year 11 Physics','course':'VCE Physics Units 1 and 2','source':'Cambridge Senior Science VCE Physics Units 1&2 (2023)','root':ROOT,'units':[]}
for un in (1,2):
  U={'n':un,'title':UNITS[un],'aos':[]}
  for an,(uu,a,title) in AOS.items():
    if uu!=un: continue
    A={'n':a,'title':title,'folder':an,'chapters':[],'files':[]}
    for cn,ch in tree.get(an,{}).items():
      if cn=='_other':
        names=sorted({f.split('/')[2] for f in ch['files'] if len(f.split('/'))>3 and re.match(r'\d\.\d\d ',f.split('/')[2])})
        A['options']=[{'n':x[:4].replace('.0','.'),'title':x[5:]} for x in names]
        A['files']=sorted({f.split('/')[-1] for f in ch['files'] if 'README' not in f and len(f.split('/'))==3});continue
      n=int(cn[2:4]);C={'n':n,'title':cn[5:],'folder':f'Unit {un}\\{an}\\{cn}','sections':[],'chapter':collections.Counter(),'testMarks':TESTS.get(n)}
      for f in ch['files']: C['chapter'][kind(f.split('/')[-1])]+=1
      for sn,files in ch['secs'].items():
        code=sn[:2];K=collections.Counter(kind(f.split('/')[-1]) for f in files)
        pr=[re.sub(r'^\d[A-Z] Practical ','',f.split('/')[-1].rsplit('.',1)[0]).replace('–','-') for f in files if kind(f.split('/')[-1])=='prac']
        if code in U1: pr=[x.replace('–','-') for x in U1[code]['prac']]
        we=[w.replace('–','-') for w in U1.get(code,{}).get('we',[])] if code in U1 else None
        C['sections'].append({'files':fl(files),'code':code,'title':sn[3:],'checkins':K['checkin'],'sectionQs':K['sq'],'worksheets':K['ws'],'pracs':pr,'ppts':K['ppt'],'workedExamples':we,'folder':f"{C['folder']}\\{sn}"})
      C['chapter']=dict(C['chapter']);C['files']=fl(ch['files']);A['chapters'].append(C)
    U['aos'].append(A)
  out['units'].append(U)
os.makedirs(os.path.join(H,'..','data'),exist_ok=True)
json.dump(out,open(os.path.join(H,'..','data','year11.json'),'w'),indent=1,ensure_ascii=False)
print('chapters',sum(len(a['chapters']) for u in out['units'] for a in u['aos']),'sections',sum(len(c['sections']) for u in out['units'] for a in u['aos'] for c in a['chapters']))
