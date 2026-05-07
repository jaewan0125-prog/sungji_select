#!/usr/bin/env python3
"""
Master rebuild — runs the full chain build.py → build7.py + the latest clipping fix
in a single pass against the SAME output file. All intermediate scripts assumed
the files at known names; we adapt them by symlinking / staging cooling_new.html
between steps.
"""
import os, shutil, subprocess, sys

OUT_DIR = '/sessions/confident-modest-bohr/mnt/outputs'
TARGET  = '냉각탑_선정프로그램_장비개요.html'

os.chdir(OUT_DIR)

# Step 0: start from the ORIGINAL uploaded HTML (preserved at work/cooling.html)
shutil.copy('work/cooling.html', 'cooling_new.html')

# Step 1: build.py turns cooling_new.html into the overview-modal + 5-button version (still cooling_new.html name)
print('=== build.py ===')
r = subprocess.run([sys.executable, 'work/build.py'], capture_output=True, text=True)
print(r.stdout[-500:]); print(r.stderr[-300:])

# Now rename the result so subsequent scripts find their expected filename
if os.path.exists(TARGET):
    # We can't delete, so overwrite via Python
    pass
# Use python to atomically overwrite
with open('cooling_new.html','rb') as src, open(TARGET,'wb') as dst:
    dst.write(src.read())

# Steps 2-7: build2.py through build7.py all read/write 냉각탑_선정프로그램_장비개요.html
for n in [2,3,4,5,6,7]:
    print(f'=== build{n}.py ===')
    r = subprocess.run([sys.executable, f'work2/build{n}.py'], capture_output=True, text=True)
    print(r.stdout[-300:]); print(r.stderr[-200:])

# Step 8: clipping fix — apply directly here
with open(TARGET,'r',encoding='utf-8') as f: src = f.read()

OLD = """    html, body {
      width: 210mm; height: auto !important; min-height: 0 !important;
      background: white !important;
      margin: 0 !important; padding: 0 !important;
      overflow: visible !important;
    }"""
NEW = """    html, body {
      /* @page의 margin이 자동으로 인쇄 영역을 잘라주므로 너비를 명시하지 않음 */
      width: auto !important; max-width: 100% !important;
      height: auto !important; min-height: 0 !important;
      background: white !important;
      margin: 0 !important; padding: 0 !important;
      overflow: visible !important;
      box-sizing: border-box;
    }
    body * { box-sizing: border-box !important; max-width: 100%; }
    .report-table, .calc-unified, .calc-table, .ov-fullspec, .ov-flowtable {
      table-layout: fixed !important; word-wrap: break-word !important;
    }
    .calc-unified thead th { white-space: nowrap !important; }
    .report-selected { grid-template-columns: minmax(0, 1fr) auto !important; }
    .report-selected .model-spec-row { flex-wrap: wrap !important; }"""
if OLD in src:
    src = src.replace(OLD, NEW)
    print('=== clipping fix applied ===')
else:
    print('!!! OLD anchor for clipping fix not found')

with open(TARGET,'w',encoding='utf-8') as f: f.write(src)

# Final sanity
print(f'\nFINAL: {TARGET} → {os.path.getsize(TARGET)} bytes')
for needle in ['openOverview', 'openMakeupReport', 'openLouverReport',
               'printOverlay', 'MODEL_DIAGRAMS',
               "ovChooseDoc('makeup')", "ovChooseDoc('louver')",
               'class="ov-print-btn"', 'tabular-nums', 'Pretendard',
               'minmax(0, 1fr) auto', 'width: auto !important']:
    print(f'  {needle:38s}: {src.count(needle)}')
