// ===== 1C labs. Every lab opens with a clicker walkthrough (stager, from sims.js), then hands over the controls
// with one job and a way to show the answer. Data: Cambridge Table 1C-1 (speed of light in media) and
// Table 1C-2 (refractive index of glass for each colour). Physics notes are beside each lab.
(()=>{
const fr=x=>`<span style="display:inline-block">${mx(x)}</span>`;
// Fresnel reflectance for unpolarised light (fraction reflected at a boundary); 1 when totally internally reflected
const fres=(n1,n2,ti)=>{const s=n1*Math.sin(ti)/n2;if(s>=1)return 1;const tt=Math.asin(s),ci=Math.cos(ti),ct=Math.cos(tt);
  const rs=((n1*ci-n2*ct)/(n1*ci+n2*ct))**2,rp=((n1*ct-n2*ci)/(n1*ct+n2*ci))**2;return (rs+rp)/2};
// missions that tick themselves, each with a "Show me" button that sets the answer state
function mis(side,list,state){let i=0,hold=0,done=false;const box=el('div','mis');side.append(box);
  const draw=()=>{box.className='mis'+(done?' ok':'');box.innerHTML=`<div class="lbl">Mission ${i+1} of ${list.length}${done?' · done':''}</div><div class="mt">${mx(list[i].t)}</div>${done?`<div class="ms">${mx(list[i].d)}</div>`:''}<div class="btns">${done&&i<list.length-1?'<button class="btn nx">Next mission</button>':''}${done?'':'<button class="btn alt sm">Show me</button>'}</div>`;
    const b=$('.nx',box);if(b)b.onclick=()=>{i++;done=false;hold=0;draw()};const s=$('.sm',box);if(s)s.onclick=()=>list[i].show()};draw();
  return {tick(dt){if(done)return;if(list[i].ok(state())){hold+=dt;if(hold>.6){done=true;draw()}}else hold=0},reset(){i=0;done=false;hold=0;draw()}}}
const setSl=(inp,v)=>{inp.value=v;inp.oninput()};
const pickPill=(d,i)=>$$('.pill',d)[i].click();
const arc=(c,x,y,r,a0,a1,col,w=2)=>{c.strokeStyle=col;c.lineWidth=w;c.beginPath();c.arc(x,y,r,Math.min(a0,a1),Math.max(a0,a1));c.stroke()};
const arrowHead=(c,x,y,ang,col,s=11)=>{c.fillStyle=col;c.beginPath();c.moveTo(x,y);c.lineTo(x-s*Math.cos(ang-.4),y-s*Math.sin(ang-.4));c.lineTo(x-s*Math.cos(ang+.4),y-s*Math.sin(ang+.4));c.fill()};

// Cambridge Table 1C-1: speed of light (x 10^8 m/s); n = c/v with c = 3.00 x 10^8 m/s
const MAT={air:['Air',3.00],water:['Water',2.25],glass:['Plate glass',1.98],plastic:['Plastic lens',1.74],diamond:['Diamond',1.24]};
const nOf=k=>3.00/MAT[k][1];

// ---------- fronts: wave crests crossing from air into a slower material
// mode "why" (loop 1): why the ray bends. mode "speed" (loop 2): work out n = c/v for each material.
SIMS.fronts=(host,o)=>{const {c,side,W,H}=lab(host,800,470),CX=400,BY=200,L1=46,BW=120,speed=o.mode==='speed';
  let th=45,mk=speed?'water':'glass',p=0,k=0,rate=1;
  const ths=slider(side,'Angle the crests arrive at',0,70,1,45,x=>x+'°',x=>th=x);
  const keys=speed?['water','glass','plastic','diamond']:['air','water','glass','diamond'];
  const mats=choice(side,'Second material',keys.map(q=>[q,q==='air'?'Air (no change)':MAT[q][0]]),mk,q=>{mk=q;if(A)A.clear()});
  const out=el('div','read');side.append(out);let A=null,tk=null;
  if(speed){const box=el('div');side.append(box);box.append(el('div','muted','Work out $n$ for this material. Then try the others.'.replace(/\$n\$/,mx('$n$'))));
    A=ask(box,'$n$','',()=>nOf(mk),.015);const sa=el('button','btn alt','Show answer');sa.style.marginTop='6px';sa.onclick=()=>A.show();box.append(sa)}
  else tk=mis(side,[
    {t:'Make the crests cross at an angle without bending.',ok:s=>s.mk==='air'&&s.th>=20,show:()=>{pickPill(mats,0);setSl(ths,45)},d:'Air to air: no change of speed, so no bending. Bending needs a change of speed.'},
    {t:'Square on: send the crests in at 0° into glass. Does the ray bend?',ok:s=>s.mk==='glass'&&s.th===0,show:()=>{pickPill(mats,2);setSl(ths,0)},d:'No. Both ends of each crest slow at the same moment, so the crest does not turn. It still slows down.'},
    {t:'Find the material and angle that bend the ray the most.',ok:s=>s.mk==='diamond'&&s.th>=65,show:()=>{pickPill(mats,3);setSl(ths,70)},d:'Diamond at a steep angle. Diamond slows light the most, so one end of the crest is held back the most.'}],()=>({mk,th}));
  const stage=stager(host,side,speed?[
      'Light goes from air into water, square on, so it does not bend. Watch the crests.',
      'In air, light travels at $3.00 \\times 10^8$ m/s. In water it slows to $2.25 \\times 10^8$ m/s.',
      'The <b>refractive index</b> compares the two: $n = \\dfrac{c}{v} = \\dfrac{3.00 \\times 10^8}{2.25 \\times 10^8} = 1.33$',
      'Crests reach the water at the same rate as they leave the source: same frequency. Slower, so they bunch up: shorter wavelength.',
      ''
    ]:[
      'Light from a ray box, drawn as wave crests. The orange <b class="hl">ray</b> shows the direction. Crests are at right angles to it.',
      'The crests reach the glass at an angle. Follow the <b class="pk">pink crest</b>: its left end reaches the glass first.',
      'Light is slower in glass. The left end slows down while the right end is still moving fast in air.',
      'So the crest swings round and the ray turns <b>towards the normal</b>: the dashed line at 90° to the surface.',
      'Inside the glass the crests are closer together: same frequency, slower speed, shorter wavelength.',
      ''],q=>{k=q;const free=q===(speed?4:5);rate=free?1:.55;
      if(speed){mk='water';th=q<4?0:30;if(q===4){pickPill(mats,0);setSl(ths,30)}}
      else{mk='glass';th=45;if(free){pickPill(mats,2);setSl(ths,45);tk.reset()}}});
  loop(host,dt=>{stage();p+=dt*55*rate;if(tk&&k===5)tk.tick(dt);c.clearRect(0,0,W,H);
    const n2=nOf(mk),t1=th*D,t2=Math.asin(Math.sin(t1)/n2),tint=(n2-1)*.16;
    c.fillStyle=`rgba(125,211,252,${tint})`;c.fillRect(0,BY,W,H-BY);c.strokeStyle='#5b6aa8';c.lineWidth=2;ln(c,0,BY,W,BY);
    txt(c,'Air: fast',16,26,C.mu);txt(c,MAT[mk][0]+(mk==='air'?'':': slower'),16,H-14,C.mu);
    const nh=!speed&&k>=3;c.setLineDash([6,6]);c.strokeStyle=nh?'#fff':C.mu;c.lineWidth=nh?2.5:1.5;ln(c,CX,20,CX,H-20);c.setLineDash([]);txt(c,'normal',CX+6,34,nh?'#fff':C.mu,'600 13px Inter');
    const half=(th_,kk,sgn)=>{const sn=Math.sin(th_),cs=Math.cos(th_),xe=[-BW/Math.cos(t1),BW/Math.cos(t1)];
      c.save();c.beginPath();sgn<0?c.rect(0,0,W,BY):c.rect(0,BY,W,H-BY);c.clip();
      const k0=Math.floor(-p/L1);for(let j=k0-16;j<=k0+16;j++){const cc=(j*L1+p)*kk,pts=[];
        xe.forEach(x=>{const s=cc-x*sn;if(s*sgn>=0)pts.push([x+s*sn,s*cs]);else if(Math.abs(sn)>1e-6){const xb=cc/sn;if(xb>=xe[0]-1e-6&&xb<=xe[1]+1e-6)pts.push([xb,0])}});
        if(pts.length<2)continue;const hot=((j%6)+6)%6===0&&(speed||k>=1);c.strokeStyle=hot?C.pk:C.cy;c.lineWidth=hot?4:2;ln(c,CX+pts[0][0],BY+pts[0][1],CX+pts[1][0],BY+pts[1][1])}c.restore()};
    half(t1,1,-1);half(t2,1/n2,1);
    c.strokeStyle=C.am;c.lineWidth=2.5;ln(c,CX-260*Math.sin(t1),BY-260*Math.cos(t1),CX,BY);ln(c,CX,BY,CX+320*Math.sin(t2),BY+320*Math.cos(t2));
    if(!speed&&k===2&&th>0){txt(c,'slows first',CX-150,BY+30,C.pk,'700 17px Inter','center');txt(c,'still fast',CX+150,BY-18,C.pk,'700 17px Inter','center')}
    if(!speed&&k>=3&&th>0){arc(c,CX,BY,60,-Math.PI/2-t1,-Math.PI/2,C.am,2.5);arc(c,CX,BY,76,Math.PI/2-t2,Math.PI/2,C.am,2.5);
      txt(c,'θ₁',CX-92*Math.sin(t1/2),BY-92*Math.cos(t1/2)+6,C.am,'700 18px Inter','center');txt(c,'θ₂',CX+104*Math.sin(t2/2),BY+104*Math.cos(t2/2)+6,C.am,'700 18px Inter','center')}
    const sp=(100/n2).toFixed(0);
    out.innerHTML=`<table class="rec"><tr><th></th><th>Air</th><th>${MAT[mk][0]}</th></tr><tr><td>Speed (× 10⁸ m/s)</td><td>3.00</td><td><b>${MAT[mk][1].toFixed(2)}</b></td></tr><tr><td>Crest spacing</td><td>100%</td><td><b>${sp}%</b></td></tr><tr><td>Frequency</td><td colspan="2">same: the source sets it</td></tr>${speed?'':`<tr><td>Angle to normal</td><td>${th}°</td><td><b>${(t2/D).toFixed(1)}°</b></td></tr>`}</table>`})};

// ---------- raybox: a ray box, a block and a protractor.
// mode "snell" (loop 3): record pairs of angles, find what stays the same.
// mode "mystery" (loop 4): the method of Practical 1C-1: graph sin(theta1) against sin(theta2), gradient = n.
// mode "tir" (loop 6): the ray starts in the block; find the critical angle.
SIMS.raybox=(host,o)=>{const mode=o.mode||(o.mystery?'mystery':'snell'),{c,cv,side,W,H}=lab(host,800,470),CX=400,BY=235;
  const up=mode==='tir';let th=40,nb=1.5,name='Glass',rows=[],k=0,demo=mode==='mystery',fit=false;
  const sl=slider(side,'Angle of incidence (or drag the ray box)',0,85,mode==='tir'?.5:1,40,x=>x+'°',x=>th=x);
  const MY={A:[1.36,'ethanol'],B:[1.47,'glycerol'],C:[1.63,'dense flint glass']},LOW={water:[1.33,'Water'],glass:[1.5,'Glass'],diamond:[2.42,'Diamond']};
  let mys='A',low='glass',A,box,res,tb,pills;
  const tab=()=>{if(!tb)return;tb.innerHTML=rows.length?`<table class="rec"><tr><th>${mx('$\\theta_1$')}</th><th>${mx('$\\theta_2$')}</th>${mode==='mystery'?`<th>${mx('$\\sin\\theta_1$')}</th><th>${mx('$\\sin\\theta_2$')}</th>`:`<th>${mx('$\\dfrac{\\sin\\theta_1}{\\sin\\theta_2}$')}</th>`}</tr>${rows.map(r=>`<tr><td>${r[0]}°</td><td>${r[1].toFixed(1)}°</td>${mode==='mystery'?`<td>${Math.sin(r[0]*D).toFixed(3)}</td><td>${Math.sin(r[1]*D).toFixed(3)}</td>`:`<td><b>${(Math.sin(r[0]*D)/Math.sin(r[1]*D)).toFixed(2)}</b></td>`}</tr>`).join('')}</table>`:`<span class="muted">${mode==='mystery'?'Record at least five angles.':'Record four different angles. Look for a number that does not change.'}</span>`};
  const rec=a=>{const s=Math.sin(a*D)/nb;if(a>0&&s<1){rows=rows.filter(r=>r[0]!==a);rows.push([a,Math.asin(s)/D]);rows.sort((x,y)=>x[0]-y[0]);rows=rows.slice(-(mode==='mystery'?6:5));tab()}};
  if(mode==='snell'){pills=choice(side,'Lower material',[['water','Water'],['glass','Glass'],['diamond','Diamond']],'glass',q=>{low=q;nb=LOW[q][0];name=LOW[q][1];rows=[];tab();A.clear()});
    const rb=el('button','btn','Record this pair of angles');rb.onclick=()=>rec(th);side.append(rb);tb=el('div');side.append(tb);tab();
    box=el('div');side.append(box);A=ask(box,'ratio','',()=>nb,.02);const sa=el('button','btn alt','Show answer');sa.style.marginTop='6px';box.append(sa);
    sa.onclick=()=>{rows=[];[20,40,60,80].forEach(rec);A.show()}}
  if(mode==='mystery'){pills=choice(side,'Block',[['A','Mystery A'],['B','Mystery B'],['C','Mystery C']],'A',q=>{mys=q;nb=MY[q][0];name='Mystery '+q;rows=[];fit=false;tab();A.clear();res.innerHTML=''});
    const rb=el('button','btn','Record this pair of angles');rb.onclick=()=>rec(th);side.append(rb);tb=el('div');side.append(tb);tab();
    box=el('div');side.append(box);A=ask(box,'$n$','',()=>nb,.03);res=el('div','read');
    const sa=el('button','btn alt','Show answer');sa.style.marginTop='6px';box.append(sa,res);
    sa.onclick=()=>{rows=[];[10,20,30,40,50,60].forEach(rec);fit=true;A.show();res.innerHTML=`Gradient = ${nb.toFixed(2)}: Mystery ${mys} is <b>${MY[mys][1]}</b>.`};
    $('button',box).addEventListener('click',()=>setTimeout(()=>{const ok=$('.mk',box).classList.contains('ok');if(ok)fit=true;res.innerHTML=ok?`Mystery ${mys} is <b>${MY[mys][1]}</b> (n = ${nb.toFixed(2)}).`:'Check: calculator in degrees? Which angle is in air and which is in the block?'},0))}
  if(mode==='tir'){pills=choice(side,'Block',[['water','Water'],['glass','Glass'],['diamond','Diamond']],'glass',q=>{low=q;nb=LOW[q][0];name=LOW[q][1];A.clear()});
    box=el('div');side.append(box);box.append(el('div','muted','Find the critical angle of each block. Nothing is given.'));
    A=ask(box,'$\\theta_c$','°',()=>Math.asin(1/nb)/D,.02);const sa=el('button','btn alt','Show answer');sa.style.marginTop='6px';box.append(sa);
    sa.onclick=()=>{setSl(sl,Math.round(Math.asin(1/nb)/D*2)/2+.5);A.show()}}
  const out=el('div','read');if(mode==='tir')side.append(out);
  drag(cv,W,(x,y)=>{if(!side.style.display&&k>=0){const dx=Math.abs(x-CX),dy=up?y-BY:BY-y;if(dy>8)setSl(sl,Math.max(0,Math.min(85,Math.round(Math.atan2(dx,dy)/D))))}});
  const caps={snell:[
      'A ray box shines a thin ray from air into a glass block.',
      'The dashed line is the <b>normal</b>, at 90° to the surface. Angles are measured from the normal, not from the surface.',
      '$\\theta_1$ is the angle in air. $\\theta_2$ is the angle in the glass. Here 40° in air becomes 25.4° in glass.',
      'Your job: record four pairs of angles. One number in the table does not change. Find it.',
      ''],
    mystery:[
      'Practical 1C-1: find $n$ for a block you cannot identify. First, a practice run with plain glass.',
      'Shine the ray in. Measure $\\theta_1$ in air and $\\theta_2$ in the block.',
      'Repeat at five or six angles. Work out $\\sin\\theta_1$ and $\\sin\\theta_2$ for each.',
      'Plot $\\sin\\theta_1$ up, $\\sin\\theta_2$ across. A straight line through the origin. Its gradient is $n$: here 1.50.',
      ''],
    tir:[
      'Now the ray starts inside the glass and goes up into air.',
      'Going into a lower $n$, the ray bends <b>away</b> from the normal. A weak ray also reflects back: <b>partial internal reflection</b>.',
      'As the angle grows, the ray in air swings down towards the surface and gets fainter. The reflected ray gets brighter.',
      'At the <b>critical angle</b> $\\theta_c$ the ray in air skims along the surface: $\\theta_2 = 90°$. For this glass $\\theta_c = 41.8°$.',
      'Past it, no light gets out. All of it reflects: <b>total internal reflection</b>.',
      '']}[mode];
  let sweep=0;
  const stage=stager(host,side,caps,q=>{k=q;const free=q===caps.length-1;
    if(mode==='snell'){nb=1.5;rows=[];th=q===0?0:40;if(free){pickPill(pills,1);setSl(sl,40);rows=[];tab();A.clear()}}
    if(mode==='mystery'){if(!free){demo=true;nb=1.5;name='Practice glass';rows=[];fit=q===3;if(q>=2)[20,30,40,50,60].forEach(rec);else th=q===0?0:40;if(q===1)th=40}
      else{demo=false;fit=false;pickPill(pills,0);rows=[];tab();setSl(sl,40);A.clear();res.innerHTML=''}}
    if(mode==='tir'){nb=1.5;name='Glass';th=[20,20,30,41.8,55][q]??30;sweep=q===2?30:0;if(free){pickPill(pills,1);setSl(sl,30);A.clear()}}});
  // a small graph of sin(theta1) against sin(theta2), in the lower left of the canvas
  const graph=()=>{const gx=26,gy=448,gw=170,gh=170;c.fillStyle='rgba(7,11,31,.92)';c.fillRect(gx-20,gy-gh-26,gw+34,gh+46);
    c.strokeStyle=C.mu;c.lineWidth=1.5;ln(c,gx,gy,gx+gw,gy);ln(c,gx,gy,gx,gy-gh);
    txt(c,'sin θ₁',gx+4,gy-gh-10,C.mu,'600 12px Inter');txt(c,'sin θ₂',gx+gw,gy+16,C.mu,'600 12px Inter','right');txt(c,'0',gx-12,gy+14,C.mu,'600 11px Inter');txt(c,'1',gx-12,gy-gh+4,C.mu,'600 11px Inter');txt(c,'1',gx+gw-4,gy+14,C.mu,'600 11px Inter');
    rows.forEach(r=>dot(c,gx+Math.sin(r[1]*D)*gw,gy-Math.sin(r[0]*D)*gh,4.5,C.am));
    if(fit&&rows.length){let sxy=0,sxx=0;rows.forEach(r=>{const x=Math.sin(r[1]*D),y=Math.sin(r[0]*D);sxy+=x*y;sxx+=x*x});const g=sxy/sxx,xm=Math.min(1,1/g);
      c.strokeStyle=C.pk;c.lineWidth=2;ln(c,gx,gy,gx+xm*gw,gy-g*xm*gh);txt(c,'gradient = '+g.toFixed(2),gx+gw-4,gy-gh+24,C.pk,'700 14px Inter','right')}};
  loop(host,dt=>{stage();if(sweep&&k===2){th=Math.min(41,th+dt*2.5)}
    c.clearRect(0,0,W,H);const n1=up?nb:1,n2=up?1:nb,t1=th*D,s2=n1*Math.sin(t1)/n2,tir=s2>=1,t2=tir?Math.PI/2:Math.asin(s2),d=up?1:-1,R=fres(n1,n2,t1);
    c.fillStyle=`rgba(125,211,252,${(nb-1)*.16})`;c.fillRect(0,BY,W,H-BY);c.strokeStyle='#5b6aa8';c.lineWidth=2;ln(c,0,BY,W,BY);
    txt(c,'Air, n = 1.00',16,26,C.mu);txt(c,mode==='mystery'&&!demo?name+', n = ?':name+', n = '+nb.toFixed(2),mode==='mystery'?W-16:16,H-14,C.mu,'600 14px Inter',mode==='mystery'?'right':'left');
    c.setLineDash([6,6]);c.strokeStyle=k>=1||mode!=='snell'?'#cfd7f5':C.mu;c.lineWidth=1.5;ln(c,CX,14,CX,H-14);c.setLineDash([]);
    for(let a=-90;a<=90;a+=5){const r1=a%30===0?150:a%10===0?158:163;[1,-1].forEach(v=>{c.strokeStyle='#3a4790';c.lineWidth=1.5;ln(c,CX+r1*Math.sin(a*D),BY+v*r1*Math.cos(a*D),CX+170*Math.sin(a*D),BY+v*170*Math.cos(a*D));
      if(a%30===0&&a)txt(c,Math.abs(a)+'°',CX+188*Math.sin(a*D),BY+v*188*Math.cos(a*D)+4,'#5b6aa8','600 11px Inter','center')})}
    const ix=CX-215*Math.sin(t1),iy=BY+d*215*Math.cos(t1);
    c.strokeStyle=C.am;c.lineWidth=4;ln(c,ix,iy,CX,BY);
    // reflected ray: brightness follows the fraction reflected (Fresnel), shown at least faintly
    c.globalAlpha=tir?1:Math.min(1,.18+R*1.6);ln(c,CX,BY,CX+215*Math.sin(t1),BY+d*215*Math.cos(t1));c.globalAlpha=1;
    if(!tir){c.globalAlpha=Math.max(.25,1-R);ln(c,CX,BY,CX+225*Math.sin(t2),BY-d*225*Math.cos(t2));c.globalAlpha=1}
    c.save();c.translate(ix,iy);c.rotate(Math.atan2(BY-iy,CX-ix));c.fillStyle='#e8ecff';c.fillRect(-46,-14,46,28);c.restore();
    const a0=up?Math.PI/2:-Math.PI/2;
    if(th>0)arc(c,CX,BY,54,up?a0:a0-t1,up?a0+t1:a0,C.am);if(!tir&&th>0)arc(c,CX,BY,70,up?-a0:-a0-t2,up?-a0+t2:-a0,C.am);
    c.fillStyle='rgba(9,14,40,.85)';c.fillRect(W-214,10,204,66);
    txt(c,'θ₁ = '+(+th.toFixed(1))+'°',W-22,36,C.am,'700 19px Inter','right');
    txt(c,tir?'θ₂: no ray out':'θ₂ = '+(t2/D).toFixed(1)+'°',W-22,64,C.am,'700 19px Inter','right');
    if(tir)txt(c,'No ray gets out: total internal reflection',CX,60,C.pk,'700 17px Inter','center');
    else if(mode==='tir'&&th>0)txt(c,`${Math.round(R*100)}% reflects back, ${100-Math.round(R*100)}% gets out`,CX,60,C.mu,'600 15px Inter','center');
    if(mode==='mystery')graph();
    if(mode==='tir')out.innerHTML=tir?'All the light reflects.':`Ray out at <b>${(t2/D).toFixed(1)}°</b>. Reflected: <b>${Math.round(R*100)}%</b>`})};

// ---------- c1_depth: apparent depth. A coin under water seen from above.
// Exact ray tracing: two rays from the coin reach the two sides of the eye's pupil; their back-extensions cross at the image.
// Looking straight down this gives apparent depth = real depth / n (to within 0.1%); from the side the image is shallower still.
SIMS.c1_depth=(host,o)=>{const {c,side,W,H}=lab(host,800,470),S=2.5,SY=190,X0=250,HE=68,PUP=2.5;let Dp=40,n=1.33,ex=40,k=0;
  const X=cm=>X0+cm*S,Y=cm=>SY+cm*S; // cm: x right of the coin, y down from the surface
  // surface point xs (cm) where a ray from the coin (0, Dp) leaves the water and reaches the eye point (xe, -HE)
  const hit=xe=>{const f=xs=>{const tw=Math.atan2(xs,Dp),sa=n*Math.sin(tw);if(Math.abs(sa)>=1)return Math.sign(xs)*1e9;return xs+HE*Math.tan(Math.asin(sa))-xe};
    let a=Math.min(0,xe),b=Math.max(0,xe);for(let i=0;i<60;i++){const m=(a+b)/2;(f(m)>0)?b=m:a=m}return (a+b)/2};
  const trace=xe=>{const xs=hit(xe),ta=Math.asin(n*Math.sin(Math.atan2(xs,Dp)));return {xs,ta}};
  const image=()=>{const r1=trace(ex-PUP),r2=trace(ex+PUP);// back-extend: x = xs - y*tan(ta) for y>0 (below the surface)
    const t1=Math.tan(r1.ta),t2=Math.tan(r2.ta);if(Math.abs(t1-t2)<1e-9)return {x:0,y:Dp/n,r1,r2};const y=(r2.xs-r1.xs)/(t2-t1);return {x:r1.xs-y*t1,y,r1,r2}};
  const ds=slider(side,'Real depth of the coin',10,80,1,40,x=>x+' cm',x=>Dp=x);
  const es=slider(side,'Move your eye sideways',0,110,1,40,x=>x+' cm',x=>ex=x);
  const liq=choice(side,'Liquid',[[1.33,'Water, n = 1.33'],[1.5,'Glass, n = 1.50']],1.33,q=>n=q);
  const out=el('div','read');side.append(out);
  const tk=mis(side,[
    {t:'Water. Look straight down (eye at 0 cm). Make the coin <b>look</b> 45 cm deep.',ok:s=>s.n===1.33&&s.ex<=1&&Math.abs(s.img-45)<.6,show:()=>{pickPill(liq,0);setSl(es,0);setSl(ds,60)},d:'Real depth 60 cm. $\\dfrac{60}{1.33} = 45$ cm. It looks shallower than it is.'},
    {t:'Change to glass. Look straight down. Make the coin look 30 cm deep.',ok:s=>s.n===1.5&&s.ex<=1&&Math.abs(s.img-30)<.6,show:()=>{pickPill(liq,1);setSl(es,0);setSl(ds,45)},d:'$\\dfrac{45}{1.50} = 30$ cm. A bigger $n$ lifts the image more.'},
    {t:'Leave the coin alone. Move your eye far to the side. Does the coin look deeper or shallower?',ok:s=>s.ex>=70,show:()=>setSl(es,90),d:'Shallower still. $\\dfrac{\\text{real depth}}{n}$ only works when you look nearly straight down.'}],()=>({n,ex,img:image().y}));
  const im0=(()=>{const a=Dp,b=n,e=ex;Dp=40;n=1.33;ex=40;const r=image().y;Dp=a;n=b;ex=e;return r})();
  const stage=stager(host,side,[
    'A coin lies on the bottom of a tank of water, 40 cm down. Your eye looks in from above.',
    'Light from the coin leaves the water. Going into air (lower $n$), each ray bends <b>away</b> from the normal.',
    'Your brain assumes light travels in straight lines. It traces the rays back: the dashed lines.',
    `The dashed lines meet higher up. That point is the <b>image</b>. The coin looks ${im0.toFixed(0)} cm deep, not 40 cm.`,
    'Look straight down and the rule is simple: apparent depth $\\approx \\dfrac{\\text{real depth}}{n} = \\dfrac{40}{1.33} = 30$ cm.',
    ''],q=>{k=q;if(q<5){Dp=40;n=1.33;ex=q===4?0:40}else{pickPill(liq,0);setSl(ds,40);setSl(es,40);tk.reset()}});
  loop(host,dt=>{stage();if(k===5)tk.tick(dt);c.clearRect(0,0,W,H);const im=image();
    c.fillStyle=`rgba(125,211,252,${(n-1)*.3})`;c.fillRect(0,SY,W,Y(85)-SY);c.strokeStyle='#5b6aa8';c.lineWidth=2;ln(c,0,SY,W,SY);
    c.fillStyle='#232b55';c.fillRect(0,Y(85),W,H-Y(85));txt(c,n===1.33?'Water':'Glass',W-16,SY+24,C.mu,'600 14px Inter','right');txt(c,'Air',W-16,SY-12,C.mu,'600 14px Inter','right');
    // depth ruler at the left
    c.strokeStyle=C.mu;c.lineWidth=1.5;ln(c,30,SY,30,Y(80));for(let d=0;d<=80;d+=10){ln(c,30,Y(d),d%20?38:44,Y(d));if(d%20===0)txt(c,d+' cm',50,Y(d)+5,C.mu,'600 12px Inter')}
    // coin and eye
    c.fillStyle='#fbb040';c.beginPath();c.ellipse(X(0),Y(Dp),14,5,0,0,7);c.fill();txt(c,'coin',X(0),Y(Dp)+22,C.am,'600 13px Inter','center');
    const exx=X(ex),eyy=Y(-HE);c.strokeStyle='#fff';c.lineWidth=2;c.beginPath();c.ellipse(exx,eyy,16,9,0,0,7);c.stroke();dot(c,exx,eyy,5,'#fff');txt(c,'eye',exx+22,eyy+5,'#fff','600 13px Inter');
    // rays
    [im.r1,im.r2].forEach((r,i)=>{const xe=ex+(i?PUP:-PUP);c.strokeStyle=C.cy;c.lineWidth=2.5;ln(c,X(0),Y(Dp),X(r.xs),SY);ln(c,X(r.xs),SY,X(xe),eyy);arrowHead(c,(X(r.xs)+X(xe))/2,(SY+eyy)/2,Math.atan2(eyy-SY,X(xe)-X(r.xs)),C.cy)});
    if(k>=1){const r=im.r2;c.setLineDash([4,5]);c.strokeStyle='#cfd7f5';c.lineWidth=1.2;ln(c,X(r.xs),SY-60,X(r.xs),SY+60);c.setLineDash([])}
    if(k>=2){c.setLineDash([7,6]);c.strokeStyle=C.pk;c.lineWidth=2;[im.r1,im.r2].forEach(r=>ln(c,X(r.xs),SY,X(im.x),Y(im.y)));c.setLineDash([])}
    if(k>=3){c.globalAlpha=.6;c.fillStyle=C.pk;c.beginPath();c.ellipse(X(im.x),Y(im.y),14,5,0,0,7);c.fill();c.globalAlpha=1;txt(c,'image',X(im.x)-22,Y(im.y)+5,C.pk,'700 14px Inter','right');
      c.strokeStyle=C.pk;c.lineWidth=1;c.setLineDash([2,4]);ln(c,30,Y(im.y),X(im.x)-14,Y(im.y));c.setLineDash([])}
    if(k>=3)txt(c,`looks ${im.y.toFixed(1)} cm deep`,X(0)+90,Y(Dp)+30>H-10?H-10:Y(Dp)+30,C.pk,'700 16px Inter');
    out.innerHTML=`Real depth <b>${Dp} cm</b><br>Looks <b class="pk">${im.y.toFixed(1)} cm</b> deep<br>${fr('$\\dfrac{\\text{real}}{n}$')} = <b>${(Dp/n).toFixed(1)} cm</b>`})};

// ---------- c1_fibre: a straight optical fibre. Core n = 1.50; cladding n chosen. The laser enters the flat end in air.
// Inside, the ray meets the core wall at phi = 90 - theta_r. phi >= critical angle: total internal reflection, no loss.
// phi < critical angle: most light refracts into the cladding and is absorbed by the coating; a little reflects (Fresnel).
// Widest launch angle that stays in: sin(alpha) = sqrt(n_core^2 - n_clad^2) (cladding 1.48: 14.1, 1.46: 20.1, 1.40: 32.6 degrees).
SIMS.c1_fibre=(host,o)=>{const {c,side,W,H}=lab(host,800,470),N1=1.5,FX=130,FE=790,CT=180,CB=290,CL=150,CLB=320,JT=136,JB=334,MY=(CT+CB)/2;let al=10,n2=1.40,k=0,t=0;
  const as=slider(side,'Launch angle into the fibre',0,60,.5,10,x=>x+'°',x=>al=x);
  const cl=choice(side,'Cladding',[[1.48,'n = 1.48'],[1.46,'n = 1.46'],[1.4,'n = 1.40']],1.4,q=>{n2=q;A.clear()});
  const out=el('div','read');side.append(out);const box=el('div');side.append(box);
  box.append(el('div','muted','Find the widest launch angle that still stays in the core.'));
  const amax=()=>Math.asin(Math.sqrt(N1*N1-n2*n2))/D,A=ask(box,'widest','°',amax,.04);
  const sa=el('button','btn alt','Show answer');sa.style.marginTop='6px';sa.onclick=()=>{setSl(as,Math.floor(amax()*2)/2);A.show()};box.append(sa);
  const stage=stager(host,side,[
    'An optical fibre: a glass <b>core</b>, wrapped in <b>cladding</b> with a lower $n$, inside a plastic coating.',
    'A laser shines into the end. The ray refracts as it enters the core.',
    'It meets the core wall at a big angle, more than the critical angle. Total internal reflection: all the light stays in.',
    'So it bounces all the way along. Almost no light is lost, even over kilometres.',
    'Launch it too steeply and it meets the wall at less than the critical angle. Most of it leaks out at every bounce.',
    ''],q=>{k=q;if(q<5){n2=1.4;al=q<4?20:40}else{pickPill(cl,2);setSl(as,10);A.clear()}});
  loop(host,dt=>{stage();t+=dt;c.clearRect(0,0,W,H);
    const tr=Math.asin(Math.sin(al*D)/N1),phi=Math.PI/2-tr,thc=Math.asin(n2/N1),tir=phi>=thc,Rw=fres(N1,n2,phi);
    // fibre layers
    c.fillStyle='#2a2f45';c.fillRect(FX,JT,FE-FX,JB-JT);c.fillStyle='rgba(125,211,252,.16)';c.fillRect(FX,CL,FE-FX,CLB-CL);c.fillStyle='rgba(125,211,252,.34)';c.fillRect(FX,CT,FE-FX,CB-CT);
    c.strokeStyle='#5b6aa8';c.lineWidth=1.5;ln(c,FX,CT,FE,CT);ln(c,FX,CB,FE,CB);ln(c,FX,CL,FE,CL);ln(c,FX,CLB,FE,CLB);
    txt(c,'coating',FE-6,JT+12,C.mu,'600 12px Inter','right');txt(c,'cladding, n = '+n2.toFixed(2),FE-6,CL+20,C.mu,'600 13px Inter','right');txt(c,'core, n = 1.50',FE-6,CT+22,'#cfd7f5','600 13px Inter','right');
    // laser and entry
    const L=150,lx=FX-L*Math.cos(al*D),ly=MY-L*Math.sin(al*D);c.save();c.translate(lx,ly);c.rotate(al*D);c.fillStyle='#e8ecff';c.fillRect(-44,-10,44,20);c.restore();
    c.strokeStyle=C.pk;c.lineWidth=3.5;ln(c,lx,ly,FX,MY);
    c.setLineDash([5,5]);c.strokeStyle=C.mu;c.lineWidth=1.2;ln(c,FX-60,MY,FX+60,MY);c.setLineDash([]);
    if(al>0)txt(c,al+'°',FX-66,MY-6,C.am,'700 14px Inter','right');
    // path inside: zigzag; fade by the reflected fraction at each wall when not totally reflected
    let x=FX,y=MY,dy=1,I=1,bounces=0,first=null;const dx=1/Math.tan(tr||1e-6);
    c.lineWidth=3.5;
    while(x<FE&&I>.002){const yt=dy>0?CB:CT,len=tr>0?(yt-y)/dy*dx:FE-x,nx=Math.min(FE,x+Math.abs(len)),ny=tr>0?y+(nx-x)/dx*dy:y;
      c.strokeStyle=`rgba(244,114,182,${Math.max(.08,I)})`;ln(c,x,y,nx,ny);
      if(nx>=FE)break;
      if(!tir){const psi=Math.asin(N1*Math.sin(phi)/n2),ox=nx+(CLB-CB)*Math.tan(psi);c.strokeStyle=`rgba(244,114,182,${Math.max(.1,I*(1-Rw))})`;ln(c,nx,ny,ox,dy>0?CLB:CL);
        dot(c,ox,dy>0?CLB:CL,4,`rgba(248,113,113,${Math.max(.2,I)})`);if(!first)first=[ox,dy>0?CLB+18:CL-10];I*=Rw}
      x=nx;y=ny;dy=-dy;bounces++}
    if(first)txt(c,'leaks out, absorbed',first[0]+8,first[1]+(first[1]>MY?14:-4),'#f87171','700 14px Inter');
    if(k===2||k===3||k===5&&tir){/* angle at the first wall */const x1=FX+(CB-MY)/Math.tan(tr||1e-6);if(tr>0&&x1<FE){c.setLineDash([4,4]);c.strokeStyle='#cfd7f5';c.lineWidth=1.2;ln(c,x1,CB-50,x1,CB+20);c.setLineDash([]);
      arc(c,x1,CB,34,-Math.PI/2-phi,-Math.PI/2,C.am);txt(c,(phi/D).toFixed(1)+'°',x1-38,CB-36,C.am,'700 14px Inter','right')}}
    const end=Math.max(0,tir?100:I*100);
    txt(c,'light reaching the far end: '+(tir?'all of it':end<1?'almost none':end.toFixed(0)+'%'),W/2,H-20,tir?C.gr:'#f87171','700 18px Inter','center');
    out.innerHTML=`Angle at the core wall <b>${(phi/D).toFixed(1)}°</b><br>Critical angle <b>${(thc/D).toFixed(1)}°</b><br>${tir?'<b class="gr">Stays in</b>':'<b class="no">Leaks out</b>'}`})};

// ---------- c1_prism: dispersion in a 60 degree glass prism.
// n for each colour from Cambridge Table 1C-2 (typical glass): red 1.509, yellow 1.511, green 1.515, blue 1.517, violet 1.521.
// Exact ray trace at both faces; deviation = i + e - 60. Violet has the biggest n: it deviates most and is the first to be trapped.
SIMS.c1_prism=(host,o)=>{const {c,side,W,H}=lab(host,800,470);
  const COL=[['Red',1.509,'#ef4444'],['Yellow',1.511,'#facc15'],['Green',1.515,'#22c55e'],['Blue',1.517,'#3b82f6'],['Violet',1.521,'#a855f7']];
  const Lx=150,Ly=380,Rx=430,Ry=380,Ax=290,Ay=380-280*Math.sqrt(3)/2,Px=(Lx+Ax)/2,Py=(Ly+Ay)/2,SX=780;
  let inc=48,light='white',k=0,seen={r:0,v:0};
  const is=slider(side,'Angle of incidence',20,80,.1,48,x=>x.toFixed(1)+'°',x=>inc=x);
  const lp=choice(side,'Light',[['white','White'],['Red','Red only'],['Violet','Violet only']],'white',q=>{light=q;if(q==='Red')seen.r=1;if(q==='Violet')seen.v=1});
  const out=el('div','read');side.append(out);
  const trace=n=>{const i=inc*D,r1=Math.asin(Math.sin(i)/n),din=(30*D)-r1;// canvas angles, y down: inward normal of the left face points at +30 degrees
    const dx=Math.cos(din),dy=Math.sin(din);// hit the right face: A + s(R - A)
    const ux=Rx-Ax,uy=Ry-Ay,den=dx*uy-dy*ux,s=((Ax-Px)*dy-(Ay-Py)*dx)/den,tq=((Ax-Px)*uy-(Ay-Py)*ux)/den;
    const Qx=Ax+s*ux,Qy=Ay+s*uy,e=60*D-r1,se=n*Math.sin(e);
    if(s<0||s>1)return {Qx,Qy,bad:true};
    if(se>=1)return {Qx,Qy,tir:true,e};const ex=Math.asin(se),dout=-30*D+ex;return {Qx,Qy,dout,dev:(inc+ex/D-60),ex}};
  const tk=mis(side,[
    {t:'Which colour bends most? Send in red only, then violet only.',ok:s=>s.seen.r&&s.seen.v,show:()=>{pickPill(lp,1);setTimeout(()=>pickPill(lp,2),700)},d:'Violet. In glass violet has the biggest $n$ (1.521, red 1.509). It slows the most, so it bends the most.'},
    {t:'White light. Find an angle where violet is trapped inside but red still gets out.',ok:s=>s.light==='white'&&s.vt&&!s.rt,show:()=>{pickPill(lp,0);setSl(is,29.1)},d:'Violet has the biggest $n$, so the smallest critical angle. It is the first colour to be totally internally reflected.'}],
    ()=>({seen,light,vt:!!trace(1.521).tir,rt:!!trace(1.509).tir}));
  const stage=stager(host,side,[
    'A narrow beam of white light hits a glass prism.',
    'White light is a mix of colours. In glass each colour has a slightly different $n$: from 1.509 for red to 1.521 for violet.',
    'So each colour bends by a different amount going in, and again coming out. The colours fan out: <b>dispersion</b>.',
    'The close-up shows where each colour lands on the screen. <b>Violet bends most. Red bends least.</b>',
    ''],q=>{k=q;if(q<4){inc=48;light='white'}else{pickPill(lp,0);setSl(is,48);seen={r:0,v:0};tk.reset()}});
  loop(host,dt=>{stage();if(k===4)tk.tick(dt);c.clearRect(0,0,W,H);
    // prism and screen
    c.fillStyle='rgba(125,211,252,.16)';c.strokeStyle='#7d8bd0';c.lineWidth=2;c.beginPath();c.moveTo(Lx,Ly);c.lineTo(Ax,Ay);c.lineTo(Rx,Ry);c.closePath();c.fill();c.stroke();
    c.fillStyle='#cfd7f5';c.fillRect(SX,20,8,H-40);txt(c,'screen',SX-6,H-24,C.mu,'600 12px Inter','right');txt(c,'glass prism',Ax,Ly+26,C.mu,'600 13px Inter','center');
    const i=inc*D,din0=30*D-i,bx=Px-260*Math.cos(din0),by=Py-260*Math.sin(din0);
    c.strokeStyle='#fff';c.lineWidth=4;ln(c,bx,by,Px,Py);
    c.setLineDash([5,5]);c.strokeStyle=C.mu;c.lineWidth=1.2;ln(c,Px-60*Math.cos(30*D),Py-60*Math.sin(30*D),Px+50*Math.cos(30*D),Py+50*Math.sin(30*D));c.setLineDash([]);
    const show=COL.filter(cc=>light==='white'||cc[0]===light),hits=[];let rows='';
    show.forEach(([nm,n,col])=>{const r=trace(n);c.strokeStyle=col;c.lineWidth=k>=2||light!=='white'?2.2:1.2;c.globalAlpha=k>=1||light!=='white'?1:.35;ln(c,Px,Py,r.Qx,r.Qy);c.globalAlpha=1;
      if(r.tir||r.bad){rows+=`<tr><td style="color:${col}">${nm}</td><td>${n.toFixed(3)}</td><td>trapped</td></tr>`;if(r.tir){// totally reflected at the second face: a short piece of the reflected ray inside the prism
          const r1=Math.asin(Math.sin(i)/n),dd=30*D-r1,nx=Math.cos(-30*D),ny=Math.sin(-30*D),dt=Math.cos(dd)*nx+Math.sin(dd)*ny,rx=Math.cos(dd)-2*dt*nx,ry=Math.sin(dd)-2*dt*ny;
          c.strokeStyle=col;c.lineWidth=2;ln(c,r.Qx,r.Qy,r.Qx+70*rx,r.Qy+70*ry)}return}
      const tS=(SX-r.Qx)/Math.cos(r.dout),yS=r.Qy+tS*Math.sin(r.dout);c.strokeStyle=col;c.lineWidth=2.2;
      if(yS<H&&yS>0){ln(c,r.Qx,r.Qy,SX,yS);hits.push([yS,col])}else{const tt=((r.dout>0?H:0)-r.Qy)/Math.sin(r.dout);ln(c,r.Qx,r.Qy,r.Qx+tt*Math.cos(r.dout),r.Qy+tt*Math.sin(r.dout))}
      rows+=`<tr><td style="color:${col}">${nm}</td><td>${n.toFixed(3)}</td><td><b>${r.dev.toFixed(2)}°</b></td></tr>`});
    if(show.some(cc=>trace(cc[1]).tir))txt(c,'trapped colours reflect inside the prism',Ax,40,C.pk,'700 15px Inter','center');
    // close-up of the screen, x10 about red's spot (or the first spot)
    if(hits.length&&k>=3){const bxx=560,byy=60,bw=200,bh=150,ref=hits[0][0];c.fillStyle='rgba(9,14,40,.92)';c.fillRect(bxx,byy,bw,bh);c.strokeStyle='#5b6aa8';c.lineWidth=1.5;c.strokeRect(bxx,byy,bw,bh);
      txt(c,'close-up of the screen (×10)',bxx+bw/2,byy-8,C.mu,'600 12px Inter','center');
      hits.forEach(([y,col],j)=>{const yy=byy+30+(y-ref)*10;if(yy>byy&&yy<byy+bh){c.fillStyle=col;c.fillRect(bxx+60,yy-3,80,6)}});
      if(hits.length>1){txt(c,'red',bxx+52,byy+34,'#ef4444','600 12px Inter','right')}}
    out.innerHTML=`<table class="rec"><tr><th>Colour</th><th>${mx('$n$')}</th><th>Bent by</th></tr>${rows}</table><div class="muted" style="margin-top:4px">${mx('$n$')} values: Cambridge Table 1C-2</div>`})};
})();
