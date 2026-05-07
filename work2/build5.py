#!/usr/bin/env python3
"""5th pass — clean leftover purples / ambers and unify recommendation cards."""
import re, os

SRC = '냉각탑_선정프로그램_장비개요.html'
with open(SRC,'r',encoding='utf-8') as f: src=f.read()

EXTRA = {
    # Purple — ALL recommendation card → unified primary→orange gradient
    '#4a148c': 'var(--pri-900)',
    '#7b1fa2': 'var(--pri-600)',
    # Amber shades → orange family
    '#ffb300': 'var(--org-600)',
    '#ffa726': 'var(--org-500)',
    '#ff9800': 'var(--org-500)',
    '#ff7043': 'var(--org-500)',
    '#fffde7': 'var(--org-100)',
    '#ffecb3': 'var(--org-100)',
    '#ffe0b2': 'var(--org-200)',
    '#bf360c': 'var(--org-800)',
    # Indigo recommendation (height) — keep but normalize
    '#3949ab': 'var(--pri-600)',
    '#e8eaf6': 'var(--pri-50)',
    '#c5cae9': 'var(--pri-100)',
    '#1a237e': 'var(--pri-900)',
    # Teal recommendation (area) → green family
    '#00796b': 'var(--grn-700)',
    '#e0f2f1': 'var(--grn-100)',
    '#b2dfdb': 'var(--grn-200)',
    '#004d40': 'var(--grn-800)',
    # Spare highlights
    '#e8f0fe': 'var(--pri-50)',
    '#e3f2fd': 'var(--pri-100)',
    '#f1f8ff': 'var(--pri-50)',
    '#e8f5e9': 'var(--grn-100)',
    '#c8e6c9': 'var(--grn-200)',
    '#1b5e20': 'var(--grn-800)',
    # leftover neutrals
    '#eceff1': 'var(--ink-100)',
    '#e8eaed': 'var(--ink-100)',
    '#9e9e9e': 'var(--ink-300)',
    '#757575': 'var(--ink-500)',
    '#546e7a': 'var(--ink-600)',
    # purple gradient hex variants
    '#667eea': 'var(--pri-700)',
    '#764ba2': 'var(--pri-900)',
}
for k,v in EXTRA.items():
    src = re.sub(re.escape(k), v, src, flags=re.IGNORECASE)

# orange-ish dynamic accent in #ff8a65 already mapped earlier
# Final color survey
left = re.findall(r'#[0-9a-fA-F]{6}\b', src)
from collections import Counter
print(Counter(left).most_common(20))

with open(SRC,'w',encoding='utf-8') as f: f.write(src)
print('size:', os.path.getsize(SRC))
