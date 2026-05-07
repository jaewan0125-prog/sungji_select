#!/usr/bin/env python3
"""
3rd revision:
  1) Bump reportOverlay z-index above overviewOverlay so the report shows on top.
  2) Lock 비산율 0.002% (already fixed) and 농축배율 C = 6.
  3) Make both reports fit on a single A4 portrait page (compact redesign).
  4) Fix the 'unit' wrapping next to the result number (no line break).
  5) Drop sections that no longer carry information (C-comparison table since C is fixed,
     velocity/free-area comparison tables since values are fixed).
"""
import os, re

SRC = '냉각탑_선정프로그램_장비개요.html'
DST = SRC

with open(SRC, 'r', encoding='utf-8') as f:
    src = f.read()


# ============================================================
# 1) Bump z-index of report-overlay above ov-overlay (1050) and below ph-overlay (1200)
#    Original CSS: '.report-overlay { ... z-index: 1000; ... }'
# ============================================================
src = src.replace(
    'background: rgba(15, 25, 50, 0.65);\n    display: none;\n    align-items: flex-start;\n    justify-content: center;\n    z-index: 1000;',
    'background: rgba(15, 25, 50, 0.65);\n    display: none;\n    align-items: flex-start;\n    justify-content: center;\n    z-index: 1100;'
)


# ============================================================
# 2) CSS changes: nowrap unit, compact print, single-row layouts
#    Insert/replace just inside the existing extra calc CSS we added before.
# ============================================================
# Replace the existing .calc-result-card .num rule to add nowrap + smaller unit
# Old chunk:
OLD_NUM_BLOCK = """  .calc-result-card .num {
    font-family: 'Consolas', monospace;
    font-size: 22px; font-weight: 800; color: #c62828;
    letter-spacing: -0.5px;
  }
  .calc-result-card .num .unit {
    font-size: 13px; color: #546e7a;
    font-weight: 500; margin-left: 4px;
  }"""

NEW_NUM_BLOCK = """  .calc-result-card .num {
    font-family: 'Consolas', monospace;
    font-size: 22px; font-weight: 800; color: #c62828;
    letter-spacing: -0.5px;
    white-space: nowrap;
  }
  .calc-result-card .num .unit {
    font-size: 12.5px; color: #546e7a;
    font-weight: 500; margin-left: 4px;
    white-space: nowrap;
    display: inline-block;
  }
  /* 결과 박스가 가로로 좁아지면 라벨/숫자가 한 줄에 안 들어갈 수 있어서, 두 줄로 자연스럽게 흐르도록 wrap */
  .calc-result-card { flex-wrap: wrap; }

  /* 컴팩트 박스 — 1페이지 fit 용 */
  .calc-mini-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin: 8px 0 12px;
  }
  .calc-mini-row .cell {
    background: #f8f9fb; border: 1px solid #cfd8dc;
    border-radius: 4px; padding: 6px 10px;
    text-align: center;
  }
  .calc-mini-row .cell .k {
    font-size: 10.5px; color: #607d8b;
    letter-spacing: 0.3px; font-weight: 600;
    margin-bottom: 1px;
  }
  .calc-mini-row .cell .v {
    font-family: 'Consolas', monospace; font-weight: 800;
    font-size: 14px; color: #1e3c72;
  }
  .calc-mini-row .cell .v .u {
    font-family: 'Malgun Gothic', sans-serif;
    font-size: 11px; color: #546e7a; font-weight: 500;
    margin-left: 2px;
  }

  /* 손실 계산 단일 통합표 (E/D/B/M 한 표) */
  .calc-unified {
    width: 100%; border-collapse: collapse;
    font-size: 12.5px; margin: 4px 0 8px;
  }
  .calc-unified th, .calc-unified td {
    border: 1px solid #b0bec5; padding: 6px 10px; text-align: center;
  }
  .calc-unified thead th {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white; font-weight: 700; letter-spacing: 0.3px;
  }
  .calc-unified td:nth-child(1) {
    text-align: left; font-weight: 700; color: #1e3c72; width: 14%;
  }
  .calc-unified td:nth-child(2) {
    text-align: left; font-family: 'Consolas', monospace;
    color: #263248; font-size: 11.5px; width: 30%;
  }
  .calc-unified td:nth-child(3) { width: 24%; }
  .calc-unified td:last-child {
    font-family: 'Consolas', monospace;
    font-weight: 800; color: #c62828;
    background: #fff8e1;
  }

  /* 작은 footer/disclaimer 한 줄 */
  .calc-mini-footer {
    margin-top: 10px; padding-top: 8px;
    border-top: 1.5px solid #1e3c72;
    display: grid;
    grid-template-columns: 1fr auto auto;
    gap: 12px;
    align-items: center;
    font-size: 10px; color: #607d8b;
  }
  .calc-mini-footer .note {
    font-size: 10px; color: #5d4037; line-height: 1.45;
  }
  .calc-mini-footer .corp {
    color: #1e3c72; font-weight: 700; font-size: 11px;
  }
  .calc-mini-footer .stamp {
    border: 1.5px solid #1e3c72; color: #1e3c72;
    padding: 2px 7px; border-radius: 3px;
    font-size: 9px; font-weight: 700; letter-spacing: 1px;
  }

  /* ===== 인쇄 시 1페이지 fit 강제 ===== */
  @media print {
    @page { size: A4 portrait; margin: 10mm 12mm; }
    .calc-mini-row { gap: 5px !important; margin: 5px 0 7px !important; }
    .calc-mini-row .cell { padding: 4px 7px !important; }
    .calc-mini-row .cell .k { font-size: 8pt !important; }
    .calc-mini-row .cell .v { font-size: 11pt !important; }
    .calc-mini-row .cell .v .u { font-size: 8.5pt !important; }
    .calc-unified { font-size: 9pt !important; margin: 3px 0 5px !important; }
    .calc-unified th, .calc-unified td { padding: 3px 6px !important; }
    .calc-mini-footer { font-size: 8pt !important; padding-top: 5px !important; margin-top: 6px !important; }
    .calc-mini-footer .note { font-size: 7.5pt !important; }
    .calc-result-card { padding: 6px 11px !important; margin: 5px 0 4px !important; page-break-inside: avoid; }
    .calc-result-card .num { font-size: 14pt !important; }
    .calc-result-card .num .unit { font-size: 9.5pt !important; }
    .calc-result-card .label { font-size: 9pt !important; }
    .calc-result-card .label .sub { font-size: 7.5pt !important; }
    .report-section-title { font-size: 9.5pt !important; padding: 3px 9px !important; margin: 6px 0 3px !important; }
    .report-selected { padding: 5px 10px !important; }
    .report-selected .model-info .model-code { font-size: 13pt !important; }
    .report-selected .model-info .model-desc { font-size: 7.5pt !important; }
    .report-selected .model-spec-row .spec-cell { padding: 0 9px !important; }
    .report-selected .model-spec-row .spec-cell .num { font-size: 10pt !important; }
    .report-selected .model-spec-row .spec-cell .label { font-size: 7pt !important; }
    .report-meta { font-size: 9pt !important; margin-bottom: 5px !important; gap: 1px 14px !important; }
    .report-meta .row .v.editable { font-size: 9pt !important; }
    .report-header { padding-bottom: 4px !important; margin-bottom: 5px !important; }
    .report-header .title-block .main-title { font-size: 15pt !important; }
    .report-header .title-block .eyebrow { font-size: 7pt !important; }
    .report-header .title-block .sub-title { font-size: 8pt !important; }
    .report-header .logo-block img { height: 28px !important; }
    .report-header .logo-block .corp { font-size: 7pt !important; }
    .report-body { padding: 0 !important; font-size: 9.5pt !important; }
    .report-modal { box-shadow: none !important; }
  }
"""

# Find the existing CSS_ADD anchor (the block that already exists from last build)
# Replace OLD_NUM_BLOCK with NEW_NUM_BLOCK
assert OLD_NUM_BLOCK in src, 'OLD_NUM_BLOCK not found'
src = src.replace(OLD_NUM_BLOCK, NEW_NUM_BLOCK)


# ============================================================
# 3) Replace the entire openMakeupReport function body with a compact 1-page version
# ============================================================
# We'll match from `function openMakeupReport(...)` to the matching closing brace
# of the function. Easier: capture up to the next `// ============ 루버` comment.

MUW_OLD_PATTERN = re.compile(
    r'function openMakeupReport\(modelType, modelCRT, cells\) \{.*?\n\}\n\n// ============ 루버',
    re.DOTALL
)
m = MUW_OLD_PATTERN.search(src)
assert m, 'openMakeupReport block not found'

MUW_NEW = r"""function openMakeupReport(modelType, modelCRT, cells) {
  const I = _captureInputs();
  if (!I) { alert('계산값이 없습니다. 먼저 「선정 계산」을 실행해주세요.'); return; }

  const Q     = I.flowM3h;            // 순환 수량 (㎥/h ≈ T/h)
  const range = I.range;              // ΔT
  const tin = I.tin, tout = I.tout, twb = I.twb;

  // 고정 계수
  const evapRatePerC = 0.00166;       // 0.166%/℃ (Range 기준)
  const driftRate    = 0.00002;       // 0.002% (고효율 엘리미네이터)
  const C            = 6;             // 농축배율 고정

  // 손실 계산
  const E = Q * evapRatePerC * range;          // 증발손실
  const D = Q * driftRate;                     // 비산손실
  const B = (E - (C - 1) * D) / (C - 1);       // 농축배수
  const M = E + D + B;                         // 총 보급수
  const evapPct = evapRatePerC * range * 100;  // %로 표시

  const variantSuffix = _optionSuffix(modelType, I);
  const variantCode   = `${modelType}-${modelCRT}${variantSuffix}`;
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
        <div class="spec-cell"><span class="label">Range</span><span class="num">${range.toFixed(1)} ℃</span></div>
        <div class="spec-cell"><span class="label">총 호칭</span><span class="num">${modelCRT*cells} CRT</span></div>
      </div>
    </div>

    <div class="report-section-title">2. 설계 조건 / Design Conditions</div>
    <div class="calc-mini-row">
      <div class="cell"><div class="k">순환 수량 Q</div><div class="v">${Q.toFixed(1)}<span class="u">㎥/h</span></div></div>
      <div class="cell"><div class="k">입구 / 출구 (HWT/CWT)</div><div class="v">${tin.toFixed(1)} / ${tout.toFixed(1)}<span class="u">℃</span></div></div>
      <div class="cell"><div class="k">습구 (WBT)</div><div class="v">${twb.toFixed(1)}<span class="u">℃</span></div></div>
      <div class="cell"><div class="k">Range / Approach</div><div class="v">${range.toFixed(1)} / ${(tout-twb).toFixed(1)}<span class="u">℃</span></div></div>
    </div>

    <div class="report-section-title">3. 손실 계산 (Loss Calculation)　·　고정값 [비산 0.002% · 농축배율 C = ${C}]</div>
    <table class="calc-unified">
      <thead>
        <tr>
          <th>항목</th>
          <th>계산식</th>
          <th>적용</th>
          <th>값 (T/h)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>증발손실 E<br><span style="font-size:10px;font-weight:400;color:#78909c;">Evaporation</span></td>
          <td>Q × 0.166% × ΔT</td>
          <td>${Q.toFixed(2)} × 0.00166 × ${range.toFixed(1)}</td>
          <td>${E.toFixed(3)}</td>
        </tr>
        <tr>
          <td>비산손실 D<br><span style="font-size:10px;font-weight:400;color:#78909c;">Drift Loss</span></td>
          <td>Q × 0.002%</td>
          <td>${Q.toFixed(2)} × 0.00002</td>
          <td>${D.toFixed(3)}</td>
        </tr>
        <tr>
          <td>농축배수 B<br><span style="font-size:10px;font-weight:400;color:#78909c;">Blowdown</span></td>
          <td>(E − (C−1)·D) ÷ (C−1)</td>
          <td>(${E.toFixed(3)} − ${((C-1)*D).toFixed(3)}) ÷ ${C-1}</td>
          <td>${B.toFixed(3)}</td>
        </tr>
        <tr>
          <td>총 보급수 M<br><span style="font-size:10px;font-weight:400;color:#78909c;">Make-up</span></td>
          <td>E + D + B</td>
          <td>${E.toFixed(3)} + ${D.toFixed(3)} + ${B.toFixed(3)}</td>
          <td>${M.toFixed(3)}</td>
        </tr>
      </tbody>
    </table>

    <div class="calc-result-card">
      <div class="label">총 보급수 소요량 (C = ${C}, 정상 운전 기준)<span class="sub">Total Make-up Water Demand · ${evapPct.toFixed(2)}% Evaporation</span></div>
      <div class="num">${M.toFixed(3)}<span class="unit">T/h</span></div>
    </div>

    <div class="calc-mini-row">
      <div class="cell"><div class="k">시간당 / Hourly</div><div class="v">${M.toFixed(3)}<span class="u">T/h</span></div></div>
      <div class="cell"><div class="k">시간당 / L 단위</div><div class="v">${(M*1000).toFixed(0)}<span class="u">L/h</span></div></div>
      <div class="cell"><div class="k">일 (24h) / Daily</div><div class="v">${(M*24).toFixed(2)}<span class="u">T/일</span></div></div>
      <div class="cell"><div class="k">월 (30일) / Monthly</div><div class="v">${(M*24*30).toFixed(1)}<span class="u">T/월</span></div></div>
    </div>

    <div class="calc-mini-footer">
      <div class="note">
        ※ 증발율 0.166%/℃ × Range (HVAC 표준) · 비산율 0.002% (고효율 엘리미네이터) · 농축배율 C = ${C} (HVAC 일반 5~7).<br>
        ※ 정확한 C값은 원수 수질·수처리 방식에 따라 변동되며 수처리 전문회사 검토 권장. 기동·정지 충수량 별도 계상.
      </div>
      <span class="stamp">CONFIDENTIAL</span>
      <div class="corp">(주)성지공조기술<br><span style="font-size:9px;font-weight:500;color:#78909c;">${meta.dateStr}</span></div>
    </div>
  `;

  document.getElementById('reportBody').innerHTML = reportHtml;
  document.getElementById('reportOverlay').classList.add('show');
  document.body.style.overflow = 'hidden';
}

// ============ 루버"""

src = src[:m.start()] + MUW_NEW + src[m.end():]


# ============================================================
# 4) Replace openLouverReport with a compact 1-page version
# ============================================================
LVR_OLD_PATTERN = re.compile(
    r'function openLouverReport\(modelType, modelCRT, cells\) \{.*?\n\}\n\n',
    re.DOTALL
)
m = LVR_OLD_PATTERN.search(src)
assert m, 'openLouverReport block not found'

LVR_NEW = r"""function openLouverReport(modelType, modelCRT, cells) {
  const I = _captureInputs();
  if (!I) { alert('계산값이 없습니다. 먼저 「선정 계산」을 실행해주세요.'); return; }

  const sp = getVariantSpec(modelType, modelCRT, I);
  if (!sp) { alert('해당 모델의 풍량 데이터가 없어 루버면적 검토가 불가합니다.'); return; }

  const cmmPerCell = sp.cmm;
  const cmmTotal   = cmmPerCell * cells;
  const V_MAX      = 5;        // 풍속 5 m/s
  const FREE_AREA  = 0.5;      // 개구율 50%
  const m3sTotal   = cmmTotal / 60;
  const denom      = V_MAX * FREE_AREA;        // 2.5 m/s effective
  const Atot       = m3sTotal / denom;
  const Acell      = Atot / cells;

  const variantSuffix = _optionSuffix(modelType, I);
  const variantCode   = `${modelType}-${modelCRT}${variantSuffix}`;
  const meta = _genDocId('LVR', modelType, modelCRT, cells, I);
  document.getElementById('reportDocId').textContent = meta.docId;

  const reportHtml = `
    <div class="report-header">
      <div class="title-block">
        <div class="eyebrow">SUNGJI LOUVER AREA REVIEW</div>
        <div class="main-title">루버면적 검토서</div>
        <div class="sub-title">Inlet / Discharge Louver Area Calculation</div>
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
    <div class="calc-mini-row">
      <div class="cell"><div class="k">최대 루버 풍속</div><div class="v">${V_MAX}<span class="u">m/s 이하</span></div></div>
      <div class="cell"><div class="k">개구율 (Net Free Area)</div><div class="v">${(FREE_AREA*100).toFixed(0)}<span class="u">% 이상</span></div></div>
      <div class="cell"><div class="k">셀 수</div><div class="v">${cells}<span class="u">Cell</span></div></div>
      <div class="cell"><div class="k">총 풍량</div><div class="v">${cmmTotal.toLocaleString()}<span class="u">CMM</span></div></div>
    </div>

    <div class="report-section-title">3. 계산 (Calculation)</div>
    <table class="calc-unified">
      <thead>
        <tr>
          <th style="width:18%;">항목</th>
          <th>계산식 (Theoretical)</th>
          <th>적용 (Applied)</th>
          <th style="width:22%;">값</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>이론식</td>
          <td colspan="3" style="text-align:center;font-style:italic;">A (m²) = Total Air Volume (m³/s) ÷ ( Maximum Louver Velocity × Free Area Ratio )</td>
        </tr>
        <tr>
          <td>총 풍량</td>
          <td>CMM_total = CMM/Cell × Cell</td>
          <td>${cmmPerCell.toLocaleString()} × ${cells}</td>
          <td>${cmmTotal.toLocaleString()} CMM<br><span style="font-size:10px;font-weight:500;color:#78909c;">${m3sTotal.toFixed(2)} m³/s</span></td>
        </tr>
        <tr>
          <td>필요 면적 A</td>
          <td>(CMM ÷ 60) ÷ (V × FreeArea)</td>
          <td>${m3sTotal.toFixed(2)} ÷ (${V_MAX} × ${(FREE_AREA*100).toFixed(0)}%) = ${m3sTotal.toFixed(2)} ÷ ${denom.toFixed(2)}</td>
          <td>${Atot.toFixed(2)} m²</td>
        </tr>
        <tr>
          <td>셀당 면적</td>
          <td>A ÷ Cell</td>
          <td>${Atot.toFixed(2)} ÷ ${cells}</td>
          <td>${Acell.toFixed(2)} m² / Cell</td>
        </tr>
      </tbody>
    </table>

    <div class="calc-result-card">
      <div class="label">필요 루버 면적 (흡입측 = 토출측)<span class="sub">Required Louver Area · ${V_MAX} m/s · Free Area ${(FREE_AREA*100).toFixed(0)}%</span></div>
      <div class="num">${Atot.toFixed(2)}<span class="unit">m²</span></div>
    </div>

    <div class="calc-mini-row">
      <div class="cell"><div class="k">총 필요 면적</div><div class="v">${Atot.toFixed(2)}<span class="u">m²</span></div></div>
      <div class="cell"><div class="k">셀당 면적</div><div class="v">${Acell.toFixed(2)}<span class="u">m²/Cell</span></div></div>
      <div class="cell"><div class="k">적용 풍속</div><div class="v">${V_MAX}<span class="u">m/s</span></div></div>
      <div class="cell"><div class="k">적용 개구율</div><div class="v">${(FREE_AREA*100).toFixed(0)}<span class="u">%</span></div></div>
    </div>

    <div class="calc-mini-footer">
      <div class="note">
        ※ ASHRAE / 일본 냉동공조 협회 권고에 따른 표준 풍속 ${V_MAX} m/s 이하 기준. 정숙·저소음 요구 시 3 ~ 4 m/s 강화 권장.<br>
        ※ 본 면적은 유효 통기 면적이며 루버 프레임·지지대 등 비통기부 제외 net 기준. 흡입측·토출측 동일 면적 권장.
      </div>
      <span class="stamp">CONFIDENTIAL</span>
      <div class="corp">(주)성지공조기술<br><span style="font-size:9px;font-weight:500;color:#78909c;">${meta.dateStr}</span></div>
    </div>
  `;

  document.getElementById('reportBody').innerHTML = reportHtml;
  document.getElementById('reportOverlay').classList.add('show');
  document.body.style.overflow = 'hidden';
}

"""

src = src[:m.start()] + LVR_NEW + src[m.end():]


# ============================================================
# 5) Write
# ============================================================
with open(DST, 'w', encoding='utf-8') as f:
    f.write(src)

# Sanity
def cnt(needle): return src.count(needle)
print('OK. wrote', DST, '→', os.path.getsize(DST), 'bytes')
print('  z-index 1100:                 ', cnt('z-index: 1100'))
print('  C = 6 fixed:                  ', cnt('const C            = 6'))
print('  drift 0.002 fixed:            ', cnt('const driftRate    = 0.00002'))
print('  white-space: nowrap (.num):   ', cnt('.calc-result-card .num {'))
print('  calc-unified (single table):  ', cnt('class="calc-unified"'))
print('  C-comparison table left:      ', cnt('농축배율(C)에 따른 보급수량 비교'))
print('  velocity comparison left:     ', cnt('풍속·개구율별 면적 변화'))
