#!/usr/bin/env python3
"""
10th pass — three fixes:
  1. 전역 `.unit { position:absolute }` 가 입력필드 단위(°C, ㎥/h)용으로 만들어졌는데
     같은 클래스명이 결과박스의 `<span class="unit">T/h</span>`/`m²` 에도 적용되어
     unit 텍스트가 페이지 우측 상단으로 절대위치 이동해버리는 버그를 수정.
  2. 선정보고서의 Notes 한 줄짜리 disclaimer 를 5줄로 재구성 (각 항목별 1줄씩).
  3. 보급수 / 루버 인쇄 시 하단 여백이 과하게 남는 문제 — 폰트·패딩·gap 을 키워서
     A4 1페이지를 자연스럽게 채우도록 조정.
"""
import re, os

SRC = '냉각탑_선정프로그램_장비개요.html'
with open(SRC,'r',encoding='utf-8') as f: src=f.read()

# ============================================================
# 1) 결과박스 unit — position 리셋 (전역 .unit absolute 무력화)
# ============================================================
OLD_NUM_CSS = """  .calc-result-card .num {
    font-family: var(--font-mono);
    font-size: 24px; font-weight: 800; color: var(--org-600);
    letter-spacing: -0.5px;
    white-space: nowrap;
    display: inline-flex; align-items: baseline; gap: 4px;
  }
  .calc-result-card .num .unit {
    font-size: 16px; color: var(--org-700);
    font-weight: 700; letter-spacing: 0.2px;
    white-space: nowrap;
    display: inline-block;
  }"""
NEW_NUM_CSS = """  .calc-result-card .num {
    font-family: var(--font-mono);
    font-size: 28px; font-weight: 800; color: var(--org-600);
    letter-spacing: -0.5px;
    white-space: nowrap;
    display: inline-flex; align-items: baseline; gap: 6px;
  }
  /* 전역 .unit{position:absolute} 가 결과박스에는 적용되지 않도록 리셋 */
  .calc-result-card .num .unit {
    position: static !important;
    right: auto !important; top: auto !important;
    transform: none !important;
    pointer-events: auto !important;
    font-size: 18px; color: var(--org-700);
    font-weight: 700; letter-spacing: 0.2px;
    white-space: nowrap;
    display: inline-block;
  }"""
assert OLD_NUM_CSS in src
src = src.replace(OLD_NUM_CSS, NEW_NUM_CSS)


# ============================================================
# 2) 선정보고서 disclaimer 5줄로 재구성
# ============================================================
OLD_DISC = """    <div class="report-disclaimer">
      <b>※ Notes</b> · 1 CRT = 4.53 kW = 3,900 kcal/h (표준 37/32/27℃ 기준) · Rating Factor 자동 보정 · 옥외 표준 설치 가정 · 실제 설치환경(흡입 장애·토출 덕트·기류 간섭 등) 별도 검토 필요. 자세한 사항은 (주)성지공조기술로 문의 바랍니다.
    </div>"""
NEW_DISC = """    <div class="report-disclaimer">
      <b>※ Notes &amp; Disclaimer</b><br>
      1) 호칭능력(CRT)은 표준 설계조건 (입구 37℃ / 출구 32℃ / 습구 27℃, 1 CRT = 4.53 kW = 3,900 kcal/h) 기준으로 산정되었습니다.<br>
      2) Rating Factor 는 성지공조기술 자체 데이터베이스 기반으로 입력 조건(입·출구·습구온도)에 따라 자동 보정되었습니다.<br>
      3) 본 결과는 표준 옥외 노출 설치, 추가 정압 손실 없음, 외부 부속(차폐판·소음기 등) 미적용 조건을 가정한 값입니다.<br>
      4) 실제 설치환경(흡입 장애·토출 덕트·기류 간섭·공조계통 압력 등)에 따라 별도 보정 검토가 필요합니다.<br>
      5) 자세한 사항은 (주)성지공조기술로 문의 바랍니다.
    </div>"""
assert OLD_DISC in src
src = src.replace(OLD_DISC, NEW_DISC)


# ============================================================
# 3) 보급수·루버 — 인쇄/화면 모두 페이지를 더 채우도록 조정
#    핵심: calc-mini-row, calc-result-card, calc-unified 의
#    폰트·패딩·gap 을 키움. + 인쇄 모드에서 본문 폰트도 약간 상향.
# ============================================================

# 3-a) 결과박스 화면용 padding 키움
OLD_RESULT_BOX_BASE = """  .calc-result-card {
    background: linear-gradient(135deg, var(--org-100) 0%, var(--org-100) 100%);
    border: 2px solid var(--org-600);
    border-radius: 6px;
    padding: 12px 16px;
    margin: 14px 0 4px;
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 14px;
    align-items: center;
  }"""
NEW_RESULT_BOX_BASE = """  .calc-result-card {
    background: linear-gradient(135deg, var(--org-100) 0%, var(--org-100) 100%);
    border: 2.5px solid var(--org-600);
    border-radius: 8px;
    padding: 18px 22px;
    margin: 18px 0 6px;
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 18px;
    align-items: center;
  }"""
if OLD_RESULT_BOX_BASE in src:
    src = src.replace(OLD_RESULT_BOX_BASE, NEW_RESULT_BOX_BASE)


# 3-b) calc-mini-row 화면용 패딩 키움
OLD_MINI_ROW = """  .calc-mini-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin: 8px 0 12px;
  }
  .calc-mini-row .cell {
    background: var(--bg-50); border: 1px solid var(--ink-200);
    border-radius: 4px; padding: 6px 10px;
    text-align: center;
  }
  .calc-mini-row .cell .k {
    font-size: 10.5px; color: var(--ink-500);
    letter-spacing: 0.3px; font-weight: 600;
    margin-bottom: 1px;
  }
  .calc-mini-row .cell .v {
    font-family: var(--font-mono); font-weight: 800;
    font-size: 14px; color: var(--pri-800);
  }
  .calc-mini-row .cell .v .u {
    font-family: 'Malgun Gothic', sans-serif;
    font-size: 11px; color: var(--ink-600); font-weight: 500;
    margin-left: 2px;
  }"""
NEW_MINI_ROW = """  .calc-mini-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin: 12px 0 16px;
  }
  .calc-mini-row .cell {
    background: var(--bg-50); border: 1px solid var(--ink-200);
    border-radius: 6px; padding: 11px 14px 12px;
    text-align: center;
  }
  .calc-mini-row .cell .k {
    font-size: 11px; color: var(--ink-500);
    letter-spacing: 0.3px; font-weight: 600;
    margin-bottom: 4px;
  }
  .calc-mini-row .cell .v {
    font-family: var(--font-mono); font-weight: 800;
    font-size: 18px; color: var(--pri-800); letter-spacing: -0.3px;
  }
  .calc-mini-row .cell .v .u {
    font-family: var(--font-sans);
    font-size: 12px; color: var(--ink-600); font-weight: 500;
    margin-left: 3px;
  }"""
if OLD_MINI_ROW in src:
    src = src.replace(OLD_MINI_ROW, NEW_MINI_ROW)


# 3-c) calc-unified 화면용 폰트/패딩 키움
OLD_CALC_UNI = """  .calc-unified {
    width: 100%; border-collapse: collapse;
    font-size: 12.5px; margin: 4px 0 8px;
  }
  .calc-unified th, .calc-unified td {
    border: 1px solid var(--ink-300); padding: 6px 10px; text-align: center;
  }"""
NEW_CALC_UNI = """  .calc-unified {
    width: 100%; border-collapse: collapse;
    font-size: 13px; margin: 6px 0 10px;
  }
  .calc-unified th, .calc-unified td {
    border: 1px solid var(--ink-300); padding: 9px 12px; text-align: center;
  }"""
if OLD_CALC_UNI in src:
    src = src.replace(OLD_CALC_UNI, NEW_CALC_UNI)


# 3-d) 인쇄 모드에서 페이지를 더 채우도록 조정 — 보급수·루버 전용
#     기존 인쇄 룰을 더 여유있게
OLD_PRINT_TUNE = """  @media print {
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
    .calc-result-card .num .unit { font-size: 11pt !important; color: var(--org-700) !important; font-weight: 700 !important; }
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
  }"""
NEW_PRINT_TUNE = """  @media print {
    @page { size: A4 portrait; margin: 12mm 14mm; }
    /* 보급수·루버 보고서 — 페이지를 자연스럽게 채우도록 폰트·패딩 여유 있게 */
    .calc-mini-row { gap: 8px !important; margin: 9px 0 11px !important; }
    .calc-mini-row .cell { padding: 8px 11px 9px !important; }
    .calc-mini-row .cell .k { font-size: 8.5pt !important; margin-bottom: 3px !important; }
    .calc-mini-row .cell .v { font-size: 13pt !important; }
    .calc-mini-row .cell .v .u { font-size: 9pt !important; }
    .calc-unified { font-size: 10pt !important; margin: 6px 0 9px !important; }
    .calc-unified th, .calc-unified td { padding: 6px 9px !important; }
    .calc-mini-footer { font-size: 8.5pt !important; padding-top: 7px !important; margin-top: 10px !important; }
    .calc-mini-footer .note { font-size: 8pt !important; line-height: 1.5; }
    .calc-result-card { padding: 12px 16px !important; margin: 11px 0 7px !important; page-break-inside: avoid; }
    .calc-result-card .num { font-size: 22pt !important; }
    .calc-result-card .num .unit { font-size: 14pt !important; color: var(--org-700) !important; font-weight: 700 !important; }
    .calc-result-card .label { font-size: 10.5pt !important; }
    .calc-result-card .label .sub { font-size: 8.5pt !important; }
    .report-section-title { font-size: 11pt !important; padding: 5px 11px !important; margin: 9px 0 5px !important; }
    .report-selected { padding: 8px 13px !important; }
    .report-selected .model-info .model-code { font-size: 15pt !important; }
    .report-selected .model-info .model-desc { font-size: 9pt !important; }
    .report-selected .model-spec-row .spec-cell { padding: 0 12px !important; }
    .report-selected .model-spec-row .spec-cell .num { font-size: 12pt !important; }
    .report-selected .model-spec-row .spec-cell .label { font-size: 8pt !important; }
    .report-meta { font-size: 10pt !important; margin-bottom: 8px !important; gap: 2px 18px !important; }
    .report-meta .row .v.editable { font-size: 10pt !important; }
    .report-header { padding-bottom: 7px !important; margin-bottom: 9px !important; }
    .report-header .title-block .main-title { font-size: 18pt !important; }
    .report-header .title-block .eyebrow { font-size: 8pt !important; }
    .report-header .title-block .sub-title { font-size: 9pt !important; }
    .report-header .logo-block img { height: 34px !important; }
    .report-header .logo-block .corp { font-size: 8.5pt !important; }
    .report-body { padding: 0 !important; font-size: 10.5pt !important; }
    .report-modal { box-shadow: none !important; }
  }"""
if OLD_PRINT_TUNE in src:
    src = src.replace(OLD_PRINT_TUNE, NEW_PRINT_TUNE)


# 3-e) 선정서 추가 인쇄 룰도 살짝 여유 있게 (1페이지 fit 유지하면서)
#     이전 build9 에서 추가한 EXTRA_PRINT 블록을 갱신
OLD_EXTRA = """  /* === 선정서 1페이지 fit 강화 === */
  @media print {
    .report-body { font-size: 10pt !important; }
    .report-disclaimer { padding: 6px 11px !important; font-size: 8.5pt !important; line-height: 1.45 !important; }
    .report-footer { padding-top: 6px !important; margin-top: 7px !important; }
    .report-footer .copyright { font-size: 7.5pt !important; line-height: 1.35; }
    .report-footer .signature .corp-name { font-size: 9pt !important; }
    .report-grid { font-size: 9pt !important; gap: 1px 18px !important; }
    .report-grid .row { padding: 2px 0 !important; }
    .report-table { font-size: 9pt !important; }
    .report-table th, .report-table td { padding: 3px 7px !important; }
    /* 결과 박스 단위는 인쇄에서도 또렷하게 */
    .calc-result-card { padding: 8px 13px !important; }
    .calc-result-card .num { font-size: 17pt !important; }
    .calc-result-card .num .unit { font-size: 12pt !important; }
  }"""
NEW_EXTRA = """  /* === 선정서 1페이지 fit (5줄 disclaimer 포함) === */
  @media print {
    .report-disclaimer { padding: 8px 12px !important; font-size: 9pt !important; line-height: 1.55 !important; margin-top: 9px !important; }
    .report-footer { padding-top: 7px !important; margin-top: 9px !important; }
    .report-footer .copyright { font-size: 8pt !important; line-height: 1.4; }
    .report-footer .signature .corp-name { font-size: 9.5pt !important; }
    .report-grid { font-size: 9.5pt !important; gap: 2px 20px !important; }
    .report-grid .row { padding: 2.5px 0 !important; }
    .report-table { font-size: 9.5pt !important; }
    .report-table th, .report-table td { padding: 4px 8px !important; }
  }"""
if OLD_EXTRA in src:
    src = src.replace(OLD_EXTRA, NEW_EXTRA)


# ============================================================
# Save
# ============================================================
with open(SRC,'w',encoding='utf-8') as f: f.write(src)
print('OK. wrote', SRC, '→', os.path.getsize(SRC), 'bytes')
def cnt(s): return src.count(s)
print('  unit position-static fix:    ', cnt('position: static !important'))
print('  5-line disclaimer:           ', cnt('1) 호칭능력(CRT)은'))
print('  enlarged result-card padding:', cnt('padding: 18px 22px'))
print('  enlarged calc-mini-row .v:   ', cnt('font-size: 18px; color: var(--pri-800)'))
