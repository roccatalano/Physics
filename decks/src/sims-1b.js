// ===== 1B labs
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
