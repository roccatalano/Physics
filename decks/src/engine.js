// Chapter deck engine. A chapter holds sections (1A, 1B, 1C) in order. Every slide declares a mode
// (what students are doing), and the look follows the mode. build.py supplies CHAPTER and wraps each
// section's slides and page sources in <div class="sec">.
const $=(s,e=document)=>e.querySelector(s),$$=(s,e=document)=>[...e.querySelectorAll(s)];
const el=(t,c,h)=>{const e=document.createElement(t);if(c)e.className=c;if(h!=null)e.innerHTML=h;return e};
const pick=a=>a[Math.floor(Math.random()*a.length)];
const mx=s=>String(s).replace(/\$([^$]+)\$/g,(_,t)=>katex.renderToString(t.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&'),{throwOnError:false}));
function mathAll(root){const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),ns=[];
  while(w.nextNode())if(w.currentNode.nodeValue.includes('$'))ns.push(w.currentNode);
  ns.forEach(n=>{const sp=document.createElement('span');sp.innerHTML=mx(n.nodeValue.replace(/&/g,'&amp;').replace(/</g,'&lt;'));n.replaceWith(sp)})}
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
  practise:['Exercise book','On your own. Full working. Check as you go.',svg('<path d="M4 20l1-5L16 4l4 4L9 19l-5 1zM14 6l4 4"/>')]};

// ---------- sections: each has its own title slide, slides and one or more reference pages
const stage=$('#stage'),CH=CHAPTER;
const SECS=$$('.sec',stage).map((d,i)=>({...CH.sections[i],el:d,pages:$$('.pagesrc',d)}));
const desk=s=>`<div class="bring">${s.desk||CH.desk}</div>`;
SECS.forEach(s=>s.el.prepend(el('section','slide title',`<div class="code">${s.code}</div><div class="sub">Unit ${CH.unit} · ${CH.aos} · Chapter ${CH.code}</div><h1>${s.title}</h1>${desk(s)}`)));
const toc=el('section','slide contents','<h2>Contents</h2><div class="toc"></div><div class="how">Click a line to jump there, or type its slide number then G. Press C to come back to this page.</div>');
stage.prepend(toc);
stage.prepend(el('section','slide title',`<div class="code">${CH.code}</div><div class="sub">Unit ${CH.unit} · ${CH.aos} · Chapter ${CH.code}</div><h1>${CH.title}</h1>${desk(CH)}`));

// ---------- the reference book pages: A4 sheets of 8 mm ruled paper, built once, shown at each stage
function pageTitle(sec,i){const t=sec.pages[i].dataset.title;return t||`${sec.code} ${sec.title}`}
function mkPage(sec,i,b){const src=sec.pages[i],NB=Math.max(0,...$$('.bk',src).map(k=>+k.dataset.b));
  const p=el('div','page',`<div class="ptop"></div><div class="phd"><span>${pageTitle(sec,i)}</span><span>...... / ...... / ......</span></div><div class="tl"></div><div class="mg"></div><div class="md"></div>`+src.innerHTML);
  $$('.bk',p).forEach(k=>{const n=+k.dataset.b;k.classList.add(b>NB?'all':n>b?'later':n<b?'done':'now')});return p}
const secOf=s=>SECS.find(x=>x.el.contains(s));
SECS.forEach(sec=>$$('.slide[data-mode=book]',sec.el).forEach(s=>{const b=+s.dataset.b,i=(+s.dataset.page||1)-1;
  if(!sec.pages[i])throw new Error(`${sec.code}: a book slide asks for page ${i+1}, but the section has ${sec.pages.length}`);
  if(s.classList.contains('pageslide')){const n=sec.pages.length;
    s.append(el('div','fitwrap',`<div class="fit"></div><div class="chk"><h3>Your page should match this</h3><p>Left of the line: notes, formulas, diagrams.</p><p>Right of the line: worked examples.</p><p>One line of writing on each ruled line.</p><p class="pp">Press <b>P</b> to print ${n>1?`the ${n} pages for ${sec.code}`:'this page'} at full size for anyone away.</p></div>`));$('.fit',s).append(mkPage(sec,i,99));return}
  const w=el('div','bookwrap','<div class="vw"></div><div class="aside"><div class="thumb"><div class="vp"></div></div></div>');s.append(w);
  $('.vw',w).append(mkPage(sec,i,b));$('.thumb',w).prepend(mkPage(sec,i,b))}));
function place(s){const vw=$('.vw',s);if(!vw)return;const pg=$('.page',vw),nw=$('.now',pg),U=pg.offsetHeight/37.125,k=$('.thumb',s).clientWidth/pg.offsetWidth;
  const y=Math.max(0,Math.min(pg.offsetHeight-vw.clientHeight,nw?nw.offsetTop+nw.offsetParent.offsetTop-2.2*U:0));
  pg.style.transform=`translateY(${-y}px)`;const vp=$('.vp',s);vp.style.top=y*k+'px';vp.style.height=vw.clientHeight*k+'px'}
// every finished page, ready to print; prepPrint picks which ones go on paper
const pr=el('div');pr.id='print';SECS.forEach(sec=>sec.pages.forEach((_,i)=>{const p=mkPage(sec,i,99);p.dataset.sec=sec.code;pr.append(p)}));document.body.append(pr);
function prepPrint(all){const sec=secOf(S[cur]),want=p=>all||!sec||p.dataset.sec===sec.code;let first=true;
  $$('.page',pr).forEach(p=>{const on=want(p);p.classList.toggle('skip',!on);p.classList.toggle('brk',on&&!first);if(on)first=false})}

// ---------- header, footer and contents
const S=$$('.slide');let cur=0,st0=0,sdur=0;
S.forEach((s,i)=>{const m=MODES[s.dataset.mode];
  if(m)s.prepend(el('div','hd',`<span class="mode">${m[2]}${m[0]}</span><span class="do">${s.dataset.do||m[1]}</span><span style="flex:1"></span>${s.dataset.tag?`<span class="ctag">${s.dataset.tag}</span>`:''}<span class="tm"></span>`));
  s.append(el('div','pg',`${i+1} / ${S.length}`))});
const go=n=>()=>show(n);
SECS.forEach(sec=>{const col=el('div','tsec'),first=S.indexOf($('.slide',sec.el));let k=0;
  const b=el('button','sh',`<b>${sec.code}</b><span class="nm">${sec.title}</span><i>${first+1}</i>`);b.onclick=go(first);col.append(b);
  $$('.slide[data-loop],.slide[data-part]',sec.el).forEach(s=>{const n=S.indexOf(s),lp=s.dataset.loop!=null;
    const e=el('button','',`<span class="lp">${lp?'Loop '+(++k):''}</span><span class="nm">${lp?s.dataset.loop:s.dataset.part}</span><i>${n+1}</i>`);e.onclick=go(n);col.append(e)});
  $('.toc',toc).append(col)});
mathAll(stage);mathAll(pr);

// ---------- moving through the deck. Every reveal is reachable with PageDown alone.
const steps=s=>$$('.st',s);
const KEY='deck:'+CH.code+':'+CH.title;
function save(){try{const s=S[cur],sec=secOf(s);localStorage.setItem(KEY,JSON.stringify({n:cur,sec:sec?sec.code:null,k:sec?$$('.slide',sec.el).indexOf(s):cur}))}catch(e){}}
function saved(){try{const v=JSON.parse(localStorage.getItem(KEY));if(!v)return 0;
  if(v.sec){const sec=SECS.find(x=>x.code===v.sec),ss=sec&&$$('.slide',sec.el);if(ss&&ss[v.k])return S.indexOf(ss[v.k])}
  return Math.min(S.length-1,v.n||0)}catch(e){return 0}}
function show(n,all){S[cur].classList.remove('on');cur=Math.max(0,Math.min(S.length-1,n));const s=S[cur];s.classList.add('on');
  steps(s).forEach(e=>e.classList.toggle('shown',!!all));
  if(s===toc){const sec=SECS.find(x=>x.el.contains(S[Math.max(0,+toc.dataset.from||0)]));$$('.toc .sh',toc).forEach((b,i)=>b.classList.toggle('here',SECS[i]===sec))}
  st0=performance.now();sdur=+s.dataset.t||0;place(s);try{history.replaceState(null,'','#'+(cur+1))}catch(e){}save()}
function next(){const h=steps(S[cur]).filter(e=>!e.classList.contains('shown'));if(h.length)h[0].classList.add('shown');else if(cur<S.length-1)show(cur+1)}
function prev(){const v=steps(S[cur]).filter(e=>e.classList.contains('shown'));if(v.length)v[v.length-1].classList.remove('shown');else if(cur>0)show(cur-1,true)}
let typed='',typedAt=0;
addEventListener('keydown',e=>{if(/INPUT|SELECT|TEXTAREA/.test(e.target.tagName))return;
  if(['ArrowRight','PageDown','Enter'].includes(e.key)){e.preventDefault();next()}
  else if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();prev()}
  else if(/^[0-9]$/.test(e.key)){const now=performance.now();typed=(now-typedAt>3000?'':typed)+e.key;typedAt=now}
  else if((e.key==='g'||e.key==='G')&&typed){show(+typed-1);typed=''}
  else if(e.key==='c'||e.key==='C'){if(S[cur]!==toc){toc.dataset.from=cur;show(S.indexOf(toc))}}
  else if(e.key==='p'||e.key==='P'){prepPrint(e.shiftKey);print()}
  else if(e.key==='f'||e.key==='F')document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()});
addEventListener('beforeprint',()=>{if(!$$('.page.skip,.page.brk',pr).length)prepPrint(false)});
stage.addEventListener('click',e=>{if(e.target.closest('.tm'))st0=performance.now();if(e.target.closest('.lab,.sorter,.nav,button,input,a'))return;next()});
const nav=el('div','nav','<button title="Back">◀</button><button title="Next">▶</button>');stage.append(nav);
nav.children[0].onclick=prev;nav.children[1].onclick=next;
// per-slide timer (data-t seconds); click it to restart
const clock=x=>{const a=Math.abs(x);return (x<0?'+':'')+Math.floor(a/60)+':'+String(a%60).padStart(2,'0')};
setInterval(()=>{const tm=$('.tm',S[cur]);if(!tm)return;
  if(!sdur)tm.style.display='none';else{const left=Math.round(sdur-(performance.now()-st0)/1000);tm.style.display='';tm.textContent=clock(left);tm.classList.toggle('over',left<0)}},250);
function fit(){const k=Math.min(innerWidth/1280,innerHeight/720);stage.style.transform=`translate(-50%,-50%) scale(${k})`}
addEventListener('resize',fit);fit();

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
// load the handwriting fonts now, so a page printed before any page is on screen still uses them
try{document.fonts.load("16px 'Patrick Hand'");document.fonts.load("700 16px Kalam")}catch(e){}
function init(){$$('.lab').forEach(h=>SIMS[h.dataset.sim](h,JSON.parse(h.dataset.o||'{}')));$$('.sorter').forEach(h=>SIMS.sorter(h));
  const h=+location.hash.slice(1);show(h?h-1:saved())}
