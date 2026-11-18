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
// background waves (same as the slide decks)
(()=>{const bg=document.getElementById('bg');if(!bg)return;const bl=[['#7dd3fc',.08,38,520,.05,650],['#fbb040',.06,28,380,-.04,676],['#7dd3fc',.05,22,300,.03,700]].map(([c,o,a,l,s,y])=>[el('path',{fill:'none',stroke:c,'stroke-opacity':o,'stroke-width':3},bg),a,l,s,y]);
 const t0=performance.now();(function f(){const t=(performance.now()-t0)/1000;bl.forEach(([p,a,l,s,y])=>{let d='';for(let x=0;x<=1280;x+=10)d+=(x?'L':'M')+x+','+(y-a*Math.sin(2*Math.PI*(x/l-t*s))).toFixed(1);p.setAttribute('d',d)});requestAnimationFrame(f)})()})();
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
