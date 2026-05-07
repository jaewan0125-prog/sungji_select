#!/usr/bin/env python3
"""
Critical fix — :root tokens got self-referenced during color migration.
Restore concrete hex values for every CSS custom property in :root.
"""
import re, os

SRC = '냉각탑_선정프로그램_장비개요.html'
with open(SRC, 'r', encoding='utf-8') as f:
    src = f.read()

# Definitions block — find :root { ... } and rewrite tokens
ROOT_RE = re.compile(r':root\s*\{[\s\S]*?\}', re.MULTILINE)
m = ROOT_RE.search(src)
assert m, ':root block not found'

NEW_ROOT = """:root {
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
}"""

src = src[:m.start()] + NEW_ROOT + src[m.end():]

# Sanity: confirm no recursive var(--xxx-yyy): var(--xxx-yyy)
bad = re.findall(r'(--[a-z]+-\d+):\s*var\(\1\)', src)
print('recursive token issues remaining:', len(bad))

with open(SRC, 'w', encoding='utf-8') as f:
    f.write(src)
print('size:', os.path.getsize(SRC))
