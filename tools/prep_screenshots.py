# -*- coding: utf-8 -*-
"""폰에서 찍은 원본 스크린샷을 플레이 스토어 규격으로 다듬는다.

    python tools/prep_screenshots.py <원본폴더>

왜 필요한가
    1. 🚨 **비율.** 플레이는 «긴 변이 짧은 변의 2배 이내» 를 요구한다.
       S8 원본 1080×2220 은 2.056 이라 **그대로 올리면 거절된다.**
       위아래를 잘라내면 집 버튼과 캐릭터가 잘리므로, **좌우에 배경색을 덧대** 비율만 맞춘다.
       덧대는 색은 그 이미지의 모서리에서 뽑는다 — 노란 신호 화면은 노랑으로 덧대야
       이음매가 안 보인다.
    2. **오른쪽 가장자리의 스크롤바.** 안드로이드가 직접 그리는 오버레이 스크롤바라
       CSS 로는 못 없앤다(2026-09-02 확인). 가장자리 몇 px 를 잘라내 지운다.

주의
    ⚠ 아이폰에서 찍은 화면은 쓰지 않는다 — 이모지 그림이 애플 저작권이다.
      안드로이드(Noto Color Emoji)는 오픈 라이선스라 괜찮다.
"""
import os
import sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, 'store-assets', 'screenshots')

CROP_RIGHT  = 18     # 스크롤바가 차지하는 폭 (x 1064~1080 에서 관측)
MAX_RATIO   = 1.98   # 2.0 이 한계지만 반올림 사고를 피해 여유를 둔다

# 스토어에 보일 순서. 앞의 3장이 검색 결과에 먼저 뜨므로 가장 설명적인 것을 앞에 둔다.
ORDER = [
    ('01-menu.png',     '01-메뉴'),
    ('02-reaction.png', '02-번쩍'),
    ('03-trio.png',     '03-삼총사'),
    ('04-match.png',    '04-같은그림찾기'),
    ('05-land.png',     '05-땅따먹기'),
    ('06-five.png',     '06-딱다섯'),
    ('07-bomb.png',     '07-폭탄돌리기'),
    ('08-odd.png',      '08-다른색하나'),
]


def bg_of(im):
    """모서리 네 곳에서 배경색을 고른다. 셋 이상 같으면 그 색으로 본다."""
    w, h = im.size
    corners = [im.getpixel(p) for p in ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3))]
    for c in corners:
        if corners.count(c) >= 3:
            return c
    return corners[0]


def prep(src, dst):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    im = im.crop((0, 0, w - CROP_RIGHT, h))          # 스크롤바 제거
    w, h = im.size

    need = int(h / MAX_RATIO + 0.5)                  # 비율을 맞추는 데 필요한 최소 너비
    if need > w:
        pad = need - w
        left = pad // 2
        canvas = Image.new('RGB', (need, h), bg_of(im))
        canvas.paste(im, (left, 0))
        im = canvas

    im.save(dst)
    return im.size, im.size[1] / im.size[0]


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    srcdir = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)

    print(f'{"파일":<18} {"크기":>12} {"비율":>6}   결과')
    print('-' * 52)
    bad = False
    for src_name, out_name in ORDER:
        src = os.path.join(srcdir, src_name)
        if not os.path.exists(src):
            print(f'{out_name:<18} {"—":>12} {"—":>6}   🔴 원본 없음: {src_name}')
            bad = True
            continue
        size, ratio = prep(src, os.path.join(OUT, out_name + '.png'))
        ok = ratio <= 2.0 and min(size) >= 320 and max(size) <= 3840
        bad |= not ok
        print(f'{out_name:<18} {f"{size[0]}×{size[1]}":>12} {ratio:>6.3f}   {"OK" if ok else "🔴 규격 위반"}')

    print(f'\n→ {OUT}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
