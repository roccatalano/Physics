// Physics lesson deck: click / → / space = next line of working, then next slide; ← = back one line (or previous slide);
// F = full screen; Home / End. Phase timers start when a slide is reached, keep running across the phase's slides,
// and reset when the phase changes.
(()=>{const S=[...document.querySelectorAll('.slide')];let i=0,ph=null,t0=0,dur=0;
 const steps=s=>[...s.querySelectorAll('.st')];
 function show(n,all){S.forEach(s=>s.classList.remove('on'));i=Math.max(0,Math.min(S.length-1,n));const s=S[i];s.classList.add('on');
  steps(s).forEach(e=>e.classList.toggle('shown',!!all));
  const p=s.dataset.phase||'';if(p!==ph){ph=p;t0=performance.now();dur=(+s.dataset.min||0)*60}
  // load interactives only when their slide is shown
  s.querySelectorAll('iframe[data-yt]').forEach(f=>{if(!f.src)f.src='https://www.youtube-nocookie.com/embed/'+f.dataset.yt+'?'+f.dataset.q});
  S.forEach(o=>{if(o!==s)o.querySelectorAll('iframe[data-yt]').forEach(f=>{if(f.src)f.removeAttribute('src')})});
  s.querySelectorAll('iframe[data-src]').forEach(f=>{if(!f.src){const P=decodeURIComponent(location.pathname),base=/\/lessons\/library\//.test(P)?'../../interactives/':/\/(lessons|library)\//.test(P)?'../interactives/':'interactives/';f.src=base+f.dataset.src}});
  try{history.replaceState(null,'','#'+(i+1))}catch(e){}
  requestAnimationFrame(()=>fit(s))}
 // shrink a slide's content (not its bar or footer) until it fits the 720 px slide
 function fit(s){if(s.dataset.fit)return;const kids=[...s.children].filter(c=>!c.matches('.bar,.foot,.tags,.seq'));let z=1;
  const over=()=>s.scrollHeight>s.clientHeight+4||[...s.querySelectorAll('.rows .card,.rows .sol')].some(c=>c.scrollHeight>c.clientHeight+6)||kids.some(k=>k.getBoundingClientRect().bottom>s.getBoundingClientRect().bottom-30);
  while(over()&&z>.55){z-=.05;kids.forEach(k=>k.style.zoom=z)}s.dataset.fit=z.toFixed(2)}
 function next(){const h=steps(S[i]).filter(e=>!e.classList.contains('shown'));if(h.length){h[0].classList.add('shown');return}if(i<S.length-1)show(i+1)}
 function prev(){const v=steps(S[i]).filter(e=>e.classList.contains('shown'));if(v.length){v[v.length-1].classList.remove('shown');return}if(i>0)show(i-1,true)}
 addEventListener('keydown',e=>{if(e.target.tagName==='IFRAME')return;
  if(['ArrowRight',' ','PageDown','Enter'].includes(e.key)){e.preventDefault();next()}
  else if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){e.preventDefault();prev()}
  else if(e.key==='Home')show(0);else if(e.key==='End')show(S.length-1);
  else if(e.key==='f'||e.key==='F')document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()});
 document.getElementById('stage').addEventListener('click',e=>{if(e.target.closest('iframe,a,button'))return;next()});
 setInterval(()=>{const tm=S[i].querySelector('.timer');if(!tm)return;if(!dur){tm.style.display='none';return}
  const left=Math.round(dur-(performance.now()-t0)/1000),a=Math.abs(left);tm.textContent=(left<0?'+':'')+Math.floor(a/60)+':'+String(a%60).padStart(2,'0');tm.classList.toggle('over',left<0)},250);
 show((+location.hash.slice(1)||1)-1)})();
