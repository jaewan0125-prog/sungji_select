#!/usr/bin/env python3
"""
Augment 냉각탑_선정프로그램_장비개요.html:
  - Add CSS for makeup-water and louver-area report bodies (reusing report-overlay)
  - Replace placeholder ovChooseDoc('makeup'/'louver') logic with full report generators
  - Add openMakeupReport() and openLouverReport() functions that populate the existing
    reportOverlay/reportBody (so they get the @media print formatting for free).
  - Auto-fills using the user's design inputs (Q, Tin, Tout, Twb) and the selected
    model's CMM × cells for louver.
"""
import re, os, sys

SRC = '냉각탑_선정프로그램_장비개요.html'
DST = SRC

with open(SRC, 'r', encoding='utf-8') as f:
    src = f.read()

# ---------- 1. Add CSS for makeup/louver report bodies ----------
# Insert just before the print @media block (line ~584 area in original)
# Actually, safer: insert before the very last @media (max-width: 760px) block in style
CSS_ADD = r"""
  /* ============ 보급수 / 루버 보고서 추가 스타일 (report-body 위에 얹음) ============ */
  .calc-meta {
    display: grid;
    grid-template-columns: repeat(2, minmax(0,1fr));
    gap: 8px 28px;
    font-size: 13px;
    margin-bottom: 18px;
    background: linear-gradient(135deg, #f8f9fb 0%, #eef2f7 100%);
    border: 1px solid #cfd8dc;
    border-radius: 6px;
    padding: 12px 16px;
  }
  .calc-meta .row { display: flex; gap: 10px; align-items: baseline; min-width: 0; }
  .calc-meta .row .k {
    color: #455a64; font-weight: 600;
    flex: 0 0 92px;
  }
  .calc-meta .row .v {
    flex: 1; color: #1a1a1a;
    font-family: 'Consolas', monospace; font-weight: 700;
    border-bottom: 1px dotted #cfd8dc; padding-bottom: 1px;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .calc-step {
    border: 1.5px solid #cfd8dc;
    border-radius: 6px;
    padding: 12px 16px 14px;
    margin-bottom: 12px;
    background: white;
  }
  .calc-step .step-head {
    display: flex; align-items: baseline; gap: 8px;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid #eceff1;
  }
  .calc-step .step-head .num {
    background: #1e3c72; color: white;
    width: 20px; height: 20px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 800;
    flex-shrink: 0;
  }
  .calc-step .step-head .t {
    font-size: 13px; font-weight: 800; color: #1e3c72; letter-spacing: 0.2px;
  }
  .calc-step .step-head .t .en {
    font-size: 11px; color: #78909c; font-weight: 500; letter-spacing: 0.3px;
    margin-left: 6px;
  }
  .calc-step .formula-line {
    font-family: 'Consolas', 'Cambria Math', monospace;
    background: #f8f9fb; border-left: 3px solid #2a5298;
    padding: 8px 12px; margin: 6px 0;
    font-size: 12.5px; color: #263248;
    border-radius: 0 4px 4px 0;
    overflow-x: auto;
  }
  .calc-step .formula-line .lhs { color: #c62828; font-weight: 700; }
  .calc-step .formula-line .res {
    color: #c62828; font-weight: 800; font-size: 13.5px;
    background: #fff8e1; padding: 1px 6px; border-radius: 3px;
    margin-left: 4px;
  }
  .calc-step .note {
    font-size: 11.5px; color: #546e7a;
    margin-top: 4px; line-height: 1.55;
    padding-left: 6px; border-left: 2px solid #eceff1;
  }
  .calc-result-card {
    background: linear-gradient(135deg, #fff8f8 0%, #ffe5e5 100%);
    border: 2px solid #c62828;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 14px 0 4px;
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 14px;
    align-items: center;
  }
  .calc-result-card .label {
    font-size: 11.5px; color: #c62828;
    font-weight: 800; letter-spacing: 0.5px;
  }
  .calc-result-card .label .sub { color: #546e7a; font-weight: 500; font-size: 10.5px; display: block; margin-top: 1px;}
  .calc-result-card .num {
    font-family: 'Consolas', monospace;
    font-size: 22px; font-weight: 800; color: #c62828;
    letter-spacing: -0.5px;
  }
  .calc-result-card .num .unit {
    font-size: 13px; color: #546e7a;
    font-weight: 500; margin-left: 4px;
  }
  .calc-table {
    width: 100%; border-collapse: collapse;
    font-size: 12.5px; margin-top: 4px;
  }
  .calc-table th, .calc-table td {
    border: 1px solid #b0bec5; padding: 6px 10px; text-align: center;
  }
  .calc-table thead th {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white; font-weight: 700; letter-spacing: 0.3px;
  }
  .calc-table tbody tr.highlight {
    background: #fff8e1; font-weight: 800;
  }
  .calc-table tbody tr.highlight td:first-child { color: #c62828; }
  .calc-criteria {
    background: #fffde7; border-left: 4px solid #f9a825;
    padding: 10px 14px; margin: 10px 0;
    font-size: 12px; line-height: 1.65; color: #5d4037;
    border-radius: 0 4px 4px 0;
  }
  .calc-criteria .crit-title { font-weight: 800; color: #ef6c00; margin-bottom: 4px; }
  .calc-criteria ul { margin: 4px 0 0 16px; padding: 0; }
  .calc-criteria li { margin-bottom: 2px; }

  /* 인쇄 시 추가 형식 보정 */
  @media print {
    .calc-meta { font-size: 9.5pt !important; padding: 8px 12px !important; }
    .calc-step { padding: 8px 12px 10px !important; margin-bottom: 8px !important; page-break-inside: avoid; }
    .calc-step .step-head .t { font-size: 10pt !important; }
    .calc-step .formula-line { font-size: 9.5pt !important; padding: 5px 9px !important; }
    .calc-result-card { padding: 9px 12px !important; margin: 9px 0 4px !important; page-break-inside: avoid; }
    .calc-result-card .num { font-size: 16pt !important; }
    .calc-table { font-size: 9pt !important; page-break-inside: avoid; }
    .calc-table th, .calc-table td { padding: 4px 7px !important; }
    .calc-criteria { font-size: 8.5pt !important; padding: 6px 11px !important; }
  }

"""

# Anchor: the ov-overlay rule we added previously, insert *before* it
ov_anchor = '  /* ============ 장비 개요 (Equipment Overview) 모달 ============ */'
assert ov_anchor in src
src = src.replace(ov_anchor, CSS_ADD + ov_anchor)


# ---------- 2. Replace the makeup/louver branches in ovChooseDoc ----------
OLD_BRANCHES = """  if (action === 'makeup') {
    openPh({
      headTitle: '보급수계산서 / Make-up Water Worksheet',
      icon: '💧',
      title: '보급수계산서',
      msg: '보급수계산서 자료는 추후 연결 예정입니다.<br>파일이 준비되면 이 위치에서 즉시 다운로드(또는 표시)할 수 있도록 연결됩니다.<br><br><span style="font-size:11.5px;color:#78909c;">※ 증발손실 + 비산손실 + 농축배수 합산 계산표</span>'
    });
    return;
  }
  if (action === 'louver') {
    openPh({
      headTitle: '루버면적검토서 / Louver Area Review',
      icon: '🪟',
      title: '루버면적검토서',
      msg: '루버면적검토서 자료는 추후 연결 예정입니다.<br>파일이 준비되면 이 위치에서 즉시 다운로드(또는 표시)할 수 있도록 연결됩니다.<br><br><span style="font-size:11.5px;color:#78909c;">※ 흡입풍속 / 유효 면적 / 압력손실 계산표</span>'
    });
    return;
  }"""

NEW_BRANCHES = """  if (action === 'makeup') {
    openMakeupReport(ctx.modelType, ctx.modelCRT, ctx.cells);
    return;
  }
  if (action === 'louver') {
    openLouverReport(ctx.modelType, ctx.modelCRT, ctx.cells);
    return;
  }"""

assert OLD_BRANCHES in src
src = src.replace(OLD_BRANCHES, NEW_BRANCHES)


# ---------- 3. Add openMakeupReport / openLouverReport functions ----------
# Insert just before the closing `</script>` (right before the keydown listener block)
INSERTION_ANCHOR = "document.addEventListener('keydown', (e) => {"
assert INSERTION_ANCHOR in src

NEW_FUNCS = r"""// ============ 보급수 계산서 (Make-up Water Report) ============
function _genDocId(prefix, modelType, modelCRT, cells, I) {
  const now = new Date();
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth()+1).padStart(2,'0');
  const dd = String(now.getDate()).padStart(2,'0');
  const seed = `${prefix}${modelType}${modelCRT}${cells}${I.tin}${I.tout}${I.twb}`;
  let h = 0; for (let i=0;i<seed.length;i++) h = ((h<<5)-h+seed.charCodeAt(i))|0;
  const hash = Math.abs(h).toString(36).toUpperCase().slice(0,5);
  return { docId: `SJ-${prefix}-${yyyy}${mm}${dd}-${hash}`, dateStr: `${yyyy}. ${mm}. ${dd}.`, issueDate: `${yyyy}년 ${parseInt(mm)}월 ${parseInt(dd)}일`, yyyy };
}

function openMakeupReport(modelType, modelCRT, cells) {
  const I = _captureInputs();
  if (!I) { alert('계산값이 없습니다. 먼저 「선정 계산」을 실행해주세요.'); return; }

  // 입력값
  const Q = I.flowM3h;                         // 순환 수량 (㎥/h ≈ T/h)
  const range = I.range;                       // ΔT (℃)
  const tin = I.tin, tout = I.tout, twb = I.twb;

  // 손실 계산 (HVAC 표준)
  // E (증발량) = Q × 0.00166 × ΔT  (≈ ΔT 1℃당 0.166% 증발)
  //   ※ 첨부 양식의 0.83%/100 = ΔT 5℃ 기준값과 동일
  const evapRatePerC = 0.00166;
  const E = Q * evapRatePerC * range;          // T/h
  const evapPct = (evapRatePerC * range * 100); // % of Q

  // D (비산량) = Q × 0.002% (고효율 엘리미네이터 기준)
  const driftRate = 0.00002;
  const D = Q * driftRate;                     // T/h

  // 농축배율 C — 기본 5 (HVAC 일반), 표는 3~7
  const C_DEFAULT = 5;

  function calcBM(c) {
    const B = (E - (c - 1) * D) / (c - 1);
    const M = E + D + B;
    return { B, M };
  }
  const main = calcBM(C_DEFAULT);
  const B = main.B, M = main.M;

  // 일/월 환산
  const M_day = M * 24;
  const M_month = M_day * 30;

  // 농축배율별 표
  const cValues = [3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7];
  let tableRows = '';
  for (const c of cValues) {
    const { B: Bc, M: Mc } = calcBM(c);
    const hl = (c === C_DEFAULT) ? ' class="highlight"' : '';
    const star = (c === C_DEFAULT) ? ' ★' : '';
    tableRows += `<tr${hl}><td>${c.toFixed(1)}${star}</td><td>${Bc.toFixed(3)}</td><td>${Mc.toFixed(3)}</td><td>${(Mc*24).toLocaleString('ko-KR',{maximumFractionDigits:1})}</td></tr>`;
  }

  const variantSuffix = _optionSuffix(modelType, I);
  const variantCode = `${modelType}-${modelCRT}${variantSuffix}`;

  const meta = _genDocId('MUW', modelType, modelCRT, cells, I);
  document.getElementById('reportDocId').textContent = meta.docId;

  const reportHtml = `
    <div class="report-header">
      <div class="title-block">
        <div class="eyebrow">SUNGJI MAKE-UP WATER CALCULATION</div>
        <div class="main-title">보급수 계산서</div>
        <div class="sub-title">Cooling Tower Make-up Water Consumption Report</div>
      </div>
      <div class="logo-block">
        <img src="sj_logo.svg" alt="(주)성지공조기술">
        <div class="corp">SUNGJI Air Conditioning Technology Co., Ltd.</div>
      </div>
    </div>

    <div class="report-meta">
      <div class="row"><div class="k">발행</div><div class="v">(주)성지공조기술</div></div>
      <div class="row"><div class="k">현장명</div><div class="v editable" contenteditable="true" data-placeholder="현장명 입력 (Project Name)" oninput="_saveSiteName(this)" spellcheck="false">${_savedSiteName || ''}</div></div>
      <div class="row"><div class="k">발행일자</div><div class="v">${meta.issueDate}</div></div>
    </div>

    <div class="report-section-title">1. 적용 모델 (Selected Model)</div>
    <div class="report-selected">
      <div class="model-info">
        <div class="model-code">${variantCode} × ${cells}Cell</div>
        <div class="model-desc">${MODEL_DESC[modelType]} (${modelType}-Series)${_optionDesc(modelType, I)}</div>
      </div>
      <div class="model-spec-row">
        <div class="spec-cell"><span class="label">설계 유량</span><span class="num">${Q.toFixed(1)} ㎥/h</span></div>
        <div class="spec-cell"><span class="label">Range (ΔT)</span><span class="num">${range.toFixed(1)} ℃</span></div>
        <div class="spec-cell"><span class="label">총 호칭</span><span class="num">${modelCRT*cells} CRT</span></div>
      </div>
    </div>

    <div class="report-section-title">2. 설계 조건 (Design Conditions)</div>
    <div class="calc-meta">
      <div class="row"><div class="k">순환 수량 (Q)</div><div class="v">${Q.toFixed(2)} ㎥/h　(${(Q*1000/60).toFixed(0)} LPM)</div></div>
      <div class="row"><div class="k">입구 온도</div><div class="v">${tin.toFixed(1)} ℃ (HWT)</div></div>
      <div class="row"><div class="k">출구 온도</div><div class="v">${tout.toFixed(1)} ℃ (CWT)</div></div>
      <div class="row"><div class="k">습구 온도</div><div class="v">${twb.toFixed(1)} ℃ (WBT)</div></div>
      <div class="row"><div class="k">Range</div><div class="v">${range.toFixed(2)} ℃</div></div>
      <div class="row"><div class="k">Approach</div><div class="v">${(tout-twb).toFixed(2)} ℃</div></div>
    </div>

    <div class="report-section-title">3. 손실 계산 (Loss Calculation)</div>

    <div class="calc-step">
      <div class="step-head"><span class="num">1</span><span class="t">증발손실 / Evaporation Loss<span class="en">E</span></span></div>
      <div class="formula-line"><span class="lhs">E</span> = Q × 0.166% × ΔT  =  ${Q.toFixed(2)} × 0.00166 × ${range.toFixed(1)}  →  <span class="res">${E.toFixed(3)} T/h</span></div>
      <div class="note">개방형 냉각탑은 순환수의 일부가 증발하면서 잠열을 빼앗아 냉각이 이루어집니다.<br>증발율 ≈ 0.166%/℃ (Range 기준) · 본 조건에서 약 ${evapPct.toFixed(2)}% 증발</div>
    </div>

    <div class="calc-step">
      <div class="step-head"><span class="num">2</span><span class="t">비산손실 / Drift Loss<span class="en">D</span></span></div>
      <div class="formula-line"><span class="lhs">D</span> = Q × 0.002%  =  ${Q.toFixed(2)} × 0.00002  →  <span class="res">${D.toFixed(3)} T/h</span></div>
      <div class="note">송풍기 기류로 인한 미세 물방울 비산. 고효율 엘리미네이터(Eliminator) 기준 0.002% 적용.</div>
    </div>

    <div class="calc-step">
      <div class="step-head"><span class="num">3</span><span class="t">농축배수 / Blowdown<span class="en">B (C = ${C_DEFAULT.toFixed(1)})</span></span></div>
      <div class="formula-line"><span class="lhs">B</span> = ( E − (C−1)·D ) ÷ (C−1)  =  ( ${E.toFixed(3)} − ${(C_DEFAULT-1)*D < 1e-6 ? '0' : ((C_DEFAULT-1)*D).toFixed(3)} ) ÷ ${C_DEFAULT-1}  →  <span class="res">${B.toFixed(3)} T/h</span></div>
      <div class="note">C : 농축배율 (Cycle of Concentration) — 일반 HVAC C = 5 ~ 7, 산업 프로세스 C = 4 ~ 5 적용.<br>정확한 C 값은 수처리 전문 회사 검토 필요.</div>
    </div>

    <div class="calc-step">
      <div class="step-head"><span class="num">4</span><span class="t">총 보급수량 / Make-up Water<span class="en">M = E + D + B</span></span></div>
      <div class="formula-line"><span class="lhs">M</span> = ${E.toFixed(3)} + ${D.toFixed(3)} + ${B.toFixed(3)}  →  <span class="res">${M.toFixed(3)} T/h</span></div>
    </div>

    <div class="calc-result-card">
      <div class="label">총 보급수 소요량 (C = ${C_DEFAULT}, 정상 운전 기준)<span class="sub">Total Make-up Water Demand at Design Condition</span></div>
      <div class="num">${M.toFixed(3)}<span class="unit">T/h</span></div>
    </div>

    <div class="report-section-title">4. 농축배율(C)에 따른 보급수량 비교</div>
    <table class="calc-table">
      <thead>
        <tr>
          <th style="width:18%;">농축배율 C<br><span style="font-size:10px;font-weight:400;opacity:0.85;">Cycle of Conc.</span></th>
          <th style="width:24%;">B (T/h)<br><span style="font-size:10px;font-weight:400;opacity:0.85;">Blowdown</span></th>
          <th style="width:24%;">M (T/h)<br><span style="font-size:10px;font-weight:400;opacity:0.85;">Make-up</span></th>
          <th>일 보급수 (T/일)<br><span style="font-size:10px;font-weight:400;opacity:0.85;">Daily Make-up</span></th>
        </tr>
      </thead>
      <tbody>${tableRows}</tbody>
    </table>

    <div class="calc-criteria">
      <div class="crit-title">▌ 보급수 산정 기준 / Standards</div>
      <ul>
        <li>증발율 0.166%/℃ × Range (HVAC 표준)</li>
        <li>비산율 0.002% (고효율 엘리미네이터 기준, 일반 0.05% → 본 모델 0.002% 적용)</li>
        <li>농축배율 C : 본 검토는 HVAC 표준 <b>C = ${C_DEFAULT}</b> 적용 (일반 5~7 범위)</li>
        <li>일/월 환산 : 24시간/30일 정상 운전 기준</li>
      </ul>
    </div>

    <div class="report-section-title">5. 결론 (Conclusion)</div>
    <div class="report-grid">
      <div class="row"><div class="k">시간당 보급수</div><div class="v"><b>${M.toFixed(3)} T/h</b>　(${(M*1000).toFixed(0)} L/h)</div></div>
      <div class="row"><div class="k">일 보급수 (24h)</div><div class="v"><b>${M_day.toLocaleString('ko-KR',{maximumFractionDigits:2})} T/일</b></div></div>
      <div class="row"><div class="k">월 보급수 (30일)</div><div class="v"><b>${M_month.toLocaleString('ko-KR',{maximumFractionDigits:1})} T/월</b></div></div>
      <div class="row"><div class="k">보급관 권장 구경</div><div class="v">25 A (모델 기본)</div></div>
    </div>

    <div class="report-disclaimer">
      <b>※ Notes &amp; Disclaimer</b><br>
      1) 본 계산서는 정상 운전 기준 시간당 보급수 소요량을 산정한 것이며, 기동·정지 충수량은 별도 계상이 필요합니다.<br>
      2) 농축배율 C 값은 원수의 수질·수처리 방식에 따라 변동되며, 정확한 C 값은 수처리 전문 회사 검토를 권장합니다.<br>
      3) 비산율은 고효율 엘리미네이터 적용 기준이며, 일반 엘리미네이터의 경우 0.05% 수준으로 보급수량이 증가할 수 있습니다.<br>
      4) Range·습구온도 변동 또는 부분부하 운전 시 증발손실이 비례 변동하므로 실제 운전 조건 기준으로 재산정 필요합니다.
    </div>

    <div class="report-footer">
      <span class="doc-stamp">CONFIDENTIAL</span>
      <div class="copyright">
        Copyright ⓒ ${meta.yyyy} (주)성지공조기술 (Sungji Air Conditioning Technology Co., Ltd.) All rights reserved.<br>
        본 보급수 계산서의 모든 콘텐츠 및 산정 로직에 대한 저작권은 (주)성지공조기술에 있으며, 무단 복제·재배포·상업적 이용을 금합니다.
      </div>
      <div class="signature">
        <div class="corp-name">(주)성지공조기술</div>
        <div>Sungji A.C.T. Co., Ltd.</div>
        <div style="font-size:10px;color:#90a4ae;">발행일: ${meta.dateStr}</div>
      </div>
    </div>
  `;

  document.getElementById('reportBody').innerHTML = reportHtml;
  document.getElementById('reportOverlay').classList.add('show');
  document.body.style.overflow = 'hidden';
}

// ============ 루버면적 검토서 (Louver Area Review Report) ============
function openLouverReport(modelType, modelCRT, cells) {
  const I = _captureInputs();
  if (!I) { alert('계산값이 없습니다. 먼저 「선정 계산」을 실행해주세요.'); return; }

  const sp = getVariantSpec(modelType, modelCRT, I);
  if (!sp) {
    alert('해당 모델의 풍량 데이터가 없어 루버면적 검토가 불가합니다.');
    return;
  }

  // 풍량 (CMM)
  const cmmPerCell = sp.cmm;
  const cmmTotal = cmmPerCell * cells;

  // 적용 기준
  const V_MAX = 5;            // 풍속 5 m/s
  const FREE_AREA = 0.5;      // 개구율 50%

  // 필요 면적: A = (CMM_total ÷ 60) ÷ (V × FreeArea)
  // CMM = m³/min, m³/s = CMM/60, A = (m³/s) / (m/s) = m²
  const m3sTotal   = cmmTotal / 60;
  const m3sPerCell = cmmPerCell / 60;
  const denom = V_MAX * FREE_AREA;        // 2.5 m/s effective
  const Atot  = m3sTotal / denom;
  const Acell = m3sPerCell / denom;

  // 풍속별 비교 (4.0, 4.5, 5.0, 5.5, 6.0 m/s)
  const vList = [4.0, 4.5, 5.0, 5.5, 6.0];
  let vRows = '';
  for (const v of vList) {
    const a = (cmmTotal / 60) / (v * FREE_AREA);
    const ac = a / cells;
    const hl = (Math.abs(v - V_MAX) < 1e-6) ? ' class="highlight"' : '';
    const star = (Math.abs(v - V_MAX) < 1e-6) ? ' ★' : '';
    vRows += `<tr${hl}><td>${v.toFixed(1)}${star}</td><td>${a.toFixed(2)}</td><td>${ac.toFixed(2)}</td></tr>`;
  }

  // 개구율별 비교 (40, 45, 50, 55, 60%)
  const fList = [0.40, 0.45, 0.50, 0.55, 0.60];
  let fRows = '';
  for (const f of fList) {
    const a = (cmmTotal / 60) / (V_MAX * f);
    const ac = a / cells;
    const hl = (Math.abs(f - FREE_AREA) < 1e-6) ? ' class="highlight"' : '';
    const star = (Math.abs(f - FREE_AREA) < 1e-6) ? ' ★' : '';
    fRows += `<tr${hl}><td>${(f*100).toFixed(0)} %${star}</td><td>${a.toFixed(2)}</td><td>${ac.toFixed(2)}</td></tr>`;
  }

  const variantSuffix = _optionSuffix(modelType, I);
  const variantCode = `${modelType}-${modelCRT}${variantSuffix}`;
  const meta = _genDocId('LVR', modelType, modelCRT, cells, I);
  document.getElementById('reportDocId').textContent = meta.docId;

  const reportHtml = `
    <div class="report-header">
      <div class="title-block">
        <div class="eyebrow">SUNGJI LOUVER AREA REVIEW</div>
        <div class="main-title">루버면적 검토서</div>
        <div class="sub-title">Cooling Tower Inlet / Discharge Louver Area Calculation</div>
      </div>
      <div class="logo-block">
        <img src="sj_logo.svg" alt="(주)성지공조기술">
        <div class="corp">SUNGJI Air Conditioning Technology Co., Ltd.</div>
      </div>
    </div>

    <div class="report-meta">
      <div class="row"><div class="k">발행</div><div class="v">(주)성지공조기술</div></div>
      <div class="row"><div class="k">현장명</div><div class="v editable" contenteditable="true" data-placeholder="현장명 입력 (Project Name)" oninput="_saveSiteName(this)" spellcheck="false">${_savedSiteName || ''}</div></div>
      <div class="row"><div class="k">발행일자</div><div class="v">${meta.issueDate}</div></div>
    </div>

    <div class="report-section-title">1. 검토 대상 / Subject</div>
    <div class="report-selected">
      <div class="model-info">
        <div class="model-code">${variantCode} × ${cells}Cell</div>
        <div class="model-desc">${MODEL_DESC[modelType]} (${modelType}-Series)${_optionDesc(modelType, I)}</div>
      </div>
      <div class="model-spec-row">
        <div class="spec-cell"><span class="label">셀당 풍량</span><span class="num">${cmmPerCell.toLocaleString()} CMM</span></div>
        <div class="spec-cell"><span class="label">총 풍량</span><span class="num">${cmmTotal.toLocaleString()} CMM</span></div>
        <div class="spec-cell"><span class="label">총 호칭</span><span class="num">${modelCRT*cells} CRT</span></div>
      </div>
    </div>

    <div class="report-section-title">2. 적용 기준 / Design Criteria</div>
    <div class="calc-criteria">
      <div class="crit-title">▌ 흡입측 / 토출측 LOUVER 적용 기준</div>
      <ul>
        <li>최대 루버 풍속 <b>${V_MAX} m/s</b> 이하 (Maximum Louver Velocity ≤ ${V_MAX} m/s)</li>
        <li>유효 개구율 (Net Free Area) <b>${(FREE_AREA*100).toFixed(0)}%</b> 이상 ([${(FREE_AREA*100).toFixed(0)}% 기준 적용])</li>
        <li>본 검토는 흡입측·토출측 동일 기준 적용 (양측 동일 면적 권장)</li>
      </ul>
    </div>

    <div class="report-section-title">3. 계산식 / Theoretical Formula</div>
    <div class="calc-step">
      <div class="step-head"><span class="num">①</span><span class="t">이론식<span class="en">Theoretical Equation</span></span></div>
      <div class="formula-line">필요 루버 면적 (m²)  =  Total Air Volume (m³/s)  ÷  ( Maximum Louver Velocity × Free Area Ratio )</div>
      <div class="note">CMM 단위는 60으로 나누어 m³/s로 환산 후 적용 — A = (CMM ÷ 60) ÷ (V × FreeArea)</div>
    </div>

    <div class="calc-step">
      <div class="step-head"><span class="num">②</span><span class="t">전체 풍량<span class="en">Total Air Volume</span></span></div>
      <div class="formula-line"><span class="lhs">CMM_total</span> = ${cmmPerCell.toLocaleString()} CMM × ${cells} Cell  →  <span class="res">${cmmTotal.toLocaleString()} CMM</span> (${m3sTotal.toFixed(2)} m³/s)</div>
    </div>

    <div class="calc-step">
      <div class="step-head"><span class="num">③</span><span class="t">필요 루버 면적<span class="en">Required Louver Area</span></span></div>
      <div class="formula-line"><span class="lhs">A</span> = ( ${cmmTotal.toLocaleString()} ÷ 60 ) ÷ ( ${V_MAX} × ${(FREE_AREA*100).toFixed(0)}% )  =  ${m3sTotal.toFixed(2)} ÷ ${denom.toFixed(2)}  →  <span class="res">${Atot.toFixed(2)} m²</span></div>
      <div class="note">셀당 필요 면적 = ${Atot.toFixed(2)} ÷ ${cells} = <b>${Acell.toFixed(2)} m²</b> / Cell</div>
    </div>

    <div class="calc-result-card">
      <div class="label">필요 루버 면적 (흡입측 = 토출측)<span class="sub">Required Louver Area · ${V_MAX} m/s · Free Area ${(FREE_AREA*100).toFixed(0)}%</span></div>
      <div class="num">${Atot.toFixed(2)}<span class="unit">m²　(셀당 ${Acell.toFixed(2)} m²)</span></div>
    </div>

    <div class="report-section-title">4. 풍속·개구율별 면적 변화</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
      <div>
        <div style="font-size:11.5px;color:#1e3c72;font-weight:700;margin-bottom:5px;">▌ 풍속별 (개구율 ${(FREE_AREA*100).toFixed(0)}% 고정)</div>
        <table class="calc-table">
          <thead>
            <tr>
              <th>풍속 (m/s)</th>
              <th>총 면적 (m²)</th>
              <th>셀당 (m²)</th>
            </tr>
          </thead>
          <tbody>${vRows}</tbody>
        </table>
      </div>
      <div>
        <div style="font-size:11.5px;color:#1e3c72;font-weight:700;margin-bottom:5px;">▌ 개구율별 (풍속 ${V_MAX} m/s 고정)</div>
        <table class="calc-table">
          <thead>
            <tr>
              <th>개구율</th>
              <th>총 면적 (m²)</th>
              <th>셀당 (m²)</th>
            </tr>
          </thead>
          <tbody>${fRows}</tbody>
        </table>
      </div>
    </div>

    <div class="report-section-title">5. 결론 (Conclusion)</div>
    <div class="report-grid">
      <div class="row"><div class="k">필요 루버 면적</div><div class="v"><b>${Atot.toFixed(2)} m²</b> (흡입 = 토출)</div></div>
      <div class="row"><div class="k">셀당 필요 면적</div><div class="v"><b>${Acell.toFixed(2)} m² / Cell</b></div></div>
      <div class="row"><div class="k">적용 풍속</div><div class="v">${V_MAX} m/s</div></div>
      <div class="row"><div class="k">적용 개구율</div><div class="v">${(FREE_AREA*100).toFixed(0)} %</div></div>
    </div>

    <div class="report-disclaimer">
      <b>※ Notes &amp; Disclaimer</b><br>
      1) 본 검토는 ASHRAE / 일본 냉동공조 협회 권고에 따른 표준 풍속 ${V_MAX} m/s 이하 기준이며, 정숙·저소음 요구 시 3 ~ 4 m/s로 강화 가능합니다.<br>
      2) 개구율(Net Free Area)은 루버 형태·블레이드 각도에 따라 35 ~ 60% 범위에서 변동되며, 본 검토는 일반형 ${(FREE_AREA*100).toFixed(0)}% 기준입니다.<br>
      3) 흡입측·토출측 면적은 동일 기준 적용을 권장하며, 흡입 장애가 예상되는 경우 1.2 ~ 1.5배 여유 면적을 확보하시기 바랍니다.<br>
      4) 본 면적은 유효 통기 면적이며, 루버 프레임·지지대 등 비통기부를 제외한 net 면적 기준입니다.
    </div>

    <div class="report-footer">
      <span class="doc-stamp">CONFIDENTIAL</span>
      <div class="copyright">
        Copyright ⓒ ${meta.yyyy} (주)성지공조기술 (Sungji Air Conditioning Technology Co., Ltd.) All rights reserved.<br>
        본 검토서의 모든 콘텐츠 및 산정 로직에 대한 저작권은 (주)성지공조기술에 있으며, 무단 복제·재배포·상업적 이용을 금합니다.
      </div>
      <div class="signature">
        <div class="corp-name">(주)성지공조기술</div>
        <div>Sungji A.C.T. Co., Ltd.</div>
        <div style="font-size:10px;color:#90a4ae;">발행일: ${meta.dateStr}</div>
      </div>
    </div>
  `;

  document.getElementById('reportBody').innerHTML = reportHtml;
  document.getElementById('reportOverlay').classList.add('show');
  document.body.style.overflow = 'hidden';
}

"""

src = src.replace(INSERTION_ANCHOR, NEW_FUNCS + INSERTION_ANCHOR)


# ---------- 4. Final write ----------
with open(DST, 'w', encoding='utf-8') as f:
    f.write(src)

print('OK. wrote', DST, '→', os.path.getsize(DST), 'bytes')

# Sanity sniff
for needle in ['openMakeupReport', 'openLouverReport', "ovChooseDoc('makeup')",
               "ovChooseDoc('louver')", '농축배율', 'Cycle of Conc', 'Maximum Louver Velocity']:
    n = src.count(needle)
    print(f'  {needle!r:42s}: {n}')
