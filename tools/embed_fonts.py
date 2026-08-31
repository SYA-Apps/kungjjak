# -*- coding: utf-8 -*-
"""글꼴을 web/index.html 안에 base64 로 심는다.

왜 필요한가
    지금까지는 Google Fonts CDN 을 <link> 로 불러왔다. 이 앱은 완전 오프라인이고
    안드로이드 래핑 때 INTERNET 권한도 뺄 계획이라, CDN 을 그대로 두면 앱 안에서는
    글꼴이 **무조건** 깨진다. 그래서 실제로 쓰는 글자만 골라 파일 안에 넣는다.

무엇을 하는가
    1. index.html 에 실제로 등장하는 글자를 모두 모은다 (주석까지 포함 — 여유분)
    2. Jua / Gothic A1(400·700) 원본을 내려받아 tools/.fontcache/ 에 둔다
    3. 그 글자들만 남기고 woff2 로 줄인다 (pyftsubset)
    4. base64 로 <style> 맨 앞에 @font-face 로 심는다
    5. CDN <link> 세 줄을 지운다

언제 다시 돌리는가
    ⚠ 화면에 나오는 **한글 문구를 새로 추가했다면 반드시 다시 돌린다.**
    서브셋에 없는 글자는 시스템 글꼴로 떨어져 톤이 깨진다.

    python tools/embed_fonts.py

여러 번 돌려도 안전하다 (기존 임베드 블록을 지우고 다시 만든다).

글꼴 라이선스: Jua, Gothic A1 모두 SIL Open Font License 1.1 — 임베드·재배포 가능.
"""
import base64
import io
import os
import re
import subprocess
import sys
import urllib.request

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML  = os.path.join(ROOT, 'web', 'index.html')
CACHE = os.path.join(ROOT, 'tools', '.fontcache')

START = '/* FONTS-EMBED-START — tools/embed_fonts.py 가 만든다. 직접 고치지 말 것 */'
END   = '/* FONTS-EMBED-END */'

BASE = 'https://raw.githubusercontent.com/google/fonts/main/'
FACES = [
    # (글꼴 이름, 굵기, 원본 경로)
    ('Jua',       400, 'ofl/jua/Jua-Regular.ttf'),
    ('Gothic A1', 400, 'ofl/gothica1/GothicA1-Regular.ttf'),
    ('Gothic A1', 700, 'ofl/gothica1/GothicA1-Bold.ttf'),
]

# 화면에 안 쓰더라도 넣어 두는 최소 글자 (숫자·문장부호·자주 쓸 낱말)
EXTRA = (
    '0123456789'
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ' !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    '·—–…“”‘’•×÷±°'
    '가나다라마바사아자차카타파하'
    '점수승리무패다시시작준비끝판번째초분'
)


def log(msg):
    print(msg)


def fetch(path):
    """원본 ttf 를 내려받아 캐시에 둔다."""
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    dest = os.path.join(CACHE, os.path.basename(path))
    if os.path.exists(dest) and os.path.getsize(dest) > 100000:
        return dest
    log('  받는 중 %s' % os.path.basename(path))
    req = urllib.request.Request(BASE + path, headers={'User-Agent': 'kungjjak-build'})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, 'wb') as f:
        f.write(r.read())
    return dest


def strip_embed(s):
    """이미 심어 둔 블록을 걷어낸다 (다시 돌릴 수 있게)."""
    i, j = s.find(START), s.find(END)
    if i == -1 or j == -1:
        return s
    return s[:i] + s[j + len(END):].lstrip('\n')


def strip_cdn(s):
    """CDN <link> 세 줄과 그 위 경고 주석을 지운다."""
    s = re.sub(
        r'<!-- ⚠ 출시 전 반드시 교체.*?-->\n', '', s, flags=re.S)
    s = re.sub(
        r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"[^>]*>\n',
        '', s)
    s = re.sub(
        r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*" rel="stylesheet">\n',
        '', s)
    return s


def subset(ttf, chars, out):
    txt = out + '.chars.txt'
    io.open(txt, 'w', encoding='utf-8').write(chars)
    cmd = [
        sys.executable, '-m', 'fontTools.subset', ttf,
        '--text-file=' + txt,
        '--output-file=' + out,
        '--flavor=woff2',
        '--no-hinting',
        '--desubroutinize',
        '--drop-tables+=DSIG',
        '--name-IDs=',
        '--layout-features=*',
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print(r.stdout.decode('utf-8', 'replace'))
        print(r.stderr.decode('utf-8', 'replace'))
        sys.exit('서브셋 실패: ' + ttf)
    os.remove(txt)
    return os.path.getsize(out)


def main():
    s = io.open(HTML, encoding='utf-8').read()
    before = len(s.encode('utf-8'))

    s = strip_embed(s)
    s = strip_cdn(s)

    # 파일에 등장하는 모든 글자 + 최소 보장 글자
    chars = set(s) | set(EXTRA)
    chars = {c for c in chars if c not in '\r\n\t'}
    hangul = sorted(c for c in chars if '가' <= c <= '힣')
    log('글자 %d 자 (그중 한글 %d 자)' % (len(chars), len(hangul)))

    text = ''.join(sorted(chars))
    blocks, total = [], 0
    for family, weight, path in FACES:
        ttf = fetch(path)
        out = os.path.join(CACHE, os.path.basename(path).replace('.ttf', '.sub.woff2'))
        size = subset(ttf, text, out)
        total += size
        b64 = base64.b64encode(open(out, 'rb').read()).decode('ascii')
        log('  %-12s %s  %6.1f KB' % (family, weight, size / 1024.0))
        blocks.append(
            "@font-face{font-family:'%s';font-style:normal;font-weight:%d;"
            "font-display:block;\n  src:url(data:font/woff2;base64,%s) format('woff2')}"
            % (family, weight, b64))

    embed = START + '\n' + '\n'.join(blocks) + '\n' + END + '\n'

    if '<style>\n' not in s:
        sys.exit('<style> 를 못 찾았다')
    s = s.replace('<style>\n', '<style>\n' + embed, 1)

    io.open(HTML, 'w', encoding='utf-8', newline='').write(s)
    after = len(s.encode('utf-8'))
    log('\nwoff2 합계 %.1f KB → index.html %.0f KB → %.0f KB'
        % (total / 1024.0, before / 1024.0, after / 1024.0))


if __name__ == '__main__':
    main()
