/* 관심기업 페이지: 매일 갱신되는 주가(prices.json)로 주가 연동 가치평가 지표를 다시 계산해 보여준다.
   실적 숫자(이익·현금흐름·순현금·NAV)는 분석 기준일 값 그대로이고, 주가만 바뀐다고 가정한다. */
(function(){
  var slug=(location.pathname.match(/companies\/([^\/]+)\//)||[])[1];
  if(!slug)return;
  var css=document.createElement('style');
  css.textContent=
  '.lp{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin:14px 0 4px}'+
  '.lp h3{margin:0 0 2px;font-size:1rem}.lp .sub{font-size:.8rem;color:var(--muted);margin:0 0 10px}'+
  '.lp .row1{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:flex-end;margin-bottom:8px}'+
  '.lp .px{font-size:1.6rem;font-weight:700;font-family:var(--mono,monospace)}'+
  '.lp .chg{font-size:.92rem;font-weight:600}.lp .up{color:#c0392b}.lp .dn{color:#2a6fd6}'+
  '@media (prefers-color-scheme: dark){.lp .up{color:#ef7a6b}.lp .dn{color:#6aa6f5}}'+
  '.lp svg{display:block;width:100%;max-width:340px;height:46px}'+
  '.lp table{width:100%;border-collapse:collapse;font-size:.84rem;margin-top:6px}'+
  '.lp th,.lp td{padding:5px 4px;border-top:1px solid var(--line);text-align:right;white-space:nowrap}'+
  '.lp th:first-child,.lp td:first-child{text-align:left;white-space:normal}'+
  '.lp th{color:var(--muted);font-weight:600;font-size:.76rem}'+
  '.lp .tw{overflow-x:auto}.lp .sc{margin-top:10px;font-size:.9rem}.lp .sc b{font-size:1.05rem}'+
  '.lp .note{font-size:.76rem;color:var(--muted);margin-top:8px;line-height:1.5}'+
  '.lp a{color:inherit}';
  document.head.appendChild(css);

  function J(u){return fetch(u,{cache:'no-store'}).then(function(r){if(!r.ok)throw 0;return r.json()}).catch(function(){return null})}
  Promise.all([J('../base.json'),J('../prices.json'),J('../../market/data.json'),J('../earnings.json')]).then(function(a){
    var B=a[0]&&a[0][slug],P=a[1]&&a[1].prices&&a[1].prices[slug],M=a[2],E=a[3]&&a[3].companies&&a[3].companies[slug];
    if(!B||!P||!P.points||!P.points.length)return;
    render(B,P,M,E);
  });

  function clip(v){return Math.max(0,Math.min(1,v))}
  var RULES={cn_ev:function(x){return clip((25-x)/20)},pe:function(x){return clip((25-x)/17)},
    cn_yield:function(y){return clip(y/0.10)},nc:function(y){return clip(y/0.5)},
    en_ev:function(x){return clip((5-x)/2.5)},en_yield:function(y){return clip(y/0.20)},
    pnav:function(x){return clip((1.5-x)/1)}};
  function cur(c,v){var d=c==='KRW'?0:2;var s=v.toLocaleString('ko-KR',{minimumFractionDigits:d,maximumFractionDigits:d});
    return c==='KRW'?'₩'+s:c==='HKD'?'HK$'+s:'$'+s}
  function fmtX(k,x){if(x===null||x===undefined||!isFinite(x))return '—';
    return /수익률|순현금/.test(k)?(x*100).toFixed(1)+'%':x.toFixed(/NAV/.test(k)?2:1)+'배'}
  function tier(v){return v>=8?'sc-g':v>=6?'sc-y':'sc-r'}
  function last(s){return s&&s.points&&s.points.length?s.points[s.points.length-1]:null}

  function render(B,P,M,E){
    var pts=P.points,lp=pts[pts.length-1],p1=lp[1],p0=B.price,r=p1/p0;
    var c=P.currency, dPct=(r-1)*100;
    var evR=(B.ev+B.mcap*(r-1))/B.ev;   // 순현금(순부채)은 고정, 시가총액 변화만큼 EV 변화
    var rows=[],vp=B.val_pillar,newPil=null;
    if(vp){
      newPil=0;
      vp.items.forEach(function(it){
        var x1=it.x;
        if(it.move==='ev')x1=it.x*evR; else if(it.move==='price')x1=it.x*r; else if(it.move==='inv')x1=it.x/r;
        var pts1=it.rule?RULES[it.rule](x1):it.pts;
        if(it.move==='ev'&&B.kind==='cn'&&B.ev+B.mcap*(r-1)<=0)pts1=1;
        newPil+=pts1;
        rows.push([it.k,it.x===null?it.val:fmtX(it.k,it.x),it.move==='fixed'?(it.x===null?it.val:fmtX(it.k,it.x))+' (실적 지표)':fmtX(it.k,x1),it.pts.toFixed(2),pts1.toFixed(2)]);
      });
    }
    // 에너지: 현재 유가 기준 NAV(참고, 점수 미반영)
    var navLive='';
    if(B.kind==='energy'&&B.nav_sec!=null&&B.nav_per10!=null&&M&&M.series){
      var key=B.nav_bench==='Brent'?'brent_front':'wti_front',o=last(M.series[key]);
      if(o){var nav=B.nav_sec+(o[1]-B.nav_oil0)*B.nav_per10/10;
        navLive='<p class="note">참고: 현재 '+B.nav_bench+' 근월물 $'+o[1].toFixed(2)+'('+o[0]+')가 장기간 유지된다고 가정한 세후 NAV는 주당 약 $'+nav.toFixed(2)+
        (nav>0?', 주가/NAV '+(p1/nav).toFixed(2)+'배':'(마이너스)')+'입니다. 점수에는 SEC 기준가 NAV만 씁니다.</p>';}
    }
    // 스파크라인: 분석 기준일 90일 전부터
    var from=new Date(B.date);from.setDate(from.getDate()-90);var fs=from.toISOString().slice(0,10);
    var sp=pts.filter(function(p){return p[0]>=fs});
    var lo=Math.min.apply(null,sp.map(function(p){return p[1]})),hi=Math.max.apply(null,sp.map(function(p){return p[1]}));
    var W=340,H=46,X=function(i){return i/(sp.length-1||1)*(W-4)+2},Y=function(v){return H-3-(v-lo)/((hi-lo)||1)*(H-6)};
    var path=sp.map(function(p,i){return (i?'L':'M')+X(i).toFixed(1)+' '+Y(p[1]).toFixed(1)}).join('');
    var bi=sp.findIndex(function(p){return p[0]>=B.date});
    var mark=bi>=0?'<line x1="'+X(bi)+'" x2="'+X(bi)+'" y1="0" y2="'+H+'" stroke="currentColor" stroke-opacity=".35" stroke-dasharray="2 2"/>':'';
    var svg='<svg viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="none" aria-label="최근 주가 추이"><path d="'+path+'" fill="none" stroke="var(--accent,#2a78d6)" stroke-width="1.6"/>'+mark+'</svg>';

    var sc='';
    if(vp){
      var tot=vp.others+newPil;
      sc='<div class="sc">가치평가 '+vp.score.toFixed(2)+' → <b>'+newPil.toFixed(2)+'</b> / '+vp.max+
         ' · 종합 매력도(주가 반영 추정) <b class="'+tier(tot)+'" style="color:var(--sc)">'+tot.toFixed(1)+'</b> <span style="color:var(--muted)">(분석 시점 '+(B.score!=null?B.score.toFixed(1):'—')+')</span></div>';
    }
    var html='<h3>오늘 주가 반영</h3><p class="sub">매일 시장 지표와 함께 자동 갱신 · 분석 기준일 '+B.date+' 대비</p>'+
      '<div class="row1"><div><div class="px">'+cur(c,p1)+'</div><div style="font-size:.78rem;color:var(--muted)">'+lp[0]+' 종가 · <a href="'+P.link+'" target="_blank" rel="noopener">출처</a></div></div>'+
      '<div class="chg '+(dPct>=0?'up':'dn')+'">'+(dPct>=0?'+':'')+dPct.toFixed(1)+'%<div style="font-size:.76rem;color:var(--muted);font-weight:400">분석 시점 '+cur(c,p0)+'</div></div>'+
      '<div style="flex:1;min-width:180px">'+svg+'<div style="font-size:.72rem;color:var(--muted)">점선 = 분석 기준일</div></div></div>'+
      (rows.length?'<div class="tw"><table><thead><tr><th>가치평가 항목</th><th>분석 시점</th><th>현재 주가</th><th>점수</th></tr></thead><tbody>'+
        rows.map(function(x){return '<tr><td>'+x[0]+'</td><td>'+x[1]+'</td><td>'+x[2]+'</td><td>'+(x[3]===x[4]?x[4]:x[3]+'→'+x[4])+'</td></tr>'}).join('')+'</tbody></table></div>':'')+
      sc+navLive+(E?'<p class="note"><b>실적 반영:</b> 현재 분석은 '+E.reflected_period+' 실적까지 반영 · 다음 발표 '+E.period+' '+E.date+' ('+E.status+(E.kind?', '+E.kind:'')+')'+(E.next?' / '+E.next.date+' ('+E.next.status+', '+E.next.kind+')':'')+'. 발표 후 실적보고서를 확인해 분석을 갱신합니다.</p>':'')+
      '<p class="note">이익·현금흐름·순현금·순부채·NAV는 최근 실적보고서 기준 그대로 두고 주가만 바꿔 다시 계산한 추정치입니다. 이 페이지의 나머지 분석은 실적 발표 후 갱신됩니다. 투자 권유가 아닙니다.</p>';
    var box=document.createElement('section');box.className='lp';box.id='livePrice';box.innerHTML=html;
    var hd=document.querySelector('header.page');
    if(hd)hd.insertAdjacentElement('afterend',box);else document.querySelector('main').prepend(box);
  }
})();
