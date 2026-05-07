#!/usr/bin/env python3
"""
8th pass:
  • Replace MODEL_DIAGRAMS data URIs with the new equipment renderings
    (work3/SJMO.jpg / SJMO-A.jpg / SJCO.jpg / SJXO.jpg).
  • Re-architect the overview modal to remove duplicated content:
      - Sidebar key-list 10 rows  → 5 essentials (호칭/Cell, 셀구성, 총호칭, 실여유율, 외형치수)
      - 개요 tab spec-mini       → REMOVED (overlaps sidebar)
      - 개요 tab summary table   → simplified into a single-glance hero card
      - 사양 tab                 → unchanged (full equipment specs live here)
      - 설계 조건 tab            → unchanged (input conditions only)
"""
import re, os, json, base64

SRC = '냉각탑_선정프로그램_장비개요.html'
with open(SRC, 'r', encoding='utf-8') as f: src = f.read()

# ============================================================
# 1) Swap MODEL_DIAGRAMS data URIs
# ============================================================
def b64uri(p):
    with open(p, 'rb') as f:
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()

NEW_DIAGS = {
    'SJMO':   b64uri('work3/SJMO.jpg'),
    'SJMO-A': b64uri('work3/SJMO-A.jpg'),
    'SJCO':   b64uri('work3/SJCO.jpg'),
    'SJXO':   b64uri('work3/SJXO.jpg'),
}

# Replace the entire MODEL_DIAGRAMS object (regex match across the whole block)
DIAG_BLOCK_RE = re.compile(
    r"const MODEL_DIAGRAMS\s*=\s*\{[^}]*?\};",
    re.DOTALL
)
m = DIAG_BLOCK_RE.search(src)
assert m, 'MODEL_DIAGRAMS block not found'

new_block = "const MODEL_DIAGRAMS = {\n"
for k, uri in NEW_DIAGS.items():
    new_block += f"  '{k}':{' '*(8-len(k))}'{uri}',\n"
new_block = new_block.rstrip(',\n') + '\n};'
src = src[:m.start()] + new_block + src[m.end():]


# ============================================================
# 2) Simplify sidebar keyHtml — 10 → 5 rows
# ============================================================
OLD_KEY = """  const keyHtml = [
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
  ].map(r => `<div class="ov-keyrow"><div class="k">${r.k}</div><div class="v ${r.cls}">${r.v}</div></div>`).join('');"""

NEW_KEY = """  // 사이드바: 식별 + 핵심 5개 (전체 사양은 「사양 상세」탭에)
  const keyHtml = [
    {k:'호칭 / Capacity',     v:`${modelCRT} CRT × ${cells}Cell`,                              cls:'accent'},
    {k:'총 호칭능력 / Total', v:`${totalCap} CRT`,                                             cls:'accent'},
    {k:'실여유율 / Reserve',  v:`${reservePct} %`,                                             cls:(parseFloat(reservePct) < 0 ? 'warn' : '')},
    {k:'팬 모터 / Fan',       v: sp ? `${sp.kw} kW × ${cells}EA` : '—',                        cls:''},
    {k:'외형 (L×W×H)',        v: sp ? `${totalLen.toLocaleString()}×${sp.W.toLocaleString()}×${sp.H.toLocaleString()}` : '—', cls:''}
  ].map(r => `<div class="ov-keyrow"><div class="k">${r.k}</div><div class="v ${r.cls}">${r.v}</div></div>`).join('');"""

assert OLD_KEY in src
src = src.replace(OLD_KEY, NEW_KEY)


# ============================================================
# 3) Replace 개요 탭 spec-mini + 선정결과요약 표 with a single-glance hero card.
#    These two were near-duplicates of sidebar + spec tab.
# ============================================================
OLD_OVR_BLOCK = """  document.getElementById('ovSpecMini').innerHTML = `
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
  `;"""

NEW_OVR_BLOCK = """  // 개요 탭 — 운전 조건 한눈에 (사이드바와 중복되지 않는 항목 위주)
  document.getElementById('ovSpecMini').innerHTML = `
    <div class="ov-stats">
      <div class="stat"><div class="k">설계 유량</div><div class="v">${I.flowM3h.toFixed(1)}<span class="u">㎥/h</span></div></div>
      <div class="stat"><div class="k">Range</div><div class="v">${I.range.toFixed(1)}<span class="u">℃</span></div></div>
      <div class="stat"><div class="k">Approach</div><div class="v">${I.approach.toFixed(1)}<span class="u">℃</span></div></div>
      <div class="stat"><div class="k">송풍 풍량</div><div class="v">${sp ? (sp.cmm*cells).toLocaleString() : '—'}<span class="u">CMM</span></div></div>
      <div class="stat"><div class="k">최소 요구용량</div><div class="v">${I.minCapacity.toFixed(1)}<span class="u">CRT</span></div></div>
      <div class="stat"><div class="k">운전 중량</div><div class="v">${sp ? (sp.opW*cells).toLocaleString() : '—'}<span class="u">kg</span></div></div>
    </div>
    <div class="ov-principle">
      <div class="ph"><span class="dot"></span><b>운전 원리</b></div>
      <div class="pb">${_principleText(modelType)}</div>
    </div>
  `;

  // 선정 결과 한 줄 — Range/Approach/유량은 이미 위에 있으므로 핵심 결과만 강조
  document.getElementById('ovSummary').innerHTML = `
    <div class="ov-result-strip">
      <div class="rs"><div class="k">최소 요구</div><div class="v">${I.minCapacity.toFixed(1)} CRT</div></div>
      <div class="arr">→</div>
      <div class="rs hl"><div class="k">선정 모델</div><div class="v">${variantCode} × ${cells}Cell</div></div>
      <div class="arr">=</div>
      <div class="rs"><div class="k">총 호칭</div><div class="v">${totalCap} CRT <span class="pct">(여유 ${reservePct}%)</span></div></div>
    </div>
  `;"""

assert OLD_OVR_BLOCK in src
src = src.replace(OLD_OVR_BLOCK, NEW_OVR_BLOCK)


# ============================================================
# 4) Add _principleText() helper (운전 원리 짧은 설명) and CSS for new blocks
# ============================================================
HELPER_FN = """// 모델별 짧은 운전 원리 설명 (개요 탭)
function _principleText(t) {
  const T = {
    'SJMO':   '압입송풍식 직교류 — 측면의 시로코 팬이 공기를 강제 송풍하여 직각 방향으로 흐르는 충진재 표면의 순환수를 냉각합니다. 설치 높이가 낮아 실내·지하 등 제약공간에 유리합니다.',
    'SJMO-A': '모듈형 흡입송풍식 직교류 — 측면 액시얼 팬이 충진재를 통과한 공기를 외부로 흡입 토출합니다. 모듈화된 구조로 협소공간에서도 단순 조립·반입이 가능합니다.',
    'SJCO':   '대향류형 흡입송풍식 — 상부 액시얼 팬이 외기를 아래에서 위로 끌어올리며 충진재 위에서 분사된 순환수와 정반대 방향으로 만나 효율적으로 열교환합니다.',
    'SJXO':   '직교류 흡입송풍식 — 상부 흡입 팬이 측면 루버를 통해 공기를 빨아들이고, 충진재를 흘러내리는 순환수와 직각으로 만나 냉각합니다. 대용량·저소음 운용에 적합합니다.'
  };
  return T[t] || '냉각수가 충진재 표면을 흐르며 송풍기로 유입된 외기와 접촉, 일부 증발에 의한 잠열 방출로 냉각됩니다.';
}

"""

# Insert HELPER_FN just BEFORE openOverview
ANCHOR = "function openOverview(modelType, modelCRT, cells)"
assert ANCHOR in src
src = src.replace(ANCHOR, HELPER_FN + ANCHOR)


# ============================================================
# 5) CSS for the new ov-stats grid + ov-principle + ov-result-strip
#    Insert before the print color-preserve rule (existing :end of <style>)
# ============================================================
NEW_CSS = """
  /* 개요 탭 — 통계 카드 그리드 */
  .ov-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-bottom: 14px;
  }
  .ov-stats .stat {
    background: linear-gradient(135deg, var(--bg-50) 0%, var(--bg-100) 100%);
    border: 1px solid var(--ink-100);
    border-radius: 8px;
    padding: 9px 12px;
  }
  .ov-stats .stat .k {
    font-size: 10.5px;
    font-weight: 600;
    color: var(--ink-500);
    letter-spacing: 0.3px;
    margin-bottom: 2px;
  }
  .ov-stats .stat .v {
    font-size: 17px;
    font-weight: 800;
    color: var(--pri-800);
    letter-spacing: -0.5px;
    line-height: 1.1;
  }
  .ov-stats .stat .v .u {
    font-size: 11px;
    color: var(--ink-500);
    font-weight: 500;
    margin-left: 3px;
  }

  /* 개요 탭 — 운전 원리 카드 */
  .ov-principle {
    background: var(--pri-50);
    border-left: 4px solid var(--pri-600);
    border-radius: 0 8px 8px 0;
    padding: 11px 14px 12px;
    margin-bottom: 12px;
  }
  .ov-principle .ph {
    display: flex; align-items: center; gap: 7px;
    font-size: 12px; color: var(--pri-800);
    margin-bottom: 4px;
  }
  .ov-principle .ph .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--org-600);
    display: inline-block;
  }
  .ov-principle .ph b { font-weight: 800; letter-spacing: 0.2px; }
  .ov-principle .pb {
    font-size: 12.5px;
    color: var(--ink-700);
    line-height: 1.6;
  }

  /* 개요 탭 — 선정 결과 한 줄 strip */
  .ov-result-strip {
    display: grid;
    grid-template-columns: 1fr auto 1.6fr auto 1fr;
    gap: 10px;
    align-items: stretch;
    background: linear-gradient(135deg, var(--bg-50) 0%, var(--bg-100) 100%);
    border: 1px solid var(--ink-100);
    border-radius: 10px;
    padding: 11px 14px;
  }
  .ov-result-strip .rs {
    text-align: center;
    padding: 4px 6px;
  }
  .ov-result-strip .rs .k {
    font-size: 10.5px;
    color: var(--ink-500);
    font-weight: 600;
    letter-spacing: 0.4px;
    margin-bottom: 2px;
  }
  .ov-result-strip .rs .v {
    font-size: 14px;
    font-weight: 800;
    color: var(--ink-900);
    letter-spacing: -0.3px;
  }
  .ov-result-strip .rs.hl {
    background: linear-gradient(135deg, var(--pri-800) 0%, var(--pri-700) 100%);
    border-radius: 8px;
    padding: 7px 10px;
  }
  .ov-result-strip .rs.hl .k { color: rgba(255,255,255,0.78); }
  .ov-result-strip .rs.hl .v { color: white; font-size: 16px; }
  .ov-result-strip .rs .pct {
    font-size: 11px; color: var(--org-600); font-weight: 700; margin-left: 3px;
  }
  .ov-result-strip .arr {
    align-self: center;
    color: var(--ink-300);
    font-size: 18px;
    font-weight: 800;
  }

  /* 좁은 화면에서는 strip 을 세로 흐름으로 */
  @media (max-width: 880px) {
    .ov-stats { grid-template-columns: repeat(2, 1fr); }
    .ov-result-strip { grid-template-columns: 1fr; gap: 6px; }
    .ov-result-strip .arr { display: none; }
  }
"""

# Insert just BEFORE the @media print block (the consolidated one)
# Find where the *first* existing @media print block ends to know where to put
INSERT_ANCHOR = '  @media print {\n    @page { size: A4 portrait; margin: 12mm 14mm; }'
assert INSERT_ANCHOR in src
src = src.replace(INSERT_ANCHOR, NEW_CSS + '\n' + INSERT_ANCHOR)


# ============================================================
# 6) Adjust the "ov-hero" min-height since spec-mini is now wider/taller
#    Keep big diagram more prominent.
# ============================================================
OLD_HERO_GRID = "  .ov-hero { display: grid; grid-template-columns: 1.4fr 1fr; gap: 18px; align-items: stretch; }"
NEW_HERO_GRID = "  .ov-hero { display: grid; grid-template-columns: 1.05fr 1fr; gap: 18px; align-items: stretch; }"
src = src.replace(OLD_HERO_GRID, NEW_HERO_GRID)


# ============================================================
# 7) Save
# ============================================================
with open(SRC, 'w', encoding='utf-8') as f:
    f.write(src)
print('OK. wrote', SRC, '→', os.path.getsize(SRC), 'bytes')

def cnt(s): return src.count(s)
print('  new MODEL_DIAGRAMS embedded:', cnt('data:image/jpeg;base64,'))
print('  ov-stats grid:              ', cnt('class="ov-stats"'))
print('  ov-principle:               ', cnt('class="ov-principle"'))
print('  ov-result-strip:            ', cnt('class="ov-result-strip"'))
print('  _principleText():           ', cnt('function _principleText('))
print('  sidebar key rows: should be ~5 (was 10):', cnt("''}\n  ].map"), '← (배열 종결자 카운트, 1 expected)')
