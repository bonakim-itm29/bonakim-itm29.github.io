# 브라질 ADR 페이지 독립 사실 확인 ({LIST})

당신은 이 페이지를 만든 적이 없는 검증자입니다. 대상 페이지: /home/claude/bonakim-itm29.github.io/macro-notes/companies/{slug}/index.html (서술 원본: /mnt/user-data/outputs/fruiting/br/content_br_*.py 의 해당 키).

## 확인할 것
1. 서술(lead, thesis, elements, heads, macro_read, monitor, frame, vnote)의 모든 숫자를 근거와 대조:
   - 실적: /mnt/user-data/outputs/fruiting/br/data/verification.json ["rows"][원천 티커] (a/b 값), extract_SBS_IMG.json, data/ix20f.json(20-F 연간).
   - 필요하면 SEC 원문 /mnt/user-data/outputs/fruiting/br/raw/{원천 티커}/ (BeautifulSoup으로 표 구조 유지해 읽기, 이미지 표는 Read로 보기).
   - 주가·매크로·점수: /mnt/user-data/outputs/fruiting/br/data/page_data.json ["data"][키] (stats, eda.full, cnval, scen, score), data/rr_beta.json.
   - 이벤트: /mnt/user-data/outputs/fruiting/br/events_{원천 티커}.json 과 raw_events/ 원문.
   "(계산)" 표시된 값은 직접 다시 계산(python)해 반올림 범위(±0.1%p, ±1 단위) 안인지 본다.
2. 데이터에 근거 없는 사실(회사 역사, 시장점유율, 정책, 인물 등 기억으로 보충한 내용)이 있으면 지적.
3. 금지 사항: 투자 권유·목표주가 표현, 이선철 대표 1인칭, 칼럼 제목·번호·직접 인용, 변수명(R, fit, res, beta) 노출.
4. 단위·통화 혼동(US$ vs R$, 억/조, 백만), 전년비 방향(+/−), 기간 혼동(2분기 vs 상반기).

원천 티커: VALE, PBR, ITUB, NU, BBD, ABEV, SBS, ERJ(키 EMBJ), AXIA(키 AXIA3.SA).

## 출력
수정이 필요한 항목만 목록으로: (종목, 위치(필드·불릿 번호), 현재 문장 일부, 문제, 근거 값, 고친 문장 제안). 문제가 없으면 "문제 없음". 파일은 고치지 마세요. 한국어로, 항목당 2줄 이내.
