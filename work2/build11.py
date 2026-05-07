#!/usr/bin/env python3
"""
11th pass — fit selection report onto 1 page WITH the 5-line disclaimer.
Strategy: remove the standalone dimensions sub-box (duplicates spec table info)
and tighten print typography slightly.
"""
import os, re

SRC = '냉각탑_선정프로그램_장비개요.html'
with open(SRC,'r',encoding='utf-8') as f: src=f.read()

# ============================================================
# 1) 외형치수 box 단순화 — 컴팩트한 1-2줄 박스로
# ============================================================
OLD_DIM = """    <div style="border:1px solid var(--ink-300);border-radius:4px;padding:12px 16px;background:var(--bg-50);margin-top:12px;">
      <div style="font-size:12px;color:var(--pri-800);font-weight:700;margin-bottom:10px;letter-spacing:0.5px;border-bottom:1px solid var(--ink-200);padding-bottom:6px;">▌외형 치수 / Overall Dimensions (L × W × H, mm)</div>

      <div style="background:var(--org-100);border:2px solid var(--org-600);border-radius:4px;padding:10px 14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span style="font-size:11px;color:var(--org-600);font-weight:800;letter-spacing:0.3px;">▶ ${variantLabel}</span>
          <span style="font-size:11px;color:var(--ink-600);font-family:var(--font-sans);font-weight:700;">${variantCode}</span>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:11.5px;">
          <div>
            <div style="color:var(--ink-400);font-size:10px;margin-bottom:2px;">셀당 (Per Cell)</div>
            <div style="font-family:var(--font-sans);font-weight:700;color:#1a1a1a;font-size:12.5px;">${perCellDim} mm</div>
          </div>
          <div>
            <div style="color:var(--ink-400);font-size:10px;margin-bottom:2px;">전체 (Total ${cells}Cell)</div>
            <div style="font-family:var(--font-sans);font-weight:800;color:var(--org-600);font-size:13px;">${totalDim} mm</div>
          </div>
        </div>
      </div>

    </div>
  `;"""
NEW_DIM = """    <div class="report-dim-row">
      <div class="dim-head">
        <span class="t">▌외형 치수 (Dimensions L × W × H, mm)</span>
        <span class="vlabel">▶ ${variantLabel} · <b>${variantCode}</b></span>
      </div>
      <div class="dim-body">
        <span class="cell"><span class="k">셀당</span> ${perCellDim} mm</span>
        <span class="sep">/</span>
        <span class="cell total"><span class="k">전체 ${cells}Cell</span> ${totalDim} mm</span>
      </div>
    </div>
  `;"""
assert OLD_DIM in src
src = src.replace(OLD_DIM, NEW_DIM)


# ============================================================
# 2) Add CSS for the compact dimensions row
# ============================================================
CSS_ADD = """
  /* 선정서 외형치수 한 줄 컴팩트 박스 */
  .report-dim-row {
    border: 2px solid var(--org-600);
    background: var(--org-100);
    border-radius: 5px;
    padding: 8px 14px;
    margin-top: 10px;
    font-size: 12.5px;
  }
  .report-dim-row .dim-head {
    display: flex; justify-content: space-between; align-items: baseline;
    padding-bottom: 5px; margin-bottom: 5px;
    border-bottom: 1px solid var(--org-200);
  }
  .report-dim-row .dim-head .t {
    font-size: 11.5px; font-weight: 800; color: var(--pri-800); letter-spacing: 0.3px;
  }
  .report-dim-row .dim-head .vlabel {
    font-size: 10.5px; color: var(--ink-600); letter-spacing: 0.2px;
  }
  .report-dim-row .dim-head .vlabel b {
    color: var(--org-700); font-weight: 700;
  }
  .report-dim-row .dim-body {
    display: flex; align-items: baseline;
    gap: 14px; flex-wrap: wrap;
    font-size: 12px;
  }
  .report-dim-row .dim-body .cell {
    color: var(--ink-900); font-weight: 700;
  }
  .report-dim-row .dim-body .cell .k {
    font-size: 10px; color: var(--ink-500); font-weight: 600; margin-right: 5px;
  }
  .report-dim-row .dim-body .cell.total {
    color: var(--org-700); font-weight: 800; font-size: 13px;
  }
  .report-dim-row .dim-body .sep { color: var(--ink-300); font-weight: 400; }

"""
# Insert at the top of the @media print block area (right before extra print)
ANCHOR = '  /* === 선정서 1페이지 fit'
assert ANCHOR in src
src = src.replace(ANCHOR, CSS_ADD + ANCHOR)


# ============================================================
# 3) 인쇄 모드 — 선정서 약간 더 컴팩트화 + 외형치수 박스도 컴팩트
# ============================================================
OLD_EXTRA = """  /* === 선정서 1페이지 fit (5줄 disclaimer 포함) === */
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

NEW_EXTRA = """  /* === 선정서 1페이지 fit (5줄 disclaimer 포함) === */
  @media print {
    .report-disclaimer { padding: 6px 11px !important; font-size: 8.5pt !important; line-height: 1.5 !important; margin-top: 7px !important; }
    .report-footer { padding-top: 5px !important; margin-top: 7px !important; }
    .report-footer .copyright { font-size: 7.5pt !important; line-height: 1.35; }
    .report-footer .signature .corp-name { font-size: 9pt !important; }
    .report-grid { font-size: 9pt !important; gap: 1px 18px !important; }
    .report-grid .row { padding: 2px 0 !important; }
    .report-table { font-size: 9pt !important; }
    .report-table th, .report-table td { padding: 3px 7px !important; }
    /* 컴팩트 외형치수 박스 */
    .report-dim-row { padding: 6px 11px !important; margin-top: 7px !important; font-size: 9pt !important; }
    .report-dim-row .dim-head { padding-bottom: 3px !important; margin-bottom: 3px !important; }
    .report-dim-row .dim-head .t { font-size: 8.5pt !important; }
    .report-dim-row .dim-head .vlabel { font-size: 8pt !important; }
    .report-dim-row .dim-body { font-size: 9pt !important; gap: 10px !important; }
    .report-dim-row .dim-body .cell.total { font-size: 9.5pt !important; }
    .report-dim-row .dim-body .cell .k { font-size: 7.5pt !important; }
    /* 섹션 타이틀 */
    .report-section-title { font-size: 9.5pt !important; padding: 3px 9px !important; margin: 7px 0 4px !important; }
    /* 선택 모델 박스 */
    .report-selected { padding: 5px 10px !important; }
    .report-selected .model-info .model-code { font-size: 13pt !important; }
    .report-selected .model-info .model-desc { font-size: 8pt !important; }
    .report-selected .model-spec-row .spec-cell .num { font-size: 11pt !important; }
    .report-selected .model-spec-row .spec-cell .label { font-size: 7.5pt !important; }
    /* meta 영역 */
    .report-meta { font-size: 9pt !important; margin-bottom: 6px !important; gap: 1px 16px !important; }
    /* header */
    .report-header { padding-bottom: 5px !important; margin-bottom: 6px !important; }
    .report-header .title-block .main-title { font-size: 16pt !important; }
    .report-header .title-block .eyebrow { font-size: 7.5pt !important; }
    .report-header .title-block .sub-title { font-size: 8.5pt !important; }
    .report-header .logo-block img { height: 30px !important; }
    .report-header .logo-block .corp { font-size: 7.5pt !important; }
  }"""
assert OLD_EXTRA in src
src = src.replace(OLD_EXTRA, NEW_EXTRA)


# ============================================================
# Save
# ============================================================
with open(SRC,'w',encoding='utf-8') as f: f.write(src)
print('OK. wrote', SRC, '→', os.path.getsize(SRC), 'bytes')
def cnt(s): return src.count(s)
print('  report-dim-row used:', cnt('class="report-dim-row"'))
print('  print-tune updated:', cnt('.report-dim-row { padding: 6px'))
