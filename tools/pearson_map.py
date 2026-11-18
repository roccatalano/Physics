# Maps every Pearson Heinemann Physics 11 (5E) resource on the shared drive to the Cambridge structure.
# Cambridge is the backbone: each Pearson file is attached to a Cambridge section, chapter, AoS or the whole course.
# Input: tools/pearson_drive_ids.json (Drive path -> file id, Pearson Resources folder 17qgPQpd-XkLkS-ygIB2e_Xtmmu45jwOY).
# The unofficial textbook PDF is excluded and never linked.
import json,os,re
H=os.path.dirname(os.path.abspath(__file__))
IDS=json.load(open(os.path.join(H,'pearson_drive_ids.json')))
# Pearson section (topic) -> Cambridge sections. Used for the cross-map and for OE numbers.
PSEC={'2.1':(['1A'],'Longitudinal and transverse waves'),'2.2':(['1A'],'Measuring waves'),'2.3':(['1B'],'Electromagnetic waves'),
 '3.1':(['1C'],'Reflection, refraction, total internal reflection'),'3.2':(['1C'],'Dispersion, polarisation, rainbows and mirages'),
 '4.1':(['2A'],'Heat, temperature and internal energy'),'4.2':(['2A'],'Specific heat capacity'),'4.3':(['2A'],'Latent heat'),'4.4':(['2A'],'Conduction, convection and radiation'),
 '5.1':(['2B'],'Thermal radiation and Wien\'s law'),'5.2':(['2B'],'Global warming and climate change'),
 '6.1':(['3A'],'Nuclear stability and isotopes'),'6.2':(['3B'],'Alpha, beta and gamma radiation'),'6.3':(['3C','3D'],'Half-life and decay series'),'6.4':(['3E'],'Radiation and the human body'),
 '7.1':(['4A'],'Energy from mass and binding energy'),'7.2':(['4B','4C'],'Fission, fusion and nuclear energy for Australia'),
 '8.1':(['5A'],'Electric charge'),'8.2':(['5A','5B'],'Current and potential difference'),'8.3':(['5B','5E'],'Electrical energy and power'),'8.4':(['5C','6A'],'Resistance, ohmic and non-ohmic'),
 '9.1':(['5C','5D'],'Series and parallel circuits'),'9.2':(['6A'],'Voltage dividers, sensors and diodes'),'9.3':(['6B','6C'],'Electricity at home and electrical safety')}
PCH={2:['1A','1B'],3:['1C'],4:['2A'],5:['2B'],6:['3A','3B','3C','3D','3E'],7:['4A','4B','4C'],8:['5A','5B','5C','5E','6A'],9:['5C','5D','6A','6B','6C'],
     10:['7A'],11:['7B','7C'],12:['8A','8B'],13:['9A','9B','9C'],14:['8C']}
PCHN={2:'Waves and electromagnetic radiation',3:'Light',4:'Thermal energy',5:'Thermal energy, EM radiation and climate',6:'Radiation from the nucleus',7:'Nuclear energy',8:'Electrical physics',9:'Electric circuits',10:'Scalars and vectors',11:'Linear motion',12:'Momentum and force',13:'Energy and motion',14:'Forces and equilibrium'}
PRAC={'PA01':'1A','PA02':'1C','PA03':'1B','PA04':'2A','PA05':'2A','PA06':'2A','PA07':'3B','PA08':'3C','PA09':'4B','PA10':'5A','PA11':'6A','PA12':'5C','PA13':'5D','PA14':'5E',
      'PA15':'7B','PA16':'7C','PA17':'7C','PA18':'7C','PA19':'8B','PA20':'7C','PA21':'9B','PA22':'8A','PA23':'9B'}
OE={'2.2.1':'1A','3.2.1':'1C','4.4.1':'2A','4.4.2':'2A','5.2.1':'2B','6.3.1':'3B','6.3.2':'3C','6.4.1':'3E','6.4.2':'3E','7.2.1':'4B','7.2.2':'4C',
    '8.1.1':'5A','8.2.1':'5B','8.2.2':'5B','8.4.1':'6A','8.4.2':'5D','9.1.1':'6A','10.3.1':'8C','12.3.1':'8B','12.4.1':'8A','12.6.1':'8A','13.2.1':'9C'}
VID={'Extreme wave science':'1A','Why is the ocean blue-':'1C','What is fire-':'2A','The greenhouse effect and global warming':'2B','Alpha, beta and gamma radiation':'3B',
     'Flow of charge through a conductor':'5A','The properties of a series circuit':'5C','Current in a parallel circuit':'5D','Scalars and vectors':'7A','Reading from a graph':'7B',
     'How do airplanes fly-':'8B','The potential for fun':'9B','Equilibrium':'8C','Force arm':'8C'}
SEC2CH=lambda s:int(s[0])
def item(path,label,ref):
  b=path.split('/')[-1];return {'label':label,'name':b.rsplit('.',1)[0].replace('–','-').replace('—','-'),'ext':b.rsplit('.',1)[-1],'id':IDS[path],'ref':ref,'path':path}
def build():
  sec={};ch={};aos={};unit={};course=[];options={};inv=[];unmapped=[]
  for p in sorted(IDS):
    b=p.split('/')[-1];name=b.rsplit('.',1)[0]
    m=re.match(r'(PA\d\d) ',b)
    if m:
      lab='Risk assessment' if 'risk assessment' in b else 'Practical (SAB SPARKlab)'
      sec.setdefault(PRAC[m.group(1)],[]).append(item(p,lab,m.group(1)));continue
    m=re.match(r'(?:OE|Online experiment) (\d+\.\d+\.\d+)',b)
    if m:
      t=OE[m.group(1)];lab='Online experiment' if not re.search('teacher',b) else ('Teacher notes' if 'notes' in b else 'Risk assessment')
      sec.setdefault(t,[]).append(item(p,lab,'OE '+m.group(1)));continue
    if '/Videos/' in p:
      sec.setdefault(VID[name],[]).append(item(p,'Video',''));continue
    m=re.match(r'Ch(\d\d) fully worked solutions',b)
    if m:
      n=int(m.group(1))
      for c in sorted({SEC2CH(s) for s in PCH[n]}): ch.setdefault(c,[]).append(item(p,'Fully worked solutions',f'Pearson Ch {n}'))
      continue
    m=re.match(r'Unit (\d)/(AoS\d)',p)
    if m and ('SAB' in b or 'Review fully worked' in b or 'risk assessment' in b):
      u,a=int(m.group(1)),int(m.group(2)[3])
      lab='AoS review solutions' if 'Review' in b else 'SAB worksheet solutions' if 'worksheet solutions' in b else 'SAB exam question solutions' if 'exam question' in b else 'Prac teacher notes' if 'teacher notes' in b else 'Prac solutions' if 'practical activity solutions' in b else 'Risk assessment'
      aos.setdefault((u,a),[]).append(item(p,lab,f'Pearson Unit {u} AoS {a}'));continue
    m=re.match(r'Unit (\d) fully worked solutions',b)
    if m: unit.setdefault(int(m.group(1)),[]).append(item(p,'Fully worked solutions (all chapters)','Pearson'));continue
    m=re.search(r'Option (2\.\d+)',p)
    if m: options.setdefault(m.group(1),[]).append(item(p,'Teacher notes' if 'teacher notes' in b else 'Option reading',f'Option {m.group(1)}'));continue
    if 'AoS3 Investigation' in p: inv.append(item(p,name,'Investigation'));continue
    if p.startswith('00 Course-wide'): course.append(item(p,name,'Course-wide'));continue
    unmapped.append(p)
  return dict(sec=sec,ch=ch,aos=aos,unit=unit,course=course,options=options,inv=inv,unmapped=unmapped)
if __name__=='__main__':
  r=build();print({k:(len(v) if not isinstance(v,dict) else sum(len(x) for x in v.values())) for k,v in r.items()});print(r['unmapped'])
