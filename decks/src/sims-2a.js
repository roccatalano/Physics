// ===== 2A labs (Thermal energy). Every lab: clicker walkthrough first, then a job for the class.
const A2={mix:(a,b,k)=>{k=Math.max(0,Math.min(1,k));const p=s=>[1,3,5].map(i=>parseInt(s.slice(i,i+2),16)),x=p(a),y=p(b);return`rgb(${x.map((v,i)=>v+(y[i]-v)*k|0)})`},
  ray:()=>Math.sqrt(-2*Math.log(1-Math.random()))/1.2533,           // speed factor, mean 1 (2D speed spread)
  expo:m=>-m*Math.log(1-Math.random()),                               // energy with mean m (2D kinetic energy spread)
  nice:x=>{const e=10**Math.floor(Math.log10(x)),f=x/e;return(f<=1?1:f<=2?2:f<=5?5:10)*e},
  K:c=>c+273,C:k=>k-273,
  fmtC:t=>(t<0?'−':'')+Math.abs(t).toFixed(0)+' °C',
  ease:(v,t,dt,r=3)=>v+(t-v)*Math.min(1,dt*r)};

// ---------- Loop 1 and 2: a box of gas. Temperature is the average kinetic energy; thermal energy is the total.
SIMS.a2_particles=(host,o)=>{const {c,side,W,H}=lab(host,800,470),kel=o.mode==='kelvin';
  const BX=24,BY=34,BW=kel?560:520,BH=402;let T=300,N=kel?50:40,tT=300,tN=N,k=0,showC=false;
  const P=[...Array(120)].map(()=>({x:BX+20+Math.random()*(BW-40),y:BY+20+Math.random()*(BH-40),a:Math.random()*7,s:A2.ray()}));
  let sT,sN,tick;
  if(kel){sT=slider(side,'Temperature',0,500,5,300,x=>x+' K',x=>{tT=x});
    side.append(el('div','note','The thermometer only reads kelvin. Convert first: K = °C + 273.'));
    tick=missions(side,[
      {t:'Set the gas to <b>77 °C</b>.',ok:s=>s.T===350,d:'77 + 273 = 350 K.'},
      {t:'Set the gas to <b>−73 °C</b>.',ok:s=>s.T===200,d:'−73 + 273 = 200 K.'},
      {t:'Make every particle <b>stop</b>.',ok:s=>s.T===0,d:'0 K = −273 °C: absolute zero. The particles have no kinetic energy left to lose. Nothing can be colder.'}],()=>({T:tT}))}
  else{sT=slider(side,'Temperature',0,600,10,300,x=>x+' K',x=>{tT=x});sN=slider(side,'Number of particles',10,120,10,40,x=>x,x=>{tN=x});
    tick=missions(side,[
      {t:'Double the thermal energy. Keep the temperature at <b>300 K</b>.',ok:s=>s.T===300&&s.N===80,d:'Twice the particles, each with the same average energy. The temperature did not change.'},
      {t:'Double the thermal energy with only <b>40 particles</b>.',ok:s=>s.N===40&&s.T===600,d:'Each particle now has twice the kinetic energy on average. Twice the kelvin temperature.'},
      {t:'Make it <b>hotter</b> than 300 K but with <b>less</b> thermal energy than 120 units.',ok:s=>s.T>300&&s.N*s.T/100<120,d:'Like a spark from a sparkler: very hot, but so few particles that it holds little energy.'}],()=>({T:tT,N:tN}))}
  const out=el('div','read');side.append(out);
  const caps=kel?['This box of gas has a thermometer that reads in <b>kelvin</b>, K. It is at 300 K now.',
      'Cool it down. The particles slow. Thermal energy is leaving the gas.',
      'At <b>0 K</b> every particle has stopped. This is <b>absolute zero</b>. Nothing can be colder.',
      'A kelvin is the same size as a degree Celsius. Only the zero is different: 0 K is −273 °C and 273 K is 0 °C.','']
    :['A box of gas. Every particle moves in a random direction at its own speed.',
      'Colour shows speed: <b class="cy">blue</b> is slow, <b class="pk">pink</b> is fast. There is always a spread of speeds.',
      '<b class="hl">Temperature</b> measures the <b>average</b> kinetic energy of the particles. Double the kelvin temperature: double the average.',
      '<b class="hl">Thermal energy</b> is the <b>total</b> random kinetic and potential energy of all the particles. In a gas it is nearly all kinetic.',
      'Twice the particles at the same temperature: the same average, twice the total.',''];
  const stage=stager(host,side,caps,q=>{k=q;showC=kel&&q===3;const last=q===caps.length-1;
    if(kel)tT=[300,100,0,273,300][q];else{tT=[300,300,600,300,300,300][q];tN=q===4?80:40}
    if(last){sT.value=300;sT.oninput();if(sN){sN.value=40;sN.oninput()}}});
  loop(host,dt=>{const q=stage();if(q===caps.length-1)tick(dt);
    T=Math.abs(tT-T)<.5?tT:A2.ease(T,tT,dt);N=tN;const sp=Math.sqrt(Math.max(0,T)/300);
    c.clearRect(0,0,W,H);c.strokeStyle='#3a4790';c.lineWidth=3;c.strokeRect(BX,BY,BW,BH);
    for(let i=0;i<N;i++){const p=P[i];if(Math.random()<dt*.6){p.a=Math.random()*7;p.s=A2.ray()}
      const v=p.s*sp*95;p.x+=Math.cos(p.a)*v*dt;p.y+=Math.sin(p.a)*v*dt;
      if(p.x<BX+7){p.x=BX+7;p.a=Math.PI-p.a}if(p.x>BX+BW-7){p.x=BX+BW-7;p.a=Math.PI-p.a}if(p.y<BY+7){p.y=BY+7;p.a=-p.a}if(p.y>BY+BH-7){p.y=BY+BH-7;p.a=-p.a}
      dot(c,p.x,p.y,6,A2.mix('#7dd3fc','#f472b6',(p.s*sp-.4)/1.4))}
    const avg=T/100,tot=N*T/100;
    if(kel){const x=700,yb=420,yt=60,yk=K=>yb-(yb-yt)*K/500;
      c.fillStyle='#151b3d';c.fillRect(x-14,yt-10,28,yb-yt+20);c.fillStyle='#f87171';c.fillRect(x-7,yk(T),14,yb-yk(T));dot(c,x,yb+10,15,'#f87171');
      for(let K=0;K<=500;K+=50){c.strokeStyle=C.mu;c.lineWidth=1.5;ln(c,x+14,yk(K),x+24,yk(K));txt(c,K+' K',x+30,yk(K)+5,K===0?C.am:C.mu,'600 13px Inter')}
      if(showC)[[0,'−273 °C'],[273,'0 °C'],[373,'100 °C']].forEach(([K,s])=>{c.strokeStyle=C.pk;ln(c,x-24,yk(K),x-14,yk(K));txt(c,s,x-28,yk(K)+5,C.pk,'700 13px Inter','right')});
      if(T<1e-3){c.fillStyle='rgba(7,11,31,.85)';c.fillRect(BX+BW/2-190,BY+BH/2-30,380,46);txt(c,'Every particle has stopped: 0 K',BX+BW/2,BY+BH/2,'#fff','700 22px Space Grotesk','center')}
      out.innerHTML=`Thermometer: <b>${Math.round(T)} K</b>`}
    else{const bars=[[600,'average KE','per particle',avg,6,C.cy,k===2],[700,'thermal','energy (total)',tot,720,C.am,k===3||k===4]];
      bars.forEach(([x,a,b,v,mx,col,hi])=>{const h=330*v/mx;c.fillStyle='#151b3d';c.fillRect(x-30,70,60,330);c.fillStyle=col;c.fillRect(x-30,400-h,60,h);
        if(hi){c.strokeStyle='#fff';c.lineWidth=3;c.strokeRect(x-32,68,64,334)}
        txt(c,v.toFixed(1),x,60,col,'700 16px Inter','center');txt(c,a,x,424,C.mu,'600 13px Inter','center');txt(c,b,x,442,C.mu,'600 13px Inter','center')});
      out.innerHTML=`Temperature <b>${Math.round(T)} K</b><br>Average KE <b>${avg.toFixed(1)} units</b> per particle<br>Thermal energy <b>${N} × ${avg.toFixed(1)} = ${tot.toFixed(0)} units</b>`}})};

// ---------- Loop 3: two blocks touching. Conduction until thermal equilibrium.
SIMS.a2_contact=host=>{const {c,side,W,H}=lab(host,800,470);
  const KC={cu:[2,'Copper strip','#f59e0b'],gl:[.12,'Glass','#7dd3fc'],air:[.02,'Air gap','#33407a']};
  let T1=80,T2=20,v1=80,v2=20,m1=1,m2=1,con='cu',touch=false,t=0,teq=null,hist=[],start=[80,20],k=0,pk=[];
  const reset=()=>{touch=false;t=0;teq=null;hist=[];pk=[];T1=v1;T2=v2;start=[T1,T2]};
  const s1=slider(side,'Left block',0,100,5,80,x=>x+' °C',x=>{v1=x;reset()}),s2=slider(side,'Right block',0,100,5,20,x=>x+' °C',x=>{v2=x;reset()});
  slider(side,'Left mass',1,3,.5,1,x=>x.toFixed(1)+' kg',x=>{m1=x;reset()});slider(side,'Right mass',1,3,.5,1,x=>x.toFixed(1)+' kg',x=>{m2=x;reset()});
  const ch=choice(side,'Between the blocks',[['cu','Copper strip'],['gl','Glass'],['air','Air gap']],'cu',q=>{con=q;reset()});
  const bt=el('div','btns');side.append(bt);const go=el('button','btn','Touch');go.onclick=()=>{reset();touch=true};const rs=el('button','btn alt','Separate');rs.onclick=reset;bt.append(go,rs);
  const tick=missions(side,[
    {t:'Touch them. Wait until heat stops flowing.',ok:s=>s.eq,d:'Same temperature on both sides: <b>thermal equilibrium</b>. No more heat flows.'},
    {t:'Make heat flow from <b>right to left</b>, with a difference of 10 °C or more.',ok:s=>s.touch&&s.s2-s.s1>=10,d:'Heat always flows from hotter to colder, whichever side that is.'},
    {t:'Reach equilibrium in <b>under 5 s</b>, starting 60 °C apart or more.',ok:s=>s.eq&&s.teq<5&&s.gap>=60,d:'A good conductor between them makes the flow fast.'},
    {t:'Make both blocks end at exactly <b>60 °C</b>, starting at least 20 °C apart.',ok:s=>s.eq&&Math.abs(s.T1-60)<.3&&s.gap>=20,d:'The bigger block changes temperature less. It takes more energy to change it.'}],
    ()=>({eq:touch&&teq!==null,touch,T1,T2,teq,s1:start[0],s2:start[1],gap:Math.abs(start[0]-start[1])}));
  const out={};
  const stage=stager(host,side,['Two blocks of the same metal. The left one is at 80 °C, the right one at 20 °C. They are not touching.',
    'The particles in the hot block vibrate harder. Colour shows temperature: <b class="cy">blue</b> cold, <b class="pk">pink</b> hot.',
    'Touch them. At the join, hard-vibrating particles jostle their neighbours and pass energy on. This is <b class="hl">conduction</b>.',
    'The energy that flows is <b class="hl">heat</b>. It flows from hot to cold until both are at the same temperature: <b>thermal equilibrium</b>.',
    'Now put an air gap between them. Air is an <b>insulator</b>: the heat crawls across. Metal is a <b>conductor</b>.',''],
    q=>{k=q;$$('input',side).forEach((i,n)=>{i.value=[80,20,1,1][n];i.oninput()});
      con=q===4?'air':'cu';$$('.pill',ch).forEach((p,i)=>p.classList.toggle('on',i===(q===4?2:0)));reset();touch=q>=2&&q<5});
  const col=Tc=>A2.mix('#7dd3fc','#f472b6',Tc/100);
  loop(host,dt=>{const q=stage();if(q===5)tick(dt);
    if(touch){const n=4,h=dt/n;for(let i=0;i<n;i++){const f=KC[con][0]*(T1-T2);T1-=f*h/m1;T2+=f*h/m2}t+=dt;
      if(teq===null&&Math.abs(T1-T2)<.5)teq=t;if(hist.length===0||t-hist[hist.length-1][0]>.1)hist.push([t,T1,T2])}
    c.clearRect(0,0,W,H);const S=24,R=7,Y0=62,gapw=touch?26:80,cx=400,c1=Math.round(3*m1),c2=Math.round(3*m2);
    const blk=(x0,cols,Tc,dir)=>{for(let i=0;i<cols;i++)for(let j=0;j<R;j++){const a=1.6*Math.sqrt(A2.K(Tc)/273)*(.6+Tc/60);
      const x=x0+dir*(i*S+S/2)+(Math.random()-.5)*a*2,y=Y0+j*S+S/2+(Math.random()-.5)*a*2;dot(c,x,y,7.5,col(Tc))}};
    blk(cx-gapw/2,c1,T1,-1);blk(cx+gapw/2,c2,T2,1);
    c.fillStyle=KC[con][2];if(con!=='air'||!touch)c.globalAlpha=touch?.9:.35;const sw=touch?gapw-8:26;c.fillRect(cx-sw/2,Y0,sw,R*S);c.globalAlpha=1;
    txt(c,KC[con][1],cx,Y0+R*S+40,C.mu,'600 13px Inter','center');
    txt(c,T1.toFixed(1)+' °C',cx-gapw/2-c1*S/2,Y0-12,col(T1),'700 18px Inter','center');txt(c,T2.toFixed(1)+' °C',cx+gapw/2+c2*S/2,Y0-12,col(T2),'700 18px Inter','center');
    txt(c,m1.toFixed(1)+' kg',cx-gapw/2-c1*S/2,Y0+R*S+20,C.mu,'600 13px Inter','center');txt(c,m2.toFixed(1)+' kg',cx+gapw/2+c2*S/2,Y0+R*S+20,C.mu,'600 13px Inter','center');
    const f=touch?KC[con][0]*(T1-T2):0;
    if(touch&&Math.abs(f)>.02){if(Math.random()<Math.min(1,Math.abs(f)*dt*1.5))pk.push({x:f>0?cx-60:cx+60,y:Y0+Math.random()*R*S,d:Math.sign(f)});
      pk.forEach(p=>p.x+=p.d*90*dt);pk=pk.filter(p=>Math.abs(p.x-cx)<62);pk.forEach(p=>dot(c,p.x,p.y,4,C.am));
      txt(c,f>0?'heat →':'← heat',cx,Y0+R*S+62,C.am,'700 16px Inter','center')}else pk=[];
    // temperature against time
    const gx=70,gy=310,gw=700,gh=130,tm=Math.max(10,A2.nice(Math.max(t,teq||0)*1.1||10)),X=s=>gx+gw*s/tm,Yt=v=>gy+gh-gh*v/100;
    c.strokeStyle='#1e2858';c.lineWidth=1;for(let v=0;v<=100;v+=20){ln(c,gx,Yt(v),gx+gw,Yt(v));txt(c,v+' °C',gx-8,Yt(v)+4,C.mu,'600 12px Inter','right')}
    for(let i=0;i<=10;i++){ln(c,X(i*tm/10),gy,X(i*tm/10),gy+gh);txt(c,+(i*tm/10).toFixed(1)+(i===10?' s':''),X(i*tm/10),gy+gh+16,C.mu,'600 12px Inter','center')}
    [[1,col(start[0]>start[1]?100:0)],[2,col(start[1]>start[0]?100:0)]].forEach(([j])=>{c.beginPath();hist.forEach(([s,a,b],i)=>{const y=Yt(j===1?a:b);i?c.lineTo(X(s),y):c.moveTo(X(s),y)});c.strokeStyle=j===1?C.am:C.cy;c.lineWidth=3;c.stroke()});
    txt(c,'left',gx+6,gy+14,C.am,'700 13px Inter');txt(c,'right',gx+46,gy+14,C.cy,'700 13px Inter');
    txt(c,touch?(teq!==null?`Thermal equilibrium after ${teq.toFixed(1)} s. Both at ${((T1*m1+T2*m2)/(m1+m2)).toFixed(1)} °C.`:`Touching for ${t.toFixed(1)} s. Heat is flowing.`):'Not touching. No heat flows.',cx,22,teq!==null&&touch?C.gr:'#fff','700 15px Inter','center')})};

// ---------- Loop 5: evaporative cooling. The fastest particles escape the surface.
SIMS.a2_evap=host=>{const {c,side,W,H}=lab(host,800,470);
  const L={x0:60,x1:500,top:96,surf:216,bot:440},NE=1150,ESC=980,ROOM=295,NP=80;let T=343,lid=true,wind=false,esc=0,k=0,P=[],V=[];
  const newP=()=>({x:L.x0+10+Math.random()*(L.x1-L.x0-20),y:L.surf+10+Math.random()*(L.bot-L.surf-20),a:Math.random()*7,e:A2.expo(T)});
  const fill=()=>{T=343;esc=0;P=[...Array(NP)].map(newP);V=[]};fill();
  const lp=choice(side,'Lid',[[1,'On'],[0,'Off']],1,q=>lid=!!q),wp=choice(side,'Breeze',[[0,'Off'],[1,'On']],0,q=>wind=!!q);
  const bt=el('div','btns');side.append(bt);const rf=el('button','btn alt','Fresh hot drink');rf.onclick=fill;bt.append(rf);
  const tick=missions(side,[
    {t:'Take the lid off. Watch which particles leave.',ok:s=>!s.lid&&s.esc>=5,d:'Only fast particles at the surface escape. Each one takes a lot of energy with it.'},
    {t:'Cool the drink below <b>50 °C</b>.',ok:s=>s.T<323,d:'A breeze carries the vapour away, so escaped particles cannot fall back in.'},
    {t:'Stop the evaporative cooling.',ok:s=>s.lid,d:'Nothing escapes, so no evaporative cooling. It still cools slowly by conduction and radiation.'}],()=>({lid,esc,T}));
  const out=el('div','read');side.append(out);
  const setP=(d,i)=>$$('.pill',d).forEach((p,j)=>p.classList.toggle('on',j===i));
  const stage=stager(host,side,['A hot drink at 70 °C with a lid on. Each dot is one water particle.',
    'Colour shows kinetic energy. Most particles are in the middle. A few are very fast: <b class="pk">pink</b>.',
    'Lid off. A fast particle that reaches the surface can break free. It <b class="hl">evaporates</b>.',
    'Each escape removes one of the most energetic particles. The <b>average</b> left behind drops, so the <b>temperature</b> drops.',
    'A breeze sweeps the vapour away before it can fall back in. The drink cools faster.',''],
    q=>{k=q;lid=q<2||q===5;wind=q===4;if(q===0||q===5)fill();setP(lp,lid?0:1);setP(wp,wind?1:0)});
  loop(host,dt=>{const q=stage();if(q===5)tick(dt);
    // collisions share energy between pairs: keeps a spread of energies with the right average
    for(let i=0;i<NP/3;i++){const a=P[Math.random()*NP|0],b=P[Math.random()*NP|0],s=a.e+b.e,u=Math.random();a.e=u*s;b.e=s-a.e}
    const m=P.reduce((s,p)=>s+p.e,0)/NP;P.forEach(p=>p.e*=T/m);
    T-=(.0016+(wind?.004:0))*(T-ROOM)*dt;   // exchange with the room: conduction and radiation, plus forced convection in a breeze
    // escapes also need (T/343)^12: water's vapour pressure falls about 12 times from 70 °C to 22 °C
    P.forEach((p,i)=>{const v=Math.sqrt(p.e)*4.5;p.x+=Math.cos(p.a)*v*dt;p.y+=Math.sin(p.a)*v*dt;
      if(p.x<L.x0+6){p.x=L.x0+6;p.a=Math.PI-p.a}if(p.x>L.x1-6){p.x=L.x1-6;p.a=Math.PI-p.a}if(p.y>L.bot-6){p.y=L.bot-6;p.a=-p.a}
      if(p.y<L.surf+4){if(!lid&&p.e>ESC&&Math.sin(p.a)<0&&Math.random()<(T/343)**12){V.push({x:p.x,y:L.surf-8,e:p.e,vx:0,vy:-60});T-=(p.e-T)/NE;esc++;P[i]=newP()}else{p.y=L.surf+4;p.a=-p.a}}});
    V.forEach(v=>{v.vx+=((wind?260:0)-v.vx)*dt*2+(Math.random()-.5)*80*dt;v.vy+=(Math.random()-.5)*90*dt;v.x+=v.vx*dt;v.y+=v.vy*dt;
      if(lid&&v.y<L.top+6){v.y=L.top+6;v.vy=Math.abs(v.vy)}
      if(!wind&&Math.random()<dt*.35)v.vy=Math.abs(v.vy)+20;          // some vapour drifts back down
      if(v.vy>0&&v.y>=L.surf&&v.x>L.x0&&v.x<L.x1){T+=(v.e-T)/NE;v.gone=1}});
    V=V.filter(v=>!v.gone&&v.y>-10&&v.x<W+10&&v.x>-10);
    c.clearRect(0,0,W,H);
    c.fillStyle='rgba(125,211,252,.08)';c.fillRect(L.x0,L.surf,L.x1-L.x0,L.bot-L.surf);c.strokeStyle='#5b6aa8';c.lineWidth=4;
    c.beginPath();c.moveTo(L.x0-4,L.top);c.lineTo(L.x0-4,L.bot+4);c.lineTo(L.x1+4,L.bot+4);c.lineTo(L.x1+4,L.top);c.stroke();
    c.lineWidth=1.5;c.setLineDash([4,5]);ln(c,L.x0,L.surf,L.x1,L.surf);c.setLineDash([]);txt(c,'surface',L.x1-8,L.surf-6,C.mu,'600 12px Inter','right');
    if(lid){c.fillStyle='#94a3c8';c.fillRect(L.x0-14,L.top-10,L.x1-L.x0+28,10)}
    if(wind)for(let i=0;i<5;i++){const y=40+i*12,x=((performance.now()/4+i*150)%900)-100;c.strokeStyle='rgba(148,163,200,.5)';c.lineWidth=2;ln(c,x,y,x+60,y)}
    P.forEach(p=>dot(c,p.x,p.y,5.5,p.e>ESC?C.pk:A2.mix('#3b82f6','#fbb040',p.e/700)));V.forEach(v=>dot(c,v.x,v.y,5.5,C.pk));
    // spread of energies, with the escape energy marked
    const hx=560,hy=330,hw=210,hh=180,em=1500,X=e=>hx+hw*e/em;c.fillStyle='#151b3d';c.fillRect(hx-6,hy-hh-24,hw+16,hh+60);
    c.beginPath();c.moveTo(X(0),hy);for(let e=0;e<=em;e+=20)c.lineTo(X(e),hy-hh*.9*Math.exp(-e/T)*343/T);c.lineTo(X(em),hy);c.closePath();c.fillStyle='rgba(125,211,252,.35)';c.fill();
    c.save();c.beginPath();c.rect(X(ESC),hy-hh,hw,hh);c.clip();c.beginPath();c.moveTo(X(ESC),hy);for(let e=ESC;e<=em;e+=20)c.lineTo(X(e),hy-hh*.9*Math.exp(-e/T)*343/T);c.lineTo(X(em),hy);c.closePath();c.fillStyle=C.pk;c.fill();c.restore();
    c.strokeStyle=C.pk;c.lineWidth=2;ln(c,X(ESC),hy-hh,X(ESC),hy);txt(c,'fast enough',X(ESC)+4,hy-hh+12,C.pk,'700 12px Inter');txt(c,'to escape',X(ESC)+4,hy-hh+26,C.pk,'700 12px Inter');
    txt(c,'kinetic energy →',hx+hw,hy+16,C.mu,'600 12px Inter','right');txt(c,'how many particles',hx,hy-hh-8,C.mu,'600 12px Inter');
    txt(c,(T-273).toFixed(1)+' °C',hx+hw/2,hy+48,'#fff','700 26px Space Grotesk','center');
    out.innerHTML=`Drink: <b>${(T-273).toFixed(1)} °C</b> · room 22 °C<br>Particles escaped: <b>${esc}</b>`})};

// ---------- Loops 6 and 7: a heater of known power. Read c or L off the graph.
A2.axis=mx=>{const st=A2.nice(mx/8);return{tm:Math.ceil(mx/st-1e-9)*st,st}};
SIMS.a2_heat=(host,o)=>{const {c,cv,side,W,H}=lab(host,800,470),curve=o.mode==='curve';
  const MAT={w:[4190,'Water'],al:[890,'Aluminium'],cu:[385,'Copper']},MYS=[[800,'window glass'],[850,'household bricks'],[880,'concrete'],[890,'aluminium'],[385,'copper']];
  let Pw=1000,m=1,mat='w',mys=pick(MYS),tr=[],k=0,cur=[0,0],drawn=0,j=0,A=[],res=null;
  const G={x:84,y:30,w:690,h:380};
  // water heated from ice at -20 C: warm ice, melt, warm water, boil, steam to 120 C (steam c = 2010 J/(kg K), standard value)
  const phases=()=>{let t=0;return[[2093,-20,0],[0,0,0,334000],[4190,0,100],[0,100,100,2256000],[2010,100,120]].map(([cc,a,b,Lh])=>{const d=Lh?m*Lh/Pw:m*cc*(b-a)/Pw,p={t0:t,t1:t+d,a,b};t+=d;return p})};
  const Tat=(tt,ph)=>{for(const p of ph)if(tt<=p.t1)return p.a+(p.b-p.a)*(tt-p.t0)/Math.max(1e-9,p.t1-p.t0);return ph[ph.length-1].b};
  const sP=slider(side,'Heater power',500,2000,100,1000,x=>x+' W',x=>{Pw=x;if(curve)fresh()}),sM=slider(side,curve?'Mass of ice':'Mass',.5,2,.1,1,x=>x.toFixed(1)+' kg',x=>{m=x;if(curve)fresh()});
  const ch=curve?null:choice(side,'Material',[['w','Water'],['al','Aluminium'],['cu','Copper'],['my','Mystery']],'w',q=>mat=q);
  if(!curve){const bt=el('div','btns');side.append(bt);const hb=el('button','btn','Heat it'),cl=el('button','btn alt','Clear graph');bt.append(hb,cl);
    hb.onclick=()=>{const cc=mat==='my'?mys[0]:MAT[mat][0];tr.push({c:cc,P:Pw,m,mys:mat==='my',name:mat==='my'?'Mystery':MAT[mat][1],t:0,tend:m*cc*70/Pw});if(tr.length>3)tr.shift()};cl.onclick=()=>tr=[]}
  const box=el('div','a2w');side.append(box);box.append(el('div','muted',curve?'Drag the two orange rulers. Nothing is given.':'Heat the mystery block. Read the graph. Nothing is given.'));
  A=curve?[ask(box,'$L_{\\text{fusion}}$','J/kg',()=>334000*1,.06),ask(box,'$c_{\\text{water}}$','J/(kg K)',()=>4190,.08),ask(box,'$L_{\\text{vap}}$','J/kg',()=>2256000,.06)]
    :[ask(box,'gradient','K/s',()=>{const t=tr.filter(x=>x.mys).pop();return t?t.P/(t.m*t.c):NaN},.08),ask(box,'$c$','J/(kg K)',()=>mys[0],.08)];
  const nb=el('div','btns');side.append(nb);res=el('div','read');
  if(!curve){const nw=el('button','btn alt','New mystery');nw.onclick=()=>{mys=pick(MYS);tr=tr.filter(x=>!x.mys);A.forEach(a=>a.clear());res.innerHTML=''};nb.append(nw)}
  const sa=el('button','btn alt','Show answers');nb.append(sa);side.append(res);
  sa.onclick=()=>{if(!curve&&!tr.some(x=>x.mys)){res.innerHTML='Heat the mystery block first.';return}A.forEach(a=>a.show());
    res.innerHTML=mx(curve?'Water, Tables 2A-3 and 2A-4: <b>334 kJ/kg</b>, <b>4190 J/(kg K)</b>, <b>2256 kJ/kg</b>.':`$c = \\dfrac{P}{m \\times \\text{gradient}}$. The mystery is <b>${mys[0]} J/(kg K)</b>: ${mys[1]} in Table 2A-3.`)};
  function fresh(){drawn=0;A.forEach(a=>a.clear());if(res)res.innerHTML=''}
  const out=el('div','read');side.append(out);
  const caps=curve?['1.0 kg of ice at −20 °C on a 1000 W heater: 1000 J every second. No heat escapes.',
      'The ice warms. The graph slopes up: $Q = mc\\Delta T$.',
      'At 0 °C the graph goes <b>flat</b>. The ice is melting. The energy breaks bonds, so the temperature does not change: $Q = mL$.',
      'All melted. The water warms. It slopes less steeply than the ice did: water has a higher $c$.',
      'At 100 °C it goes flat again while the water boils. This flat part is the longest: $L$ for boiling is almost 7 times $L$ for melting.',
      'The two orange rulers measure time. Put them at the ends of a flat part, then:<br>$L = \\dfrac{Pt}{m}$','']
    :['A 1.0 kg block on a 1000 W heater: 1000 J every second. No heat escapes. It starts at 20 °C and stops at 90 °C.',
      'Water first. The temperature climbs slowly.',
      'Same heater, same mass, copper. It warms about 11 times faster.',
      'The <b>gradient</b> is the temperature rise each second. A low $c$ means a steep graph.',
      'Put $Q = Pt$ into $Q = mc\\Delta T$ and rearrange:<br>$c = \\dfrac{P}{m \\times \\text{gradient}}$<br>Practical 2A-2 uses this method.',''];
  const last=caps.length-1;
  const stage=stager(host,side,caps,q=>{k=q;sP.value=1000;sM.value=1;sP.oninput();sM.oninput();
    if(curve){const ph=phases();drawn=q===0?0:q===5?ph[4].t1:q===last?0:Math.min(drawn,[0,ph[0].t1,ph[1].t1,ph[2].t1,ph[4].t1][q]);cur=q===5?[ph[1].t0,ph[1].t1]:q===last?[300,1500]:[0,0]}
    else{tr=[];if(q>=1&&q<last)tr.push({c:4190,P:1000,m:1,name:'Water',t:q===1?0:1e9,tend:1*4190*70/1000});if(q>=2&&q<last)tr.push({c:385,P:1000,m:1,name:'Copper',t:q===2?0:1e9,tend:1*385*70/1000});
      if(q===last){mat='w';$$('.pill',ch).forEach((p,i)=>p.classList.toggle('on',i===0))}}});
  let tmNow=1;
  drag(cv,W,(x,y,down)=>{if(!curve||k<last)return;const tt=Math.max(0,Math.min(tmNow,(x-G.x)/G.w*tmNow));if(down)j=Math.abs(tt-cur[0])<=Math.abs(tt-cur[1])?0:1;cur[j]=Math.round(tt)});
  loop(host,dt=>{const q=stage();c.clearRect(0,0,W,H);let ax,ymin,ymax,ph,tot;
    if(curve){ph=phases();tot=ph[4].t1;ax=A2.axis(tot*1.02);ymin=-40;ymax=140;
      const goal=q>=1&&q<=4?[0,ph[0].t1,ph[1].t1,ph[2].t1,ph[4].t1][q]:tot;if(q>0)drawn=Math.min(goal,drawn+tot/(q<5?2.5:7)*dt)}
    else{ax=A2.axis(Math.max(60,...tr.map(x=>x.tend))*1.05);ymin=0;ymax=100;tr.forEach(x=>x.t=Math.min(x.tend,x.t+ax.tm/5*dt))}
    const tm=tmNow=ax.tm,X=s=>G.x+G.w*s/tm,Y=v=>G.y+G.h-G.h*(v-ymin)/(ymax-ymin);
    c.lineWidth=1;for(let v=ymin;v<=ymax;v+=10){c.strokeStyle=v%20===0?'#28336e':'#1a2350';ln(c,G.x,Y(v),G.x+G.w,Y(v));if(v%20===0)txt(c,(v<0?'−'+(-v):v)+' °C',G.x-8,Y(v)+4,C.mu,'600 12px Inter','right')}
    for(let i=0;i*ax.st/2<=tm+1e-9;i++){const s=i*ax.st/2;c.strokeStyle=i%2?'#1a2350':'#28336e';ln(c,X(s),G.y,X(s),G.y+G.h);if(i%2===0)txt(c,+s.toPrecision(6)+(s+ax.st/2>tm+1e-9?' s':''),X(s),G.y+G.h+18,C.mu,'600 12px Inter','center')}
    c.strokeStyle='#5b6aa8';c.lineWidth=2;ln(c,G.x,Y(0),G.x+G.w,Y(0));txt(c,'time',G.x+G.w,G.y+G.h+36,C.mu,'600 12px Inter','right');
    if(curve){c.beginPath();c.moveTo(X(0),Y(-20));ph.forEach(p=>{if(drawn>p.t0)c.lineTo(X(Math.min(drawn,p.t1)),Y(Tat(Math.min(drawn,p.t1),ph)))});c.strokeStyle=C.cy;c.lineWidth=3.5;c.stroke();
      if(q<last)[['ice'],['melting'],['water'],['boiling'],['steam']].forEach(([s],i)=>{const p=ph[i];if(drawn>=p.t1-1e-6)txt(c,s,X((p.t0+p.t1)/2)+(i===0?22:0),Y((p.a+p.b)/2)+(i===0?16:-14),i%2?C.am:C.cy,'700 14px Inter','center')});
      if(q>=5){cur.forEach((tt,i)=>{c.strokeStyle=C.am;c.lineWidth=2;ln(c,X(tt),G.y,X(tt),G.y+G.h);c.fillStyle=C.am;c.fillRect(X(tt)-9,G.y-12,18,12);txt(c,tt.toFixed(0)+' s',X(tt)+(i?6:-6),G.y+18+i*18,C.am,'700 13px Inter',i?'left':'right')});
        out.innerHTML=`Heater <b>${Pw} W</b> · ice <b>${m.toFixed(1)} kg</b><br>Rulers <b>${Math.abs(cur[1]-cur[0]).toFixed(0)} s</b> apart`}
      else out.innerHTML=`Heater <b>${Pw} W</b> · ice <b>${m.toFixed(1)} kg</b>`}
    else{tr.forEach((x,i)=>{const col=x.mys?C.pk:x.c===4190?C.cy:x.c===385?C.am:C.gr;c.globalAlpha=i<tr.length-1?.5:1;c.beginPath();c.moveTo(X(0),Y(20));c.lineTo(X(x.t),Y(20+x.P*x.t/(x.m*x.c)));c.strokeStyle=col;c.lineWidth=3.5;c.stroke();
        if(x.t>=x.tend)txt(c,`${x.name}, ${x.m.toFixed(1)} kg, ${x.P} W`,Math.min(X(x.t)+8,G.x+G.w-200),Y(92)-16*i,col,'700 13px Inter');c.globalAlpha=1});
      if(q===3&&tr[0]){const x=tr[0],t1=200,y1=20+x.P*t1/(x.m*x.c);c.strokeStyle=C.pk;c.lineWidth=2;c.setLineDash([5,5]);ln(c,X(0),Y(20),X(t1),Y(20));ln(c,X(t1),Y(20),X(t1),Y(y1));c.setLineDash([]);
        txt(c,'rise',X(t1)+8,Y((20+y1)/2)+5,C.pk,'700 15px Inter');txt(c,'run',X(t1/2),Y(20)+20,C.pk,'700 15px Inter','center')}
      out.innerHTML=`Heater <b>${Pw} W</b> · mass <b>${m.toFixed(1)} kg</b> · ${mat==='my'?'mystery':MAT[mat][1].toLowerCase()}`}})};
