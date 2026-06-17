/* ============================================
   PDflow — interaction.js
   All JS: Nav · 3D · Demo · Toolx · CountUp
   Magnetic · Cursor · Exit · FAQ · A11y
   ============================================ */
(function(){'use strict';

/* ---- Nav ---- */
var nav=document.getElementById('nav'),ham=document.getElementById('navHam'),links=document.getElementById('navLinks'),floatCta=document.getElementById('floatCta');
window.addEventListener('scroll',function(){var y=window.scrollY;nav&&nav.classList.toggle('scrolled',y>50);floatCta&&floatCta.classList.toggle('show',y>800);},{passive:true});
ham&&links&&(ham.addEventListener('click',function(){links.classList.toggle('open');ham.setAttribute('aria-expanded',String(links.classList.contains('open')));}),links.querySelectorAll('.nav-link').forEach(function(a){a.addEventListener('click',function(){links.classList.remove('open');ham.setAttribute('aria-expanded','false');});}));

/* ---- Smooth scroll ---- */
document.querySelectorAll('a[href^="#"]').forEach(function(a){a.addEventListener('click',function(e){var id=this.getAttribute('href');if(id.length<2)return;var t=document.querySelector(id);if(t){e.preventDefault();window.scrollTo({top:t.getBoundingClientRect().top+window.scrollY-80,behavior:'smooth'});}});});

/* ---- Nav active highlight ---- */
(function(){var secs=document.querySelectorAll('section[id]'),navLinks=document.querySelectorAll('.nav-link');if(secs.length&&navLinks.length&&'IntersectionObserver' in window){new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var id=e.target.id;navLinks.forEach(function(l){l.classList.toggle('active',l.getAttribute('href')==='#'+id);});}});},{threshold:.3,rootMargin:'-80px 0px -50% 0px'}).observe(secs[0]);secs.forEach(function(s,idx){if(idx>0)new(IntersectionObserver)(function(es){es.forEach(function(e){if(e.isIntersecting){var id=e.target.id;navLinks.forEach(function(l){l.classList.toggle('active',l.getAttribute('href')==='#'+id);});}});},{threshold:.3,rootMargin:'-80px 0px -50% 0px'}).observe(s);});}})();

/* ---- IntersectionObserver Reveal ---- */
(function(){var els=document.querySelectorAll('.reveal');if('IntersectionObserver' in window&&els.length){new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('r-visible');}});},{threshold:.15,rootMargin:'0px 0px -40px 0px'}).observe(els[0]);els.forEach(function(el,idx){if(idx>0)new(IntersectionObserver)(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('r-visible');}});},{threshold:.15,rootMargin:'0px 0px -40px 0px'}).observe(el);});}else{els.forEach(function(el){el.classList.add('r-visible');});}})();

/* ---- Hero 3D Mouse Tracking ---- */
(function(){var win=document.getElementById('heroWin'),stage=document.getElementById('heroStage'),pref=window.matchMedia('(prefers-reduced-motion:reduce)');if(!win||!stage||pref.matches)return;stage.addEventListener('mousemove',function(e){var r=stage.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;win.style.transform='rotateY('+(x*-6)+'deg) rotateX('+(y*4)+'deg)';});stage.addEventListener('mouseleave',function(){win.style.transform='rotateY(-3deg) rotateX(2deg)';});})();

/* ---- Demo Steps ---- */
(function(){var steps=document.querySelectorAll('.demo-step'),slides=document.querySelectorAll('.demo-slide');steps.forEach(function(s){s.addEventListener('click',function(){var idx=parseInt(this.dataset.step,10)-1;steps.forEach(function(st){st.classList.remove('active');});this.classList.add('active');slides.forEach(function(sl,i){sl.classList.toggle('active',i===idx);});});});})();

/* ---- Toolbox Horizontal Scroll ---- */
(function(){var track=document.getElementById('toolx'),leftBtn=document.getElementById('toolxL'),rightBtn=document.getElementById('toolxR');if(!track||!leftBtn||!rightBtn)return;var scrollAmt=340;leftBtn.addEventListener('click',function(){track.scrollBy({left:-scrollAmt,behavior:'smooth'});});rightBtn.addEventListener('click',function(){track.scrollBy({left:scrollAmt,behavior:'smooth'});});if(window.innerWidth>1024){var isDown=false,startX=0,scrollL=0;track.addEventListener('mousedown',function(e){isDown=true;startX=e.pageX-track.offsetLeft;scrollL=track.scrollLeft;});track.addEventListener('mouseleave',function(){isDown=false;});track.addEventListener('mouseup',function(){isDown=false;});track.addEventListener('mousemove',function(e){if(!isDown)return;e.preventDefault();var x=e.pageX-track.offsetLeft,walk=(x-startX)*.8;track.scrollLeft=scrollL-walk;});}})();

/* ---- CountUp Animation ---- */
(function(){var counters=document.querySelectorAll('.stat-num,.conv-num');if(!counters.length)return;var animated=new Set();function animateCount(el){var target=parseFloat(el.dataset.target||el.dataset.count||el.textContent),isFloat=target%1!==0,duration=2000,start=performance.now();function step(now){var p=Math.min((now-start)/duration,1),cur=p<.5?2*p*p:-1+(4-2*p)*p;/*easeInOutQuad*/var val=cur*target;el.textContent=isFloat?val.toFixed(1):Math.round(val);if(p<1)requestAnimationFrame(step);else el.textContent=isFloat?target.toFixed(1):Math.round(target);}requestAnimationFrame(step);}
if('IntersectionObserver' in window){new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting&&!animated.has(e.target)){animated.add(e.target);animateCount(e.target);}});},{threshold:.5}).observe(counters[0]);counters.forEach(function(c,idx){if(idx>0)new(IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting&&!animated.has(e.target)){animated.add(e.target);animateCount(e.target);}});},{threshold:.5}).observe(c);});}else{counters.forEach(function(c){animateCount(c);});}})();

/* ---- Magnetic Button ---- */
(function(){var btns=document.querySelectorAll('.magnetic');if(window.matchMedia('(prefers-reduced-motion:reduce)').matches)return;btns.forEach(function(btn){btn.addEventListener('mousemove',function(e){var r=btn.getBoundingClientRect(),x=e.clientX-r.left-r.width/2,y=e.clientY-r.top-r.height/2;btn.style.transform='translate('+(x*.15)+'px,'+(y*.15)+'px)';});btn.addEventListener('mouseleave',function(){btn.style.transform='';});});})();

/* ---- Cursor Light ---- */
(function(){var light=document.createElement('div');light.className='cursor-light';document.body.appendChild(light);var timeout;if(window.matchMedia('(prefers-reduced-motion:reduce)').matches)return;document.addEventListener('mousemove',function(e){light.classList.add('active');light.style.transform='translate('+(e.clientX-200)+'px,'+(e.clientY-200)+'px)';clearTimeout(timeout);});document.addEventListener('mouseleave',function(){light.classList.remove('active');});})();

/* ---- Floating CTA (Exit Intent) ---- */
(function(){var el=floatCta;if(!el)return;var exitCount=0;document.addEventListener('mouseleave',function(e){if(e.clientY<0&&exitCount<2){el.classList.add('show');exitCount++;setTimeout(function(){if(window.scrollY<800)el.classList.remove('show');},3000);}});})();

/* ---- FAQ ---- */
(function(){var items=document.querySelectorAll('.faq-item');items.forEach(function(item){var btn=item.querySelector('.faq-q');if(!btn)return;btn.addEventListener('click',function(){var open=item.classList.contains('open');items.forEach(function(fi){fi.classList.remove('open');var b=fi.querySelector('.faq-q');if(b)b.setAttribute('aria-expanded','false');});if(!open){item.classList.add('open');btn.setAttribute('aria-expanded','true');}});});
/* FAQ search */
var search=document.getElementById('faqSearch');if(search){search.addEventListener('input',function(){var q=this.value.toLowerCase().trim();items.forEach(function(item){var qText=item.querySelector('.faq-q span');if(!qText)return;var match=qText.textContent.toLowerCase().includes(q);item.style.display=match?'':'none';});});}
/* FAQ URL anchor */
if(window.location.hash){var hash=window.location.hash.substring(1),target=document.getElementById(hash);if(target&&target.classList.contains('faq-item')){target.classList.add('open');var qb=target.querySelector('.faq-q');if(qb)qb.setAttribute('aria-expanded','true');}}})();

/* ---- Keyboard ---- */
document.addEventListener('keydown',function(e){if(e.key==='Escape'){var l=document.getElementById('navLinks');if(l&&l.classList.contains('open')){l.classList.remove('open');document.getElementById('navHam').focus();}}});

/* ---- Console ---- */
console.log('%c印流PDflow%c\nDocument Creation Platform','color:#8B5CF6;font-size:20px;font-weight:700;padding:8px 0','color:#A1A1AA;font-size:12px');

/* ---- Image lazy (fallback) ---- */
if(!('loading' in HTMLImageElement.prototype)&&'IntersectionObserver' in window){document.querySelectorAll('img[loading="lazy"]').forEach(function(img){new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var i=e.target;i.src=i.src;}})},{threshold:.1}).observe(img);});}

})();
