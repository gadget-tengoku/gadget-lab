(function(){
var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches,fine=matchMedia('(pointer:fine)').matches;
if(fine&&!reduce){var g=document.createElement('div');g.className='cursor-glow';document.body.appendChild(g);
addEventListener('mousemove',function(e){g.style.transform='translate('+e.clientX+'px,'+e.clientY+'px)'},{passive:true});
document.querySelectorAll('.acard,.gear,.card,.pcard,.rank,.contact-card').forEach(function(el){el.classList.add('tilt');
el.addEventListener('mousemove',function(e){var r=el.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;el.style.transform='perspective(900px) rotateX('+(-y*7)+'deg) rotateY('+(x*9)+'deg) translateY(-4px)'});
el.addEventListener('mouseleave',function(){el.style.transform=''})})}
var cols=['#00f5d4','#7b5cff','#ff3d9a','#ffd23f'];
document.addEventListener('click',function(e){var t=e.target.closest('.btn,.shine-btn,.sticky-cta a,.rank-cta');if(!t||reduce)return;
for(var i=0;i<18;i++){var s=document.createElement('span');s.className='spark';s.style.background=cols[i%4];s.style.boxShadow='0 0 10px '+cols[i%4];s.style.left=e.clientX+'px';s.style.top=e.clientY+'px';document.body.appendChild(s);
var a=Math.random()*Math.PI*2,d=40+Math.random()*80;s.animate([{transform:'translate(0,0) scale(1)',opacity:1},{transform:'translate('+Math.cos(a)*d+'px,'+Math.sin(a)*d+'px) scale(0)',opacity:0}],{duration:600+Math.random()*300,easing:'cubic-bezier(.2,.8,.2,1)'}).onfinish=(function(n){return function(){n.remove()}})(s)}},true);
document.querySelectorAll('[data-count]').forEach(function(el){var to=+el.dataset.count,st=null;function f(ts){if(!st)st=ts;var p=Math.min((ts-st)/1200,1);el.textContent=Math.round(to*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(f)}
if('IntersectionObserver'in window){new IntersectionObserver(function(es,o){es.forEach(function(x){if(x.isIntersecting){requestAnimationFrame(f);o.disconnect()}})}).observe(el)}else el.textContent=to});
})();