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
