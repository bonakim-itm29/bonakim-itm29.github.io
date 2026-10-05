/* 종합 매력도 색 구분: 8점 이상 녹색, 6점 이상 노랑, 6점 미만 빨강 */
(function(){
  function tier(v){return v>=8?'g':v>=6?'y':'r'}
  var css=document.createElement('style');
  css.textContent='.sc-g{--sc:#2e7d4f}.sc-y{--sc:#b8860b}.sc-r{--sc:#c0392b}'+
  '@media (prefers-color-scheme: dark){.sc-g{--sc:#5fc58a}.sc-y{--sc:#e6b93d}.sc-r{--sc:#ef7a6b}}'+
  '.scorebox.sc-g .big,.scorebox.sc-y .big,.scorebox.sc-r .big{color:var(--sc)}'+
  '.scorebox.sc-g .gauge i,.scorebox.sc-y .gauge i,.scorebox.sc-r .gauge i{background:var(--sc)}'+
  '.sc-note{font-size:12px;color:var(--muted);margin-top:4px}';
  document.head.appendChild(css);
  function apply(){
    var el=document.getElementById('scTotal');if(!el||!el.textContent)return false;
    var v=parseFloat(el.textContent);if(isNaN(v))return false;
    var box=el.closest('.scorebox');if(!box)return true;
    box.classList.add('sc-'+tier(v));
    if(!box.querySelector('.sc-note')){var n=document.createElement('div');n.className='sc-note';
      n.textContent=(v>=8?'녹색':v>=6?'노랑':'빨강')+' 구간 · 기준: 8점 이상 녹색, 6점 이상 노랑, 6점 미만 빨강';
      box.querySelector('.gauge').after(n)}
    return true}
  if(!apply()){var t=setInterval(function(){if(apply())clearInterval(t)},150);setTimeout(function(){clearInterval(t)},5000)}
})();
