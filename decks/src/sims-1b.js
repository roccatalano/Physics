// ===== 1B labs. Each opens with a clicker walkthrough (invisible .stg markers on the slide), then hands over.
// Every mission has a "Show me" button so the class can see the right answer.
// Region edges are Cambridge Table 1B-1: radio > 1 m, microwave 1 m to 1 mm, IR 1 mm to 700 nm,
// visible 700 nm to 400 nm, UV 400 nm to 10 nm, X-ray 10 nm to 10 pm, gamma < 10 pm. c = 3.00 x 10^8 m/s.
const B1C=3.00e8;
const B1REG=[['Radio',3,0,'#64748b'],['Microwave',0,-3,'#0ea5e9'],['Infrared',-3,Math.log10(700e-9),'#ef4444'],['Visible',Math.log10(700e-9),Math.log10(400e-9),'#facc15'],
  ['Ultraviolet',Math.log10(400e-9),-8,'#8b5cf6'],['X-ray',-8,-11,'#22c55e'],['Gamma',-11,-13.01,'#f97316']];
const b1Sci=(x,n=3)=>{const k=Math.floor(Math.log10(x)+1e-9),m=x/10**k;return m.toFixed(n-1)+' × 10'+SUP(k)};
function b1Len(x){const U=[[1e3,'km',1e3],[1,'m',1],[1e-2,'cm',1e-2],[1e-3,'mm',1e-3],[1e-6,'μm',1e-6],[1e-9,'nm',1e-11],[1e-12,'pm',0]],u=U.find(u=>x>=u[2]*.9995);return (x/u[0]).toPrecision(3)+' '+u[1]}
function b1Freq(f){if(f>=1e12)return b1Sci(f)+' Hz';const U=[[1e9,'GHz'],[1e6,'MHz'],[1e3,'kHz']],u=U.find(u=>f>=u[0]*.9995);return +(f/u[0]).toPrecision(3)+' '+u[1]}
// walkthrough: like stager, but the caption sits in a given box and the controls box can stay visible
function b1Stage(host,caps,onStage,opt={}){const sl=host.closest('.slide'),n=$$('.stg',sl).length,box=opt.box||el('div','capbox');if(!opt.box)host.append(box);let last=-1;
  return ()=>{const k=n?Math.min(caps.length-1,$$('.stg.shown',sl).length):caps.length-1;
    if(k!==last){last=k;const free=k===caps.length-1;if(opt.side)opt.side.style.display=free?'':'none';box.style.display=free?'none':'';
      box.innerHTML=`<small>Step ${k+1} of ${caps.length-1}</small><p>${mx(caps[k])}</p><i>Click for the next step</i>`;onStage(k)}return k}}
// missions that tick themselves, each with a "Show me" button that sets the answer
function b1Missions(side,list,state){let i=0,hold=0,done=false;const box=el('div','mis');side.append(box);
  const draw=()=>{box.className='mis'+(done?' ok':'');box.innerHTML=`<div class="lbl">Mission ${i+1} of ${list.length}${done?' · done':''}</div><div class="mt">${mx(list[i].t)}</div>${done?`<div class="ms">${mx(list[i].d)}</div>`:''}<div class="btns">${done&&i<list.length-1?'<button class="btn nx">Next mission</button>':''}${done?'':'<button class="btn alt sh">Show me</button>'}</div>`;
    const b=$('.nx',box);if(b)b.onclick=()=>{i++;done=false;hold=0;draw()};const s=$('.sh',box);if(s)s.onclick=()=>list[i].show()};draw();
  const tick=dt=>{if(done)return;if(list[i].ok(state())){hold+=dt;if(hold>.8){done=true;draw()}}else hold=0};
  tick.reset=()=>{i=0;done=false;hold=0;draw()};return tick}
const b1Arrow=(c,x1,y1,x2,y2,col,w=2.5)=>{c.strokeStyle=col;c.fillStyle=col;c.lineWidth=w;ln(c,x1,y1,x2,y2);const g=Math.atan2(y2-y1,x2-x1);c.beginPath();c.moveTo(x2,y2);c.lineTo(x2-11*Math.cos(g-.4),y2-11*Math.sin(g-.4));c.lineTo(x2-11*Math.cos(g+.4),y2-11*Math.sin(g+.4));c.fill()};

// ----- 1B lab 1: sound and a radio wave cross a sealed box. Pump out the air: only the EM wave gets through.
SIMS.b1_em=(host,o)=>{const {c,side,W,H}=lab(host,800,470);let t=0,air=1,fMHz=150,k=0,tE=0,tS=0,lastOut='';
  const X0=96,X1=704,PXM=(X1-X0)/6;   // the lanes are 6.0 m long: 101 px per metre
  const yS=128,yE=338;
  // air particles: a fixed random scatter, shared by both lanes. Fewer are drawn as the air is pumped out.
  let seed=7;const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
  const P=[];for(let x=X0;x<=X1;x+=9)for(let y=40;y<=430;y+=26)P.push({x:x+(rnd()-.5)*4,y:y+(rnd()-.5)*10,r:rnd()});P.sort((a,b)=>a.r-b.r);
  const airS=slider(side,'Air left in the box',0,100,5,100,x=>x+'%',x=>air=x/100);
  const fS=slider(side,'Radio frequency',100,400,10,150,x=>x+' MHz',x=>fMHz=x);
  const out=el('div','read');side.append(out);
  const set=(a,f)=>{airS.value=a;airS.oninput();fS.value=f;fS.oninput()};
  const tick=b1Missions(side,[
    {t:'Pump out all the air. Which signal still reaches the far side?',ok:s=>s.air===0,show:()=>set(0,fMHz),d:'Only the radio wave. Sound needs particles to pass it along. An EM wave does not.'},
    {t:'Make the radio wavelength exactly 1.00 m.',ok:s=>s.f===300,show:()=>set(air*100,300),d:'$f = 300$ MHz. Check: $f\\lambda = 3.00 \\times 10^{8}$ m/s, which is $c$.'},
    {t:'Now make it 2.00 m. What happened to the frequency?',ok:s=>s.f===150,show:()=>set(air*100,150),d:'It halved to 150 MHz. Double the wavelength, half the frequency. The speed stays $c$.'}],()=>({air,f:fMHz}));
  const stage=b1Stage(host,[
    'A sealed box of air. A <b class="hl">speaker</b> sends sound across the top. An <b class="hl">antenna</b> sends a radio wave across the bottom.',
    'Sound: the speaker pushes the air. Each particle bumps the next one along.',
    'The antenna shakes charges up and down. That makes a changing <b class="hl">electric field</b>.',
    'A changing electric field makes a changing <b class="pk">magnetic field</b>, at right angles to it.',
    'Both fields vibrate at right angles to the direction of travel. An EM wave is <b>transverse</b>.',
    'Look at the air particles in the bottom lane. None of them move. The fields do the vibrating.',
    ''],q=>{k=q;if(q===1)tS=t;if(q===2)tE=t;if(q<6){air=1;fMHz=150}else{set(100,150);tick.reset()}},{side});
  loop(host,dt=>{const kk=stage();if(kk===6)tick(dt);t+=dt;c.clearRect(0,0,W,H);
    const sound=kk===0||kk===1||kk>=6,emOn=kk>=2,bOn=kk>=3||kk===0,lam=B1C/(fMHz*1e6),Lpx=lam*PXM;
    // the box
    c.strokeStyle='#33407a';c.lineWidth=2;c.setLineDash([8,6]);c.strokeRect(70,22,660,426);c.setLineDash([]);
    txt(c,'sealed box',726,40,C.mu,'600 13px Inter','right');
    // air particles: the top lane ones move with the sound, the rest stay still
    const n=Math.round(P.length*air),ks=2*Math.PI/60,ws=2*Math.PI*1;
    for(let i=0;i<n;i++){const p=P[i];let x=p.x;const top=p.y<230;
      if(top&&sound){const front=X0+(t-tS)*60;if(p.x<front)x+=12*Math.sin(ks*(p.x-X0)-ws*t)}
      dot(c,x,p.y,2.3,top?'#5b6aa8':(kk===5?'#e8ecff':'#3a4478'))}
    if(kk===5){c.strokeStyle='#e8ecff';c.lineWidth=1.5;c.setLineDash([4,5]);c.strokeRect(X0-10,240,X1-X0+20,200);c.setLineDash([]);txt(c,'these particles stay still',W/2,234,'#e8ecff','700 15px Inter','center')}
    // speaker and microphone
    c.fillStyle='#fbb040';c.fillRect(X0-24,yS-22,14,44);c.beginPath();c.moveTo(X0-10,yS-12);c.lineTo(X0+6,yS-26);c.lineTo(X0+6,yS+26);c.lineTo(X0-10,yS+12);c.fill();
    txt(c,'speaker',X0-16,yS+48,C.am,'600 13px Inter','center');
    const mic=sound?air:0;dot(c,X1+14,yS,10,'#cbd5e1');c.fillStyle='#cbd5e1';c.fillRect(X1+11,yS+8,6,24);
    txt(c,'microphone',X1+14,yS+50,C.mu,'600 13px Inter','center');
    for(let j=0;j<5;j++){c.fillStyle=j<Math.round(mic*5)?'#4ade80':'#1e2858';c.fillRect(X1+2+j*6,yS-44-j*3,4,8+j*3)}
    // antenna, with a charge shaking up and down, and the receiver
    c.strokeStyle='#cbd5e1';c.lineWidth=4;ln(c,X0-16,yE-60,X0-16,yE+60);
    const w=2*Math.PI*0.9*(fMHz/150),q=Math.sin(-w*t);
    if(emOn||kk===0)dot(c,X0-16,yE-40*q,8,C.am);
    txt(c,'antenna',X0-16,yE+84,C.am,'600 13px Inter','center');
    c.strokeStyle='#cbd5e1';c.lineWidth=3;ln(c,X1+14,yE-34,X1+14,yE+34);c.beginPath();c.arc(X1+14,yE-34,9,0,7);c.stroke();
    txt(c,'receiver',X1+14,yE+84,C.mu,'600 13px Inter','center');
    // the EM wave: E up and down (orange), B in and out of the page (pink, drawn on a slant)
    if(emOn||kk===0){const vpx=w/(2*Math.PI)*Lpx,front=kk===0||kk>=6?X1:Math.min(X1,X0+(t-tE)*vpx);
      c.strokeStyle=C.mu;c.lineWidth=1.5;ln(c,X0,yE,X1,yE);
      for(let x=X0,dx=Math.max(4,Lpx/16);x<=front;x+=dx){const s=Math.sin(2*Math.PI*(x-X0)/Lpx-w*t);
        c.strokeStyle=C.am;c.lineWidth=2.2;ln(c,x,yE,x,yE-s*70);
        if(bOn){c.strokeStyle=C.pk;c.lineWidth=1.6;ln(c,x,yE,x-s*26,yE+s*20)}}
      if(kk>=3||kk===0){txt(c,'E',X0+10,yE-82,C.am,'700 20px Space Grotesk');if(bOn)txt(c,'B',X0+6,yE+60,C.pk,'700 20px Space Grotesk')}
      if(kk===4){b1Arrow(c,X1-150,yE+100,X1-30,yE+100,'#fff');txt(c,'travel',X1-90,yE+90,'#fff','700 15px Inter','center');
        b1Arrow(c,X0+60,yE-6,X0+60,yE-80,C.am);b1Arrow(c,X0+60,yE,X0+30,yE+24,C.pk)}
      if(kk>=6){const xa=X0+30;b1Arrow(c,xa,yE+98,xa+Lpx,yE+98,'#fff',2);b1Arrow(c,xa+Lpx,yE+98,xa,yE+98,'#fff',2);txt(c,'λ = '+lam.toFixed(2)+' m',xa+Lpx/2,yE+90,'#fff','700 15px Inter','center')}}
    if(kk===1){txt(c,'sound',W/2,yS-56,'#fff','700 17px Space Grotesk','center')}
    txt(c,'Animation slowed down a lot',W/2,462,'#64748b','600 12px Inter','center');
    const sig=emOn||kk>=6;
    const o2=`Microphone: <b>${!sound?'...':mic>.6?'loud':mic>0?'quiet':'silent'}</b><br>Radio receiver: <b>${sig?'signal':'...'}</b><br>$f = ${fMHz}$ MHz &nbsp; $\\lambda = ${(lam).toFixed(2)}$ m<br>Speed: <b>$c = 3.00 \\times 10^8$ m/s</b>`;if(o2!==lastOut){lastOut=o2;out.innerHTML=mx(o2)}});
};

// ----- 1B lab 2
SIMS.b1_spectrum=(host,o)=>{const {c,cv,side,W,H}=lab(host,800,470);let e=3,t=0,k=0;const xe=q=>40+(3-q)/16*720;
  const SIZE=[[3,'a small town'],[2,'a football oval'],[1,'a house'],[0,'a person'],[-1,'a hand'],[-2,'a fingernail'],[-3,'a grain of sand'],[-4,'the width of a hair'],[-5,'a red blood cell'],[-6,'a bacterium'],[-7,'a virus'],[-8,'a large molecule'],[-9,'a small molecule'],[-10,'an atom'],[-99,'smaller than an atom']];
  const nmRGB=w=>{let r=0,g=0,b=0;if(w<440){r=(440-w)/60;b=1}else if(w<490){g=(w-440)/50;b=1}else if(w<510){g=1;b=(510-w)/20}else if(w<580){r=(w-510)/70;g=1}else if(w<645){r=1;g=(645-w)/65}else r=1;return`rgb(${r*255|0},${g*255|0},${b*255|0})`};
  const sl=slider(side,'Slide along the spectrum',0,16,.001,0,()=>'',v=>e=3-v);sl.parentElement.querySelector('b').remove();
  const out=el('div','read');side.append(out);
  const setE=q=>{sl.value=3-q;sl.oninput();e=q};
  const near=q=>s=>Math.abs(s.e-q)<.03,fq=f=>Math.log10(B1C/f);
  const tick=b1Missions(side,[
    {t:'A radio station broadcasts at <b>100.3 MHz</b>. Find it.',ok:near(fq(100.3e6)),show:()=>setE(fq(100.3e6)),d:'Radio. $\\lambda = \\dfrac{c}{f} = 2.99$ m: one wave is taller than a person.'},
    {t:'A microwave oven runs at <b>2.45 GHz</b>. Find it.',ok:near(fq(2.45e9)),show:()=>setE(fq(2.45e9)),d:'Microwave. $\\lambda = 12.2$ cm: about the width of your hand.'},
    {t:'Green light has $\\lambda = 550$ nm. Find it. What is its frequency?',ok:near(Math.log10(550e-9)),show:()=>setE(Math.log10(550e-9)),d:'Visible. $f = \\dfrac{c}{\\lambda} = 5.45 \\times 10^{14}$ Hz. Visible light is a thin sliver.'},
    {t:'A hospital X-ray has $\\lambda = 0.10$ nm. Find it.',ok:near(-10),show:()=>setE(-10),d:'X-ray. One wave is about the size of an atom.'}],()=>({e}));
  drag(cv,W,(x,y)=>{if(k<6||y>130)return;setE(Math.max(-13,Math.min(3,3-(x-40)/720*16)))});
  const stage=b1Stage(host,[
    'Every kind of EM wave, laid out by wavelength. This is the <b class="hl">electromagnetic spectrum</b>.',
    'Longest waves on the left: <b>radio</b>. One wave can be longer than a building.',
    'Going right, the waves get shorter: radio, microwave, infrared, visible, ultraviolet, X-ray, gamma.',
    '<b>Visible light</b> is a thin sliver: 400 nm (violet) to 700 nm (red). We cannot see the rest.',
    'They all travel at $c$. So as $\\lambda$ gets shorter, $f$ gets higher: $c = f\\lambda$.',
    'Higher frequency means more <b class="hl">energy</b>. Gamma rays carry the most.',
    ''],q=>{k=q;if(q<6)setE([2,1,-1,Math.log10(550e-9),-4,-12][q]);else{setE(3);tick.reset()}},{side});
  loop(host,dt=>{const kk=stage();if(kk===6)tick(dt);t+=dt;c.clearRect(0,0,W,H);const lam=10**e,f=B1C/lam,r=B1REG.find(r=>e<=r[1]&&e>r[2])||B1REG[6];
    B1REG.forEach((q,j)=>{const a=xe(q[1]),b=xe(Math.max(-13,q[2])),lit=kk===2||kk>=4||q===r||kk===0;
      if(q[0]==='Visible'){const g=c.createLinearGradient(a,0,b,0);[700,620,560,500,430].forEach((w,i)=>g.addColorStop(i/4,nmRGB(w)));c.fillStyle=g}else c.fillStyle=q[3];
      c.globalAlpha=q===r?1:lit?.6:.25;c.fillRect(a,52,b-a,46);c.globalAlpha=1;
      const lab=q[0]==='Ultraviolet'?'UV':q[0]==='Infrared'?'IR':q[0]==='Microwave'?'Micro':q[0];
      if(b-a>30)txt(c,lab,(a+b)/2,80,'#fff','700 13px Inter','center')});
    const xv=(xe(B1REG[3][1])+xe(B1REG[3][2]))/2;c.strokeStyle='#facc15';c.lineWidth=1.5;ln(c,xv,52,xv,40);txt(c,'visible',xv,34,'#facc15','700 13px Inter','center');
    [[3,'1 km'],[0,'1 m'],[-3,'1 mm'],[-6,'1 μm'],[-9,'1 nm'],[-12,'1 pm']].forEach(([q,s])=>{c.strokeStyle=C.mu;c.lineWidth=1;ln(c,xe(q),98,xe(q),106);txt(c,s,xe(q),121,C.mu,'600 12px Inter','center')});
    txt(c,'λ longer, f lower',40,18,C.mu,'600 12px Inter');txt(c,'λ shorter, f higher',760,18,C.mu,'600 12px Inter','right');
    const px=xe(e);c.beginPath();c.moveTo(px,50);c.lineTo(px-9,36);c.lineTo(px+9,36);c.fillStyle='#fff';c.fill();c.strokeStyle='#fff';c.lineWidth=2;ln(c,px,46,px,102);
    // the wave itself: drawn longer or shorter on a squeezed scale (the real range is far too big to draw)
    const L=600*Math.pow(14/600,(3-e)/16),col=r[0]==='Visible'?nmRGB(lam*1e9):r[3];
    c.beginPath();for(let x=40;x<=760;x+=1){const y=232-Math.sin((x-40)/L*2*Math.PI-t*4)*50;x>40?c.lineTo(x,y):c.moveTo(x,y)}c.strokeStyle=col;c.lineWidth=3;c.stroke();
    txt(c,'wave drawn to a squeezed scale',760,296,'#64748b','600 12px Inter','right');
    txt(c,r[0],W/2,340,col,'700 34px Space Grotesk','center');
    txt(c,e<-10.5?'One wave is smaller than an atom':'One wave is about the size of '+SIZE.find(s=>e>=s[0]-.5)[1],W/2,374,'#e8ecff','600 18px Inter','center');
    // energy meter: grows with frequency
    const fr=(3-e)/16;txt(c,'energy',140,420,C.mu,'600 14px Inter','right');c.fillStyle='#1e2858';c.fillRect(150,406,500,18);c.fillStyle=kk===5?C.am:'#fbb04099';c.fillRect(150,406,500*Math.max(.02,fr),18);
    txt(c,'low',150,444,C.mu,'600 12px Inter');txt(c,'high',650,444,C.mu,'600 12px Inter','right');
    out.innerHTML=`Wavelength <b>λ = ${b1Len(lam)}</b><br>Frequency <b>f = ${b1Freq(f)}</b><br>Region: <b>${r[0]}</b>`})};

// ----- 1B lab 3: which region does the job? Walkthrough with one example, then the class answers on whiteboards.
SIMS.b1_sorter=(host,o)=>{const J=[['Broadcasting an FM station across a city',0,'Long waves travel far and bend around buildings. Low energy, so safe.'],
  ['Wi-fi in your house',1,'Short enough to carry lots of data, long enough to pass through walls.'],
  ['Heating leftovers',1,'Water in the food absorbs microwaves and warms up.'],
  ['A TV remote control',2,'Low energy and harmless. It only has to cross the room.'],
  ['Plants making food (photosynthesis)',3,'Leaves absorb red and blue light.'],
  ['A lamp that kills germs in drinking water',4,'Enough energy to damage the germs, without heating the water.'],
  ['Making vitamin D in your skin',4,'Ultraviolet in sunlight starts the reaction in the skin.'],
  ['Seeing a broken bone',5,'X-rays pass through soft tissue but are stopped by bone.'],
  ['Checking bags at the airport',5,'X-rays pass through the bag but not through metal or dense objects.'],
  ['Killing bacteria inside sealed packs of syringes',6,'Gamma passes right through the pack. It has the energy to kill bacteria.']];
  const EX=['A camera that finds a lost hiker at night',2,'A warm body gives off infrared. The camera sees it in the dark.'];
  let i=0,k=0,shown=false;host.classList.add('b1-sort');
  host.innerHTML='<div class="job"></div><div class="regs"></div><div class="b1-low"><div class="fb"></div><div class="b1-cap"></div><div class="b1-ctl"><button class="btn alt sa">Show answer</button><button class="btn nx">Next job</button><span class="muted sc"></span></div></div>';
  const job=$('.job',host),regs=$('.regs',host),fb=$('.fb',host),nx=$('.nx',host),sa=$('.sa',host),sc=$('.sc',host),cap=$('.b1-cap',host),ctl=$('.b1-ctl',host);
  const reveal=(q,ok)=>{shown=true;$$('button',regs).forEach((x,j)=>{x.classList.toggle('dim',j!==q[1]);x.classList.remove('no')});fb.innerHTML=`<b class="gr">${ok?'✓ ':''}${B1REG[q[1]][0]}.</b> ${q[2]}`;sa.style.visibility='hidden'};
  B1REG.forEach((r,j)=>{const b=el('button','',r[0]);b.style.setProperty('--k',r[3]);b.onclick=()=>{if(k<4||shown)return;
    if(j===J[i][1])reveal(J[i],true);else{b.classList.remove('no');void b.offsetWidth;b.classList.add('no');fb.innerHTML='<span class="muted">Not that one. How much energy does it need? What must it get through?</span>'}};regs.append(b)});
  const draw=(q,n)=>{job.innerHTML=`<small>${n}: which region does it?</small>${q[0]}`;fb.innerHTML='';shown=false;sa.style.visibility='';$$('button',regs).forEach(x=>x.classList.remove('dim','no'))};
  sa.onclick=()=>reveal(J[i],false);
  nx.onclick=()=>{i=(i+1)%J.length;draw(J[i],`Job ${i+1} of ${J.length}`);sc.textContent=''};
  const stage=b1Stage(host,[
    'Each card is a job. Name the region of the spectrum that does it.',
    'Ask two things. How much energy does the job need? What does the wave have to get through?',
    'The answer lights up. The reason sits underneath it.',
    'Your turn. Write the region on your whiteboard. Show on three. Then we check it here.',
    ''],q=>{k=q;if(q<4){draw(EX,'Example');if(q===2)reveal(EX,false)}else{i=0;draw(J[0],`Job 1 of ${J.length}`)}},{box:cap,side:ctl});
  (function f(){stage();requestAnimationFrame(f)})()};

// the old names, still used by the engine's test deck
SIMS.em=h=>SIMS.b1_em(h,{});SIMS.spectrum=h=>SIMS.b1_spectrum(h,{});SIMS.sorter=h=>{h.classList.remove('sorter');h.classList.add('lab');SIMS.b1_sorter(h,{})};
