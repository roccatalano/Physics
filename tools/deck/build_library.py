# Builds the slide library: one deck per Cambridge section with every usable slide (each has a data-sid ID the
# lesson generator can pick). Usage: python3 tools/deck/build_library.py [section codes...]   (default: all)
# Output: lessons/library/<code>.html (+ lessons/library/library.json listing every slide id, type and label).
import os,sys,json,re
H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,H)
import build_deck as B
R=os.path.join(H,'..','..');OUT=os.path.join(R,'lessons','library');os.makedirs(OUT,exist_ok=True)
IX=json.load(open(os.path.join(R,'interactives','interactives.json')))
AOS={1:(1,1,'Light and heat'),2:(1,1,'Light and heat'),3:(1,2,'Nuclear'),4:(1,2,'Nuclear'),5:(1,3,'Electricity'),6:(1,3,'Electricity'),7:(2,1,'Motion'),8:(2,1,'Motion'),9:(2,1,'Motion')}
def sentences(t):
  flat=' '.join(p.strip() for p in t.split('\n') if p.strip())
  return [x for x in re.split(r'(?<=[.!?])\s+(?=[A-Z•$])',flat) if x.strip()]
def spec_for(code):
  s=B.SEC[code];ch=s['chapter'];u,a,an=AOS[ch];sl=[];lab={}
  def add(d,label):sl.append(d);lab[d['id']]=(d['type'],label)
  if s.get('criteria'):
    for k in range(0,len(s['criteria']),3):add({'type':'goals','id':f'{code}-goals-{k//3+1}','criteria':s['criteria'][k:k+3]},'Learning goals '+', '.join(s['criteria'][k:k+3]))
  gl=[g['id'] for g in s.get('glossary',[])];fm=[f['id'] for f in s.get('formulas',[])]
  for k in range(0,max(len(gl),1),5):
    if gl[k:k+5] or (k==0 and fm):add({'type':'keyideas','id':f'{code}-key-{k//5+1}','glossary':gl[k:k+5],'formulas':fm[:2] if k==0 else []},'Key ideas '+str(k//5+1))
  figs={f['id']:f for f in s.get('figures',[])};used=set()
  for c in s.get('chunks',[]):
    ss=sentences(c['text']);fig=next((f for f in c.get('figures',[]) if f in figs and figs[f].get('img')),None)
    for k in range(0,len(ss),4):
      d={'type':'new','id':f'{c["id"]}-{k//4+1}','chunk':c['id'],'from':k,'sentences':4}
      if fig and k==0:d['figure']=fig;used.add(fig)
      add(d,f'New knowledge: {c.get("heading","")} ({k//4+1})')
  for fid,f in figs.items():
    if f.get('img') and fid not in used:add({'type':'figure','id':f'{fid}-fig','figure':fid},f'{f.get("label","")} {f.get("caption","")}')
  for m in IX:
    if m.get('year',11)==11 and m['section']==code:add({'type':'interactive','id':'IX-'+m['id'],'id_ix':m['id'],'heading':m['title']},'Interactive: '+m['title'])
  for v in s.get('resources',[]):
    if v['kind']=='video' and v.get('yt') and not v.get('status'):add({'type':'video','id':v['id'],'item':v['id'],'heading':'Video'},'Video: '+v['title'][:70])
  for w in s.get('worked_examples',[]):add({'type':'wedo','id':w['id'],'item':w['id'],'kib':fm[0] if fm else None},'We do: '+w.get('title',''))
  for q in (s.get('worksheet') or {}).get('questions',[]):
    if q.get('answer'):add({'type':'youtry','id':q['id'],'item':q['id'],'kib':fm[0] if fm and q.get('kind')=='calc' else None},f'Worksheet Q{q.get("n")}')
  for q in s.get('section_questions',[]):
    if q.get('answer'):add({'type':'youtry','id':q['id'],'item':q['id']},f'Section Q{q.get("n")}')
  sets={}
  for q in s.get('checkins',[]):sets.setdefault(q.get('set',1),[]).append(q)
  for st,qs in sets.items():
    for k in range(0,len(qs),3):add({'type':'donow','id':f'{code}-CI{st}-{k//3+1}','items':[q['id'] for q in qs[k:k+3]],'labels':[f'Check-in set {st} · Q{q.get("n")}' for q in qs[k:k+3]]},f'Check-in set {st}')
  ex=[{'crit':c,'q':B.CRIT[c]['exit_candidates'][0]} for c in s.get('criteria',[]) if B.CRIT.get(c,{}).get('exit_candidates') and B.CRIT[c]['exit_candidates'][0] in B.IDX]
  for k in range(0,len(ex),3):add({'type':'exit','id':f'{code}-exit-{k//3+1}','items':ex[k:k+3]},'Exit ticket '+', '.join(x['crit'] for x in ex[k:k+3]))
  for d in sl:
    if d['type']=='interactive':d['id_keep']=d['id'];d['id']=d['id'];d['_ix']=d.pop('id_ix')
  return {'name':f'library/{code}','title':s['title'],'unit':u,'aos':a,'aos_name':an,'lesson':0,'sections':[code],'slides':sl},lab
if __name__=='__main__':
  codes=sys.argv[1:] or sorted(B.SEC,key=lambda c:(int(re.match(r'\d+',c).group()),c))
  allm=json.load(open(os.path.join(OUT,'library.json'))) if os.path.exists(os.path.join(OUT,'library.json')) else {}
  for c in codes:
    sp,lab=spec_for(c)
    for d in sp['slides']:
      if d['type']=='interactive':d['id'],d['_sid']=d['_ix'],d['id']
    # build_deck's interactive type reads sd['id'] as the interactive file; keep the slide id in data-sid via _sid
    page,_=B.build(sp);fn=os.path.join(OUT,c+'.html');open(fn,'w').write(page)
    allm[c]={'title':sp['title'],'slides':[{'n':k+1,'id':d.get('_sid',d['id']),'type':t,'label':l} for k,(d,(t,l)) in enumerate(zip(sp['slides'],lab.values()))]}
    print(c,len(sp['slides']),'slides',len(page)//1024,'KB')
  json.dump(allm,open(os.path.join(OUT,'library.json'),'w'),indent=1,ensure_ascii=False)
