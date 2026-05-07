#!/usr/bin/env python3
"""
4th revision — unified visual identity:
  • Primary:   blue   (#1e3c72 → #2a5298 → #4a90e2)
  • Secondary: orange (#d84315 → #ef6c00 → #ff7043 → #fff3e0)  — replaces previous red emphasis
  • Secondary: green  (#1b5e20 → #2e7d32 → #43a047 → #e8f5e9)  — for success / positive states
  • Font: Pretendard (Korean+English) loaded via CDN, with system fallbacks
  • Mono : JetBrains Mono / Consolas fallback for numbers
"""
import re, os

SRC = '냉각탑_선정프로그램_장비개요.html'
DST = SRC

with open(SRC, 'r', encoding='utf-8') as f:
    src = f.read()


# ============================================================
# 1) Inject Pretendard webfont link in <head> + override base font in <style>
# ============================================================
HEAD_OLD = '<title>성지공조기술 냉각탑 선정 프로그램</title>\n<style>'
HEAD_NEW = """<title>성지공조기술 냉각탑 선정 프로그램</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-subset.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap">
<style>
/* ============ 통합 디자인 토큰 (Design Tokens) ============ */
:root {
  /* Primary — 블루 */
  --pri-900: #142850;
  --pri-800: #1e3c72;
  --pri-700: #2a5298;
  --pri-600: #3a6ab0;
  --pri-500: #4a90e2;
  --pri-100: #e3f2fd;
  --pri-50:  #f3f7fc;

  /* Secondary — 오렌지 (강조 / 결과 / 경고) */
  --org-800: #bf360c;
  --org-700: #d84315;
  --org-600: #ef6c00;
  --org-500: #ff7043;
  --org-200: #ffccbc;
  --org-100: #fff3e0;

  /* Secondary — 그린 (성공 / 추천 / 양호) */
  --grn-800: #1b5e20;
  --grn-700: #2e7d32;
  --grn-600: #43a047;
  --grn-200: #c8e6c9;
  --grn-100: #e8f5e9;

  /* Neutral — 텍스트 / 배경 / 테두리 */
  --ink-900: #1a1a1a;
  --ink-700: #37474f;
  --ink-600: #455a64;
  --ink-500: #607d8b;
  --ink-400: #78909c;
  --ink-300: #b0bec5;
  --ink-200: #cfd8dc;
  --ink-150: #d8dde3;
  --ink-100: #e3e7ee;
  --bg-50:   #f8f9fb;
  --bg-100:  #eef2f7;
  --white:   #ffffff;

  /* Fonts */
  --font-sans: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont,
               system-ui, "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic",
               "맑은 고딕", "Segoe UI", Roboto, sans-serif;
  --font-mono: "JetBrains Mono", "Consolas", "SFMono-Regular", "Roboto Mono",
               "Cascadia Code", monospace;
}
"""
assert HEAD_OLD in src
src = src.replace(HEAD_OLD, HEAD_NEW)


# ============================================================
# 2) Replace the body font-family (line ~11) with Pretendard token
# ============================================================
src = src.replace(
    "font-family: 'Segoe UI', 'Malgun Gothic', '맑은 고딕', sans-serif;",
    "font-family: var(--font-sans);"
)

# Replace report-body font (was Times serif → use Pretendard for unified tone)
src = src.replace(
    "font-family: 'Times New Roman', 'Malgun Gothic', serif;",
    "font-family: var(--font-sans);"
)

# 보고서 헤더 corp 텍스트
src = src.replace(
    "font-family: 'Malgun Gothic', sans-serif;",
    "font-family: var(--font-sans);"
)

# 모든 Consolas monospace 토큰을 통일된 var로
src = src.replace("'Consolas', monospace", "var(--font-mono)")
src = src.replace("'Consolas', 'Cambria Math', monospace", "var(--font-mono)")
src = src.replace("font-family: monospace;", "font-family: var(--font-mono);")


# ============================================================
# 3) Color migration: red(#c62828) → orange(--org-600 #ef6c00)
#    + auxiliary red/yellow shades → orange family
# ============================================================
COLOR_MAP = {
    # Primary red → orange
    '#c62828': 'var(--org-600)',
    '#b71c1c': 'var(--org-700)',
    # Light red backgrounds → light orange
    '#fff8f8': 'var(--org-100)',
    '#ffe5e5': 'var(--org-100)',
    '#fff9c4': 'var(--org-100)',
    # Yellow accent → keep but unify under amber→orange
    '#fff8e1': 'var(--org-100)',
    '#ffd54f': 'var(--org-500)',
    # Misc warning amber
    '#f9a825': 'var(--org-600)',
    '#f57c00': 'var(--org-700)',
    '#ef6c00': 'var(--org-600)',
    '#d84315': 'var(--org-700)',
    '#ff8a65': 'var(--org-500)',
    '#ffccbc': 'var(--org-200)',
    # Browns under disclaimer
    '#5d4037': 'var(--ink-700)',
    '#4e342e': 'var(--ink-700)',
    '#e65100': 'var(--org-700)',
    # Various blue tones we used → unify
    '#1e3c72': 'var(--pri-800)',
    '#2a5298': 'var(--pri-700)',
    '#4a90e2': 'var(--pri-500)',
    '#142850': 'var(--pri-900)',
    '#1565c0': 'var(--pri-700)',
    '#90a4ae': 'var(--ink-300)',
    # Green tones
    '#2e7d32': 'var(--grn-700)',
    '#43a047': 'var(--grn-600)',
    '#388e3c': 'var(--grn-700)',
    '#66bb6a': 'var(--grn-600)',
    # Background neutrals
    '#f8f9fb': 'var(--bg-50)',
    '#eef2f7': 'var(--bg-100)',
    '#e3e7ee': 'var(--ink-100)',
    '#cfd8dc': 'var(--ink-200)',
    '#b0bec5': 'var(--ink-300)',
    '#78909c': 'var(--ink-400)',
    '#607d8b': 'var(--ink-500)',
    '#455a64': 'var(--ink-600)',
    '#37474f': 'var(--ink-700)',
    '#263248': 'var(--ink-700)',
}

# Do simple textual replacement (case-insensitive)
def replace_ci(text, m):
    pat = re.compile(re.escape(m), re.IGNORECASE)
    return pat.sub(COLOR_MAP[m], text)
for old in COLOR_MAP:
    src = replace_ci(src, old)

# rgba(...) tones for blue-ish — just a few hand-fixed
src = src.replace('rgba(42, 82, 152, 0.1)',  'rgba(42,82,152,0.10)')
src = src.replace('rgba(42, 82, 152, 0.3)',  'rgba(42,82,152,0.30)')
src = src.replace('rgba(42, 82, 152, 0.4)',  'rgba(42,82,152,0.40)')


# ============================================================
# 4) Fix body background gradient (purple) → blue
# ============================================================
src = src.replace(
    "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);",
    "background: linear-gradient(135deg, var(--pri-700) 0%, var(--pri-900) 100%);"
)


# ============================================================
# 5) Use green for "Rating Factor 로드됨" + Recommendation cards
#    (Already used green via #2e7d32 etc, now via var(--grn-700) — kept consistent)
# ============================================================


# ============================================================
# 6) Tighten print color profile so the orange/blue render the same on paper
# ============================================================
PRINT_TUNE = """
  /* ===== 인쇄 색상 보존 ===== */
  @media print {
    * {
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }
  }
</style>"""

# Replace ONLY the very last </style> in <head> (the main one). The first style block
# we added contains the design tokens and ends with } before the next CSS rule, not </style>.
# So safe to replace the LAST </style>:
last_close = src.rfind('</style>')
src = src[:last_close] + PRINT_TUNE.rstrip() + src[last_close + len('</style>'):]


# ============================================================
# 7) Quick validation log
# ============================================================
with open(DST, 'w', encoding='utf-8') as f:
    f.write(src)

print('OK. wrote', DST, '→', os.path.getsize(DST), 'bytes')

remain_red = ['#c62828', '#b71c1c', '#fff8f8', '#fff8e1', '#ffe5e5', '#ffd54f',
              '#f9a825', '#f57c00', '#ef6c00', '#d84315']
print('Color migration check:')
for c in remain_red:
    n = src.count(c)
    if n: print(f'  {c}: {n} occurrence(s) remain')
print('Pretendard link:', src.count('orioncactus/pretendard'))
print('var(--font-sans):', src.count('var(--font-sans)'))
print('var(--font-mono):', src.count('var(--font-mono)'))
print('var(--org-...):',  src.count('var(--org-'))
print('var(--grn-...):',  src.count('var(--grn-'))
print('var(--pri-...):',  src.count('var(--pri-'))
