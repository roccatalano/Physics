// Shared shell for Physics interactives: stage scaling, animation clock, background waves, helpers.
const NS='http://www.w3.org/2000/svg';
function el(tag,attrs,parent){const e=document.createElementNS(NS,tag);for(const k in attrs||{})e.setAttribute(k,attrs[k]);if(parent)parent.appendChild(e);return e}
function txt(svg,x,y,s,attrs){const t=el('text',Object.assign({x,y,fill:'#eef2ff','font-size':18,'font-weight':600},attrs||{}),svg);t.textContent=s;return t}
function fit(){const s=document.getElementById('stage'),k=Math.min(innerWidth/1280,innerHeight/720);s.style.transform=`translate(-50%,-50%) scale(${k})`}
addEventListener('resize',fit);fit();
if(/[?&]bare\b/.test(location.search))document.body.classList.add('bare');
// clock: play/pause and speed apply to every animation
const IX={t:0,play:true,speed:1,anims:[],last:performance.now()};
function loop(now){const dt=Math.min(.1,(now-IX.last)/1000);IX.last=now;if(IX.play)IX.t+=dt*IX.speed;IX.anims.forEach(f=>f(IX.t,dt));requestAnimationFrame(loop)}
requestAnimationFrame(loop);
// background per Area of Study (body data-bg): waves | nuclear | circuit | motion. Faint and slow.
(()=>{const bg=document.getElementById('bg');if(!bg)return;const kind=document.body.dataset.bg||'waves',fr=[];const t0=performance.now();
 if(kind==='waves'){const bl=[['#7dd3fc',.08,38,520,.05,650],['#fbb040',.06,28,380,-.04,676],['#7dd3fc',.05,22,300,.03,700]].map(([c,o,a,l,s,y])=>[el('path',{fill:'none',stroke:c,'stroke-opacity':o,'stroke-width':3},bg),a,l,s,y]);
  fr.push(t=>bl.forEach(([p,a,l,s,y])=>{let d='';for(let x=0;x<=1280;x+=10)d+=(x?'L':'M')+x+','+(y-a*Math.sin(2*Math.PI*(x/l-t*s))).toFixed(1);p.setAttribute('d',d)}))}
 if(kind==='nuclear'){let seed=7;const R=()=>(seed=(seed*16807)%2147483647)/2147483647;
  const ps=[...Array(26)].map(()=>({x:R()*1280,y:R()*720,vx:(R()-.5)*14,vy:(R()-.5)*14,r:3+R()*5,c:R()<.5?'#7dd3fc':'#fbb040',ph:R()*40,e:el('circle',{fill:'none','stroke-width':2},bg),f:el('circle',{fill:'none','stroke-width':2},bg),d:el('circle',{r:2.5},bg)}));
  fr.push(t=>ps.forEach(p=>{const x=((p.x+p.vx*t)%1280+1280)%1280,y=((p.y+p.vy*t)%720+720)%720,c=((t+p.ph)%40)/40;
   p.e.setAttribute('cx',x);p.e.setAttribute('cy',y);p.e.setAttribute('r',p.r);p.e.setAttribute('stroke',p.c);p.e.setAttribute('stroke-opacity',.1);
   const fl=c>.95?(c-.95)/.05:0;p.f.setAttribute('cx',x);p.f.setAttribute('cy',y);p.f.setAttribute('r',p.r+fl*40);p.f.setAttribute('stroke',p.c);p.f.setAttribute('stroke-opacity',fl?.18*(1-fl):0);
   p.d.setAttribute('cx',x+fl*60);p.d.setAttribute('cy',y-fl*35);p.d.setAttribute('fill',p.c);p.d.setAttribute('fill-opacity',fl?.25*(1-fl):0)}))}
 if(kind==='circuit'){const paths=['M0 600H260V650H560V610H900V660H1280','M0 690H140V640H420V700H760V630H1060V680H1280','M120 720V560H380V520H700V570H1000V530H1280','M0 560H200V520H500'];
  const ps=paths.map(d=>{const p=el('path',{d,fill:'none',stroke:'#7dd3fc','stroke-opacity':.07,'stroke-width':3},bg);return{p,L:p.getTotalLength(),dots:[0,1,2].map(()=>el('circle',{r:4,fill:'#fbb040','fill-opacity':.22},bg))}});
  [[260,600],[560,650],[900,660],[420,640],[760,700],[380,520],[700,570],[200,520]].forEach(([x,y])=>el('circle',{cx:x,cy:y,r:6,fill:'none',stroke:'#7dd3fc','stroke-opacity':.1,'stroke-width':2},bg));
  fr.push(t=>ps.forEach(({p,L,dots},i)=>dots.forEach((c,k)=>{const s=((t*60+k*L/3+i*90)%L),pt=p.getPointAtLength(s);c.setAttribute('cx',pt.x);c.setAttribute('cy',pt.y)})))}
 if(kind==='motion'){const arcs=[[-40,700,90,520,.10],[300,720,70,420,.07],[640,710,80,470,.09],[900,730,60,380,.06]].map(([x0,y0,h,w,o])=>{const d=[...Array(41)].map((_,i)=>{const u=i/40;return(i?'L':'M')+(x0+u*w).toFixed(1)+','+(y0-4*h*u*(1-u)).toFixed(1)}).join('');
   return{x0,y0,h,w,p:el('path',{d,fill:'none',stroke:'#7dd3fc','stroke-opacity':o,'stroke-width':3,'stroke-dasharray':'2 10','stroke-linecap':'round'},bg),c:el('circle',{r:6,fill:'#fbb040','fill-opacity':.22},bg)}});
  fr.push(t=>arcs.forEach((a,i)=>{const u=((t*.08+i*.27)%1);a.c.setAttribute('cx',a.x0+u*a.w);a.c.setAttribute('cy',a.y0-4*a.h*u*(1-u))}))}
 if(kind==='fields'){const cs=[[300,640,1],[980,660,-1]];const ls=[];for(let k=0;k<14;k++){const a=k/14*2*Math.PI;ls.push(el('path',{fill:'none',stroke:'#7dd3fc','stroke-opacity':.07,'stroke-width':2.5},bg))}
  cs.forEach(([x,y,q])=>el('circle',{cx:x,cy:y,r:10,fill:q>0?'#fbb040':'#7dd3fc','fill-opacity':.15},bg));
  const ds=[...Array(10)].map(()=>el('circle',{r:3.5,fill:'#fbb040','fill-opacity':.22},bg));
  const line=a=>{let x=300+14*Math.cos(a),y=640+14*Math.sin(a),pts=[[x,y]];for(let i=0;i<260;i++){let ex=0,ey=0;cs.forEach(([cx,cy,q])=>{const dx=x-cx,dy=y-cy,r=Math.hypot(dx,dy)+1;ex+=q*dx/r**3;ey+=q*dy/r**3});const m=Math.hypot(ex,ey)||1;x+=6*ex/m;y+=6*ey/m;pts.push([x,y]);if(Math.hypot(x-980,y-660)<14||x<-50||x>1330||y<300||y>780)break}return pts};
  const L=ls.map((p,k)=>{const pts=line(k/14*2*Math.PI);p.setAttribute('d',pts.map((q,i)=>(i?'L':'M')+q[0].toFixed(1)+','+q[1].toFixed(1)).join(''));return pts});
  fr.push(t=>ds.forEach((d,i)=>{const pts=L[(i*3)%L.length],u=((t*.05+i*.13)%1),q=pts[Math.floor(u*(pts.length-1))];d.setAttribute('cx',q[0]);d.setAttribute('cy',q[1])}))}
 if(kind==='coils'){const cx=[[200,640,70],[640,690,55],[1080,650,65]].map(([x,y,r])=>({x,y,r,e:el('ellipse',{cx:x,cy:y,ry:r,fill:'none',stroke:'#7dd3fc','stroke-opacity':.09,'stroke-width':3},bg),a:el('line',{x1:x,x2:x,y1:y-r-14,y2:y+r+14,stroke:'#7dd3fc','stroke-opacity':.06,'stroke-width':2},bg)}));
  const sp=el('path',{fill:'none',stroke:'#fbb040','stroke-opacity':.07,'stroke-width':3},bg);
  fr.push(t=>{cx.forEach((c,i)=>c.e.setAttribute('rx',Math.abs(c.r*Math.cos(t*.5+i))+2));let d='';for(let x=0;x<=1280;x+=10)d+=(x?'L':'M')+x+','+(560-30*Math.sin(2*Math.PI*x/640-t*.5)).toFixed(1);sp.setAttribute('d',d)})}
 if(kind==='interference'){const S=[[560,760],[720,760]],rs=[];S.forEach(([x,y],k)=>{for(let i=0;i<9;i++)rs.push([el('circle',{cx:x,cy:y,fill:'none',stroke:k?'#fbb040':'#7dd3fc','stroke-opacity':.06,'stroke-width':2.5},bg),i])});
  fr.push(t=>rs.forEach(([c,i])=>{const r=(i*60+t*14)%540;c.setAttribute('r',r);c.setAttribute('stroke-opacity',.07*(1-r/540))}))}
 (function f(){const t=(performance.now()-t0)/1000;fr.forEach(g=>g(t));requestAnimationFrame(f)})()})();
// slider helper: slider(id, fmt, onchange)
function slider(id,fmt,cb){const r=document.getElementById(id),o=document.getElementById(id+'v');const u=()=>{const v=+r.value;if(o)o.textContent=fmt?fmt(v):v;cb&&cb(v)};r.addEventListener('input',u);u();return r}
// button group: one 'on' at a time
function group(sel,cb){const bs=[...document.querySelectorAll(sel)];bs.forEach(b=>b.onclick=()=>{bs.forEach(x=>x.classList.toggle('on',x===b));cb(b.dataset.v,b)});return bs}
function toggle(id,cb,on){const b=document.getElementById(id);b.classList.toggle('on',!!on);b.onclick=()=>{b.classList.toggle('on');cb(b.classList.contains('on'))};cb(!!on);return b}
const f2=(v,d=2)=>(+v).toFixed(d);
function sig(v,n=3){if(!isFinite(v))return '∞';if(v===0)return '0';const p=Math.floor(Math.log10(Math.abs(v)));const d=Math.max(0,n-1-p);return (+v).toFixed(d)}
// play/pause + slow buttons in the tools bar; space toggles play
(()=>{const t=document.querySelector('.tools');if(!t)return;
 const p=document.createElement('button');p.textContent='❚❚ Pause';p.onclick=()=>{IX.play=!IX.play;p.textContent=IX.play?'❚❚ Pause':'▶ Play'};
 const s=document.createElement('button');s.textContent='Slow motion';s.onclick=()=>{IX.speed=IX.speed===1?.25:1;s.classList.toggle('on',IX.speed!==1)};
 const fs=document.createElement('button');fs.textContent='⛶';fs.title='Full screen';fs.onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
 t.append(p,s,fs);addEventListener('keydown',e=>{if(e.code==='Space'){e.preventDefault();p.click()}if(e.key==='f'||e.key==='F')fs.click()})})();
