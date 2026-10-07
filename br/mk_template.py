s = open('../hk3/template_hk3.html', encoding='utf-8').read()
R = []
def rep(a, b, cnt=1):
    global s
    n = s.count(a)
    assert n >= 1, ('missing', a[:80])
    if cnt == 1: assert n == 1, ('multi', n, a[:80])
    s = s.replace(a, b)
# verification text
rep('홍콩 상장사는 XBRL이 없어 네 가지 방법으로 확인했습니다. ① HKEX 원본 PDF를 서로 모르는 두 에이전트가 따로 추출해 대조, ② 합계 검증(부문 합 = 총계, 회사 제시 순현금 재계산), ③ 분기 정합(1분기 + 2분기 = 상반기), ④ 상식 범위 검사.',
    '분기 실적은 XBRL이 없는 6-K(보도자료·재무제표)라 네 가지 방법으로 확인했습니다. ① SEC 원본 HTML(표가 이미지인 쪽은 페이지 이미지)을 서로 모르는 두 에이전트가 따로 추출해 대조, ② 합계 검증(부문 합 = 총계, 회사 제시 순부채 재계산), ③ 분기 정합(1분기 + 2분기 = 상반기), ④ 상식 범위 검사. 연간 추이는 20-F의 XBRL 태그 값입니다.')
rep('<span class="sq" style="background:var(--s1)"></i>매출</span>', '<span class="sq" style="background:var(--s1)"></i>__LEG1__</span>') if '<span class="sq" style="background:var(--s1)"></i>매출</span>' in s else None
rep('<span><i class="sq" style="background:var(--s1)"></i>매출</span><span><i class="sq" style="background:var(--s3)"></i>__LEG3__</span>', '<span><i class="sq" style="background:var(--s1)"></i>__LEG1__</span><span><i class="sq" style="background:var(--s3)"></i>__LEG3__</span>')
rep('<h2><small>05</small>상장 이후 주가와 매크로</h2>', '<h2><small>05</small>장기 주가와 매크로</h2>')
rep('<button data-k="oil" aria-pressed="true">항셍지수</button>', '<button data-k="oil" aria-pressed="true">EWZ</button>')
rep('<h3>연도별 수익률: 주가 vs 항셍지수</h3>', '<h3>연도별 수익률: 주가 vs 브라질 ETF(EWZ)</h3>')
rep('<span><i style="background:var(--s2)"></i>위안화 약세(USD/CNY)</span>', '<span><i style="background:var(--s2)"></i>헤알 약세(USD/BRL)</span>')
rep('직전 252거래일로 추정한 매크로 모델(S&amp;P 500, 위안화, 구리, 10년 금리, 달러, VIX)의 예측치가(미국 지표는 홍콩 장보다 늦게 끝나므로 전날 미국장 값을 씀) 실제 움직임의 절반 이상이면',
    '직전 252거래일로 추정한 매크로 모델(S&amp;P 500, 헤알, 구리, 10년 금리, 달러, VIX)의 같은 날 예측치가 실제 움직임의 절반 이상이면')
rep('같은 날 항셍지수가 3% 이상 또는 미국 상장 중국 인터넷 ETF(KWEB, 2013년 이전은 FXI)가 5% 이상 같은 방향으로 움직여 급변동의 절반 이상을 설명하는 날은 <b>중국 공통 충격</b>(정책·규제 등 업종 전체 사건)으로 분류했습니다.',
    '같은 날 브라질 ETF(EWZ)가 3% 이상 또는 신흥국 ETF(EEM)가 5% 이상 같은 방향으로 움직여 급변동의 절반 이상을 설명하는 날은 <b>브라질 공통 충격</b>(선거·재정·정책 등 시장 전체 사건)으로 분류했습니다.')
rep('<span><i class="dot" style="background:var(--s5)"></i>중국 공통 충격</span>', '<span><i class="dot" style="background:var(--s5)"></i>브라질 공통 충격</span>')
rep('사실은 HKEX 원본 공시(PDF)에서 확인했습니다.', '사실은 SEC 원본 공시(6-K HTML)에서 확인했습니다.')
rep('민감도(주간 회귀, S&amp;P 500 통제): 위안화 1% 강세 → 주가 약 <b id="sensOil"></b>', '민감도(주간 회귀, S&amp;P 500 통제): 헤알 1% 강세 → 주가 약 <b id="sensOil"></b>')
rep('이선철 대표 프레임워크는 중국/홍콩 주식을 강세로 보며, 과거 6개월 적중률(69% vs 무작위 49%)이 가장 높았던 자산입니다',
    '이선철 대표 프레임워크는 신흥국 주식을 강세로 보며, 신흥국 강세 신호의 과거 6개월 적중률은 80%(무작위 66%)였습니다. 신흥국 가운데 원자재와 연결된 브라질을 가장 선호한다고 밝혀 왔습니다(<a href="../../etfs/ewz/index.html">EWZ 노트</a>)')
rep('<li>중국/홍콩 주식: <b>강세</b>. 신호와 과거 신뢰도(6개월 69% vs 49%)가 함께 높은 유일한 자산입니다.</li><li>논리: 시장이 "지옥을 할인하고 있는 버려진 현금흐름 자산". AI·반도체 버블 조정 과정에서 홍콩 온라인 플랫폼이 수혜를 본다는 주장입니다(26.07.07).</li><li>확인 조건: 중국 8~9월 수입 반등(수요 정상화, #436). 미국 주식·성장주는 약세로 봅니다.</li><li>2026년 10월 추가 판단: 미국 장기 실질금리 하락이 중국 플랫폼·테크 반등의 가장 중요한 대외 요인입니다. 유가를 따라 기대인플레(BEI)가 오르면 명목금리가 올라도 실질금리는 내려갈 수 있다고 봅니다.</li>',
    '<li>신흥국 주식: <b>강세</b>(6개월 적중률 80% vs 무작위 66%). 미국에서 신흥국으로의 자금 이동을 전망하며, 신흥국 가운데 원자재와 연결된 브라질을 가장 선호합니다.</li><li>논리: 원자재 슈퍼사이클, 매력적인 밸류에이션, 선제적 인플레이션 대응, 달러 약세 전환 시 상승 가속(2022~2026년 칼럼).</li><li>2026년 10월 판단: 미국 장기 실질금리가 내려가면 중국과 함께 브라질이 가장 큰 수혜를 볼 나라로 봅니다. 단기 등락은 충분히 가능하다고 봤습니다. 미국 주식은 약세로 봅니다.</li><li>칼럼은 개별 브라질 기업을 투자 대상으로 거명하지 않았고, 브라질 전체(EWZ)를 언급했습니다.</li>')
rep('프레임워크 항목은 중국/홍콩 강세 신호(1.5점, 공통), 저자의 종목 거명(0.25~0.5점), 위안화 강세 수혜(0~0.5점), 미국 실질금리 하락 수혜(0~0.5점, 2026년 10월 추가)로 구성됩니다. 에너지 종목과는 기준이 달라 점수를 서로 비교하지 않습니다.',
    '프레임워크 항목은 신흥국(브라질) 강세 신호(1.5점, 공통), 저자의 종목 거명(0.25~0.5점), 헤알 강세 수혜(0~0.5점), 미국 실질금리 하락 수혜(0~0.5점)로 구성됩니다. 가치평가는 비금융 기업(EV/EBITDA·PER·FCF 수익률·순부채/EBITDA)과 은행·핀테크(P/B·PER·주주환원수익률·ROE)에 다른 항목을 씁니다. 중국·에너지 종목과는 기준이 달라 점수를 서로 비교하지 않습니다.')
rep('<li>매크로: FRED(WTI 현물, 10년 금리, Baa−10년 스프레드, 10년 BEI), Yahoo(S&amp;P 500, 달러지수, VIX, USD/CNY, USD/HKD, 구리 선물, 항셍지수, KWEB·FXI). 항셍지수는 이 종목들을 포함하므로 회귀 변수에서 빼고 비교용으로만 썼습니다.</li>',
    '<li>매크로: FRED(WTI 현물, 10년 금리, 10년 실질금리, Baa−10년 스프레드, 10년 BEI), Yahoo(S&amp;P 500, 달러지수, VIX, USD/BRL, 구리 선물, EWZ, EEM). EWZ는 이 종목들을 포함하므로 회귀 변수에서 빼고 비교용으로만 썼습니다.</li>')
rep('<li>__FINSRC__</li><li>홍콩 종목의 일간 급변동 모델은 미국 지표를 하루 늦춰 맞췄기 때문에, 미국 상장 중국 종목(ADR)보다 "비매크로" 비중이 구조적으로 크게 나옵니다.</li>',
    '<li>__FINSRC__</li><li>미국 상장 ADR은 달러로 거래되므로 주가에 헤알 환율이 함께 들어 있습니다. 헤알 베타가 크게 나오는 이유 가운데 일부는 이 환산 효과입니다.</li>')
# JS
rep("const oilName='항셍지수';", "const oilName='EWZ';const PX=P.pxcur;")
rep("SH={SPX:'S&P 500',OIL:'WTI',CNY:'위안화',", "SH={SPX:'S&P 500',OIL:'WTI',CNY:'헤알',")
rep("(¥ 백만)", "(${P.cs} 백만)")
rep("tile('분석 시작',S.start,'HK$'+S.p0.toFixed(2)+'(수정주가)')", "tile('분석 시작',S.start,PX+S.p0.toFixed(2)+'(수정주가)')")
rep("tile('최고가','HK$'+S.peak.toFixed(2),S.peak_date),tile('같은 기간 항셍지수',pct(S.xle_cagr)+'/년','가격지수(배당 제외)')", "tile('최고가',PX+S.peak.toFixed(2),S.peak_date),tile('같은 기간 EWZ',pct(S.xle_cagr)+'/년','수정가(배당 반영)')")
rep("<span>HK$${s.p[i].toFixed(2)}</span>", "<span>${PX}${s.p[i].toFixed(2)}</span>")
rep("주가와 항셍지수가 같은 방향이었습니다. 분기 수익률 상관: 항셍지수 ", "주가와 EWZ가 같은 방향이었습니다. 분기 수익률 상관: EWZ ")
rep("<th class=\"num\">위안화 상관</th><th class=\"num\">위안화 베타</th>", "<th class=\"num\">헤알 상관</th><th class=\"num\">헤알 베타</th>")
rep("<div class=\"r\"><span>위안화</span><span>${f(R.c_oil[i])}</span></div>", "<div class=\"r\"><span>헤알 약세</span><span>${f(R.c_oil[i])}</span></div>")
rep("const TCOL={'매크로':'--s1','매크로 충격':'--s3','중국 공통 충격':'--s5'", "const TCOL={'매크로':'--s1','매크로 충격':'--s3','브라질 공통 충격':'--s5'")
rep("tile('매크로·중국 공통',(c['매크로']+c['매크로 충격']+(c['중국 공통 충격']||0))+'일','중국 공통 '+(c['중국 공통 충격']||0)+'일')", "tile('매크로·브라질 공통',(c['매크로']+c['매크로 충격']+(c['브라질 공통 충격']||0))+'일','브라질 공통 '+(c['브라질 공통 충격']||0)+'일')")
rep("<div class=\"r\"><span>위안화 당일</span><span>${pct(e.oil)}</span></div><div class=\"r\"><span>항셍·KWEB 당일</span>", "<div class=\"r\"><span>USD/BRL 당일</span><span>${pct(e.oil)}</span></div><div class=\"r\"><span>EWZ·EEM 당일</span>")
rep("<th class=\"num\">항셍·KWEB</th>", "<th class=\"num\">EWZ·EEM</th>")
rep("$('snapTiles').innerHTML=[f('CNY',3,''),f('HSI',0,''),f('UST10',2,'%',true),f('VIX',1,''),f('USD',1,''),f('COPPER',2,'$')].join('');",
    "$('snapTiles').innerHTML=[f('BRL',3,''),f('EWZ',2,'$'),f('RR',2,'%',true),f('UST10',2,'%',true),f('VIX',1,''),f('COPPER',2,'$')].join('');")
rep("peers.map(([k,v])=>`<div class=\"row${k===P.ticker?' me':''}\">", "peers.map(([k,v])=>`<div class=\"row${k===P.peername?' me':''}\">")
rep("'<div class=\"small\">같은 기준의 관심 종목(같은 업종)</div>'", "'<div class=\"small\">같은 기준의 관심 종목(브라질 ADR)</div>'")
# hero tiles
a = s.index("// hero tiles"); b = s.index("// verification")
s = s[:a] + r"""// hero tiles
$('heroTiles').innerHTML=[
 `<a class="tile" href="#score" style="text-decoration:none;border-color:var(--accent)"><span class="l">종합 매력도</span><span class="v">${P.score.total.toFixed(1)} / 10</span><span class="d">규칙 기반 학습용 점수</span></a>`,
 tile('주가 ('+(+S.last.slice(5,7))+'/'+(+S.last.slice(8))+')',PX+S.p1.toFixed(2),'분석 시작 이후 '+pct(S.tr,0)),
 tile('시가총액',P.cs+(VA.mktcap_m/1000).toFixed(0)+'B',P.cs==='R$'?'약 US$'+P.cnval.mcap_usd_b.toFixed(0)+'B':(VA.shares_m).toFixed(0)+'M주'),
 ...(P.cnval.kind==='bank'?[tile('P/B',P.cnval.pb.toFixed(2)+'배','지배주주지분 기준'),tile('PER('+P.cnval.ni_label.split('(')[0]+')',P.cnval.pe.toFixed(1)+'배','최근 반기 연환산')]
  :[tile('EV/EBITDA',P.cnval.ev_op.toFixed(1)+'배',(P.cnval.eb_label.match(/\((.*)\)/)||['',''])[1]),tile('PER('+P.cnval.ni_label.split('(')[0]+')',P.cnval.pe?P.cnval.pe.toFixed(1)+'배':'적자',(P.cnval.ni_label.match(/\((.*)\)/)||['',''])[1])]),
 tile('주가 설명력 1위',FL[Object.entries(P.eda.full.shapley).sort((a,b)=>b[1]-a[1])[0][0]],'Shapley 몫 '+Math.round(Math.max(...Object.values(P.eda.full.shapley))/P.eda.full.r2*100)+'%')].join('');

""" + s[b:]
# scenario block
a = s.index("// NAV scenarios"); b = s.index("function drawAll()")
s = s[:a] + r"""// valuation scenarios
(function(){const V=P.cnval,S=P.scen;const f=v=>v==null?'–':PX+v.toFixed(2);const pr=V.price;const cs=P.cs;const B=v=>cs+(Math.abs(v)>=1000?(v/1000).toFixed(1)+'B':v.toFixed(0)+'M');
 if(V.kind==='bank'){
  $('scLead2').innerHTML=`지금 주가 ${f(pr)}는 ADR 1주당 순자산(${f(S.rows[0].eps)})의 <b>${S.implied.toFixed(2)}배</b>, 연환산 이익의 <b>${S.implied_pe.toFixed(1)}배</b>입니다. 아래 표는 P/B를 바꿔 가며 주당 순자산에 곱해 본 <b>참고 계산(목표주가 아님)</b>입니다. 은행은 ROE가 높을수록 높은 P/B를 받는 경향이 있습니다(지금 ROE ${(V.roe*100).toFixed(1)}%).`;
  $('cnTiles').innerHTML=[tile('시가총액',cs+V.mcap_b.toFixed(0)+'B',(cs==='R$'?'약 US$'+V.mcap_usd_b.toFixed(0)+'B · ':'')+V.ads_m.toFixed(0)+'M주'),tile('지배주주지분',B(V.eq),'2026-06-30'),tile('P/B',V.pb.toFixed(2)+'배',''),tile('PER('+V.ni_label.split('(')[0]+')',V.pe.toFixed(1)+'배',(V.ni_label.match(/\((.*)\)/)||['',''])[1]),tile(V.roe_label.split('(')[0],(V.roe*100).toFixed(1)+'%',''),tile('주주환원수익률',(V.ret_yield*100).toFixed(1)+'%','최근 반기 연환산'),tile('CET1',V.cet1.toFixed(1)+'%','보통주자본비율')].join('');
  $('cnTbl').innerHTML='<caption style="text-align:left;font-weight:600;padding:6px 0">참고 계산(목표주가 아님): P/B × 주당 순자산</caption><tr><th>기준</th><th class="num">ADR 1주당</th>'+S.mults.map(m=>`<th class="num">P/B ${m.toFixed(1)}배</th>`).join('')+'</tr>'+S.rows.map(r=>`<tr><td>${r.label}</td><td class="num">${f(r.eps)}</td>${r.vals.map(v=>`<td class="num">${f(v)}</td>`).join('')}</tr>`).join('')+`<tr><td colspan="${2+S.mults.length}" class="small">현재 주가 ${f(pr)} · 값 = P/B × 주당 순자산(2026-06-30 지배주주지분 ÷ 주식 수${cs==='R$'?', 1달러 = R$'+V.usdbrl.toFixed(3)+'로 환산':''}).</td></tr>`;
  $('cnMethod').innerHTML=`<ul class="tight"><li><b>시가총액</b> = ADR 가격 × 주식 수${cs==='R$'?' × USD/BRL '+V.usdbrl.toFixed(3):''}. ${V.ads_note}.</li><li><b>이익</b>: ${V.ni_label}. <b>ROE</b>: ${V.roe_label}.</li><li><b>주주환원</b>: ${V.ret_label}.</li><li><b>P/B 1.0·1.5·2.0배는 가정이며, 표의 값은 목표주가가 아닌 참고 계산입니다.</b></li></ul>`;
 } else {
  $('scLead2').innerHTML=S.implied?`지금 주가 ${f(pr)}는 ADR 1주당 ${V.ni_label}(${f(S.rows[0].eps)})의 <b>${S.implied.toFixed(1)}배</b>입니다. 아래 표는 PER을 바꿔 가며 EPS에 곱해 본 <b>참고 계산(목표주가 아님)</b>입니다.`:`최근 이익이 마이너스라 PER로 계산하지 않았습니다.`;
  $('cnTiles').innerHTML=[tile('시가총액',cs+V.mcap_b.toFixed(0)+'B',(cs==='R$'&&PX!=='R$'?'약 US$'+V.mcap_usd_b.toFixed(0)+'B · ':'')+V.ads_m.toFixed(0)+'M주'),tile(V.nd>=0?'순부채':'순현금',B(Math.abs(V.nd)),'회사 제시'),tile('EV',cs+V.ev_b.toFixed(0)+'B','시가총액 + 순부채'),tile('EV/EBITDA',V.ev_op.toFixed(1)+'배',(V.eb_label.match(/\((.*)\)/)||['',''])[1]),tile('PER('+V.ni_label.split('(')[0]+')',V.pe?V.pe.toFixed(1)+'배':'적자',(V.ni_label.match(/\((.*)\)/)||['',''])[1]),tile('FCF 수익률',(V.fcf_yield*100).toFixed(1)+'%',(V.cf_label.match(/\((.*)\)/)||['',''])[1]),tile('순부채/EBITDA',V.nd_ebitda.toFixed(1)+'배',V.nd_ebitda<0?'순현금':'')].join('');
  $('cnTbl').innerHTML='<caption style="text-align:left;font-weight:600;padding:6px 0">참고 계산(목표주가 아님): PER × ADR 1주당 EPS</caption><tr><th>이익 기준</th><th class="num">ADR 1주당 EPS</th>'+S.mults.map(m=>`<th class="num">PER ${m}배</th>`).join('')+'</tr>'+S.rows.map(r=>`<tr><td>${r.label}</td><td class="num">${f(r.eps)}</td>${r.vals.map(v=>`<td class="num">${f(v)}</td>`).join('')}</tr>`).join('')+`<tr><td colspan="${2+S.mults.length}" class="small">현재 주가 ${f(pr)} · 값 = PER × EPS(ADR 1주 = 원주 ${V.adr}주${cs==='R$'&&PX!=='R$'?', 1달러 = R$'+V.usdbrl.toFixed(3)+'로 환산':''}).</td></tr>`;
  $('cnMethod').innerHTML=`<ul class="tight"><li><b>시가총액</b>: ${V.ads_note}.${cs==='R$'&&PX!=='R$'?' 달러 ADR 가격을 USD/BRL '+V.usdbrl.toFixed(3)+'로 헤알 환산했습니다.':''}</li><li><b>순부채</b>: ${V.nd_label}.</li><li><b>이익</b>: ${V.eb_label} · ${V.ni_label}.</li><li><b>현금흐름</b>: ${V.cf_label}.</li><li><b>PER 6·9·12배는 가정이며, 표의 값은 목표주가가 아닌 참고 계산입니다.</b></li></ul>`;
 }})();

""" + s[b:]
# glossary additions
rep("['ADS','미국예탁증서. 미국에 상장된 중국 기업 주식 묶음(알리바바·바이두 1 ADS = 보통주 8주, JD 1 ADS = 2주).'],",
    "['ADR','미국예탁증서. 해외 기업 주식을 묶어 미국 거래소에서 달러로 거래하게 한 증서. 1 ADR이 원주 몇 주인지는 회사마다 다릅니다.'],['ADS','미국예탁주식. ADR과 같은 뜻으로 씁니다(엠브라에르 1 ADS = 보통주 4주).'],['JCP','자기자본이자(Juros sobre Capital Próprio). 브라질 기업이 배당 대신 지급하는 주주환원으로, 회사는 비용으로 처리해 세금을 줄일 수 있습니다.'],['P/B','주가순자산비율. 시가총액 ÷ 자본. 은행을 비교할 때 주로 씁니다.'],['ROE','자기자본이익률. 순이익 ÷ 자본. 은행의 수익성 지표입니다.'],['CET1','보통주자본비율. 위험가중자산 대비 보통주자본 비율로, 은행의 손실 흡수력을 나타냅니다.'],['헤알','브라질 통화(R$). USD/BRL이 오르면 헤알 약세입니다.'],['EWZ','브라질 대형·중형주에 투자하는 미국 상장 ETF(iShares MSCI Brazil).'],['브라질 공통 충격','브라질 시장 전체(EWZ)나 신흥국 전체(EEM)가 같은 날 크게 움직인 경우. 선거·재정·정책 사건이 많습니다.'],['경상 순이익','은행이 일회성 항목을 뺀 이익(recurring managerial result). 회사 정의입니다.'],['B3','브라질 증권거래소(상파울루).'],")
rep("['중국 공통 충격','중국 인터넷 업종 전체가 같은 날 크게 움직인 경우. 주로 정책·규제 발표 때문입니다.'],\n", "")
rep("['항셍지수','홍콩 증시 대표 지수. 알리바바·JD 등이 포함돼 있습니다.'],\n", "")
open('template_br.html', 'w', encoding='utf-8').write(s)
import re
left = [m for m in ['항셍', '위안', 'HK$', 'HKEX', '홍콩', '중국'] if m in s]
print('leftover', left)
for m in left:
    for mm in re.finditer(re.escape(m), s): print('  ', m, s[max(0, mm.start()-80):mm.start()+60].replace('\n', ' '))
