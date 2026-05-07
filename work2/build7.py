#!/usr/bin/env python3
"""
7th pass:
  • All numbers / English use Pretendard (sans-serif Gothic) instead of monospace.
    Achieved by aliasing --font-mono → var(--font-sans) and adding
    font-variant-numeric: tabular-nums; font-feature-settings: "tnum" 1, "ss01" 1;
    so digits stay column-aligned in tables without sacrificing the Gothic look.
  • Print clean-up: only the currently visible popup prints, the rest of the page is hidden.
    Implemented with a .printing flag on the active overlay and updated @media print rules.
    Overview modal also gets a 🖨 button so it's printable too.
"""
import re, os

SRC = '냉각탑_선정프로그램_장비개요.html'
with open(SRC,'r',encoding='utf-8') as f: src=f.read()

# ============================================================
# 1) Font: --font-mono → Pretendard (sans). Body uses tabular-nums.
# ============================================================
src = src.replace(
    '  --font-mono: "JetBrains Mono", "Consolas", "SFMono-Regular", "Roboto Mono",\n'
    '               "Cascadia Code", monospace;',
    '  /* 숫자 정렬용도 — 본문 sans와 동일한 Pretendard 사용. tabular-nums로 칼럼 정렬 유지 */\n'
    '  --font-mono: var(--font-sans);'
)

# Drop the JetBrains Mono CDN link (no longer used)
src = src.replace(
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap">\n',
    ''
)

# Add tabular-nums to body (cascades to all children)
src = src.replace(
    '''  body {
    font-family: var(--font-sans);''',
    '''  body {
    font-family: var(--font-sans);
    font-variant-numeric: tabular-nums;
    font-feature-settings: "tnum" 1, "ss01" 1, "kern" 1;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;'''
)

# ============================================================
# 2) Print: only the popup tagged .printing renders.
#    Rewrite the existing @media print blocks consolidated.
# ============================================================
# Find the FIRST @media print block (the original print rules for report-overlay)
# and merge with new clean rules.

# Locate the FIRST @media print block by counting braces
first_idx = src.find('@media print {')
assert first_idx >= 0
# brace counter
i = first_idx + len('@media print ')
depth = 0
while i < len(src):
    c = src[i]
    if c == '{':
        depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0:
            i += 1
            break
    i += 1
first_block_end = i  # exclusive
old_first_block = src[first_idx:first_block_end]

# Replace with our consolidated clean-print rules
NEW_FIRST_PRINT = """@media print {
    @page { size: A4 portrait; margin: 12mm 14mm; }

    /* 인쇄 색상 보존 (블루 헤더 / 오렌지 강조) */
    * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }

    html, body {
      width: 210mm; height: auto !important; min-height: 0 !important;
      background: white !important;
      margin: 0 !important; padding: 0 !important;
      overflow: visible !important;
    }

    /* 본문 컨테이너 + 활성 표식 없는 모든 모달은 인쇄에서 제외 */
    body > .container,
    .ov-overlay:not(.printing),
    .ph-overlay:not(.printing),
    .report-overlay:not(.printing) { display: none !important; }

    /* === 활성 모달 (.printing) 공통 평탄화 === */
    .ov-overlay.printing,
    .report-overlay.printing,
    .ph-overlay.printing {
      position: static !important;
      inset: auto !important;
      background: white !important;
      padding: 0 !important;
      margin: 0 !important;
      display: block !important;
      overflow: visible !important;
      height: auto !important;
      min-height: 0 !important;
      backdrop-filter: none !important;
      z-index: auto !important;
    }
    .ov-overlay.printing .ov-modal,
    .report-overlay.printing .report-modal,
    .ph-overlay.printing .ph-modal {
      box-shadow: none !important;
      max-width: 100% !important;
      width: 100% !important;
      margin: 0 !important;
      border-radius: 0 !important;
      animation: none !important;
    }

    /* === 보고서(선정서/보급수/루버) 인쇄 디테일 === */
    .report-overlay.printing .report-toolbar { display: none !important; }
    .report-overlay.printing .report-modal { page-break-after: avoid !important; page-break-inside: avoid; }
    .report-overlay.printing .report-body { padding: 0 !important; font-size: 11pt; }

    /* === 개요 모달 인쇄 디테일 === */
    .ov-overlay.printing .ov-header .x-btn,
    .ov-overlay.printing .ov-header .ov-print-btn,
    .ov-overlay.printing .ov-tabs,
    .ov-overlay.printing .ov-footer { display: none !important; }
    .ov-overlay.printing .ov-pane { display: block !important; page-break-inside: avoid; margin-top: 8px; }
    .ov-overlay.printing .ov-pane:not(.active) { display: none !important; }
    .ov-overlay.printing .ov-body { display: block !important; }
    .ov-overlay.printing .ov-side {
      background: white !important; color: var(--ink-900) !important;
      border-bottom: 1.5px solid var(--pri-800);
      padding: 8px 10px 12px !important;
      display: grid !important;
      grid-template-columns: 200px 1fr;
      gap: 14px;
      align-items: start;
    }
    .ov-overlay.printing .ov-side .ov-thumb {
      box-shadow: none !important; padding: 0 !important;
      grid-row: span 4;
    }
    .ov-overlay.printing .ov-side .ov-model-code { color: var(--pri-800) !important; font-size: 18px !important; }
    .ov-overlay.printing .ov-side .ov-model-desc { color: var(--ink-700) !important; border-bottom: 1px solid var(--ink-200) !important; }
    .ov-overlay.printing .ov-side .ov-keyrow {
      border-bottom: 1px dotted var(--ink-200) !important;
      grid-template-columns: 130px 1fr;
    }
    .ov-overlay.printing .ov-side .ov-keyrow .k { color: var(--ink-600) !important; }
    .ov-overlay.printing .ov-side .ov-keyrow .v { color: var(--ink-900) !important; }
    .ov-overlay.printing .ov-side .ov-keyrow .v.accent { color: var(--org-700) !important; }
    .ov-overlay.printing .ov-side .ov-keyrow .v.warn   { color: var(--org-800) !important; }
    .ov-overlay.printing .ov-side .ov-tag {
      background: var(--bg-50) !important; color: var(--pri-800) !important;
      border: 1px solid var(--ink-200);
    }
    .ov-overlay.printing .ov-main { padding: 8px 10px 14px !important; }

    /* 보고서 디테일 토글 — 기존 컴팩트 폼 유지 */
    .report-section-title { page-break-after: avoid; }
    .report-table { page-break-inside: avoid; }
  }"""

src = src[:first_idx] + NEW_FIRST_PRINT + src[first_block_end:]


# ============================================================
# 3) Replace the inline `onclick="window.print();"` with a helper that
#    marks the report overlay as .printing first.
# ============================================================
src = src.replace(
    '<button onclick="window.print();">🖨 인쇄</button>',
    "<button onclick=\"printOverlay('reportOverlay')\">🖨 인쇄</button>"
)


# ============================================================
# 4) Add a 🖨 print button in the overview header (next to the X)
# ============================================================
OV_HEAD_OLD = '<button class="x-btn" onclick="closeOverview()" title="닫기">×</button>'
OV_HEAD_NEW = ('<button class="ov-print-btn" onclick="printOverlay(\'overviewOverlay\')" title="현재 탭 인쇄">🖨</button>'
               '<button class="x-btn" onclick="closeOverview()" title="닫기">×</button>')
assert OV_HEAD_OLD in src
src = src.replace(OV_HEAD_OLD, OV_HEAD_NEW)

# Add CSS for ov-print-btn (same look as x-btn but with margin-right)
src = src.replace(
    '  .ov-header .x-btn:hover { background: rgba(255,255,255,0.32); }',
    '''  .ov-header .x-btn:hover { background: rgba(255,255,255,0.32); }
  .ov-header .ov-print-btn {
    background: rgba(255,255,255,0.15); border: none; color: white;
    width: 32px; height: 32px; border-radius: 50%;
    cursor: pointer; font-size: 15px; line-height: 1; font-family: inherit;
    margin-right: 8px;
    transition: background 0.15s;
  }
  .ov-header .ov-print-btn:hover { background: rgba(255,255,255,0.32); }
  .ov-header { gap: 8px; }
  .ov-header > .ov-title { flex: 1; min-width: 0; }
  .ov-header > div:last-child { display: flex; align-items: center; }'''
)

# Wrap print + close buttons in a single flex container so they sit together right-side
src = src.replace(
    '<button class="ov-print-btn" onclick="printOverlay(\'overviewOverlay\')" title="현재 탭 인쇄">🖨</button><button class="x-btn" onclick="closeOverview()" title="닫기">×</button>',
    '<div><button class="ov-print-btn" onclick="printOverlay(\'overviewOverlay\')" title="현재 탭 인쇄">🖨</button><button class="x-btn" onclick="closeOverview()" title="닫기">×</button></div>'
)


# ============================================================
# 5) Inject the printOverlay() helper into JS (idempotent).
# ============================================================
PRINT_HELPER = """
// ============ 인쇄 도우미 ============
// 활성 모달에 .printing 클래스를 주고 window.print() 호출.
// @media print 규칙이 .printing이 붙은 overlay만 표시하도록 작성됨.
function printOverlay(overlayId) {
  const el = document.getElementById(overlayId);
  if (!el) return;
  el.classList.add('printing');
  // 인쇄 후 클래스 정리
  const cleanup = () => {
    el.classList.remove('printing');
    window.removeEventListener('afterprint', cleanup);
  };
  window.addEventListener('afterprint', cleanup);
  // 일부 브라우저는 afterprint를 안 쏠 수 있으니 fallback 타이머
  setTimeout(cleanup, 4000);
  window.print();
}

"""
# Insert just before the keydown listener — same anchor used in earlier builds
ANCHOR = "document.addEventListener('keydown', (e) => {"
assert ANCHOR in src
# Avoid double-injecting
if 'function printOverlay(' not in src:
    src = src.replace(ANCHOR, PRINT_HELPER + ANCHOR)


# ============================================================
# 6) Save
# ============================================================
with open(SRC,'w',encoding='utf-8') as f: f.write(src)

print('OK. wrote', SRC, '→', os.path.getsize(SRC), 'bytes')

def cnt(s): return src.count(s)
print('  --font-mono aliased →:           ', cnt('--font-mono: var(--font-sans)'))
print('  tabular-nums on body:           ', cnt('font-variant-numeric: tabular-nums'))
print('  printOverlay() defined:         ', cnt('function printOverlay('))
print('  Print buttons (overview+report):', cnt("printOverlay('overviewOverlay')") + cnt("printOverlay('reportOverlay')"))
print('  @media print blocks:            ', cnt('@media print'))
print('  .printing references:           ', cnt('.printing'))
