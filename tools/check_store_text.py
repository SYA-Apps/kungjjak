# -*- coding: utf-8 -*-
"""스토어 문구가 플레이 제한에 맞는지 확인한다.

    python tools/check_store_text.py

무엇을 보는가
    1. 글자 수 — 앱 이름 30자, 짧은 설명 80자, 자세한 설명 4000자.
       ⚠ 플레이는 **글자(문자) 수**로 센다. 한글 한 글자도 1자다(바이트가 아니다).
    2. 금지어 — 남의 상표를 적었는지. "○○ 같은 게임" 도 안 된다.
    3. 공개용이 아닌 메일 주소가 섞였는지 — 허용 주소 하나 말고는 전부 걸러낸다.

    docs/스토어-등록정보.md 의 ``` 블록에서 문구를 읽어온다.
    문서를 고치면 이 검사도 저절로 따라간다 — 문구를 두 군데 두지 않기 위해서다.
"""
import os
import re
import sys

# 한글 Windows 콘솔 기본 인코딩은 cp949 라 이모지를 못 찍고 그대로 죽는다.
# 하필 **검사가 실패해 이유를 알려야 하는 순간**에 터져서 traceback 만 남았다
# (2026-09-10 실측). 다른 도구들과 같은 방식으로 표준출력을 UTF-8 로 돌린다.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC  = os.path.join(ROOT, 'docs', '스토어-등록정보.md')

# 플레이 콘솔의 실제 제한
LIMITS = [
    ('앱 이름',      30),
    ('짧은 설명',    80),
    ('자세한 설명', 4000),
]

# 남의 상표 — 앱 안뿐 아니라 스토어 문구·스크린샷에도 쓰면 안 된다.
TRADEMARKS = ['set게임', 'set 게임', '도블', 'dobble', '할리갈리', 'halli galli',
              '우노', 'uno', '젠가', 'jenga', '부루마블', '모노폴리', 'monopoly']

# 공개 문구에 허용되는 주소는 이것 하나뿐이다 (C:/SYA/CLAUDE.md).
#
# 예전에는 «쓰면 안 되는 주소» 를 목록으로 들고 있었는데, 그러면 **개인 메일 주소가
# 이 공개 저장소에 그대로 박힌다**(2026-09-10 점검에서 실제로 걸렸다). 그래서 규칙을
# 뒤집었다 — 허용 주소 하나만 알고, 나머지는 무엇이든 걸러낸다. 목록을 관리할 필요도
# 없어져서 새 계정이 생겨도 저절로 걸린다.
PUBLIC_MAIL = 'sya.apps.dev@gmail.com'
MAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}')


def blocks(text):
    """마크다운 ``` 블록을 순서대로 돌려준다."""
    return re.findall(r'^```[^\n]*\n(.*?)^```', text, re.S | re.M)


def main():
    if not os.path.exists(DOC):
        raise SystemExit(f'문서가 없다: {DOC}')
    doc = open(DOC, encoding='utf-8').read()
    found = [b.strip() for b in blocks(doc)]

    if len(found) < len(LIMITS):
        raise SystemExit(f'``` 블록이 {len(found)}개뿐이다. '
                         f'앱 이름·짧은 설명·자세한 설명 순으로 {len(LIMITS)}개가 필요하다.')

    bad = False
    print(f'{"항목":<12} {"글자":>6} {"제한":>6}   결과')
    print('-' * 42)
    for (name, limit), body in zip(LIMITS, found):
        n = len(body)
        ok = n <= limit
        bad |= not ok
        print(f'{name:<12} {n:>6} {limit:>6}   {"OK" if ok else f"초과 {n - limit}자"}')

    joined = '\n'.join(found).lower()

    hits = [t for t in TRADEMARKS if t in joined]
    if hits:
        bad = True
        print(f'\n🚨 상표로 보이는 낱말: {", ".join(hits)}')
        print('   룰을 빌리는 것은 괜찮지만 이름을 쓰면 안 된다. "○○ 같은 게임" 도 안 된다.')

    mails = sorted({m for m in MAIL_RE.findall(joined) if m != PUBLIC_MAIL})
    if mails:
        bad = True
        print(f'\n🚨 공개하면 안 되는 주소: {", ".join(mails)}')
        print(f'   공개용은 언제나 {PUBLIC_MAIL} 이다.')

    if not hits and not mails:
        print('\n상표·개인 주소 검사 통과')

    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
