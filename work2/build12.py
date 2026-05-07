#!/usr/bin/env python3
"""
12th pass — 비밀번호 게이트.
  - 「추가 입력」 그룹 직후, 「선정 계산」버튼 위에 비밀번호 입력란 추가
    (type=password 이므로 입력 시 모든 글자가 점/별표로 마스킹됨)
  - SHA-256 해시 비교로 검증 (평문 비밀번호 'sealove7*' 는 코드에 노출하지 않음)
  - 인증 전: 「선정 계산」 클릭 시 비밀번호 검사 → 일치 시 계산, 불일치 시 경고
  - 첫 인증 후 세션 동안 잠금 해제 유지 (재계산 자유)
  - 페이지 새로고침 시 다시 인증 필요
"""
import os, hashlib

SRC = '냉각탑_선정프로그램_장비개요.html'
with open(SRC,'r',encoding='utf-8') as f: src=f.read()

# Password hash — SHA-256("sealove7*")
PWD_HASH = hashlib.sha256(b'sealove7*').hexdigest()
print('Password SHA-256:', PWD_HASH)

# ============================================================
# 1) Insert password input field — 부속 옵션 그룹 후, button-row 직전
# ============================================================
OLD_HTML = """        <div class="form-group" style="margin-bottom:0;">
          <label>부속 옵션 <span style="font-weight:500;color:var(--ink-400);">(SJMO·SJMO-A 적용)</span></label>
          <div class="opt-row">
            <label class="opt-chip"><input type="checkbox" id="optMist"> <span>백연감소코일</span></label>
            <label class="opt-chip"><input type="checkbox" id="optInletSilencer"> <span>흡입소음기</span></label>
            <label class="opt-chip"><input type="checkbox" id="optDischargeSilencer"> <span>토출소음기</span></label>
          </div>
        </div>
      </div>

      <div class="button-row">
        <button class="btn btn-reset" onclick="resetForm()">초기화</button>
        <button class="btn btn-primary" onclick="calculate()">선정 계산</button>
      </div>"""

NEW_HTML = """        <div class="form-group" style="margin-bottom:0;">
          <label>부속 옵션 <span style="font-weight:500;color:var(--ink-400);">(SJMO·SJMO-A 적용)</span></label>
          <div class="opt-row">
            <label class="opt-chip"><input type="checkbox" id="optMist"> <span>백연감소코일</span></label>
            <label class="opt-chip"><input type="checkbox" id="optInletSilencer"> <span>흡입소음기</span></label>
            <label class="opt-chip"><input type="checkbox" id="optDischargeSilencer"> <span>토출소음기</span></label>
          </div>
        </div>
      </div>

      <!-- 비밀번호 게이트 -->
      <div class="pwd-gate" id="pwdGate">
        <div class="pwd-head">
          <span class="lock" id="pwdLock">🔒</span>
          <span class="pwd-title">비밀번호 (Password)</span>
          <span class="pwd-status" id="pwdStatus">미인증 / Locked</span>
        </div>
        <div class="pwd-input-wrap">
          <input type="password" id="pwd" placeholder="비밀번호를 입력하세요" autocomplete="off" spellcheck="false">
          <button type="button" class="pwd-toggle" id="pwdToggle" title="표시/숨김">👁</button>
        </div>
        <div class="pwd-msg" id="pwdMsg" style="display:none;"></div>
      </div>

      <div class="button-row">
        <button class="btn btn-reset" onclick="resetForm()">초기화</button>
        <button class="btn btn-primary" id="btnCalc" onclick="calculate()">선정 계산</button>
      </div>"""

assert OLD_HTML in src
src = src.replace(OLD_HTML, NEW_HTML)


# ============================================================
# 2) Insert CSS for password block
# ============================================================
PWD_CSS = """
  /* ============ 비밀번호 게이트 ============ */
  .pwd-gate {
    background: var(--bg-50);
    border: 1.5px solid var(--ink-150);
    border-radius: 10px;
    padding: 12px 14px 13px;
    margin: 6px 0 14px;
    transition: all 0.2s;
  }
  .pwd-gate.unlocked {
    background: var(--grn-100);
    border-color: var(--grn-600);
  }
  .pwd-gate.error {
    background: var(--org-100);
    border-color: var(--org-700);
    animation: pwdShake 0.35s;
  }
  @keyframes pwdShake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-6px); }
    75% { transform: translateX(6px); }
  }
  .pwd-gate .pwd-head {
    display: flex; align-items: center; gap: 7px;
    margin-bottom: 8px;
    font-size: 13px; font-weight: 700;
    color: var(--ink-700);
  }
  .pwd-gate .pwd-head .lock { font-size: 14px; line-height: 1; }
  .pwd-gate.unlocked .pwd-head { color: var(--grn-700); }
  .pwd-gate.unlocked .pwd-head .lock { color: var(--grn-600); }
  .pwd-gate.unlocked .pwd-head .lock::before { content: '🔓'; }
  .pwd-gate.unlocked .pwd-head .lock { font-size: 0; }
  .pwd-gate.unlocked .pwd-head .lock::before { font-size: 14px; }
  .pwd-gate .pwd-title { flex: 1; min-width: 0; }
  .pwd-gate .pwd-status {
    font-size: 10.5px; font-weight: 700;
    padding: 2px 8px; border-radius: 10px;
    background: var(--ink-150); color: var(--ink-700);
    letter-spacing: 0.3px;
  }
  .pwd-gate.unlocked .pwd-status {
    background: var(--grn-200); color: var(--grn-800);
  }
  .pwd-gate.error .pwd-status {
    background: var(--org-200); color: var(--org-800);
  }
  .pwd-gate .pwd-input-wrap {
    position: relative;
    display: flex; align-items: stretch;
  }
  .pwd-gate input[type="password"],
  .pwd-gate input[type="text"] {
    width: 100%;
    padding: 11px 44px 11px 14px;
    font-size: 14px; letter-spacing: 2px;
    border: 1.5px solid var(--ink-150);
    border-radius: 7px;
    background: white;
    transition: all 0.2s;
    font-family: inherit;
    box-sizing: border-box;
  }
  .pwd-gate input:focus {
    outline: none;
    border-color: var(--pri-700);
    box-shadow: 0 0 0 3px rgba(42,82,152,0.10);
  }
  .pwd-gate.unlocked input { border-color: var(--grn-600); background: white; }
  .pwd-gate.error input { border-color: var(--org-700); }
  .pwd-gate .pwd-toggle {
    position: absolute; right: 8px; top: 50%;
    transform: translateY(-50%);
    background: transparent; border: none;
    cursor: pointer; font-size: 16px;
    padding: 6px 8px; border-radius: 5px;
    color: var(--ink-500);
    font-family: inherit;
  }
  .pwd-gate .pwd-toggle:hover { background: var(--ink-100); color: var(--pri-700); }
  .pwd-gate .pwd-msg {
    margin-top: 7px;
    font-size: 11.5px;
    padding: 7px 11px;
    border-radius: 6px;
    line-height: 1.4;
  }
  .pwd-gate .pwd-msg.error {
    background: var(--org-100); color: var(--org-700);
    border-left: 3px solid var(--org-700);
  }
  .pwd-gate .pwd-msg.success {
    background: var(--grn-100); color: var(--grn-700);
    border-left: 3px solid var(--grn-600);
  }

  /* 잠금 상태에서 선정 계산 버튼 약간 절제된 톤 */
  .btn-primary[data-locked="1"] {
    opacity: 0.78;
    background: linear-gradient(135deg, var(--ink-500) 0%, var(--ink-600) 100%);
    box-shadow: 0 4px 12px rgba(96,125,139,0.25);
  }
  .btn-primary[data-locked="1"]::before {
    content: '🔒  ';
  }
"""

# Insert before the @media (max-width: 880px) block
ANCHOR_CSS = '  @media (max-width: 880px) {'
assert ANCHOR_CSS in src
src = src.replace(ANCHOR_CSS, PWD_CSS + '\n' + ANCHOR_CSS, 1)


# ============================================================
# 3) JS — wrap calculate() with password gate
# ============================================================
PWD_JS = """// ============ 비밀번호 게이트 ============
const _PWD_HASH = '__PWD_HASH__';   // SHA-256('sealove7*')
let _isUnlocked = false;

async function _sha256(text) {
  const enc = new TextEncoder().encode(text);
  const hash = await crypto.subtle.digest('SHA-256', enc);
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2,'0')).join('');
}

async function _verifyPwd(input) {
  if (!input) return false;
  try {
    const h = await _sha256(input);
    return h === _PWD_HASH;
  } catch (e) { return false; }
}

function _setPwdState(state, msg) {
  const gate = document.getElementById('pwdGate');
  const statusEl = document.getElementById('pwdStatus');
  const msgEl = document.getElementById('pwdMsg');
  const btn = document.getElementById('btnCalc');
  gate.classList.remove('unlocked','error');
  if (state === 'unlocked') {
    gate.classList.add('unlocked');
    statusEl.textContent = '인증됨 / Unlocked';
    msgEl.style.display = 'none';
    btn.removeAttribute('data-locked');
  } else if (state === 'error') {
    gate.classList.add('error');
    statusEl.textContent = '오류 / Error';
    msgEl.className = 'pwd-msg error';
    msgEl.textContent = msg || '⚠ 비밀번호가 올바르지 않습니다.';
    msgEl.style.display = 'block';
    btn.setAttribute('data-locked','1');
  } else {
    statusEl.textContent = '미인증 / Locked';
    msgEl.style.display = 'none';
    btn.setAttribute('data-locked','1');
  }
}

// 원본 calculate 를 backup → 게이트 wrapper 로 교체
const _origCalculate = calculate;
calculate = async function() {
  if (!_isUnlocked) {
    const pwdInput = document.getElementById('pwd');
    const ok = await _verifyPwd(pwdInput.value);
    if (!ok) {
      _setPwdState('error');
      pwdInput.focus();
      pwdInput.select();
      return;
    }
    _isUnlocked = true;
    _setPwdState('unlocked');
    // 입력값 마스킹 유지 + 인증 직후 비번칸 readonly 처리하여 노출 차단
    pwdInput.value = '••••••••';
    pwdInput.setAttribute('readonly','readonly');
    pwdInput.blur();
  }
  return _origCalculate.apply(this, arguments);
};

// 비번 칸 토글 (눈 아이콘) — 잠금 해제 전에는 평문 보기 가능, 잠금 후엔 readonly 라 토글 무용
document.addEventListener('DOMContentLoaded', () => {
  const tg = document.getElementById('pwdToggle');
  const ip = document.getElementById('pwd');
  if (!tg || !ip) return;
  tg.addEventListener('click', () => {
    if (_isUnlocked) return;
    ip.type = (ip.type === 'password') ? 'text' : 'password';
  });
  // 비번 입력 변경 시 에러 상태 초기화
  ip.addEventListener('input', () => {
    if (_isUnlocked) return;
    const gate = document.getElementById('pwdGate');
    if (gate.classList.contains('error')) _setPwdState('locked');
  });
  // Enter 키로 즉시 시도
  ip.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      calculate();
    }
  });
  // 초기 상태
  _setPwdState('locked');
});
// 만약 DOMContentLoaded가 이미 발생한 환경(파일 끝에서 로드되는 일반 케이스)이면 즉시 실행
if (document.readyState !== 'loading') {
  setTimeout(() => {
    if (typeof _setPwdState === 'function') _setPwdState('locked');
  }, 0);
}

// resetForm 호출 시 비밀번호 인증 상태도 초기화
const _origResetForm = resetForm;
resetForm = function() {
  _isUnlocked = false;
  const ip = document.getElementById('pwd');
  if (ip) {
    ip.removeAttribute('readonly');
    ip.value = '';
    ip.type = 'password';
  }
  _setPwdState('locked');
  return _origResetForm.apply(this, arguments);
};

"""

PWD_JS = PWD_JS.replace('__PWD_HASH__', PWD_HASH)

# Inject right after the closing `}` of resetForm function definition.
# Anchor: the line right after resetForm definition (before document.querySelectorAll('input').forEach)
ANCHOR_JS = "document.querySelectorAll('input').forEach(input => {"
assert ANCHOR_JS in src
src = src.replace(ANCHOR_JS, PWD_JS + ANCHOR_JS)


# Avoid Enter on password running calculate without checking:
#   the existing global `keypress Enter → calculate()` already triggers our wrapper. OK.
# But the wrapper will check pwd field — perfect. Keep as is.


# ============================================================
# Save
# ============================================================
with open(SRC,'w',encoding='utf-8') as f: f.write(src)
print('OK. wrote', SRC, '→', os.path.getsize(SRC), 'bytes')
def cnt(s): return src.count(s)
print('  pwd-gate HTML:        ', cnt('class="pwd-gate"'))
print('  PWD_HASH embedded:    ', cnt(PWD_HASH))
print('  _verifyPwd defined:   ', cnt('async function _verifyPwd'))
print('  calculate wrapper:    ', cnt('const _origCalculate'))
print('  resetForm wrapper:    ', cnt('const _origResetForm'))
