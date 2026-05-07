#!/usr/bin/env python3
"""
9th pass — six-point cleanup:
  1. 모델 명칭 통일 :
       SJMO=압입모듈형, SJMO(A)=흡입송풍형, SJCO=대향류형, SJXO=직교류형
       내부 키는 'SJMO-A' 유지(데이터 호환), 표시만 'SJMO(A)' 로 통일
  2. 선정서 외형치수 영문/숫자 폰트 — 하드코드된 Consolas → var(--font-sans)
  3. 선정서 인쇄 A4 1페이지 fit — disclaimer 컴팩트화 + 패딩 축소
  4. 보급수 총 보급수 소요량 단위 (T/h) 명확 표시
  5. 루버 필요면적 단위 (m²) 명확 표시 + calc-unified 컬럼 폭 조정
  6. 선정서 footer — CONFIDENTIAL stamp 제거, "Sungji A.C.T. Co., Ltd." 라인 제거
"""
import re, os

SRC = '냉각탑_선정프로그램_장비개요.html'
with open(SRC,'r',encoding='utf-8') as f: src=f.read()

# ============================================================
# 1) MODEL_DESC 단축
# ============================================================
OLD_MODEL_DESC = """const MODEL_DESC = {
  'SJMO'  : '압입모듈형',
  'SJMO-A': '흡입모듈형',
  'SJCO'  : '대향류형 흡입송풍식',
  'SJXO'  : '직교류 흡입송풍식 대용량'
};"""
NEW_MODEL_DESC = """const MODEL_DESC = {
  'SJMO'  : '압입모듈형',
  'SJMO-A': '흡입송풍형',
  'SJCO'  : '대향류형',
  'SJXO'  : '직교류형'
};
// 내부 키 'SJMO-A' → 표시 라벨 'SJMO(A)'
function _modelLabel(t) { return t === 'SJMO-A' ? 'SJMO(A)' : t; }"""
assert OLD_MODEL_DESC in src
src = src.replace(OLD_MODEL_DESC, NEW_MODEL_DESC)


# Select 옵션도 업데이트
src = src.replace(
    '<option value="SJMO">SJMO (압입송풍식 직교류)</option>',
    '<option value="SJMO">SJMO (압입모듈형)</option>'
)
src = src.replace(
    '<option value="SJMO-A">SJMO-A (모듈형 흡입송풍식)</option>',
    '<option value="SJMO-A">SJMO(A) (흡입송풍형)</option>'
)
src = src.replace(
    '<option value="SJCO">SJCO (대향류형 흡입송풍식)</option>',
    '<option value="SJCO">SJCO (대향류형)</option>'
)
src = src.replace(
    '<option value="SJXO">SJXO (직교류 흡입송풍식 대용량)</option>',
    '<option value="SJXO">SJXO (직교류형)</option>'
)


# 운전 원리 — 새 명칭 톤으로 정리
OLD_PRIN = """  const T = {
    'SJMO':   '압입송풍식 직교류 — 측면의 시로코 팬이 공기를 강제 송풍하여 직각 방향으로 흐르는 충진재 표면의 순환수를 냉각합니다. 설치 높이가 낮아 실내·지하 등 제약공간에 유리합니다.',
    'SJMO-A': '모듈형 흡입송풍식 직교류 — 측면 액시얼 팬이 충진재를 통과한 공기를 외부로 흡입 토출합니다. 모듈화된 구조로 협소공간에서도 단순 조립·반입이 가능합니다.',
    'SJCO':   '대향류형 흡입송풍식 — 상부 액시얼 팬이 외기를 아래에서 위로 끌어올리며 충진재 위에서 분사된 순환수와 정반대 방향으로 만나 효율적으로 열교환합니다.',
    'SJXO':   '직교류 흡입송풍식 — 상부 흡입 팬이 측면 루버를 통해 공기를 빨아들이고, 충진재를 흘러내리는 순환수와 직각으로 만나 냉각합니다. 대용량·저소음 운용에 적합합니다.'
  };"""
NEW_PRIN = """  const T = {
    'SJMO':   '압입모듈형 — 측면의 시로코 팬이 공기를 강제 송풍하여 직각 방향으로 흐르는 충진재 표면의 순환수를 냉각합니다. 설치 높이가 낮아 실내·지하 등 제약공간에 유리합니다.',
    'SJMO-A': '흡입송풍형 — 측면 액시얼 팬이 충진재를 통과한 공기를 외부로 흡입·토출합니다. 모듈화된 구조로 협소공간에서도 단순 조립·반입이 가능합니다.',
    'SJCO':   '대향류형 — 상부 액시얼 팬이 외기를 아래에서 위로 끌어올리며 충진재 위에서 분사된 순환수와 정반대 방향으로 만나 효율적으로 열교환합니다.',
    'SJXO':   '직교류형 — 상부 흡입 팬이 측면 루버를 통해 공기를 빨아들이고, 충진재를 흘러내리는 순환수와 직각으로 만나 냉각합니다. 대용량·저소음 운용에 적합합니다.'
  };"""
assert OLD_PRIN in src
src = src.replace(OLD_PRIN, NEW_PRIN)


# 헤더 코멘트도 업데이트
OLD_HEAD_COM = """//   SJMO   : 압입송풍식 직교류        (Forced-draft Cross-flow)
//   SJMO-A : 모듈형 흡입송풍식 직교류 (Induced-draft Cross-flow, modular)
//   SJCO   : 대향류형 흡입송풍식      (Counter-flow Induced-draft)
//   SJXO   : 직교류 흡입송풍식 대용량 (Cross-flow Induced-draft, large)"""
NEW_HEAD_COM = """//   SJMO   : 압입모듈형  (Forced-draft Cross-flow)
//   SJMO-A : 흡입송풍형  (Induced-draft Cross-flow, modular) — 표시명 SJMO(A)
//   SJCO   : 대향류형    (Counter-flow Induced-draft)
//   SJXO   : 직교류형    (Cross-flow Induced-draft, large)"""
src = src.replace(OLD_HEAD_COM, NEW_HEAD_COM)


# 모든 사용자 노출 ${modelType} 형태를 _modelLabel 로 매핑하기엔 광범위하므로
# 안전하게 — `${modelType}-${modelCRT}` (모델 코드 표시) 패턴만 일괄 변환
# 그 외 ${MODEL_DESC[..]} 는 한글 명칭이 이미 매핑됨
src = re.sub(
    r"\$\{modelType\}-\$\{modelCRT\}",
    "${_modelLabel(modelType)}-${modelCRT}",
    src
)
# 매트릭스 헤더 / 비교표 등에서 ${t}- 또는 \b${t}\b 형태도 변환
src = re.sub(
    r"\$\{t\}-\$\{cap\}",
    "${_modelLabel(t)}-${cap}",
    src
)
# `${ctType}-${cap}` 도 사용자 표시
src = re.sub(
    r"\$\{ctType\}-\$\{(modelCap|cap)\}",
    r"${_modelLabel(ctType)}-${\1}",
    src
)
# 매트릭스 thead `<th> ... ${t} ... </th>`
src = src.replace(
    "${t}<br><span",
    "${_modelLabel(t)}<br><span"
)
# `<b>${ctType}</b>` 같은 본문 표시도
src = src.replace(
    "<b>${ctType}</b>",
    "<b>${_modelLabel(ctType)}</b>"
)
# selectModelText 부분
src = src.replace(
    "${ctType} 라인업 최대용량",
    "${_modelLabel(ctType)} 라인업 최대용량"
)
# ovModelDesc 의 fallback 텍스트
src = src.replace(
    '<div class="ov-model-desc" id="ovModelDesc">대향류형 흡입송풍식</div>',
    '<div class="ov-model-desc" id="ovModelDesc">대향류형</div>'
)


# ============================================================
# 2) 선정서 외형치수의 하드코드 Consolas → 본문 sans 폰트 토큰
# ============================================================
src = src.replace(
    "font-family:Consolas,monospace;font-weight:700;",
    "font-family:var(--font-sans);font-weight:700;"
)
src = src.replace(
    "font-family:Consolas,monospace;font-weight:800;",
    "font-family:var(--font-sans);font-weight:800;"
)


# ============================================================
# 3) 선정서 A4 1페이지 fit — disclaimer 4줄 → 1줄 컴팩트, footer 압축
#     + report-body 폰트/패딩 축소
# ============================================================
OLD_DISCLAIMER = """    <div class="report-disclaimer">
      <b>※ Notes &amp; Disclaimer</b><br>
      1) 본 선정서의 호칭능력(CRT)은 표준 설계조건(입구 37℃ / 출구 32℃ / 습구 27℃, 1 CRT = 4.53 kW = 3,900 kcal/h)을 기준으로 산정되었습니다.<br>
      2) Rating Factor는 성지공조기술 자체 데이터베이스를 기반으로 입력 조건(입구·출구·습구온도)에 따라 자동 보정되었습니다.<br>
      3) 본 선정 결과는 표준 옥외 노출 설치, 추가 정압 손실 없음, 외부 부속 장치(차폐판·소음기 등) 미적용 조건을 가정한 값입니다.<br>
      4) 실제 설치환경(흡입 장애, 토출 덕트, 기류 간섭, 공조계통 압력 등)에 따라 보정 검토가 필요하며, 자세한 사항은 (주)성지공조기술로 문의하시기 바랍니다.
    </div>"""
NEW_DISCLAIMER = """    <div class="report-disclaimer">
      <b>※ Notes</b> · 1 CRT = 4.53 kW = 3,900 kcal/h (표준 37/32/27℃ 기준) · Rating Factor 자동 보정 · 옥외 표준 설치 가정 · 실제 설치환경(흡입 장애·토출 덕트·기류 간섭 등) 별도 검토 필요. 자세한 사항은 (주)성지공조기술로 문의 바랍니다.
    </div>"""
assert OLD_DISCLAIMER in src
src = src.replace(OLD_DISCLAIMER, NEW_DISCLAIMER)


# ============================================================
# 4) 보급수 결과 박스 단위 강조  +
# 5) 루버 결과 박스 단위 강조 — CSS 한 번만 조정해서 둘 다 적용
# ============================================================
# 결과박스 unit 폰트 사이즈 키워서 확실히 보이게
OLD_NUM_CSS = """  .calc-result-card .num {
    font-family: var(--font-mono);
    font-size: 22px; font-weight: 800; color: var(--org-600);
    letter-spacing: -0.5px;
    white-space: nowrap;
  }
  .calc-result-card .num .unit {
    font-size: 12.5px; color: var(--ink-600);
    font-weight: 500; margin-left: 4px;
    white-space: nowrap;
    display: inline-block;
  }"""
NEW_NUM_CSS = """  .calc-result-card .num {
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
assert OLD_NUM_CSS in src
src = src.replace(OLD_NUM_CSS, NEW_NUM_CSS)

# 인쇄용 unit 사이즈도 함께 키움
src = src.replace(
    '.calc-result-card .num .unit { font-size: 9.5pt !important; }',
    '.calc-result-card .num .unit { font-size: 11pt !important; color: var(--org-700) !important; font-weight: 700 !important; }'
)


# ============================================================
# 5b) 루버 calc-unified 컬럼 폭 — 계산식·적용 칸 줄밀림 방지
#     항목 14% / 계산식 32% / 적용 30% / 값 24% 로 재배분
# ============================================================
OLD_LV_HDR = """    <table class="calc-unified">
      <thead>
        <tr>
          <th style="width:18%;">항목</th>
          <th>계산식 (Theoretical)</th>
          <th>적용 (Applied)</th>
          <th style="width:22%;">값</th>
        </tr>
      </thead>"""
NEW_LV_HDR = """    <table class="calc-unified">
      <colgroup>
        <col style="width:14%">
        <col style="width:34%">
        <col style="width:30%">
        <col style="width:22%">
      </colgroup>
      <thead>
        <tr>
          <th>항목</th>
          <th>계산식 (Theoretical)</th>
          <th>적용 (Applied)</th>
          <th>값</th>
        </tr>
      </thead>"""
assert OLD_LV_HDR in src
src = src.replace(OLD_LV_HDR, NEW_LV_HDR)

# 보급수 calc-unified 도 동일 패턴 — colgroup 추가해서 컬럼 폭 안정화
OLD_MUW_HDR = """    <table class="calc-unified">
      <thead>
        <tr>
          <th>항목</th>
          <th>계산식</th>
          <th>적용</th>
          <th>값 (T/h)</th>
        </tr>
      </thead>"""
NEW_MUW_HDR = """    <table class="calc-unified">
      <colgroup>
        <col style="width:14%">
        <col style="width:30%">
        <col style="width:34%">
        <col style="width:22%">
      </colgroup>
      <thead>
        <tr>
          <th>항목</th>
          <th>계산식</th>
          <th>적용</th>
          <th>값 (T/h)</th>
        </tr>
      </thead>"""
assert OLD_MUW_HDR in src
src = src.replace(OLD_MUW_HDR, NEW_MUW_HDR)


# ============================================================
# 6) 선정서 footer — CONFIDENTIAL stamp 제거, Sungji A.C.T. 라인 제거
# ============================================================
OLD_FOOTER = """    <div class="report-footer">
      <span class="doc-stamp">CONFIDENTIAL</span>
      <div class="copyright">
        Copyright ⓒ ${yyyy} (주)성지공조기술 (Sungji Air Conditioning Technology Co., Ltd.) All rights reserved.<br>
        본 선정서의 모든 콘텐츠 및 산정 로직에 대한 저작권은 (주)성지공조기술에 있으며, 무단 복제·재배포·상업적 이용을 금합니다.
      </div>
      <div class="signature">
        <div class="corp-name">(주)성지공조기술</div>
        <div>Sungji A.C.T. Co., Ltd.</div>
        <div style="font-size:10px;color:var(--ink-300);">발행일: ${dateStr}</div>
      </div>
    </div>"""
NEW_FOOTER = """    <div class="report-footer">
      <div class="copyright">
        Copyright ⓒ ${yyyy} (주)성지공조기술 (Sungji Air Conditioning Technology Co., Ltd.) All rights reserved.<br>
        본 선정서의 모든 콘텐츠 및 산정 로직에 대한 저작권은 (주)성지공조기술에 있으며, 무단 복제·재배포·상업적 이용을 금합니다.
      </div>
      <div class="signature">
        <div class="corp-name">(주)성지공조기술</div>
        <div style="font-size:10px;color:var(--ink-400);margin-top:2px;">발행일: ${dateStr}</div>
      </div>
    </div>"""
assert OLD_FOOTER in src
src = src.replace(OLD_FOOTER, NEW_FOOTER)


# 보급수·루버의 mini-footer 도 통일 — CONFIDENTIAL stamp 빼고 발행일/회사명만
OLD_MINI_FOOTER_MUW = """    <div class="calc-mini-footer">
      <div class="note">
        ※ 증발율 0.166%/℃ × Range (HVAC 표준) · 비산율 0.002% (고효율 엘리미네이터) · 농축배율 C = ${C} (HVAC 일반 5~7).<br>
        ※ 정확한 C값은 원수 수질·수처리 방식에 따라 변동되며 수처리 전문회사 검토 권장. 기동·정지 충수량 별도 계상.
      </div>
      <span class="stamp">CONFIDENTIAL</span>
      <div class="corp">(주)성지공조기술<br><span style="font-size:9px;font-weight:500;color:var(--ink-400);">${meta.dateStr}</span></div>
    </div>"""
NEW_MINI_FOOTER_MUW = """    <div class="calc-mini-footer">
      <div class="note">
        ※ 증발율 0.166%/℃ × Range (HVAC 표준) · 비산율 0.002% (고효율 엘리미네이터) · 농축배율 C = ${C} (HVAC 일반 5~7).<br>
        ※ 정확한 C값은 원수 수질·수처리 방식에 따라 변동되며 수처리 전문회사 검토 권장. 기동·정지 충수량 별도 계상.
      </div>
      <div class="corp">(주)성지공조기술<br><span style="font-size:9px;font-weight:500;color:var(--ink-400);">발행일: ${meta.dateStr}</span></div>
    </div>"""
if OLD_MINI_FOOTER_MUW in src:
    src = src.replace(OLD_MINI_FOOTER_MUW, NEW_MINI_FOOTER_MUW)

OLD_MINI_FOOTER_LVR = """    <div class="calc-mini-footer">
      <div class="note">
        ※ ASHRAE / 일본 냉동공조 협회 권고에 따른 표준 풍속 ${V_MAX} m/s 이하 기준. 정숙·저소음 요구 시 3 ~ 4 m/s 강화 권장.<br>
        ※ 본 면적은 유효 통기 면적이며 루버 프레임·지지대 등 비통기부 제외 net 기준. 흡입측·토출측 동일 면적 권장.
      </div>
      <span class="stamp">CONFIDENTIAL</span>
      <div class="corp">(주)성지공조기술<br><span style="font-size:9px;font-weight:500;color:var(--ink-400);">${meta.dateStr}</span></div>
    </div>"""
NEW_MINI_FOOTER_LVR = """    <div class="calc-mini-footer">
      <div class="note">
        ※ ASHRAE / 일본 냉동공조 협회 권고에 따른 표준 풍속 ${V_MAX} m/s 이하 기준. 정숙·저소음 요구 시 3 ~ 4 m/s 강화 권장.<br>
        ※ 본 면적은 유효 통기 면적이며 루버 프레임·지지대 등 비통기부 제외 net 기준. 흡입측·토출측 동일 면적 권장.
      </div>
      <div class="corp">(주)성지공조기술<br><span style="font-size:9px;font-weight:500;color:var(--ink-400);">발행일: ${meta.dateStr}</span></div>
    </div>"""
if OLD_MINI_FOOTER_LVR in src:
    src = src.replace(OLD_MINI_FOOTER_LVR, NEW_MINI_FOOTER_LVR)

# calc-mini-footer 의 grid template 을 stamp 제거에 맞춰 2-column 으로
src = src.replace(
    """  .calc-mini-footer {
    margin-top: 10px; padding-top: 8px;
    border-top: 1.5px solid var(--pri-800);
    display: grid;
    grid-template-columns: 1fr auto auto;
    gap: 12px;""",
    """  .calc-mini-footer {
    margin-top: 10px; padding-top: 8px;
    border-top: 1.5px solid var(--pri-800);
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 12px;"""
)


# ============================================================
# 7) 선정서 인쇄 컴팩트화 — 추가 패딩/폰트 축소 (1페이지 fit)
# ============================================================
EXTRA_PRINT = """
  /* === 선정서 1페이지 fit 강화 === */
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
  }

"""
# 마지막 </style> 직전에 삽입
last_close = src.rfind('</style>')
src = src[:last_close] + EXTRA_PRINT + src[last_close:]


# ============================================================
# Save
# ============================================================
with open(SRC,'w',encoding='utf-8') as f: f.write(src)

print('OK. wrote', SRC, '→', os.path.getsize(SRC), 'bytes')
def cnt(s): return src.count(s)
print('  _modelLabel() 정의:                ', cnt('function _modelLabel('))
print('  _modelLabel(modelType) 사용:      ', cnt('_modelLabel(modelType)'))
print('  _modelLabel(t/ctType) 사용:       ', cnt('_modelLabel(t)') + cnt('_modelLabel(ctType)'))
print('  Consolas 잔존 (없어야 함):        ', cnt('Consolas'))
print('  CONFIDENTIAL 잔존 (없어야 함):    ', cnt('CONFIDENTIAL'))
print('  Sungji A.C.T. 잔존 (없어야 함):   ', cnt('Sungji A.C.T'))
print('  변경된 MODEL_DESC:                 ', cnt("'SJCO'  : '대향류형'"))
