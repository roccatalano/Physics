// ===== 1C labs
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
