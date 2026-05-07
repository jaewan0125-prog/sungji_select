#!/usr/bin/env python3
"""Apply the calc-mini-row + calc-unified base style enlargement that build10 missed
(due to font-family token mismatch in OLD pattern)."""
import os, re

SRC = '냉각탑_선정프로그램_장비개요.html'
with open(SRC,'r',encoding='utf-8') as f: src=f.read()

# calc-mini-row screen sizes
OLD = """  .calc-mini-row {
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
    font-family: var(--font-sans);
    font-size: 11px; color: var(--ink-600); font-weight: 500;
    margin-left: 2px;
  }"""
NEW = """  .calc-mini-row {
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
assert OLD in src
src = src.replace(OLD, NEW)

# calc-unified td padding (size already applied)
OLD2 = """  .calc-unified th, .calc-unified td {
    border: 1px solid var(--ink-300); padding: 6px 10px; text-align: center;
  }"""
NEW2 = """  .calc-unified th, .calc-unified td {
    border: 1px solid var(--ink-300); padding: 9px 12px; text-align: center;
  }"""
if OLD2 in src:
    src = src.replace(OLD2, NEW2)

with open(SRC,'w',encoding='utf-8') as f: f.write(src)
print('done. size:', os.path.getsize(SRC))
def cnt(s): return src.count(s)
print('  big mini-row v 18px:', cnt('font-size: 18px; color: var(--pri-800)'))
print('  bigger mini cell padding:', cnt('padding: 11px 14px 12px'))
print('  bigger calc-unified td padding:', cnt('padding: 9px 12px; text-align: center'))
