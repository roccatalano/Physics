// Guided lesson engine. Every slide declares a mode (what students are doing), and the look follows the mode.
const $=(s,e=document)=>e.querySelector(s),$$=(s,e=document)=>[...e.querySelectorAll(s)];
const el=(t,c,h)=>{const e=document.createElement(t);if(c)e.className=c;if(h!=null)e.innerHTML=h;return e};
const pick=a=>a[Math.floor(Math.random()*a.length)];
const mx=s=>String(s).replace(/\$([^$]+)\$/g,(_,t)=>katex.renderToString(t.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&'),{throwOnError:false}));
function mathAll(root){const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),ns=[];
  while(w.nextNode())if(w.currentNode.nodeValue.includes('$'))ns.push(w.currentNode);
  ns.forEach(n=>{const sp=document.createElement('span');sp.innerHTML=mx(n.nodeValue.replace(/&/g,'&amp;').replace(/</g,'&lt;'));n.replaceWith(sp)})}
function num(x,n=3){if(!x)return'0';const e=Math.floor(Math.log10(Math.abs(x))+1e-9);
  if(e<-3||e>4)return (x/10**e).toPrecision(n)+' \\times 10^{'+e+'}';
  if(e>=n){const p=10**(e-n+1);return String(Math.round(x/p)*p)}return x.toPrecision(n)}
const SUP=s=>String(s).replace(/[-0-9]/g,d=>'⁻⁰¹²³⁴⁵⁶⁷⁸⁹'['-0123456789'.indexOf(d)]);
function si(x,unit,n=3){const P=[[12,'T'],[9,'G'],[6,'M'],[3,'k'],[0,''],[-3,'m'],[-6,'μ'],[-9,'n'],[-12,'p'],[-15,'f']];
  const e=Math.log10(x)+1e-9;if(e>=15){const k=Math.floor(e);return +(x/10**k).toPrecision(n)+' × 10'+SUP(k)+' '+unit}
  const p=P.find(p=>e>=p[0])||P[P.length-1];return +(x/10**p[0]).toPrecision(n)+' '+p[1]+unit}
const parseNum=s=>parseFloat(String(s).replace(/\s/g,'').replace(/−/g,'-').replace(/[×x*]10\^?\(?(-?\d+)\)?/i,'e$1'));

const svg=d=>`<svg viewBox="0 0 24 24">${d}</svg>`;
const MODES={
  watch:['Watch','Pens down. Eyes on the screen.',svg('<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>')],
  board:['Whiteboard','Write. Cover. Show on three.',svg('<rect x="3" y="4" width="18" height="13" rx="2"/><path d="M7 13l3-4 3 3 4-5M8 21l2-4M16 21l-2-4"/>')],
  lab:['Lab','Do the task. Jot your numbers on your whiteboard.',svg('<path d="M9 3h6M10 3v6l-5 9a2 2 0 002 3h10a2 2 0 002-3l-5-9V3M7.5 15h9"/>')],
  book:['Reference book','Copy this into your reference book. This is your notes.',svg('<path d="M12 6c-2-1.5-5-2-9-2v14c4 0 7 .5 9 2 2-1.5 5-2 9-2V4c-4 0-7 .5-9 2zM12 6v14"/>')],
  practise:['Exercise book','On your own. Full working. Check as you go.',svg('<path d="M4 20l1-5L16 4l4 4L9 19l-5 1zM14 6l4 4"/>')],
  handin:['Exit slip','Answer on your slip. Hand it in at the door.',svg('<path d="M4 7h16v4a2 2 0 000 4v4H4v-4a2 2 0 000-4V7zM10 7v12"/>')]};

// ---------- build the deck
const stage=$('#stage'),L=LESSON,TOT=L.phases.reduce((a,p)=>a+p[1],0);
stage.insertBefore(el('section','slide title',`<div class="code">${L.code}</div><div class="sub">Unit ${L.unit} · ${L.aos} · Lesson ${L.n}</div><h1>${L.title}</h1><div class="strip">${L.phases.map(p=>`<div><b>${p[1]}</b>${p[0]}</div>`).join('')}</div><div class="bring">On your desk: <b>reference book</b>, <b>whiteboard and marker</b>, <b>calculator</b>, exercise book.</div>`),stage.querySelector('.slide'));
// The reference book page: one A4 sheet of 8 mm ruled paper, built once and shown at each stage of the lesson.
const NB=Math.max(0,...$$('#pagesrc .bk').map(k=>+k.dataset.b));
function mkPage(b){const p=el('div','page',`<div class="ptop"></div><div class="phd"><span>${L.code} ${L.title}</span><span>...... / ...... / ......</span></div><div class="tl"></div><div class="mg"></div><div class="md"></div>`+$('#pagesrc').innerHTML);
  $$('.bk',p).forEach(k=>{const n=+k.dataset.b;k.classList.add(b>NB?'all':n>b?'later':n<b?'done':'now')});return p}
$$('.slide[data-mode=book]').forEach(s=>{const b=+s.dataset.b;
  if(s.classList.contains('pageslide')){s.append(el('div','fitwrap','<div class="fit"></div><div class="chk"><h3>Your page should match this</h3><p>Left of the line: notes, formulas, diagrams.</p><p>Right of the line: worked examples.</p><p>One line of writing on each ruled line.</p><p class="pp">Press <b>P</b> to print this page at full size for anyone away.</p></div>'));$('.fit',s).append(mkPage(99));return}
  const w=el('div','bookwrap','<div class="vw"></div><div class="aside"><div class="thumb"><div class="vp"></div></div></div>');s.append(w);
  $('.vw',w).append(mkPage(b));$('.thumb',w).prepend(mkPage(b))});
function place(s){const vw=$('.vw',s);if(!vw)return;const pg=$('.page',vw),nw=$('.now',pg),U=pg.offsetHeight/37.125,k=$('.thumb',s).clientWidth/pg.offsetWidth;
  const y=Math.max(0,Math.min(pg.offsetHeight-vw.clientHeight,nw?nw.offsetTop+nw.offsetParent.offsetTop-2.2*U:0));
  pg.style.transform=`translateY(${-y}px)`;const vp=$('.vp',s);vp.style.top=y*k+'px';vp.style.height=vw.clientHeight*k+'px'}
const pr=el('div');pr.id='print';pr.append(mkPage(99));document.body.append(pr);
const S=$$('.slide');let cur=0,ph=null,t0=0,dur=0,st0=0,sdur=0;
S.forEach((s,i)=>{const m=MODES[s.dataset.mode];
  if(m)s.prepend(el('div','hd',`<span class="mode">${m[2]}${m[0]}</span><span class="do">${s.dataset.do||m[1]}</span><span style="flex:1"></span>${s.dataset.tag?`<span class="ctag">${s.dataset.tag}</span>`:''}<span class="tm"></span>`));
  s.append(el('div','pg',`${i+1} / ${S.length}`))});
const pb=el('div');pb.id='phases';pb.innerHTML=L.phases.map(p=>`<i style="flex:${p[1]}" title="${p[0]}"><b></b></i>`).join('');stage.append(pb);
const cnt=el('div');cnt.id='count';stage.append(cnt);
mathAll(stage);mathAll(pr);
const steps=s=>$$('.st',s);
function show(n,all){S[cur].classList.remove('on');cur=Math.max(0,Math.min(S.length-1,n));const s=S[cur];s.classList.add('on');
  steps(s).forEach(e=>e.classList.toggle('shown',!!all));
  const p=s.dataset.phase||'';if(p!==ph){ph=p;t0=performance.now();dur=((L.phases.find(x=>x[0]===p)||[0,0])[1])*60}
  st0=performance.now();sdur=+s.dataset.t||0;place(s);try{history.replaceState(null,'','#'+(cur+1))}catch(e){}}
function next(){const h=steps(S[cur]).filter(e=>!e.classList.contains('shown'));if(h.length)h[0].classList.add('shown');else if(cur<S.length-1)show(cur+1)}
function prev(){const v=steps(S[cur]).filter(e=>e.classList.contains('shown'));if(v.length)v[v.length-1].classList.remove('shown');else if(cur>0)show(cur-1,true)}
addEventListener('keydown',e=>{if(/INPUT|SELECT|TEXTAREA/.test(e.target.tagName))return;
  if(['ArrowRight','PageDown','Enter'].includes(e.key)){e.preventDefault();next()}
  else if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();prev()}
  else if(e.key==='p'||e.key==='P')print();
  else if(e.key==='f'||e.key==='F')document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()});
stage.addEventListener('click',e=>{if(e.target.closest('.lab,.gen,.sorter,.nav,button,input,a'))return;next()});
const nav=el('div','nav','<button title="Back">◀</button><button title="Next">▶</button>');stage.append(nav);
nav.children[0].onclick=prev;nav.children[1].onclick=next;
const clock=x=>{const a=Math.abs(x);return (x<0?'+':'')+Math.floor(a/60)+':'+String(a%60).padStart(2,'0')};
setInterval(()=>{const now=performance.now(),tm=$('.tm',S[cur]);
  if(tm){if(!sdur)tm.style.display='none';else{const left=Math.round(sdur-(now-st0)/1000);tm.style.display='';tm.textContent=clock(left);tm.classList.toggle('over',left<0)}}
  const k=L.phases.findIndex(p=>p[0]===ph);$$('#phases i').forEach((b,j)=>{const f=j<k?1:j>k||k<0?0:Math.min(1,(now-t0)/1000/dur);$('b',b).style.width=f*100+'%';b.classList.toggle('over',j===k&&(now-t0)/1000>dur)})},250);
stage.addEventListener('click',e=>{if(e.target.closest('.tm'))st0=performance.now();
  if(e.target.closest('.show3')){let k=3;cnt.className='on';cnt.textContent=k;const iv=setInterval(()=>{k--;if(k>0)cnt.textContent=k;else if(k===0){cnt.textContent='SHOW';cnt.className='on go'}else{clearInterval(iv);cnt.className=''}},800)}});
function fit(){const k=Math.min(innerWidth/1280,innerHeight/720);stage.style.transform=`translate(-50%,-50%) scale(${k})`}
addEventListener('resize',fit);fit();

// ---------- You try: a new question each round, checked, with working one line at a time
const GEN={};
function initGen(box){let round=0;const make=()=>{const q=GEN[box.dataset.gen]();let k=0;round++;
  box.innerHTML=`<div class="wb"><small>Round ${round}</small>${mx(q.q)}</div><div class="row"><input placeholder="class answer"><span class="unit">${mx(q.unit||'')}</span><button class="btn chk">Check</button><span class="res"></span><span style="flex:1"></span><button class="btn alt sw">Next line of working</button><button class="btn nw">New question</button></div><div class="steps"></div>`;
  const inp=$('input',box),res=$('.res',box);
  const chk=()=>{const v=parseNum(inp.value);if(isNaN(v)){res.textContent='';return}const ok=Math.abs(v-q.ans)<=(q.abs!=null?q.abs:Math.abs(q.ans)*.025);
    res.className='res '+(ok?'ok':'no');res.textContent=ok?'✓ Correct':'✗ Not yet'};
  $('.chk',box).onclick=chk;inp.onkeydown=e=>{if(e.key==='Enter')chk()};
  $('.sw',box).onclick=()=>{if(k<q.steps.length)$('.steps',box).append(el('div','',mx(q.steps[k++])))};
  $('.nw',box).onclick=make};make()}

// ---------- lab helpers
const SIMS={};
function lab(host,W,H){host.innerHTML='';const cv=el('canvas');cv.width=W*2;cv.height=H*2;const side=el('div','side');host.append(cv,side);const c=cv.getContext('2d');c.scale(2,2);return{cv,c,side,W,H}}
function loop(host,fn){let last=performance.now();const sl=host.closest('.slide');(function f(now){const dt=Math.min(.05,(now-last)/1000);last=now;if(sl.classList.contains('on'))fn(dt);requestAnimationFrame(f)})(last)}
function slider(side,label,min,max,step,val,fmt,on){const d=el('label','sl',`<span>${label}</span><b></b><input type="range" min="${min}" max="${max}" step="${step}" value="${val}">`),i=$('input',d),b=$('b',d);
  const u=()=>{b.textContent=fmt(+i.value);on(+i.value)};i.oninput=u;side.append(d);u();return i}
function choice(side,label,opts,val,on){const d=el('div','ch',`<span>${label}</span>`);opts.forEach(([k,t])=>{const b=el('button','pill'+(k===val?' on':''),t);b.onclick=()=>{$$('.pill',d).forEach(x=>x.classList.remove('on'));b.classList.add('on');on(k)};d.append(b)});side.append(d);return d}
function drag(cv,W,fn){let on=false;const p=e=>{const r=cv.getBoundingClientRect(),k=W/r.width;return[(e.clientX-r.left)*k,(e.clientY-r.top)*k]};
  cv.addEventListener('pointerdown',e=>{on=true;cv.setPointerCapture(e.pointerId);fn(...p(e),true)});cv.addEventListener('pointermove',e=>{if(on)fn(...p(e),false)});cv.addEventListener('pointerup',()=>on=false)}
function ask(box,label,unit,truth,tol){const r=el('div','ask',`<span>${mx(label)}</span><input><span>${mx(unit)}</span><button class="btn">Check</button><span class="mk"></span>`);box.append(r);
  const inp=$('input',r),mk=$('.mk',r),go=()=>{const v=parseNum(inp.value);if(isNaN(v))return;const ok=Math.abs(v-truth())<=Math.abs(truth())*tol;mk.textContent=ok?'✓':'✗';mk.className='mk '+(ok?'ok':'no')};
  $('button',r).onclick=go;inp.onkeydown=e=>{if(e.key==='Enter')go()};return{clear(){inp.value='';mk.textContent=''},show(){inp.value=+truth().toPrecision(3);mk.textContent='✓';mk.className='mk ok'}}}
function missions(side,list,state){let i=0,hold=0,done=false;const box=el('div','mis');side.append(box);
  const draw=()=>{box.className='mis'+(done?' ok':'');box.innerHTML=`<div class="lbl">Mission ${i+1} of ${list.length}${done?' · done':''}</div><div class="mt">${mx(list[i].t)}</div>${done?`<div class="ms">${mx(list[i].d)}</div>`:''}${done&&i<list.length-1?'<button class="btn">Next mission</button>':''}`;
    const b=$('button',box);if(b)b.onclick=()=>{i++;done=false;hold=0;draw()}};draw();
  return dt=>{if(done)return;if(list[i].ok(state())){hold+=dt;if(hold>.8){done=true;draw()}}else hold=0}}
const D=Math.PI/180;
function init(){$$('.gen').forEach(initGen);$$('.lab').forEach(h=>SIMS[h.dataset.sim](h,JSON.parse(h.dataset.o||'{}')));$$('.sorter').forEach(h=>SIMS.sorter(h));show((+location.hash.slice(1)||1)-1)}
