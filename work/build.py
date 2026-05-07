#!/usr/bin/env python3
"""Rebuild cooling.html → cooling_new.html with the new overview modal.

Performs in order:
  1) Read original from work/cooling.html
  2) Inject overview CSS just before the bottom @media block
  3) Replace #docMenuOverlay HTML with the new #overviewOverlay + #phOverlay HTML
  4) Replace the JS block (openDocMenu / closeDocMenu / docMenuChoose / triggerDownload)
     with the new openOverview / closeOverview / switchOvTab / ovChooseDoc / openPh / closePh
     plus MODEL_DIAGRAMS embedded base64 data URIs
  5) Replace the on-table onclick="openDocMenu(...)" with "openOverview(...)"
  6) Replace the Escape key handler
  7) Wrap closeReport so it cooperates with the new modal stack
"""
import base64, re, sys, os

ORIG = 'work/cooling.html'
DST  = 'cooling_new.html'

with open(ORIG, 'r', encoding='utf-8') as f:
    src = f.read()

# ---------- 1. CSS BLOCK ----------
CSS_OLD = """  @media (max-width: 760px) {
    .body { grid-template-columns: 1fr; }
    .input-section { border-right: none; border-bottom: 1px solid #e8eaed; }
    .header .logo { display: none; }
    .form-row, .form-row-3 { grid-template-columns: 1fr; }
  }
</style>"""

CSS_NEW = r"""  /* ============ 장비 개요 (Equipment Overview) 모달 ============ */
  .ov-overlay {
    position: fixed; inset: 0;
    background: rgba(15, 25, 50, 0.65);
    display: none; align-items: flex-start; justify-content: center;
    z-index: 1050; padding: 24px 16px; overflow-y: auto;
    backdrop-filter: blur(2px);
  }
  .ov-overlay.show { display: flex; }
  .ov-modal {
    background: #ffffff; width: 100%; max-width: 1080px;
    border-radius: 14px; box-shadow: 0 25px 60px rgba(0,0,0,0.4);
    overflow: hidden; display: grid; grid-template-rows: auto 1fr auto;
    margin-bottom: 24px; animation: ovPop 0.2s ease-out;
  }
  @keyframes ovPop {
    from { transform: scale(0.95) translateY(8px); opacity: 0; }
    to { transform: scale(1) translateY(0); opacity: 1; }
  }
  .ov-header {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 55%, #4a90e2 100%);
    color: white; padding: 14px 22px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .ov-header .ov-title { display: flex; flex-direction: column; line-height: 1.25; }
  .ov-header .ov-title .eyebrow { font-size: 10.5px; letter-spacing: 1.5px; opacity: 0.85; font-weight: 600; }
  .ov-header .ov-title .main { font-size: 17px; font-weight: 800; margin-top: 2px; letter-spacing: 0.3px; }
  .ov-header .ov-title .main .sub { font-weight: 500; opacity: 0.78; font-size: 11.5px; margin-left: 8px; }
  .ov-header .x-btn {
    background: rgba(255,255,255,0.15); border: none; color: white;
    width: 32px; height: 32px; border-radius: 50%;
    cursor: pointer; font-size: 19px; line-height: 1; font-family: inherit;
    transition: background 0.15s;
  }
  .ov-header .x-btn:hover { background: rgba(255,255,255,0.32); }

  .ov-body { display: grid; grid-template-columns: 280px 1fr; background: #f8f9fb; min-height: 0; }

  .ov-side {
    background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    color: white; padding: 22px 20px 24px;
    display: flex; flex-direction: column; gap: 14px;
  }
  .ov-side .ov-thumb { background: #ffffff; border-radius: 10px; padding: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.18); }
  .ov-side .ov-thumb img { width: 100%; height: auto; display: block; border-radius: 4px; }
  .ov-side .ov-model-code { font-size: 22px; font-weight: 800; font-family: 'Consolas', monospace; letter-spacing: -0.5px; line-height: 1.15; margin-top: 2px; }
  .ov-side .ov-model-desc { font-size: 12px; opacity: 0.92; line-height: 1.4; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.22); }
  .ov-side .ov-keylist { display: flex; flex-direction: column; }
  .ov-side .ov-keyrow {
    display: grid; grid-template-columns: 110px 1fr; gap: 8px;
    padding: 8px 0; border-bottom: 1px dotted rgba(255,255,255,0.22);
    font-size: 12px; align-items: baseline;
  }
  .ov-side .ov-keyrow:last-child { border-bottom: none; }
  .ov-side .ov-keyrow .k { color: rgba(255,255,255,0.78); font-weight: 600; letter-spacing: 0.2px; }
  .ov-side .ov-keyrow .v {
    text-align: right; font-weight: 700; font-family: 'Consolas', monospace;
    font-size: 12.5px; letter-spacing: -0.2px;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .ov-side .ov-keyrow .v.accent { color: #ffd54f; }
  .ov-side .ov-keyrow .v.warn { color: #ff8a65; }
  .ov-side .ov-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 4px; }
  .ov-side .ov-tag {
    background: rgba(255,255,255,0.18); color: white;
    font-size: 10.5px; padding: 3px 8px; border-radius: 10px;
    font-weight: 600; letter-spacing: 0.2px;
  }

  .ov-main { padding: 20px 24px 22px; background: #ffffff; overflow: auto; }
  .ov-tabs {
    display: flex; gap: 0; border-bottom: 2px solid #e3e7ee;
    margin: -4px -4px 16px; padding: 0 4px; overflow-x: auto;
  }
  .ov-tab {
    background: transparent; border: none;
    padding: 11px 16px 10px; font-size: 13px; font-weight: 700;
    color: #78909c; cursor: pointer;
    border-bottom: 3px solid transparent; margin-bottom: -2px;
    font-family: inherit; transition: all 0.15s; white-space: nowrap;
  }
  .ov-tab:hover { color: #2a5298; }
  .ov-tab.active { color: #1e3c72; border-bottom-color: #c62828; }

  .ov-pane { display: none; }
  .ov-pane.active { display: block; }

  .ov-hero { display: grid; grid-template-columns: 1.4fr 1fr; gap: 18px; align-items: stretch; }
  .ov-hero .ov-bigdiagram {
    background: linear-gradient(135deg, #f8f9fb 0%, #eef2f7 100%);
    border: 1px solid #e3e7ee; border-radius: 10px; padding: 14px;
    display: flex; align-items: center; justify-content: center;
    min-height: 280px;
  }
  .ov-hero .ov-bigdiagram img { max-width: 100%; max-height: 320px; height: auto; display: block; }
  .ov-hero .ov-bigdiagram .nodiag { color: #b0bec5; font-size: 13px; text-align: center; padding: 40px 20px; }

  .ov-spec-mini {
    background: #ffffff; border: 1px solid #e3e7ee;
    border-radius: 10px; padding: 14px 16px;
  }
  .ov-spec-mini .title {
    font-size: 12px; font-weight: 800; color: #2a5298;
    letter-spacing: 0.5px; margin-bottom: 8px;
    padding-bottom: 6px; border-bottom: 1.5px solid #2a5298;
  }
  .ov-spec-mini .row {
    display: grid; grid-template-columns: 1fr auto; gap: 8px;
    padding: 7px 0; border-bottom: 1px dotted #cfd8dc;
    font-size: 12.5px; align-items: baseline;
  }
  .ov-spec-mini .row:last-child { border-bottom: none; }
  .ov-spec-mini .row .k { color: #546e7a; font-weight: 600; }
  .ov-spec-mini .row .v { color: #1a1a1a; font-weight: 700; font-family: 'Consolas', monospace; text-align: right; }
  .ov-spec-mini .row .v b { color: #c62828; }

  .ov-section-title {
    font-size: 13px; font-weight: 800; color: white;
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    padding: 7px 13px; margin: 16px 0 10px;
    letter-spacing: 0.3px; border-left: 4px solid #c62828;
    border-radius: 0 4px 4px 0;
  }
  .ov-flowtable {
    width: 100%; border-collapse: collapse; font-size: 12.5px;
    background: white; border-radius: 8px; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  }
  .ov-flowtable thead { background: linear-gradient(135deg, #455a64 0%, #37474f 100%); color: white; }
  .ov-flowtable th, .ov-flowtable td { padding: 8px 12px; border-bottom: 1px solid #eceff1; text-align: center; }
  .ov-flowtable th { font-weight: 700; letter-spacing: 0.2px; }
  .ov-flowtable td:first-child { text-align: left; font-weight: 600; color: #455a64; }
  .ov-flowtable tbody tr:last-child td { border-bottom: none; }
  .ov-flowtable .total-row { background: #fff8e1; font-weight: 800; }
  .ov-flowtable .total-row td { color: #c62828; }

  .ov-fullspec { width: 100%; border-collapse: collapse; font-size: 12.5px; }
  .ov-fullspec th, .ov-fullspec td { border: 1px solid #cfd8dc; padding: 8px 12px; text-align: center; }
  .ov-fullspec thead th { background: #eceff1; color: #1e3c72; font-weight: 700; }
  .ov-fullspec td:first-child { text-align: left; font-weight: 600; }
  .ov-fullspec .group-row td {
    background: #1e3c72; color: white; font-weight: 700;
    text-align: left; font-size: 11.5px; letter-spacing: 0.3px;
  }

  .ov-footer {
    background: #f8f9fb; border-top: 1.5px solid #e3e7ee;
    padding: 14px 22px;
    display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px;
  }
  .ov-action {
    background: white; border: 1.5px solid #d8dde3;
    border-radius: 9px; padding: 11px 8px 9px; cursor: pointer;
    transition: all 0.18s; text-align: center; font-family: inherit;
    display: flex; flex-direction: column; align-items: center; gap: 4px;
    min-width: 0;
  }
  .ov-action:hover {
    border-color: #2a5298; background: #f3f7fc;
    transform: translateY(-1px); box-shadow: 0 4px 10px rgba(42,82,152,0.18);
  }
  .ov-action.primary {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    border-color: #1e3c72; color: white;
  }
  .ov-action.primary:hover {
    background: linear-gradient(135deg, #142850 0%, #1e3c72 100%);
    box-shadow: 0 6px 14px rgba(30,60,114,0.28);
  }
  .ov-action .icon { font-size: 22px; line-height: 1; }
  .ov-action .label { font-size: 12.5px; font-weight: 700; color: #1e3c72; letter-spacing: 0.2px; }
  .ov-action .sub { font-size: 9.5px; color: #78909c; letter-spacing: 0.5px; }
  .ov-action.primary .label { color: white; }
  .ov-action.primary .sub { color: rgba(255,255,255,0.78); }

  /* ============ 자료 준비중 placeholder 팝업 ============ */
  .ph-overlay {
    position: fixed; inset: 0; background: rgba(15, 25, 50, 0.65);
    display: none; align-items: center; justify-content: center;
    z-index: 1200; padding: 20px; backdrop-filter: blur(3px);
  }
  .ph-overlay.show { display: flex; }
  .ph-modal {
    background: white; width: 100%; max-width: 460px;
    border-radius: 14px; box-shadow: 0 20px 50px rgba(0,0,0,0.35);
    overflow: hidden; animation: ovPop 0.18s ease-out;
  }
  .ph-modal .ph-head {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white; padding: 14px 20px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .ph-modal .ph-head .t { font-size: 16px; font-weight: 800; letter-spacing: 0.3px; }
  .ph-modal .ph-head .x-btn {
    background: rgba(255,255,255,0.15); border: none; color: white;
    width: 28px; height: 28px; border-radius: 50%;
    cursor: pointer; font-size: 17px; font-family: inherit;
  }
  .ph-modal .ph-head .x-btn:hover { background: rgba(255,255,255,0.3); }
  .ph-modal .ph-body { padding: 28px 24px 22px; text-align: center; }
  .ph-modal .ph-icon { font-size: 50px; margin-bottom: 10px; }
  .ph-modal .ph-title { font-size: 18px; font-weight: 800; color: #1e3c72; margin-bottom: 6px; }
  .ph-modal .ph-model { font-family: 'Consolas', monospace; font-size: 14px; font-weight: 700; color: #c62828; margin-bottom: 14px; }
  .ph-modal .ph-msg {
    font-size: 13px; color: #455a64; line-height: 1.6;
    background: #f8f9fb; border: 1px dashed #cfd8dc;
    border-radius: 8px; padding: 14px 16px; margin-bottom: 16px;
  }
  .ph-modal .ph-foot { padding: 0 24px 22px; text-align: right; }
  .ph-modal .ph-foot button {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white; border: none; padding: 9px 22px;
    border-radius: 7px; font-size: 13px; font-weight: 700;
    cursor: pointer; font-family: inherit;
    box-shadow: 0 4px 10px rgba(42,82,152,0.25);
  }
  .ph-modal .ph-foot button:hover { transform: translateY(-1px); box-shadow: 0 6px 14px rgba(42,82,152,0.32); }

  @media (max-width: 880px) {
    .ov-body { grid-template-columns: 1fr; }
    .ov-side { padding: 18px 18px 20px; }
    .ov-hero { grid-template-columns: 1fr; }
    .ov-footer { grid-template-columns: repeat(2, 1fr); }
  }

  @media (max-width: 760px) {
    .body { grid-template-columns: 1fr; }
    .input-section { border-right: none; border-bottom: 1px solid #e8eaed; }
    .header .logo { display: none; }
    .form-row, .form-row-3 { grid-template-columns: 1fr; }
  }
</style>"""

assert CSS_OLD in src, 'CSS_OLD anchor not found'
src = src.replace(CSS_OLD, CSS_NEW)

# ---------- 2. HTML BLOCK (replace docMenuOverlay block) ----------
HTML_OLD = """<!-- ======================== 문서 선택 팝업 ======================== -->
<div id="docMenuOverlay" class="doc-menu-overlay" onclick="closeDocMenu(event)">
  <div class="doc-menu" onclick="event.stopPropagation()">
    <div class="doc-menu-header">
      <div class="title-row">
        <span class="label">문서 선택 / Select Document</span>
        <span class="model" id="docMenuTitle">SJMO-300 × 1Cell</span>
      </div>
      <button class="x-btn" onclick="closeDocMenu()">×</button>
    </div>
    <div class="doc-menu-body">
      <button class="doc-btn" onclick="docMenuChoose('report')">
        <div class="icon">📄</div>
        <div class="title">선정서</div>
        <div class="desc">Selection Report</div>
        <span class="ext">HTML · 인쇄</span>
      </button>
      <button class="doc-btn" onclick="docMenuChoose('spec')">
        <div class="icon">📋</div>
        <div class="title">사양서</div>
        <div class="desc">Specification Sheet</div>
        <span class="ext">.HWP</span>
      </button>
      <button class="doc-btn" onclick="docMenuChoose('drawing')">
        <div class="icon">📐</div>
        <div class="title">도면</div>
        <div class="desc">Drawing</div>
        <span class="ext">.DWG</span>
      </button>
    </div>
  </div>
</div>"""

HTML_NEW = """<!-- ======================== 장비 개요 (Equipment Overview) ======================== -->
<div id="overviewOverlay" class="ov-overlay" onclick="closeOverview(event)">
  <div class="ov-modal" onclick="event.stopPropagation()">
    <div class="ov-header">
      <div class="ov-title">
        <span class="eyebrow">EQUIPMENT OVERVIEW</span>
        <span class="main">장비 개요 <span class="sub" id="ovSubtitle">선정 모델 정보 / Selected Model Information</span></span>
      </div>
      <button class="x-btn" onclick="closeOverview()" title="닫기">×</button>
    </div>

    <div class="ov-body">
      <aside class="ov-side">
        <div class="ov-thumb">
          <img id="ovThumb" src="" alt="냉각탑 개념도">
        </div>
        <div>
          <div class="ov-model-code" id="ovModelCode">SJCO-300</div>
          <div class="ov-model-desc" id="ovModelDesc">대향류형 흡입송풍식</div>
        </div>
        <div class="ov-keylist" id="ovKeyList"></div>
        <div class="ov-tags" id="ovTags"></div>
      </aside>

      <main class="ov-main">
        <div class="ov-tabs">
          <button class="ov-tab active" onclick="switchOvTab('overview', this)">개요 (Overview)</button>
          <button class="ov-tab" onclick="switchOvTab('spec', this)">사양 상세 (Specifications)</button>
          <button class="ov-tab" onclick="switchOvTab('flow', this)">설계 조건 (Design Conditions)</button>
        </div>

        <div id="ovPaneOverview" class="ov-pane active">
          <div class="ov-hero">
            <div class="ov-bigdiagram">
              <img id="ovBigDiagram" src="" alt="냉각탑 구조 개념도">
            </div>
            <div class="ov-spec-mini" id="ovSpecMini"></div>
          </div>
          <div class="ov-section-title">▌선정 결과 요약 (Selection Summary)</div>
          <div id="ovSummary"></div>
        </div>

        <div id="ovPaneSpec" class="ov-pane">
          <div class="ov-section-title">▌장비 사양 (Equipment Specifications)</div>
          <div id="ovSpecFull"></div>
        </div>

        <div id="ovPaneFlow" class="ov-pane">
          <div class="ov-section-title">▌설계 조건 / Design Conditions</div>
          <div id="ovDesignTable"></div>
        </div>
      </main>
    </div>

    <div class="ov-footer">
      <button class="ov-action primary" onclick="ovChooseDoc('report')" title="선정서 보기 / 인쇄">
        <span class="icon">📄</span>
        <span class="label">선정서</span>
        <span class="sub">SELECTION REPORT</span>
      </button>
      <button class="ov-action" onclick="ovChooseDoc('spec')" title="사양서 다운로드">
        <span class="icon">📋</span>
        <span class="label">사양서</span>
        <span class="sub">SPECIFICATION</span>
      </button>
      <button class="ov-action" onclick="ovChooseDoc('drawing')" title="도면 다운로드">
        <span class="icon">📐</span>
        <span class="label">도면</span>
        <span class="sub">DRAWING</span>
      </button>
      <button class="ov-action" onclick="ovChooseDoc('makeup')" title="보급수계산서">
        <span class="icon">💧</span>
        <span class="label">보급수계산서</span>
        <span class="sub">MAKE-UP WATER</span>
      </button>
      <button class="ov-action" onclick="ovChooseDoc('louver')" title="루버면적검토서">
        <span class="icon">🪟</span>
        <span class="label">루버면적검토서</span>
        <span class="sub">LOUVER AREA</span>
      </button>
    </div>
  </div>
</div>

<!-- ======================== 자료 준비중 placeholder 팝업 ======================== -->
<div id="phOverlay" class="ph-overlay" onclick="closePh(event)">
  <div class="ph-modal" onclick="event.stopPropagation()">
    <div class="ph-head">
      <span class="t" id="phHeadTitle">자료 준비중</span>
      <button class="x-btn" onclick="closePh()">×</button>
    </div>
    <div class="ph-body">
      <div class="ph-icon" id="phIcon">📎</div>
      <div class="ph-title" id="phTitle">자료 연결 예정</div>
      <div class="ph-model" id="phModel">SJxx-000 × 1Cell</div>
      <div class="ph-msg" id="phMsg">해당 자료는 추후 연결 예정입니다.</div>
    </div>
    <div class="ph-foot">
      <button onclick="closePh()">확인</button>
    </div>
  </div>
</div>"""

assert HTML_OLD in src, 'HTML_OLD anchor not found'
src = src.replace(HTML_OLD, HTML_NEW)

# ---------- 3. JS BLOCK (replace doc menu JS) ----------
JS_OLD = """// ============ 문서 선택 팝업 ============
// 배포 환경(웹 서버)과 로컬 환경 모두 지원 — 상대경로 사용
const SPEC_FILE_PATH = './files/spec.hwp';
const DRAWING_FILE_PATH = './files/drawing.dwg';
let _docMenuContext = null;

function openDocMenu(modelType, modelCRT, cells) {
  _docMenuContext = { modelType, modelCRT, cells };
  document.getElementById('docMenuTitle').textContent = `${modelType}-${modelCRT} × ${cells}Cell`;
  document.getElementById('docMenuOverlay').classList.add('show');
  document.body.style.overflow = 'hidden';
}

function closeDocMenu(e) {
  if (e && e.target && !e.target.classList.contains('doc-menu-overlay') && !e.target.classList.contains('x-btn')) return;
  document.getElementById('docMenuOverlay').classList.remove('show');
  if (!document.getElementById('reportOverlay').classList.contains('show')) {
    document.body.style.overflow = '';
  }
}

function docMenuChoose(action) {
  const ctx = _docMenuContext;
  if (!ctx) return;

  if (action === 'report') {
    document.getElementById('docMenuOverlay').classList.remove('show');
    openReport(ctx.modelType, ctx.modelCRT, ctx.cells);
    return;
  }

  if (action === 'spec') {
    triggerDownload(SPEC_FILE_PATH, `${ctx.modelType}-${ctx.modelCRT}_사양서.hwp`);
  } else if (action === 'drawing') {
    triggerDownload(DRAWING_FILE_PATH, `${ctx.modelType}-${ctx.modelCRT}_도면.dwg`);
  }
  document.getElementById('docMenuOverlay').classList.remove('show');
  document.body.style.overflow = '';
}

function triggerDownload(url, suggestedName) {
  const a = document.createElement('a');
  a.href = url;
  a.download = suggestedName;
  a.target = '_blank';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}"""

JS_NEW = r"""// ============ 자료 파일 경로 ============
const SPEC_FILE_PATH = './files/spec.hwp';
const DRAWING_FILE_PATH = './files/drawing.dwg';

// ============ 모델별 개념도 (성지공조기술 카탈로그 발췌) ============
const MODEL_DIAGRAMS = {
  'SJMO':   '__DIAG_SJMO__',
  'SJMO-A': '__DIAG_SJMO_A__',
  'SJCO':   '__DIAG_SJCO__',
  'SJXO':   '__DIAG_SJXO__'
};

// ============ 장비 개요 (Equipment Overview) ============
let _ovContext = null;

function openOverview(modelType, modelCRT, cells) {
  const I = _captureInputs();
  if (!I) {
    alert('계산값이 없습니다. 먼저 「선정 계산」을 실행해주세요.');
    return;
  }
  _ovContext = { modelType, modelCRT, cells, I };

  const sp = getVariantSpec(modelType, modelCRT, I);
  const variantSuffix = _optionSuffix(modelType, I);
  const variantCode = `${modelType}-${modelCRT}${variantSuffix}`;
  const totalCap = modelCRT * cells;
  const reservePct = ((totalCap / I.minCapacity - 1) * 100).toFixed(1);
  const gap = (typeof CELL_GAP !== 'undefined' && CELL_GAP[modelType]) || 0;

  document.getElementById('ovSubtitle').textContent =
    `${MODEL_DESC[modelType]} · ${cells} Cell 구성`;

  const diag = MODEL_DIAGRAMS[modelType] || '';
  const thumb = document.getElementById('ovThumb');
  const big = document.getElementById('ovBigDiagram');
  const oldNo = big.parentElement.querySelector('.nodiag');
  if (oldNo) oldNo.remove();
  if (diag) {
    thumb.src = diag; thumb.style.display = 'block';
    big.src = diag;   big.style.display = 'block';
  } else {
    thumb.removeAttribute('src'); thumb.style.display = 'none';
    big.removeAttribute('src');   big.style.display = 'none';
    const ph = document.createElement('div');
    ph.className = 'nodiag';
    ph.textContent = '개념도 없음';
    big.parentElement.appendChild(ph);
  }

  document.getElementById('ovModelCode').textContent = variantCode;
  document.getElementById('ovModelDesc').innerHTML =
    `${MODEL_DESC[modelType]}${_optionDesc(modelType, I)}`;

  const totalLen = sp ? (sp.L * cells + gap * (cells - 1)) : null;
  const keyHtml = [
    {k:'호칭능력 / Capacity',       v:`${modelCRT} CRT/Cell`,                                    cls:'accent'},
    {k:'셀 구성 / Cells',           v:`${cells} Cell`,                                           cls:''},
    {k:'총 호칭능력 / Total',       v:`${totalCap} CRT`,                                         cls:'accent'},
    {k:'실여유율 / Reserve',        v:`${reservePct} %`,                                         cls:(parseFloat(reservePct) < 0 ? 'warn' : '')},
    {k:'팬 모터 / Fan Motor',       v: sp ? `${sp.kw} kW × ${cells}EA` : '—',                    cls:''},
    {k:'풍량 / Air Volume',         v: sp ? `${(sp.cmm*cells).toLocaleString()} CMM` : '—',      cls:''},
    {k:'설계 유량 / Design Flow',   v: `${I.flowM3h.toFixed(1)} ㎥/h`,                            cls:''},
    {k:'외형 (L×W×H)',              v: sp ? `${totalLen.toLocaleString()}×${sp.W.toLocaleString()}×${sp.H.toLocaleString()}` : '—', cls:''},
    {k:'배관 입/출구 / Pipe',       v: sp ? `${sp.pipe} A` : '—',                                cls:''},
    {k:'운전 중량 / Op. Wt.',       v: sp ? `${(sp.opW*cells).toLocaleString()} kg` : '—',       cls:''}
  ].map(r => `<div class="ov-keyrow"><div class="k">${r.k}</div><div class="v ${r.cls}">${r.v}</div></div>`).join('');
  document.getElementById('ovKeyList').innerHTML = keyHtml;

  const tags = [`${MODEL_DESC[modelType]}`];
  if (I.optMist) tags.push('백연감소');
  if (I.optInletSil) tags.push('흡입소음기');
  if (I.optDischargeSil) tags.push('토출소음기');
  if (!I.optMist && !I.optInletSil && !I.optDischargeSil &&
      (modelType === 'SJMO' || modelType === 'SJMO-A')) tags.push('기본형');
  document.getElementById('ovTags').innerHTML =
    tags.map(t => `<span class="ov-tag">${t}</span>`).join('');

  document.getElementById('ovSpecMini').innerHTML = `
    <div class="title">▌핵심 사양 / Key Specifications</div>
    <div class="row"><div class="k">모델 / Model</div><div class="v"><b>${variantCode}</b></div></div>
    <div class="row"><div class="k">셀 / Cells</div><div class="v">${cells} Cell</div></div>
    <div class="row"><div class="k">호칭능력 / Capacity</div><div class="v"><b>${totalCap} CRT</b></div></div>
    <div class="row"><div class="k">유량 / Flow</div><div class="v">${I.flowM3h.toFixed(1)} ㎥/h</div></div>
    <div class="row"><div class="k">Range / Approach</div><div class="v">${I.range.toFixed(1)}℃ / ${I.approach.toFixed(1)}℃</div></div>
    <div class="row"><div class="k">팬 모터 / Fan</div><div class="v">${sp ? sp.kw : '—'} kW × ${cells}</div></div>
    <div class="row"><div class="k">실여유율 / Reserve</div><div class="v"><b>${reservePct} %</b></div></div>
  `;

  document.getElementById('ovSummary').innerHTML = `
    <table class="ov-flowtable">
      <thead>
        <tr><th>항목 / Item</th><th>셀당 / Per Cell</th><th>총합 / Total (×${cells})</th></tr>
      </thead>
      <tbody>
        <tr><td>호칭능력 / Capacity (CRT)</td><td>${modelCRT}</td><td>${totalCap}</td></tr>
        <tr><td>냉각수 유량 / Flow (LPM)</td><td>${(I.flowLpm/cells).toLocaleString('ko-KR',{maximumFractionDigits:0})}</td><td>${I.flowLpm.toLocaleString('ko-KR',{maximumFractionDigits:0})}</td></tr>
        <tr><td>송풍기 풍량 / Air (CMM)</td><td>${sp ? sp.cmm.toLocaleString() : '—'}</td><td>${sp ? (sp.cmm*cells).toLocaleString() : '—'}</td></tr>
        <tr><td>팬 모터 / Fan Motor (kW)</td><td>${sp ? sp.kw : '—'}</td><td>${sp ? (sp.kw*cells).toFixed(1) : '—'}</td></tr>
        <tr class="total-row"><td>최소 요구용량 / Min Required</td><td colspan="2">${I.minCapacity.toFixed(2)} CRT (실 ${totalCap} CRT, 여유 ${reservePct}%)</td></tr>
      </tbody>
    </table>
  `;

  if (sp) {
    const designLpmTotal = I.flowLpm;
    const designLpmPerCell = designLpmTotal / cells;
    const eaTag = (cells > 1) ? ` × ${cells}EA` : '';
    const pipeTotal = (sz) => `${sz}${eaTag}`;
    const totalDim = `${totalLen.toLocaleString()} × ${sp.W.toLocaleString()} × ${sp.H.toLocaleString()}`;
    const perCellDim = `${sp.L.toLocaleString()} × ${sp.W.toLocaleString()} × ${sp.H.toLocaleString()}`;
    document.getElementById('ovSpecFull').innerHTML = `
      <table class="ov-fullspec">
        <thead>
          <tr>
            <th style="width:34%;">항목 / Item</th>
            <th style="width:15%;">단위 / Unit</th>
            <th>셀당 / Per Cell</th>
            <th>총합 / Total (×${cells} Cell)</th>
          </tr>
        </thead>
        <tbody>
          <tr class="group-row"><td colspan="4">▌ 성능 (Performance)</td></tr>
          <tr><td>호칭능력 (Cooling Capacity)</td><td>CRT</td><td>${modelCRT}</td><td><b>${totalCap}</b></td></tr>
          <tr><td>냉각수 유량 (Design Flow)</td><td>LPM</td><td>${designLpmPerCell.toLocaleString('ko-KR',{maximumFractionDigits:0})}</td><td><b>${designLpmTotal.toLocaleString('ko-KR',{maximumFractionDigits:0})}</b></td></tr>
          <tr><td>송풍기 풍량 (Air Volume)</td><td>CMM</td><td>${sp.cmm.toLocaleString()}</td><td><b>${(sp.cmm*cells).toLocaleString()}</b></td></tr>
          <tr><td>팬 모터 동력 (Fan Motor)</td><td>kW</td><td>${sp.kw}</td><td><b>${(sp.kw*cells).toFixed(1)}</b></td></tr>

          <tr class="group-row"><td colspan="4">▌ 중량 (Weight)</td></tr>
          <tr><td>제품 중량 (Shipping)</td><td>kg</td><td>${sp.dryW.toLocaleString()}</td><td><b>${(sp.dryW*cells).toLocaleString()}</b></td></tr>
          <tr><td>운전 중량 (Operating)</td><td>kg</td><td>${sp.opW.toLocaleString()}</td><td><b>${(sp.opW*cells).toLocaleString()}</b></td></tr>

          <tr class="group-row"><td colspan="4">▌ 외형 치수 (Dimensions, mm)</td></tr>
          <tr><td>L × W × H</td><td>mm</td><td>${perCellDim}</td><td><b>${totalDim}</b></td></tr>
          <tr><td>셀 간 설치간격 (Cell Gap)</td><td>mm</td><td colspan="2">${gap}${cells > 1 ? ` × ${cells-1}개소` : ' (단일셀 N/A)'}</td></tr>

          <tr class="group-row"><td colspan="4">▌ 배관 사양 (Pipe Diameter, A)</td></tr>
          <tr><td>입/출구관 (In/Out)</td><td>A</td><td>${sp.pipe}</td><td>${pipeTotal(sp.pipe)}</td></tr>
          <tr><td>보급관 (Make-up)</td><td>A</td><td>25</td><td>${pipeTotal('25')}</td></tr>
          <tr><td>넘침관 (Overflow)</td><td>A</td><td>80</td><td>${pipeTotal('80')}</td></tr>
          <tr><td>배수관 (Drain)</td><td>A</td><td>50</td><td>${pipeTotal('50')}</td></tr>
        </tbody>
      </table>
    `;
  } else {
    document.getElementById('ovSpecFull').innerHTML =
      `<div style="color:#78909c;font-size:12.5px;padding:12px;">사양 데이터 없음 — 카탈로그 별도 확인</div>`;
  }

  document.getElementById('ovDesignTable').innerHTML = `
    <table class="ov-fullspec">
      <thead><tr><th style="width:36%;">항목 / Item</th><th>값 / Value</th></tr></thead>
      <tbody>
        <tr><td>냉각수 유량 (Design Flow)</td><td>${I.flowM3h.toFixed(2)} ㎥/h　(${I.flowLpm.toFixed(0)} LPM)</td></tr>
        <tr><td>입구 온도 (Hot Water Temp.)</td><td>${I.tin.toFixed(1)} ℃</td></tr>
        <tr><td>출구 온도 (Cold Water Temp.)</td><td>${I.tout.toFixed(1)} ℃</td></tr>
        <tr><td>외기 습구온도 (Wet Bulb)</td><td>${I.twb.toFixed(1)} ℃</td></tr>
        <tr><td>Range</td><td>${I.range.toFixed(2)} ℃</td></tr>
        <tr><td>Approach</td><td>${I.approach.toFixed(2)} ℃</td></tr>
        <tr><td>Rating Factor</td><td>${I.rf.toFixed(6)}</td></tr>
        <tr><td>설계 여유율 (Margin)</td><td>${I.margin.toFixed(1)} %</td></tr>
        <tr><td>최소 요구용량 (Min Required)</td><td><b>${I.minCapacity.toFixed(2)} CRT</b></td></tr>
        <tr><td>권장용량 (Recommended)</td><td><b>${I.marginCapacity.toFixed(2)} CRT</b></td></tr>
        <tr><td>열부하 (Heat Load)</td><td>${I.heatKw.toFixed(1)} kW　(${I.usrt.toFixed(1)} USRT)</td></tr>
      </tbody>
    </table>
  `;

  document.querySelectorAll('.ov-tab').forEach((t,i) => t.classList.toggle('active', i===0));
  document.querySelectorAll('.ov-pane').forEach((p,i) => p.classList.toggle('active', i===0));

  document.getElementById('overviewOverlay').classList.add('show');
  document.body.style.overflow = 'hidden';
}

function closeOverview(e) {
  if (e && e.target && !e.target.classList.contains('ov-overlay')) return;
  document.getElementById('overviewOverlay').classList.remove('show');
  const reportOpen = document.getElementById('reportOverlay').classList.contains('show');
  const phOpen = document.getElementById('phOverlay').classList.contains('show');
  if (!reportOpen && !phOpen) document.body.style.overflow = '';
}

function switchOvTab(name, btnEl) {
  document.querySelectorAll('.ov-tab').forEach(b => b.classList.remove('active'));
  if (btnEl) btnEl.classList.add('active');
  const map = { overview: 'ovPaneOverview', spec: 'ovPaneSpec', flow: 'ovPaneFlow' };
  document.querySelectorAll('.ov-pane').forEach(p => p.classList.remove('active'));
  const id = map[name];
  if (id) document.getElementById(id).classList.add('active');
}

function ovChooseDoc(action) {
  const ctx = _ovContext;
  if (!ctx) return;

  if (action === 'report') {
    openReport(ctx.modelType, ctx.modelCRT, ctx.cells);
    return;
  }
  if (action === 'spec') {
    triggerDownload(SPEC_FILE_PATH, `${ctx.modelType}-${ctx.modelCRT}_사양서.hwp`);
    return;
  }
  if (action === 'drawing') {
    triggerDownload(DRAWING_FILE_PATH, `${ctx.modelType}-${ctx.modelCRT}_도면.dwg`);
    return;
  }
  if (action === 'makeup') {
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
  }
}

function openPh(opt) {
  const ctx = _ovContext;
  document.getElementById('phHeadTitle').textContent = opt.headTitle || '자료 준비중';
  document.getElementById('phIcon').textContent = opt.icon || '📎';
  document.getElementById('phTitle').textContent = opt.title || '자료 연결 예정';
  document.getElementById('phModel').textContent =
    ctx ? `${ctx.modelType}-${ctx.modelCRT} × ${ctx.cells}Cell` : '';
  document.getElementById('phMsg').innerHTML = opt.msg || '추후 연결 예정입니다.';
  document.getElementById('phOverlay').classList.add('show');
  document.body.style.overflow = 'hidden';
}

function closePh(e) {
  if (e && e.target && !e.target.classList.contains('ph-overlay')) return;
  document.getElementById('phOverlay').classList.remove('show');
  const ovOpen = document.getElementById('overviewOverlay').classList.contains('show');
  const reportOpen = document.getElementById('reportOverlay').classList.contains('show');
  if (!ovOpen && !reportOpen) document.body.style.overflow = '';
}

function triggerDownload(url, suggestedName) {
  const a = document.createElement('a');
  a.href = url;
  a.download = suggestedName;
  a.target = '_blank';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}"""

assert JS_OLD in src, 'JS_OLD anchor not found'
src = src.replace(JS_OLD, JS_NEW)

# ---------- 4. onclick rename ----------
n_before = src.count('openDocMenu(')
src = src.replace('openDocMenu(', 'openOverview(')
print('renamed onclick openDocMenu → openOverview:', n_before)

# ---------- 5. Escape handler ----------
ESC_OLD = """document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    if (document.getElementById('docMenuOverlay').classList.contains('show')) {
      document.getElementById('docMenuOverlay').classList.remove('show');
      if (!document.getElementById('reportOverlay').classList.contains('show')) {
        document.body.style.overflow = '';
      }
    } else {
      closeReport();
    }
  }
});"""

ESC_NEW = """document.addEventListener('keydown', (e) => {
  if (e.key !== 'Escape') return;
  // 우선순위: placeholder → 선정서 → 개요
  const phEl     = document.getElementById('phOverlay');
  const reportEl = document.getElementById('reportOverlay');
  const ovEl     = document.getElementById('overviewOverlay');
  if (phEl     && phEl.classList.contains('show'))     { closePh({target: phEl}); return; }
  if (reportEl && reportEl.classList.contains('show')) { closeReport(); return; }
  if (ovEl     && ovEl.classList.contains('show'))     { closeOverview({target: ovEl}); return; }
});

// 선정서 닫힐 때 다른 모달이 열려있으면 body scroll 잠금 유지
const _origCloseReport_v2 = closeReport;
closeReport = function(e) {
  if (e && e.target && !e.target.classList.contains('report-overlay') && e.type === 'click') {
    if (!e.target.classList.contains('close-btn')) return;
  }
  document.getElementById('reportOverlay').classList.remove('show');
  const ovOpen = document.getElementById('overviewOverlay').classList.contains('show');
  const phOpen = document.getElementById('phOverlay').classList.contains('show');
  if (!ovOpen && !phOpen) document.body.style.overflow = '';
};"""

assert ESC_OLD in src, 'ESC_OLD anchor not found'
src = src.replace(ESC_OLD, ESC_NEW)

# ---------- 6. Inject base64 diagrams ----------
def b64uri(p):
    with open(p,'rb') as f:
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()

DIAGS = {
    '__DIAG_SJMO__'  : b64uri('work/diagrams/sjmo.jpg'),
    '__DIAG_SJMO_A__': b64uri('work/diagrams/sjmo-a.jpg'),
    '__DIAG_SJCO__'  : b64uri('work/diagrams/sjco.jpg'),
    '__DIAG_SJXO__'  : b64uri('work/diagrams/sjxo.jpg'),
}
for k, v in DIAGS.items():
    if k not in src:
        print(f'!! placeholder {k} not in src')
    src = src.replace(k, v)

# ---------- 7. Sanity ----------
remaining = ['openDocMenu', 'docMenuOverlay', 'docMenuChoose', 'closeDocMenu',
             'doc-menu-overlay', 'doc-menu-header', 'docMenuTitle']
for needle in remaining:
    if needle in src:
        print(f'!! still references: {needle}  count={src.count(needle)}')

# Write final
with open(DST, 'w', encoding='utf-8') as f:
    f.write(src)

print('OK. wrote', DST, '→', os.path.getsize(DST), 'bytes')
