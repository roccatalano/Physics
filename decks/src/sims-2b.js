// ===== 2B labs: blackbody curves (glow, Wien, area) and Earth's energy budget
// Blackbody curve: intensity at wavelength L (micrometres) for temperature T (K). Units are arbitrary.
const B2={b:2.898e-3,c2:14388,
  I:(L,T)=>{const x=B2.c2/(L*T);return x>700?0:1/(L**5*(Math.exp(x)-1))},
  peak:T=>2898/T,   // micrometres
  region:L=>L<0.4?'ultraviolet':L<=0.7?'visible':'infrared',
  rgb(nm){let r=0,g=0,b=0;if(nm<440){r=(440-nm)/60;b=1}else if(nm<490){g=(nm-440)/50;b=1}else if(nm<510){g=1;b=(510-nm)/20}else if(nm<580){r=(nm-510)/70;g=1}else if(nm<645){r=1;g=(645-nm)/65}else r=1;return`rgb(${r*255|0},${g*255|0},${b*255|0})`},
  // colour of a glowing blackbody (sRGB, from published blackbody colour tables), and how bright the glow is
  COL:[[1000,255,56,0],[1500,255,109,0],[2000,255,137,18],[3000,255,180,107],[4000,255,209,163],[5000,255,228,206],[6000,255,243,239],[6500,255,249,253],[7000,245,243,255],[8000,227,233,255],[10000,204,219,255],[13000,191,211,255]],
  glow(T){const t=B2.COL;let i=0;while(i<t.length-2&&T>t[i+1][0])i++;const [a,b]=[t[i],t[i+1]],u=Math.max(0,Math.min(1,(T-a[0])/(b[0]-a[0])));
    const col=[1,2,3].map(j=>a[j]+(b[j]-a[j])*u),k=Math.max(0,Math.min(1,(T-750)/550));
    const base=[58,63,75];return{k,css:`rgb(${col.map((v,j)=>Math.round(base[j]+(v-base[j])*k)).join(',')})`}},
  look:T=>T<750?'no glow you can see':T<1100?'dull red':T<1600?'red-orange':T<2500?'orange':T<4200?'yellow-white':T<7000?'white':'blue-white'};

// glow: an object and its curve on a log wavelength axis (0.1 to 100 micrometres, like Cambridge Figure 2B-4)
// wien: the same graph with a cursor to drag onto the peak and a table of T, peak wavelength and their product
SIMS.b2_glow=(host,o)=>{const {c,cv,side,W,H}=lab(host,800,470),wien=o.mode==='wien';
  const GX0=wien?70:220,GX1=780,GY0=58,GY1=400,GW=GX1-GX0,GH=GY1-GY0;
  const px=L=>GX0+(Math.log10(L)+1)/3*GW,Lx=x=>10**((x-GX0)/GW*3-1);
  let T=300,k=0,cur=1,rows=[],shown=false;
  const ts=slider(side,'Temperature',2,4,.005,Math.log10(300),v=>Math.round(10**v)+' K',v=>T=Math.round(10**v));
  const setT=t=>{ts.value=Math.log10(t);ts.oninput()};
  const out=el('div','read');side.append(out);
  let tick=()=>{},tbl,fb;
  if(!wien){tick=missions(side,[
      {t:'Make it <b>red hot</b>: a glow you can just see.',ok:s=>s.T>=850&&s.T<=1500,d:'Red hot, yet the peak is still in the infrared. Most of its energy is invisible.'},
      {t:'Put the <b>peak</b> in visible light.',ok:s=>s.L>=.4&&s.L<=.7,d:'Like the Sun at 5778 K. It looks white because it gives off every colour.'},
      {t:'Set it to body temperature, <b>310 K</b>. Where is the peak?',ok:s=>s.T>=305&&s.T<=315,d:'Infrared, near 9 µm. You give off infrared all the time.'},
      {t:'Make the peak sit in the <b>ultraviolet</b>.',ok:s=>s.L<.4,d:'Above about 7200 K. The hottest stars look blue-white.'}],()=>({T,L:B2.peak(T)}))}
  else{const bt=el('div','btns');side.append(bt);const rec=el('button','btn','Record'),clr=el('button','btn alt','Clear table'),sa=el('button','btn alt','Show answer');bt.append(rec,clr,sa);
    tbl=el('div');side.append(tbl);fb=el('div','note','Find the peak at three different temperatures. Look at the last column.');side.append(fb);
    rec.onclick=()=>{rows.push({T,L:cur});if(rows.length>5)rows.shift();draw()};clr.onclick=()=>{rows=[];shown=false;draw()};
    sa.onclick=()=>{cur=B2.peak(T);shown=true;draw()};
    drag(cv,W,x=>{if(k<5)return;cur=Math.max(.1,Math.min(100,Lx(x)))})}
  const fmtL=L=>L<1?Math.round(L*1000)+' nm':+L.toPrecision(3)+' µm';
  const prod=r=>(r.L*1e-6*r.T*1e3).toFixed(2)+' × 10⁻³';
  const onPk=r=>Math.abs(r.L-B2.peak(r.T))/B2.peak(r.T)<.05;
  function draw(){if(!wien)return;tbl.innerHTML=`<table class="rec"><tr><th>T (K)</th><th>λ<sub>max</sub></th><th>λ<sub>max</sub> × T (m K)</th><th></th></tr>${rows.map(r=>`<tr><td>${r.T}</td><td>${fmtL(r.L)}</td><td><b>${prod(r)}</b></td><td class="${onPk(r)?'ok':'no'}">${onPk(r)?'✓':'✗'}</td></tr>`).join('')}</table>`;
    const good=rows.filter(onPk),Ts=[...new Set(good.map(r=>Math.round(Math.log10(r.T)*12)))];
    if(shown)fb.innerHTML=mx('The peak wavelength times the temperature is always the same: $\\lambda_{max}T = 2.898 \\times 10^{-3}$ m K.');
    else if(Ts.length>=3)fb.innerHTML='<b class="gr">Three peaks found.</b> The last column is the same every time: about 2.9 × 10⁻³ m K.';
    else fb.innerHTML='Find the peak at three different temperatures. Look at the last column. (Rows with ✗ are not on the peak.)'}
  const stage=stager(host,side,wien?[
      'The same graph. The <b class="hl">orange line</b> reads the wavelength wherever it sits.',
      'Here the object is at 4000 K. Slide the line to the top of the curve: that is the <b>peak wavelength</b>, $\\lambda_{max}$.',
      'The readout under the graph tells you how close to the top you are. 100% means you are on the peak.',
      'Press <b>Record</b>. The table keeps $T$, $\\lambda_{max}$ and the two multiplied together.',
      'Your job: three different temperatures. Find each peak, record it, and look at the last column.',
      '']:[
      'An object at room temperature, 300 K. The graph shows how much radiation it gives off at each wavelength.',
      'The curve is all in the <b>infrared</b>. We cannot see it, but the object is giving off radiation.',
      'Heat it to 1000 K. A dull red glow appears. The peak is still in the infrared.',
      'Heat it to 5778 K, the temperature of the Sun\'s surface. The peak moves into visible light.',
      'At the same temperature, every <b>blackbody</b> gives this same curve, whatever it is made of.',
      ''],q=>{k=q;const last=q===5;
      if(wien){if(q<5){setT(4000);cur=q===0?1.6:B2.peak(4000);rows=q>=3?[{T:4000,L:B2.peak(4000)}]:[]}else{rows=[];shown=false;cur=1.6;setT(2500)}draw()}
      else setT([300,300,1000,5778,5778,300][q])});
  loop(host,dt=>{stage();if(k===5&&!wien)tick(dt);c.clearRect(0,0,W,H);const Lp=B2.peak(T),Im=B2.I(Lp,T);
    // bands
    const ub=px(.4),vb=px(.7);c.fillStyle='rgba(139,92,246,.13)';c.fillRect(GX0,GY0,ub-GX0,GH);
    for(let x=ub;x<vb;x++){c.fillStyle=B2.rgb(Lx(x)*1000);c.globalAlpha=.28;c.fillRect(x,GY0,1.2,GH)}c.globalAlpha=1;
    c.fillStyle='rgba(239,68,68,.08)';c.fillRect(vb,GY0,GX1-vb,GH);
    txt(c,'UV',(GX0+ub)/2,GY0-10,'#a78bfa','700 14px Inter','center');txt(c,'visible',(ub+vb)/2,GY0-10,'#fde047','700 14px Inter','center');txt(c,'infrared',(vb+GX1)/2,GY0-10,'#f87171','700 14px Inter','center');
    // axes
    c.strokeStyle='#5b6aa8';c.lineWidth=2;ln(c,GX0,GY1,GX1,GY1);ln(c,GX0,GY0,GX0,GY1);
    [.1,.2,.5,1,2,5,10,20,50,100].forEach(L=>{const x=px(L);c.strokeStyle='#1e2858';c.lineWidth=1;ln(c,x,GY0,x,GY1);txt(c,(L<1?L:L)+'',x,GY1+18,C.mu,'600 13px Inter','center')});
    txt(c,'wavelength (µm)',(GX0+GX1)/2,GY1+40,C.mu,'600 14px Inter','center');
    c.save();c.translate(GX0-14,(GY0+GY1)/2);c.rotate(-Math.PI/2);txt(c,'intensity',0,0,C.mu,'600 14px Inter','center');c.restore();
    txt(c,'height scaled to fit',GX1-6,GY0+18,C.mu,'500 12px Inter','right');
    // curve
    c.beginPath();for(let x=GX0;x<=GX1;x+=1.5){const y=GY1-B2.I(Lx(x),T)/Im*.86*GH;x===GX0?c.moveTo(x,y):c.lineTo(x,y)}
    c.lineTo(GX1,GY1);c.lineTo(GX0,GY1);c.closePath();c.fillStyle='rgba(251,176,64,.16)';c.fill();
    c.beginPath();for(let x=GX0;x<=GX1;x+=1.5){const y=GY1-B2.I(Lx(x),T)/Im*.86*GH;x===GX0?c.moveTo(x,y):c.lineTo(x,y)}c.strokeStyle=C.am;c.lineWidth=3.5;c.stroke();
    if(!wien){const g=B2.glow(T);
      c.fillStyle='#151b3d';c.beginPath();c.roundRect(14,GY0,170,GH,14);c.fill();
      if(g.k>0){const rg=c.createRadialGradient(99,190,40,99,190,40+40*g.k);rg.addColorStop(0,g.css);rg.addColorStop(1,'rgba(0,0,0,0)');c.fillStyle=rg;c.globalAlpha=.7*g.k;c.fillRect(14,GY0,170,GH);c.globalAlpha=1}
      c.fillStyle=g.css;c.beginPath();c.roundRect(54,145,90,90,10);c.fill();
      txt(c,'the object',99,GY0+26,C.mu,'600 14px Inter','center');txt(c,T+' K',99,290,'#fff','700 24px Space Grotesk','center');
      txt(c,B2.look(T),99,318,C.mu,'600 14px Inter','center');
      if(k===1||k===2){const x=px(Lp);txt(c,'peak: infrared',x,GY1-.86*GH-14,C.pk,'700 16px Inter','center')}
      if(k===3){const x=px(Lp);txt(c,'peak: visible',x,GY1-.86*GH-14,C.pk,'700 16px Inter','center')}
      out.innerHTML=`<b>${T} K</b> = ${T<273?'−':''}${Math.abs(T-273)} °C<br>Peak is in the <b>${B2.region(Lp)}</b><br>Glow you can see: <b>${B2.look(T)}</b>`}
    else{if(k>=0){const x=px(cur),h=B2.I(cur,T)/Im;c.strokeStyle=C.am;c.lineWidth=2.5;ln(c,x,GY0,x,GY1);c.fillStyle=C.am;c.fillRect(x-9,GY1-6,18,12);
        const lab=fmtL(cur);txt(c,lab,Math.min(GX1-30,Math.max(GX0+30,x)),GY1+58,C.am,'700 16px Inter','center');
        txt(c,`line at ${lab}   ·   curve height there: ${Math.round(h*100)}% of the top`,(GX0+GX1)/2,30,'#fff','600 15px Inter','center')}
      out.innerHTML=`<b>T = ${T} K</b>`}})};

// area: two curves on the same fixed scale, linear wavelength axis 0 to 4000 nm (like Cambridge Figure 2B-2)
SIMS.b2_area=host=>{const {c,side,W,H}=lab(host,800,470),GX0=70,GX1=780,GY0=40,GY1=400,GW=GX1-GX0,GH=GY1-GY0,LM=4,REF=4500;
  let T=4500,k=0,mat=0;const px=L=>GX0+L/LM*GW,Ymax=B2.I(B2.peak(6000),6000)/.92;
  const area=t=>{let s=0;for(let L=.005;L<LM;L+=.005)s+=B2.I(L,t);return s},A0=area(REF);
  const ts=slider(side,'Your object: temperature',3000,6000,10,4500,v=>v+' K',v=>T=v);const setT=t=>{ts.value=t;ts.oninput()};
  const mp=choice(side,'Your object: material',[[0,'Iron'],[1,'Carbon'],[2,'Ceramic']],0,q=>{if(q!==0)mat=1});
  const out=el('div','read');side.append(out);
  const tick=missions(side,[
    {t:'Change the <b>material</b>. What happens to the curve?',ok:s=>s.mat,d:'Nothing. Same temperature, same curve, whatever it is made of.'},
    {t:'Make your object give off <b>twice</b> the energy of the grey one.',ok:s=>s.r>=1.9&&s.r<=2.1,d:'A little hotter gives twice the area. The peak also moved to a shorter wavelength.'},
    {t:'Now make it give off <b>a quarter</b> of the energy of the grey one.',ok:s=>s.r>=.235&&s.r<=.265,d:'Cooler: much less area, and the peak moved to a longer wavelength.'}],()=>({mat,r:area(T)/A0}));
  const stage=stager(host,side,[
    'Two blackbody curves drawn to the <b>same scale</b>. Grey: an object at 4500 K.',
    'The <b>area under the curve</b> is the total energy it gives off each second.',
    'Your object (orange) starts at 4500 K too, so its curve sits right on top of the grey one.',
    'Heat yours to 5500 K. The curve gets taller, the peak moves left, and the area grows a lot.',
    ''],q=>{k=q;setT(q===3?5500:4500);if(q===4){mat=0;$$('.pill',mp).forEach((p,i)=>p.classList.toggle('on',i===0))}});
  const curve=(t,fill,stroke,dash)=>{c.beginPath();c.moveTo(GX0,GY1);for(let x=GX0;x<=GX1;x+=1.5)c.lineTo(x,GY1-B2.I((x-GX0)/GW*LM,t)/Ymax*GH);c.lineTo(GX1,GY1);c.closePath();
    if(fill){c.fillStyle=fill;c.fill()}c.beginPath();for(let x=GX0;x<=GX1;x+=1.5){const y=GY1-B2.I((x-GX0)/GW*LM,t)/Ymax*GH;x===GX0?c.moveTo(x,y):c.lineTo(x,y)}c.setLineDash(dash||[]);c.strokeStyle=stroke;c.lineWidth=3.5;c.stroke();c.setLineDash([])};
  loop(host,dt=>{stage();if(k===4)tick(dt);c.clearRect(0,0,W,H);
    const ub=px(.4),vb=px(.7);for(let x=ub;x<vb;x++){c.fillStyle=B2.rgb((x-GX0)/GW*LM*1000);c.globalAlpha=.22;c.fillRect(x,GY0,1.2,GH)}c.globalAlpha=1;
    txt(c,'visible',(ub+vb)/2,GY0-10,'#fde047','700 13px Inter','center');
    c.strokeStyle='#5b6aa8';c.lineWidth=2;ln(c,GX0,GY1,GX1,GY1);ln(c,GX0,GY0,GX0,GY1);
    for(let L=0;L<=4000;L+=500){const x=px(L/1000);c.strokeStyle='#1e2858';c.lineWidth=1;if(L)ln(c,x,GY0,x,GY1);txt(c,L+'',x,GY1+18,C.mu,'600 13px Inter','center')}
    txt(c,'wavelength (nm)',(GX0+GX1)/2,GY1+40,C.mu,'600 14px Inter','center');
    c.save();c.translate(GX0-14,(GY0+GY1)/2);c.rotate(-Math.PI/2);txt(c,'intensity (same scale for both)',0,0,C.mu,'600 14px Inter','center');c.restore();
    curve(REF,k>=1?'rgba(148,163,200,.25)':null,'#94a3c8',[8,6]);
    if(k>=2)curve(T,'rgba(251,176,64,.22)',C.am);
    txt(c,'grey: 4500 K',GX1-8,GY0+20,'#94a3c8','700 15px Inter','right');if(k>=2)txt(c,'orange: '+T+' K',GX1-8,GY0+42,C.am,'700 15px Inter','right');
    if(k>=2){const x=px(B2.peak(T)),y=GY1-B2.I(B2.peak(T),T)/Ymax*GH;dot(c,x,y,6,C.pk)}
    const r=area(T)/A0;
    out.innerHTML=`Your object: <b>${T} K</b><br>Peak: <b>${Math.round(B2.peak(T)*1000)} nm</b><br>Area compared with grey: <b class="pk">${r<.995||r>1.005?'× '+r.toFixed(2):'the same'}</b><br><span class="muted" style="font-size:13px">Area under the curve shown (0 to 4000 nm).</span>`})};

// budget: Earth's energy budget. Simple model: sunlight absorbed at the surface, one layer of air,
// no convection or evaporation. Calibrated so that today's greenhouse gases give 15 °C with 240 W/m² absorbed.
SIMS.b2_budget=host=>{const {c,side,W,H}=lab(host,800,470),SIG=5.67e-8,U=.42749,CAP=3;
  let x=100,R=100,T=288,k=0,ph=0,goal=null;
  const g=v=>1-.1**((v/100)**.47);   // share of the surface infrared that greenhouse gases absorb (0.9 today)
  const flows=()=>{const A=340-R,E=SIG*T**4,G=g(x),win=(1-G)*E,back=G*E*U,up=G*E*(1-U);return{A,E,G,win,back,up,out:win+up,N:A-win-up}};
  const gs=slider(side,'Greenhouse gases (today = 100%)',0,200,5,100,v=>v+'%',v=>{x=v;goal=null});
  const rs=slider(side,'Sunlight reflected by clouds, ice and snow',40,170,5,100,v=>v+' W/m²',v=>R=v);
  const out=el('div','read');side.append(out);
  const tick=missions(side,[
    {t:'Remove <b>all</b> the greenhouse gases. Wait until in = out.',ok:s=>s.x===0&&Math.abs(s.N)<.3,d:'Here it settles near −18 °C. All the infrared escapes straight to space.'},
    {t:'Back to today: <b>100%</b>. Wait until in = out.',ok:s=>s.x===100&&s.R===100&&Math.abs(s.N)<.3,d:'15 °C. Greenhouse gases keep the surface much warmer than it would be without them.'},
    {t:'Raise greenhouse gases to <b>150%</b>. Watch the back radiation.',ok:s=>s.x>=150&&Math.abs(s.N)<.3,d:'More back radiation, so in beat out. The surface warmed until it gave off enough to balance again.'},
    {t:'Less ice and cloud: reflect only <b>70 W/m²</b>.',ok:s=>s.R<=70&&Math.abs(s.N)<.3,d:'More sunlight absorbed, so the balance comes at a higher temperature.'}],()=>({x,R,N:flows().N}));
  const stage=stager(host,side,[
    'Sunlight brings in <b>340 W/m²</b> on average. About <b>100 W/m²</b> is reflected by clouds, ice and snow.',
    'The other <b>240 W/m²</b> is absorbed and warms the surface.',
    'The warm surface gives off <b>infrared</b>. Only a little escapes straight to space, through the <b>atmospheric window</b>.',
    '<b>Greenhouse gases</b> absorb the rest and give it off again. Some goes up to space. Some comes back down: <b>back radiation</b>.',
    'Energy in = energy out, so the temperature stays steady: 15 °C.',
    'Add more greenhouse gas. Out drops below in, so the surface warms until in and out match again.',
    ''],q=>{k=q;goal=q===5?150:null;if(q<5){gs.value=100;gs.oninput();rs.value=100;rs.oninput();T=288}if(q===6){gs.value=100;gs.oninput();rs.value=100;rs.oninput();T=288}});
  const arrow=(x1,y1,x2,y2,w,col,lbl,lx,ly,al)=>{if(w<.3)return;const a=Math.atan2(y2-y1,x2-x1),hw=Math.max(7,w*.9);c.strokeStyle=col;c.lineWidth=w;c.lineCap='butt';
    ln(c,x1,y1,x2-Math.cos(a)*hw*1.1,y2-Math.sin(a)*hw*1.1);c.fillStyle=col;c.beginPath();c.moveTo(x2,y2);
    c.lineTo(x2-Math.cos(a)*hw*1.4-Math.sin(a)*hw,y2-Math.sin(a)*hw*1.4+Math.cos(a)*hw);c.lineTo(x2-Math.cos(a)*hw*1.4+Math.sin(a)*hw,y2-Math.sin(a)*hw*1.4-Math.cos(a)*hw);c.fill();
    c.setLineDash([4,14]);c.lineDashOffset=-ph;c.strokeStyle='rgba(255,255,255,.35)';c.lineWidth=Math.min(3,w/3);ln(c,x1,y1,x2-Math.cos(a)*hw*1.4,y2-Math.sin(a)*hw*1.4);c.setLineDash([]);
    if(lbl)txt(c,lbl,lx,ly,'#fff','700 15px Inter',al||'left')};
  loop(host,dt=>{const s0=stage();ph+=dt*30;
    if(goal!==null&&x<goal){x=Math.min(goal,x+dt*20);gs.value=x;$('b',gs.parentNode).textContent=Math.round(x)+'%'}
    const show=k;let f=flows();for(let i=0;i<4;i++){T+=f.N/CAP*dt/4;f=flows()}
    if(k===6)tick(dt);
    c.clearRect(0,0,W,H);const sc=v=>v/400*44,Y_SP=70,A0=170,A1=270,G0=400;
    // space, air, ground
    c.fillStyle='#04061a';c.fillRect(0,0,W,Y_SP);txt(c,'space',14,24,C.mu,'600 14px Inter');
    c.fillStyle='rgba(125,211,252,.08)';c.fillRect(0,A0,W,A1-A0);txt(c,'air with greenhouse gases',14,A1-10,C.cy,'600 13px Inter');
    const nd=Math.round(f.G*60);for(let i=0;i<nd;i++){const xx=(i*137.5)%660+20,yy=A0+28+((i*53)%70);dot(c,xx,yy,2.4,'rgba(125,211,252,.55)')}
    c.fillStyle='#14361f';c.fillRect(0,G0,W,H-G0);txt(c,'surface',14,H-16,C.gr,'600 14px Inter');
    // sunlight
    dot(c,120,36,24,'#fde047');
    if(show>=0)arrow(135,58,250,G0,sc(340),'rgba(253,224,71,.85)','sunlight in 340',190,130);
    if(show>=0)arrow(262,G0-6,360,Y_SP-6,sc(R),'rgba(253,224,71,.55)','reflected '+Math.round(R),372,100);
    if(show>=1)txt(c,'absorbed '+Math.round(f.A),190,G0+30,'#fde047','700 16px Inter','center');
    if(show>=2){arrow(500,G0,500,A1,sc(f.E),'rgba(239,68,68,.85)','surface infrared '+Math.round(f.E),474,A1+60,'right');
      const wx=500-sc(f.E)/2+sc(f.win)/2;arrow(wx,A1,wx,Y_SP-6,sc(f.win),'rgba(239,68,68,.95)','window '+Math.round(f.win),474,Y_SP+60,'right')}
    if(show>=3){arrow(590,A0,590,Y_SP-6,sc(f.up),'rgba(248,113,113,.8)','up from gases',605,Y_SP+64);
      arrow(670,A1,670,G0,sc(f.back),'rgba(248,113,113,.8)','back radiation',652,A1+100,'right')}
    if(show>=4)txt(c,'out to space '+Math.round(f.out),520,24,'#fff','700 16px Inter','center');
    // thermometer
    const tc=T-273,ty=G0-20-(Math.max(-40,Math.min(40,tc))+40)/80*230;c.fillStyle='#1e2858';c.beginPath();c.roundRect(744,G0-260,22,250,11);c.fill();
    c.fillStyle='#ef4444';c.beginPath();c.roundRect(748,ty,14,G0-14-ty,7);c.fill();dot(c,755,G0-10,16,'#ef4444');
    txt(c,(tc>=0?'':'−')+Math.abs(tc).toFixed(1)+' °C',755,G0-268,'#fff','700 18px Space Grotesk','center');
    const N=f.N,bal=Math.abs(N)<.3;
    out.innerHTML=`In (absorbed): <b>${Math.round(f.A)} W/m²</b><br>Out to space: <b>${Math.round(f.out)} W/m²</b><br>In minus out: <b class="${bal?'ok':N>0?'no':'cy'}">${Math.abs(N)<.05?'':N>0?'+':'−'}${Math.abs(N).toFixed(1)} W/m²</b> ${bal?'balanced':N>0?'warming':'cooling'}<br>Surface: <b>${(tc>=0?'':'−')+Math.abs(tc).toFixed(1)} °C</b><br><span class="muted" style="font-size:13px">Simple model: one layer of air, no convection or evaporation. Not a forecast.</span>`})};
