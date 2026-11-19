// Interactives. Each one gives the class a job: predict then test, measure, or reach a mission state.
const C={cy:'#7dd3fc',am:'#fbb040',pk:'#f472b6',gr:'#4ade80',mu:'#94a3c8',ln:'#33407a'};
const ln=(c,x1,y1,x2,y2)=>{c.beginPath();c.moveTo(x1,y1);c.lineTo(x2,y2);c.stroke()};
const dot=(c,x,y,r,col)=>{c.beginPath();c.arc(x,y,r,0,7);c.fillStyle=col;c.fill()};
const txt=(c,s,x,y,col='#cfd7f5',f='600 14px Inter',al='left')=>{c.fillStyle=col;c.font=f;c.textAlign=al;c.fillText(s,x,y);c.textAlign='left'};

// ===== Lesson 1: one rope, three jobs. Each lab opens with a clicker-driven walkthrough, then hands over the controls.
// The slide holds invisible step markers (.stg). The number revealed so far is the stage.
function stager(host,side,caps,onStage){const sl=host.closest('.slide'),box=el('div','capbox');host.append(box);let last=-1;
  return ()=>{const k=Math.min(caps.length-1,$$('.stg.shown',sl).length);
    if(k!==last){last=k;const free=k===caps.length-1;side.style.display=free?'':'none';box.style.display=free?'none':'';
      box.innerHTML=`<small>Step ${k+1} of ${caps.length-1}</small><p>${mx(caps[k])}</p><i>Click for the next step</i>`;onStage(k)}return k}}
SIMS.wave=(host,o)=>{const {c,cv,side,W,H}=lab(host,800,470),PX=90,X=x=>40+x*PX,Y0=H/2;
  const arrow=(x1,y1,x2,y2,col)=>{c.strokeStyle=col;c.fillStyle=col;c.lineWidth=2.5;ln(c,x1,y1,x2,y2);[[x1,y1,x2,y2],[x2,y2,x1,y1]].forEach(([a,b,p,q])=>{const g=Math.atan2(b-q,a-p);c.beginPath();c.moveTo(a,b);c.lineTo(a-10*Math.cos(g-.4),b-10*Math.sin(g-.4));c.lineTo(a-10*Math.cos(g+.4),b-10*Math.sin(g+.4));c.fill()})};

  if(o.mode==='types'){let type='T',t=99,n=3,k=0;const f=1,v=2;
    const pills=choice(side,'Wave type',[['T','Transverse'],['L','Longitudinal']],'T',q=>{type=q;t=99});
    const b=el('button','btn','Send three waves');b.style.cssText='font-size:18px;padding:12px';b.onclick=()=>{n=3;t=0};side.append(b);
    const out=el('div','read');side.append(out);
    const stage=stager(host,side,[
      'A row of particles, linked together like the coils of a spring. Nothing is moving yet.',
      'Keep your eye on the <b class="pk">pink</b> particle. The dotted ring marks where it starts.',
      'The source shakes up and down once. Watch the shake pass along the row.',
      'The <b class="hl">orange band</b> shows where the energy is. It goes all the way to the far end.',
      'Look at the pink particle now. It is back where it started.',
      'Now the source pushes back and forth instead. The energy still travels. The particles still stay.',
      ''],q=>{k=q;type=q===5?'L':'T';n=q===2?1:3;t=(q===2||q===3||q===5)?0:99;if(q===6)$$('.pill',pills).forEach((p,i)=>p.classList.toggle('on',i===0))});
    loop(host,dt=>{stage();t+=dt;const A=type==='T'?.34:.2,s=x=>{const u=t-x/v;return u>0&&u<n/f?A*Math.sin(2*Math.PI*f*u):0};
      c.clearRect(0,0,W,H);const xa=Math.max(0,v*(t-n/f)),xb=Math.min(8,v*t);
      if(k>=3&&xb>xa){c.fillStyle='rgba(251,176,64,.09)';c.fillRect(X(xa),50,X(xb)-X(xa),H-100);txt(c,'energy is here',X(xa)+8,70,C.am)}
      c.strokeStyle=C.ln;c.lineWidth=1.5;c.setLineDash([5,6]);ln(c,X(0),Y0,X(8),Y0);c.setLineDash([]);
      for(let i=0;i<=64;i++){const x=i/8,d=s(x)*PX,red=i===32&&k>=1;
        if(type==='T')dot(c,X(x),Y0-d,red?9:4.5,red?C.pk:C.cy);
        else{c.strokeStyle=red?C.pk:C.cy;c.lineWidth=red?6:2.5;ln(c,X(x)+d,Y0-50,X(x)+d,Y0+50)}}
      if(k>=1){c.strokeStyle=C.pk;c.lineWidth=1.5;c.setLineDash([3,4]);c.beginPath();c.arc(X(4),Y0,15,0,7);c.stroke();c.setLineDash([]);
        txt(c,'start',X(4),Y0+(type==='T'?150:84),C.pk,'600 13px Inter','center')}
      txt(c,'source',X(0),H-24,C.mu,'600 13px Inter','center');txt(c,'8 m away',X(8),H-24,C.mu,'600 13px Inter','center');
      if(k>=2)txt(c,type==='T'?'Transverse: each particle moves up and down':'Longitudinal: each particle moves back and forth',W/2,34,'#fff','700 17px Space Grotesk','center');
      if(k>=3&&k<6)txt(c,`energy has travelled ${xb.toFixed(1)} m   ·   pink particle is ${Math.abs(s(4)).toFixed(2)} m from its start`,W/2,H-52,'#fff','600 15px Inter','center');
      out.innerHTML=`Energy has travelled <b>${xb.toFixed(1)} m</b><br>Pink particle is <b>${Math.abs(s(4)).toFixed(2)} m</b> from its start`})}

  if(o.mode==='measure'){const PY=340;let P={lam:2,T:1,A:.3},t=0,run=true,slow=false,m=[1,3],sw=0,base=0,k=0;
    const y=(x,tt)=>P.A*Math.sin(2*Math.PI*(tt/P.T-x/P.lam)),ph=()=>Math.floor(t/P.T-m[0]/P.lam-.25);
    const bt=el('div','btns');side.append(bt);const B=(s,f)=>{const b=el('button','btn alt',s);b.onclick=()=>f(b);bt.append(b);return b};
    const fz=B('Freeze',b=>{run=!run;b.textContent=run?'Freeze':'Run'});B('Slow motion',b=>{slow=!slow;b.classList.toggle('alt',!slow)});B('Reset stopwatch',()=>{sw=0;base=ph()});
    const out=el('div','read');side.append(out);const box=el('div');side.append(box);
    box.append(el('div','muted','Measure, then check. Nothing is given.'));
    const A=[ask(box,'$A$','m',()=>P.A,.13),ask(box,'$\\lambda$','m',()=>P.lam,.06),ask(box,'$T$','s',()=>P.T,.09),ask(box,'$v$','m/s',()=>P.lam/P.T,.1)];
    const nb=el('div','btns');side.append(nb);const nw=el('button','btn','New wave'),sa=el('button','btn alt','Show answers');nb.append(nw,sa);sa.onclick=()=>A.forEach(q=>q.show());
    const fresh=()=>{P={lam:pick([1,1.5,2.5,3,4]),T:pick([.5,.8,1.25,2]),A:pick([.2,.4,.5])};A.forEach(a=>a.clear());sw=0;base=ph()};nw.onclick=fresh;
    drag(cv,W,(x)=>{if(k<2)return;const xm=Math.max(0,Math.min(8,Math.round((x-40)/PX*20)/20)),j=Math.abs(xm-m[0])<Math.abs(xm-m[1])?0:1;m[j]=xm;if(j===0){sw=0;base=ph()}});
    const stage=stager(host,side,[
      'A wave on a grid. Each square is 0.5 m wide and 0.1 m high.',
      'Freeze it. <b>Amplitude</b> is the height from the rest line up to a crest. Here it is 0.30 m.',
      '<b>Wavelength</b> is the distance from one crest to the next. The two rulers measure it: 2.00 m.',
      'Let it run. <b>Period</b> is the time for one full bob of the cork. Time 5 bobs, then divide by 5.',
      ''],q=>{k=q;if(q<4){P={lam:2,T:1,A:.3};m=[1,3]}run=!(q===1||q===2);if(!run)t=.75;slow=false;sw=0;base=ph();fz.textContent='Freeze';if(q===4)fresh()});
    loop(host,dt=>{stage();if(run){const d=dt*(slow?.25:1);t+=d;sw+=d}
      c.clearRect(0,0,W,H);c.lineWidth=1;
      for(let i=0;i<=16;i++){c.strokeStyle=i%2?'#1a2350':'#28336e';ln(c,X(i/2),30,X(i/2),H-36);if(i%2===0)txt(c,i/2+(i===16?' m':''),X(i/2),H-16,C.mu,'600 13px Inter','center')}
      for(let j=-5;j<=5;j++){c.strokeStyle=j?'#1a2350':'#3a4790';ln(c,X(0),Y0-j*.1*PY,X(8),Y0-j*.1*PY);if(j%5===0||Math.abs(j)===2)txt(c,(j/10).toFixed(1),8,Y0-j*.1*PY+4,C.mu,'600 12px Inter')}
      c.beginPath();for(let px=0;px<=720;px+=2){const yy=Y0-y(px/PX,t)*PY;px?c.lineTo(40+px,yy):c.moveTo(40+px,yy)}c.strokeStyle=C.cy;c.lineWidth=3.5;c.stroke();
      if(k===1){arrow(X(1),Y0,X(1),Y0-P.A*PY,C.pk);txt(c,'A = 0.30 m',X(1)+12,Y0-P.A*PY/2+5,C.pk,'700 17px Inter')}
      if(k>=2)m.forEach(xm=>{c.strokeStyle=C.am;c.lineWidth=2;ln(c,X(xm),30,X(xm),H-36);c.fillStyle=C.am;c.fillRect(X(xm)-9,22,18,12);txt(c,xm.toFixed(2)+' m',X(xm),18,C.am,'700 13px Inter','center')});
      if(k===2){arrow(X(1),64,X(3),64,C.pk);txt(c,'λ = 2.00 m',X(2),56,C.pk,'700 17px Inter','center')}
      if(k>=3)dot(c,X(m[0]),Y0-y(m[0],t)*PY,9,C.pk);
      if(k===3)txt(c,`stopwatch ${sw.toFixed(2)} s   ·   cork bobs ${Math.max(0,ph()-base)}`,W/2,H-50,'#fff','700 18px Inter','center');
      out.innerHTML=`Rulers are <b>${Math.abs(m[1]-m[0]).toFixed(2)} m</b> apart<br>Stopwatch <b>${sw.toFixed(2)} s</b> · cork bobs <b>${Math.max(0,ph()-base)}</b>`})}

  if(o.mode==='control'){const PY=170;let f=1,v=2,A=.3,t=0,touched=false,k=0;
    const fs=slider(side,'Source: shakes per second',.5,3,.25,1,x=>x.toFixed(2)+' Hz',x=>f=x);
    choice(side,'Medium',[[4,'Light string'],[2,'Heavy rope'],[1,'Slinky spring']],2,q=>v=q);
    slider(side,'Amplitude',.1,.5,.05,.3,x=>x.toFixed(2)+' m',x=>{if(x!==.3)touched=true;A=x});
    const out=el('div','read');side.append(out);
    const tick=missions(side,[
      {t:'Make a wave with $\\lambda = 2.0$ m.',ok:s=>Math.abs(s.lam-2)<.01,d:'There are three ways to do it. Each one has the same $\\dfrac{v}{f}$.'},
      {t:'Heavy rope only. Make $\\lambda = 1.0$ m.',ok:s=>s.v===2&&s.f===2,d:'Same medium, same speed. Shaking faster squeezed the waves together.'},
      {t:'Keep the source at 1.00 Hz. Get $\\lambda = 4.0$ m.',ok:s=>s.f===1&&s.v===4,d:'A faster medium stretches the wave. The source did not change.'},
      {t:'Change only the amplitude. What happens to $\\lambda$?',ok:s=>s.touched,d:'Nothing. Amplitude changes the energy, not $v$, $f$ or $\\lambda$.'}],()=>({f,v,lam:v/f,touched}));
    const stage=stager(host,side,[
      'A hand shakes one end of a heavy rope, once every second.',
      'The <b>source</b> sets the frequency: how many waves it makes each second. Here $f = 1.00$ Hz.',
      'The <b>medium</b> sets the speed. Follow the <b class="pk">marked crest</b>: on this rope it covers 2 m every second.',
      'The wavelength is the result of those two: $\\lambda = \\dfrac{v}{f} = 2.00$ m.',
      ''],q=>{k=q;if(q<4){f=1;v=2;A=.3}else{fs.value=1.5;fs.oninput()}});
    loop(host,dt=>{stage();t+=dt;if(k===4)tick(dt);const lam=v/f;c.clearRect(0,0,W,H);
      for(let i=0;i<=8;i++){c.strokeStyle='#1e2858';c.lineWidth=1;ln(c,X(i),60,X(i),H-40);txt(c,i+(i===8?' m':''),X(i),H-18,C.mu,'600 13px Inter','center')}
      c.beginPath();for(let px=0;px<=720;px+=2){const yy=Y0-A*Math.sin(2*Math.PI*(f*t-px/PX/lam))*PY;px?c.lineTo(40+px,yy):c.moveTo(40+px,yy)}c.strokeStyle=C.cy;c.lineWidth=v===4?2:v===2?5:3.5;c.stroke();
      dot(c,X(0),Y0-A*Math.sin(2*Math.PI*f*t)*PY,11,C.am);txt(c,'source',X(0)+4,H-52,C.am,'600 13px Inter','center');
      if(k===1)txt(c,'f = 1.00 Hz: one shake every second',X(0)+20,Y0-A*PY-40,C.am,'700 17px Inter');
      if(k===2){const xc=((v*t-lam*.25)%8+8)%8;dot(c,X(xc),Y0-A*PY,9,C.pk);txt(c,'v = 2.0 m/s',X(xc),Y0-A*PY-18,C.pk,'700 17px Inter','center')}
      if(k>=3){let xk=lam*(((f*t-.25)%1+1)%1);if(xk<.25)xk+=lam;
        if(xk+lam<=8){const yb=Y0-A*PY-22;arrow(X(xk),yb,X(xk+lam),yb,C.pk);txt(c,'λ = '+lam.toFixed(2)+' m',X(xk+lam/2),yb-12,C.pk,'700 16px Inter','center')}
        else txt(c,'λ = '+lam.toFixed(2)+' m (longer than the rope shown)',W/2,50,C.pk,'700 16px Inter','center')}
      out.innerHTML=`Source sets <b>f = ${f.toFixed(2)} Hz</b><br>Medium sets <b>v = ${v.toFixed(1)} m/s</b><br>Result: <b class="pk">λ = ${lam.toFixed(2)} m</b>`})}
};

// ===== Lesson 2
SIMS.em=host=>{const {c,side,W,H}=lab(host,800,470);let t=0;
  side.append(el('div','read','<b class="hl">Electric field</b> vibrates up and down.<br><b class="cy">Magnetic field</b> vibrates in and out.<br>Both are at right angles to the direction of travel.'));
  side.append(el('div','note','No particles are moving. The fields themselves vibrate, so the wave needs <b>no medium</b>.'));
  side.append(el('div','read','In a vacuum, every electromagnetic wave travels at<br><b style="font-size:20px">c = 3.0 × 10⁸ m s⁻¹</b>'));
  loop(host,dt=>{t+=dt;c.clearRect(0,0,W,H);const x0=70,y0=250,L=640;
    c.strokeStyle=C.mu;c.lineWidth=2;ln(c,x0,y0,x0+L+40,y0);c.beginPath();c.moveTo(x0+L+52,y0);c.lineTo(x0+L+36,y0-7);c.lineTo(x0+L+36,y0+7);c.fillStyle=C.mu;c.fill();
    for(let i=0;i<=48;i++){const x=x0+i*L/48,s=Math.sin(i/48*4*Math.PI-t*3);
      c.strokeStyle=C.am;c.lineWidth=2;ln(c,x,y0,x,y0-s*120);c.strokeStyle=C.cy;ln(c,x,y0,x-s*62,y0+s*46)}
    txt(c,'E',x0-28,y0-104,C.am,'700 24px Space Grotesk');txt(c,'B',x0-52,y0+70,C.cy,'700 24px Space Grotesk');
    txt(c,'direction of travel, speed c',x0+L+40,y0+150,C.mu,'600 14px Inter','right')})};

const REG=[['Radio',3,-1,'#64748b','broadcast radio and TV, CB radio, MRI scanners'],['Microwave',-1,-3,'#0ea5e9','phones, wi-fi, GPS, radar, cooking'],['Infrared',-3,-6.155,'#ef4444','remote controls, thermal cameras, heat lamps, optical fibre'],['Visible',-6.155,-6.398,'#facc15','sight, photosynthesis, lasers'],['Ultraviolet',-6.398,-8,'#8b5cf6','sterilising, vitamin D, forensic lamps'],['X-ray',-8,-11,'#22c55e','medical imaging, airport scanners'],['Gamma',-11,-13.01,'#f97316','radiotherapy, sterilising equipment']];
const SIZE=[[3,'a small town'],[2,'a football oval'],[1,'a house'],[0,'a person'],[-1,'a hand'],[-2,'a fingernail'],[-3,'a grain of sand'],[-4,'the width of a hair'],[-5,'a red blood cell'],[-6,'a bacterium'],[-7,'a virus'],[-8,'a large molecule'],[-9,'a small molecule'],[-10,'an atom'],[-99,'smaller than an atom']];
function nmRGB(w){let r=0,g=0,b=0;if(w<440){r=(440-w)/60;b=1}else if(w<490){g=(w-440)/50;b=1}else if(w<510){g=1;b=(510-w)/20}else if(w<580){r=(w-510)/70;g=1}else if(w<645){r=1;g=(645-w)/65}else r=1;return`rgb(${r*255|0},${g*255|0},${b*255|0})`}
SIMS.spectrum=host=>{const {c,cv,side,W,H}=lab(host,800,470);let e=0,t=0;const xe=q=>40+(3-q)/16*720;
  const sl=slider(side,'Zoom through the spectrum',0,16,.01,3,()=>'',v=>e=3-v);
  const out=el('div','read');side.append(out);
  const near=q=>s=>Math.abs(s.e-q)<.035,fq=f=>Math.log10(3e8/f);
  const tick=missions(side,[
    {t:'Nova broadcasts at <b>100.3 MHz</b>. Find it.',ok:near(fq(100.3e6)),d:'Radio. One wave is about 3 m long: the size of a room.'},
    {t:'A microwave oven runs at <b>2.45 GHz</b>.',ok:near(fq(2.45e9)),d:'Microwave. $\\lambda \\approx 12$ cm, close to the width of your hand.'},
    {t:'Green light has $\\lambda = 550$ nm.',ok:near(Math.log10(550e-9)),d:'Visible light is a sliver. $f \\approx 5.5 \\times 10^{14}$ Hz.'},
    {t:'A hospital X-ray has $\\lambda = 0.10$ nm.',ok:near(-10),d:'About the size of an atom, which is why it slips through soft tissue.'}],()=>({e}));
  drag(cv,W,(x,y)=>{if(y<130){e=Math.max(-13,Math.min(3,3-(x-40)/720*16));sl.value=3-e}});
  loop(host,dt=>{t+=dt;tick(dt);c.clearRect(0,0,W,H);const lam=10**e,f=3e8/lam,r=REG.find(r=>e<=r[1]&&e>r[2])||REG[6];
    REG.forEach(q=>{const a=xe(q[1]),b=xe(Math.max(-13,q[2]));if(q[0]==='Visible'){const g=c.createLinearGradient(a,0,b,0);[700,600,550,480,400].forEach((w,i)=>g.addColorStop(i/4,nmRGB(w)));c.fillStyle=g}else c.fillStyle=q[3];
      c.globalAlpha=q===r?1:.45;c.fillRect(a,44,b-a,46);c.globalAlpha=1;if(b-a>40)txt(c,q[0],(a+b)/2,72,'#fff','700 13px Inter','center')});
    [[3,'1 km'],[0,'1 m'],[-3,'1 mm'],[-6,'1 μm'],[-9,'1 nm'],[-12,'1 pm']].forEach(([q,s])=>{c.strokeStyle=C.mu;c.lineWidth=1;ln(c,xe(q),90,xe(q),98);txt(c,s,xe(q),113,C.mu,'600 12px Inter','center')});
    txt(c,'longer wavelength, lower frequency',40,32,C.mu,'600 12px Inter');txt(c,'shorter wavelength, higher frequency',760,32,C.mu,'600 12px Inter','right');
    const px=xe(e);c.beginPath();c.moveTo(px,40);c.lineTo(px-9,24);c.lineTo(px+9,24);c.fillStyle='#fff';c.fill();c.strokeStyle='#fff';c.lineWidth=2;ln(c,px,40,px,94);
    const L=600*Math.pow(5/600,(3-e)/16),col=r[0]==='Visible'?nmRGB(lam*1e9):r[3];
    c.beginPath();for(let x=40;x<=760;x+=1){const y=240-Math.sin((x-40)/L*2*Math.PI-t*4)*58;x>40?c.lineTo(x,y):c.moveTo(x,y)}c.strokeStyle=col;c.lineWidth=3;c.stroke();
    txt(c,r[0],W/2,360,col,'700 34px Space Grotesk','center');
    txt(c,'One wave is about the size of '+SIZE.find(s=>e>=s[0]-.5)[1],W/2,396,'#e8ecff','600 19px Inter','center');
    txt(c,e<-7?'Ionising: enough energy to damage living cells':'Not ionising',W/2,430,e<-7?'#f87171':C.mu,'600 15px Inter','center');
    out.innerHTML=`Wavelength <b>λ = ${si(lam,'m')}</b><br>Frequency <b>f = ${si(f,'Hz')}</b><br>Used for: ${r[4]}`})};

SIMS.sorter=host=>{const J=[['Broadcasting an FM station across a city',0,'Long waves travel far and bend around buildings.'],['Wi-fi and mobile phone signals',1,'They carry a lot of data and pass through walls.'],['Heating food in an oven that stays cool itself',1,'Water in the food absorbs this radiation.'],['A TV remote control',2,'Low energy and harmless. A sensor on the TV picks it up.'],['A camera that finds a lost hiker at night',2,'Warm bodies give off infrared.'],['Photosynthesis',3,'Plants absorb red and blue light.'],['Sterilising surgical tools without heat',4,'It has enough energy to wreck the DNA of microbes.'],['Sunburn',4,'The same energy that kills microbes damages skin cells.'],['Seeing a broken bone',5,'It passes through soft tissue but not through bone.'],['Destroying a tumour in radiotherapy',6,'The highest energy of all, aimed very carefully.']].sort(()=>Math.random()-.5);
  let i=0,miss=0;host.innerHTML='<div class="job"></div><div class="regs"></div><div class="fb"></div><div class="row" style="display:flex;gap:12px;align-items:center"><button class="btn nx" style="font-size:18px;padding:10px 20px">Next job</button><span class="muted sc" style="font-size:18px"></span></div>';
  const job=$('.job',host),regs=$('.regs',host),fb=$('.fb',host),nx=$('.nx',host),sc=$('.sc',host);
  REG.forEach((r,k)=>{const b=el('button','',r[0]);b.style.setProperty('--k',r[3]);b.onclick=()=>{if(nx.style.visibility==='visible')return;
    if(k===J[i][1]){$$('button',regs).forEach((x,q)=>x.classList.toggle('dim',q!==k));fb.innerHTML=`<b class="gr">✓ ${r[0]}.</b> ${J[i][2]}`;nx.style.visibility='visible';nx.textContent=i<J.length-1?'Next job':'Start again'}
    else{miss++;b.classList.remove('no');void b.offsetWidth;b.classList.add('no');fb.innerHTML='<span class="muted">Not that one. Think about the energy it needs and what it has to pass through.</span>'}};regs.append(b)});
  const draw=()=>{job.innerHTML=`<small>Job ${i+1} of ${J.length}: which region does it?</small>${J[i][0]}`;fb.innerHTML='';nx.style.visibility='hidden';$$('button',regs).forEach(x=>x.classList.remove('dim','no'));sc.textContent=miss?`Wrong guesses so far: ${miss}`:''};
  nx.onclick=()=>{i++;if(i>=J.length){i=0;miss=0}draw()};draw()};

// ===== Lesson 3
const MED={1:'Air',1.33:'Water',1.5:'Glass',2.42:'Diamond'};
SIMS.fronts=host=>{const {c,side,W,H}=lab(host,800,470),CX=400,BY=190,L1=46,BW=120;let th=45,n2=1.5,p=0;
  slider(side,'Angle the crests arrive at',0,70,1,45,x=>x+'°',x=>th=x);
  choice(side,'Second material',[[1,'Air (no change)'],[1.33,'Water'],[1.5,'Glass'],[2.42,'Diamond']],1.5,k=>n2=k);
  const out=el('div','read');side.append(out);
  side.append(el('div','note','Follow one <b class="pk">pink crest</b>. Which end reaches the boundary first? What does that end do while the other end is still in air?'));
  loop(host,dt=>{p+=dt*55;c.clearRect(0,0,W,H);const t1=th*D,t2=Math.asin(Math.sin(t1)/n2);
    c.fillStyle=`rgba(125,211,252,${(n2-1)*.16})`;c.fillRect(0,BY,W,H-BY);c.strokeStyle='#5b6aa8';c.lineWidth=2;ln(c,0,BY,W,BY);
    txt(c,'Air: fast',16,26,C.mu);txt(c,MED[n2]+(n2>1?': slow':''),16,H-14,C.mu);
    c.setLineDash([6,6]);c.strokeStyle=C.mu;c.lineWidth=1.5;ln(c,CX,20,CX,H-20);c.setLineDash([]);txt(c,'normal',CX+6,34,C.mu,'600 12px Inter');
    const half=(th_,k,sgn)=>{const sn=Math.sin(th_),cs=Math.cos(th_),xe=[-BW/Math.cos(t1),BW/Math.cos(t1)];
      c.save();c.beginPath();sgn<0?c.rect(0,0,W,BY):c.rect(0,BY,W,H-BY);c.clip();
      const k0=Math.floor(-p/L1);for(let j=k0-14;j<=k0+14;j++){const cc=(j*L1+p)*k,pts=[];
        xe.forEach(x=>{const s=cc-x*sn;if(s*sgn>=0)pts.push([x+s*sn,s*cs]);else if(Math.abs(sn)>1e-6){const xb=cc/sn;if(xb>=xe[0]-1e-6&&xb<=xe[1]+1e-6)pts.push([xb,0])}});
        if(pts.length<2)continue;const hot=((j%5)+5)%5===0;c.strokeStyle=hot?C.pk:C.cy;c.lineWidth=hot?4:2;ln(c,CX+pts[0][0],BY+pts[0][1],CX+pts[1][0],BY+pts[1][1])}c.restore()};
    half(t1,1,-1);half(t2,1/n2,1);
    c.strokeStyle=C.am;c.lineWidth=2.5;ln(c,CX-260*Math.sin(t1),BY-260*Math.cos(t1),CX,BY);ln(c,CX,BY,CX+320*Math.sin(t2),BY+320*Math.cos(t2));
    out.innerHTML=`<table class="rec"><tr><th></th><th>Air</th><th>${MED[n2]}</th></tr><tr><td>Speed (×10⁸ m s⁻¹)</td><td>3.00</td><td><b>${(3/n2).toFixed(2)}</b></td></tr><tr><td>Crest spacing λ</td><td>100%</td><td><b>${(100/n2).toFixed(0)}%</b></td></tr><tr><td>Frequency</td><td colspan="2">same: the source sets it</td></tr><tr><td>Angle to normal</td><td>${th}°</td><td><b>${(t2/D).toFixed(1)}°</b></td></tr></table>`})};

SIMS.raybox=(host,o)=>{const {c,cv,side,W,H}=lab(host,800,470),CX=400,BY=235;let th=40,nb=o.mystery?1.36:1.5,up=false,rows=[],name='A';
  const sl=slider(side,'Angle of incidence (or drag the ray box)',0,85,1,40,x=>x+'°',x=>th=x);
  let res;
  if(o.mystery){const K={A:[1.36,'ethanol'],B:[1.47,'glycerol'],C:[1.63,'dense flint glass']};
    choice(side,'Unknown liquid or solid',[['A','Mystery A'],['B','Mystery B'],['C','Mystery C']],'A',k=>{name=k;nb=K[k][0];a.clear();res.innerHTML=''});
    const box=el('div');side.append(box);box.append(el('div','muted','Pick your own angle. Use Snell\'s law to find its refractive index.'));
    const a=ask(box,'$n$','',()=>nb,.03);res=el('div','read');side.append(res);
    $('button',box).addEventListener('click',()=>setTimeout(()=>{res.innerHTML=$('.mk',box).classList.contains('ok')?`Mystery ${name} is <b>${K[name][1]}</b>, n = ${nb}.`:'Check: is your calculator in degrees? Which angle is in which material?'},0));
    side.append(el('div','note','This is the method for Practical 1C-1. A better answer: repeat at three angles and average.'))}
  else{choice(side,'Lower material',[[1.33,'Water'],[1.5,'Glass'],[2.42,'Diamond']],1.5,k=>{nb=k;rows=[];tab()});
    choice(side,'Ray starts in',[[0,'Air (top)'],[1,'Lower material']],0,k=>{up=!!k;rows=[];tab()});
    const rb=el('button','btn','Record this pair of angles');side.append(rb);const tb=el('div');side.append(tb);
    var tab=()=>{tb.innerHTML=rows.length?`<table class="rec"><tr><th>θ₁</th><th>θ₂</th><th>sin θ₁ ÷ sin θ₂</th></tr>${rows.map(r=>`<tr><td>${r[0]}°</td><td>${r[1].toFixed(1)}°</td><td><b>${r[2]}</b></td></tr>`).join('')}</table>`:'<span class="muted">Record four different angles. Look for something that does not change.</span>'};tab();
    rb.onclick=()=>{const s=Math.sin(th*D)*(up?nb:1/nb);if(th>0&&s<1){rows.push([th,Math.asin(s)/D,(Math.sin(th*D)/s).toFixed(2)]);rows=rows.slice(-5);tab()}}}
  drag(cv,W,(x,y)=>{const dx=Math.abs(x-CX),dy=up?y-BY:BY-y;if(dy>8){th=Math.max(0,Math.min(85,Math.round(Math.atan2(dx,dy)/D)));sl.value=th;sl.oninput()}});
  loop(host,()=>{c.clearRect(0,0,W,H);const n1=up?nb:1,n2=up?1:nb,t1=th*D,s2=n1*Math.sin(t1)/n2,tir=s2>1,t2=tir?0:Math.asin(s2),d=up?1:-1;
    c.fillStyle=`rgba(125,211,252,${(nb-1)*.16})`;c.fillRect(0,BY,W,H-BY);c.strokeStyle='#5b6aa8';c.lineWidth=2;ln(c,0,BY,W,BY);
    txt(c,'Air, n = 1.00',16,26,C.mu);txt(c,o.mystery?'Mystery '+name+', n = ?':MED[nb]+', n = '+nb.toFixed(2),16,H-14,C.mu);
    c.setLineDash([6,6]);c.strokeStyle=C.mu;c.lineWidth=1.5;ln(c,CX,14,CX,H-14);c.setLineDash([]);
    for(let a=-90;a<=90;a+=5){const r1=a%30===0?150:a%10===0?158:163;[1,-1].forEach(v=>{c.strokeStyle='#3a4790';c.lineWidth=1.5;ln(c,CX+r1*Math.sin(a*D),BY+v*r1*Math.cos(a*D),CX+170*Math.sin(a*D),BY+v*170*Math.cos(a*D));
      if(a%30===0&&a)txt(c,Math.abs(a)+'°',CX+188*Math.sin(a*D),BY+v*188*Math.cos(a*D)+4,'#5b6aa8','600 11px Inter','center')})}
    const ix=CX-215*Math.sin(t1),iy=BY+d*215*Math.cos(t1);
    c.strokeStyle=C.am;c.lineWidth=4;ln(c,ix,iy,CX,BY);
    c.globalAlpha=tir?1:.22;ln(c,CX,BY,CX+215*Math.sin(t1),BY+d*215*Math.cos(t1));c.globalAlpha=1;
    if(!tir)ln(c,CX,BY,CX+225*Math.sin(t2),BY-d*225*Math.cos(t2));
    c.save();c.translate(ix,iy);c.rotate(Math.atan2(BY-iy,CX-ix));c.fillStyle='#e8ecff';c.fillRect(-46,-14,46,28);c.restore();
    c.strokeStyle=C.am;c.lineWidth=2;const a0=up?Math.PI/2:-Math.PI/2;
    c.beginPath();up?c.arc(CX,BY,54,a0,a0+t1):c.arc(CX,BY,54,a0-t1,a0);c.stroke();
    if(!tir){c.beginPath();up?c.arc(CX,BY,70,-a0,-a0+t2):c.arc(CX,BY,70,-a0-t2,-a0);c.stroke()}
    c.fillStyle='rgba(9,14,40,.85)';c.fillRect(W-214,10,204,tir?40:66);
    txt(c,'θ₁ = '+th+'°',W-22,36,C.am,'700 19px Inter','right');
    if(tir)txt(c,'No refracted ray: total internal reflection (next lesson)',CX,up?60:H-60,C.pk,'700 16px Inter','center');
    else txt(c,'θ₂ = '+(t2/D).toFixed(1)+'°',W-22,64,C.am,'700 19px Inter','right')})};
