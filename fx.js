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
(function(){
var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches,C=['#00f5d4','#7b5cff','#ff3d9a','#ffd23f','#ffffff'];
function toast(t){var d=document.createElement('div');d.className='gg-toast';d.innerHTML=t;document.body.appendChild(d);requestAnimationFrame(function(){d.classList.add('in')});setTimeout(function(){d.classList.remove('in');setTimeout(function(){d.remove()},500)},2600)}
function confetti(n){if(reduce)return;n=n||140;for(var i=0;i<n;i++){var p=document.createElement('i');p.className='gg-cf';p.style.left=Math.random()*100+'vw';p.style.background=C[i%5];p.style.width=(6+Math.random()*6)+'px';p.style.height=(8+Math.random()*10)+'px';document.body.appendChild(p);
var dx=(Math.random()-.5)*200,rot=Math.random()*720;p.animate([{transform:'translate(0,-20px) rotate(0)',opacity:1},{transform:'translate('+dx+'px,105vh) rotate('+rot+'deg)',opacity:.9}],{duration:2200+Math.random()*1800,delay:Math.random()*400,easing:'cubic-bezier(.2,.6,.4,1)'}).onfinish=(function(e){return function(){e.remove()}})(p)}}
window.ggConfetti=function(){confetti(160)};window.ggToast=toast;
/* 隠しコマンド */
var K=['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a'],ki=0;
addEventListener('keydown',function(e){var k=e.key.length===1?e.key.toLowerCase():e.key;ki=(k===K[ki])?ki+1:(k===K[0]?1:0);if(ki===K.length){ki=0;confetti(220);toast('隠しコマンド発見！<b>GG WP</b>');document.documentElement.classList.add('gg-rainbow');setTimeout(function(){document.documentElement.classList.remove('gg-rainbow')},6000)}});
/* ロゴ連打 */
var lc=0,lt;var logo=document.querySelector('.logo');if(logo)logo.addEventListener('click',function(e){lc++;clearTimeout(lt);lt=setTimeout(function(){lc=0},1500);if(lc>=5){e.preventDefault();lc=0;document.documentElement.classList.add('gg-rainbow');toast('連打しすぎ！<b>レインボーモード</b>');confetti(80);setTimeout(function(){document.documentElement.classList.remove('gg-rainbow')},5000)}});
/* 記事の読了でレベルアップ */
if(document.querySelector('.article-hero')){var got={};addEventListener('scroll',function(){var h=document.documentElement,p=h.scrollTop/(h.scrollHeight-h.clientHeight||1);
if(p>.5&&!got.a){got.a=1;toast('<b>LEVEL UP!</b> 半分読破')}if(p>.96&&!got.b){got.b=1;toast('<b>COMPLETE!</b> 最後まで読んでくれてありがとう');confetti(90)}},{passive:true})}
/* HEADSHOT */
document.addEventListener('pointerdown',function(e){var t=e.target.closest('.orb,.rk-img,.pc-img,.gear');if(!t||reduce)return;var d=document.createElement('div');d.className='gg-hs';d.textContent=Math.random()<.5?'HEADSHOT!':'NICE SHOT!';d.style.left=e.clientX+'px';d.style.top=e.clientY+'px';document.body.appendChild(d);
d.animate([{transform:'translate(-50%,-50%) scale(.6)',opacity:0},{transform:'translate(-50%,-120%) scale(1.15)',opacity:1,offset:.3},{transform:'translate(-50%,-220%) scale(1)',opacity:0}],{duration:900,easing:'ease-out'}).onfinish=function(){d.remove()}},true);
/* マグネットボタン */
if(matchMedia('(pointer:fine)').matches&&!reduce){document.querySelectorAll('.btn.primary,.shine-btn,.start,.mega-cta em').forEach(function(b){b.addEventListener('mousemove',function(e){var r=b.getBoundingClientRect();b.style.translate=((e.clientX-r.left-r.width/2)*.18)+'px '+((e.clientY-r.top-r.height/2)*.28)+'px'});b.addEventListener('mouseleave',function(){b.style.translate=''})})}
/* 初回だけ隠しコマンドのヒント */
try{if(!localStorage.getItem('ggHint')&&matchMedia('(pointer:fine)').matches){setTimeout(function(){toast('ヒント：このサイトには<b>隠しコマンド</b>があるらしい…')},9000);localStorage.setItem('ggHint','1')}}catch(e){}
})();
(function(){var S=new Date('2026-11-19T20:00:00+09:00').getTime(),E=new Date('2026-11-25T01:59:59+09:00').getTime(),now=Date.now();if(now>E)return;if(/blackfriday\.html/.test(location.pathname))return;
try{if(sessionStorage.getItem('bfBarClosed'))return}catch(e){}
var b=document.createElement('a');b.className='bf-bar';b.href='blackfriday.html';b.innerHTML='<span class="bf-k">BLACK FRIDAY</span><span class="bf-t"></span><span class="bf-go">攻略ページ →</span><button type="button" aria-label="閉じる">×</button>';
document.body.insertBefore(b,document.body.firstChild);document.documentElement.classList.add('has-bf');
b.querySelector('button').addEventListener('click',function(e){e.preventDefault();e.stopPropagation();b.remove();document.documentElement.classList.remove('has-bf');try{sessionStorage.setItem('bfBarClosed','1')}catch(x){}});
var t=b.querySelector('.bf-t');function p(n){return n<10?'0'+n:n}
function u(){var n=Date.now(),live=n>=S,r=(live?E:S)-n;if(r<=0&&live){b.remove();return}var d=Math.floor(r/864e5),h=Math.floor(r%864e5/36e5),m=Math.floor(r%36e5/6e4),s=Math.floor(r%6e4/1e3);
t.innerHTML=(live?'楽天ブラックフライデー開催中！終了まで ':'楽天ブラックフライデーまで ')+'<b>'+(d?d+'日 ':'')+p(h)+':'+p(m)+':'+p(s)+'</b>'}u();setInterval(u,1000)})();

(function(){
var d=document,main=d.querySelector('main');if(!main)return;
/* 共有ボタン */
var meta=d.querySelector('.article-hero .meta');
if(meta&&!d.querySelector('.gg-share')){var u=encodeURIComponent(location.href.split('#')[0].split('?')[0]),t=encodeURIComponent(d.title);
var s=d.createElement('div');s.className='gg-share';
s.innerHTML='<a href="https://twitter.com/intent/tweet?url='+u+'&text='+t+'" target="_blank" rel="noopener">Xでシェア</a><a href="https://social-plugins.line.me/lineit/share?url='+u+'" target="_blank" rel="noopener">LINEで送る</a><a href="https://b.hatena.ne.jp/entry/panel/?url='+u+'" target="_blank" rel="noopener">はてブ</a><button type="button">URLをコピー</button>';
s.querySelector('button').onclick=function(){var b=this;(navigator.clipboard?navigator.clipboard.writeText(decodeURIComponent(u)):Promise.reject()).then(function(){b.textContent='コピーしました'},function(){b.textContent='コピーできませんでした'})};
meta.after(s)}
/* 目次 */
var c=d.querySelector('.article-hero')&&d.querySelector('section:not(.article-hero) .content');
if(c&&!d.querySelector('.toc,.gg-toc')){var hs=[].slice.call(c.querySelectorAll(':scope > h2')).filter(function(h){return !/よくある質問|あわせて読みたい/.test(h.textContent)});
if(hs.length>=3){var o='';hs.forEach(function(h,i){if(!h.id)h.id='s'+(i+1);o+='<li><a href="#'+h.id+'">'+h.textContent+'</a></li>'});
var tc=d.createElement('nav');tc.className='gg-toc';tc.setAttribute('aria-label','目次');tc.innerHTML='<b>目次</b><ol>'+o+'</ol>';
var anchor=c.querySelector(':scope > .quick')||c.querySelector(':scope > .note')||c.querySelector(':scope > .lead');if(anchor)anchor.after(tc)}}
/* トップへ戻る */
var tp=d.createElement('button');tp.className='gg-top';tp.type='button';tp.setAttribute('aria-label','ページの先頭へ');tp.textContent='↑';tp.onclick=function(){scrollTo({top:0,behavior:'smooth'})};d.body.appendChild(tp);
addEventListener('scroll',function(){tp.classList.toggle('on',scrollY>800)},{passive:true});
/* 記事一覧：検索とジャンル絞り込み */
var cards=[].slice.call(d.querySelectorAll('.cards .acard'));
if(/archive\.html/.test(location.pathname)&&cards.length){var box=cards[0].parentNode;
var f=d.createElement('div');f.className='gg-find';f.id='search';f.innerHTML='<input type="search" placeholder="記事をさがす（例：マウス、加湿器、VALORANT）" aria-label="記事を検索">';
var G=[['すべて',''],['ゲーミング','VALORANT|MOUSE|KEYBOARD|EARPHONE|MONITOR|CHAIR|マウス|感度|ゲーム|FPS|コントローラー'],['暮らし・家電','加湿器|電気毛布|暖房|暮らし'],['スマホ・充電','スマホ|充電|バッテリー|USB-C'],['PC・トラブル','Windows|キーボード|モニター|Bluetooth|接続'],['VR','VR|Quest|PICO'],['ツール','ツール|診断|テスト|トレーニング|計算']];
var ch=d.createElement('div');ch.className='gg-chips';ch.innerHTML=G.map(function(g,i){return '<button type="button"'+(i?'':' class="on"')+' data-r="'+g[1]+'">'+g[0]+'</button>'}).join('');
var none=d.createElement('p');none.className='gg-none';none.textContent='見つかりませんでした。別の言葉で探してみてください。';
box.before(f);box.before(ch);box.after(none);var inp=f.querySelector('input'),re='';
function run(){var q=inp.value.trim().toLowerCase(),n=0;cards.forEach(function(a){var t=a.textContent.toLowerCase(),ok=(!q||t.indexOf(q)>=0)&&(!re||new RegExp(re,'i').test(a.textContent));a.style.display=ok?'':'none';if(ok)n++});none.style.display=n?'none':'block'}
inp.addEventListener('input',run);ch.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;ch.querySelectorAll('button').forEach(function(x){x.classList.remove('on')});b.classList.add('on');re=b.dataset.r;run()});
var q0=new URLSearchParams(location.search).get('q');if(q0){inp.value=q0;run()}}
})();
