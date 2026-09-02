# -*- coding: utf-8 -*-
"""구글플레이 피처 그래픽(1024×500)을 만든다.

    python tools/make_feature_graphic.py

왜 스크립트로 두는가
    문구나 게임 개수가 바뀌면 다시 그려야 한다. 손으로 그린 이미지 파일만 남기면
    다음에 누가 무슨 색·글꼴로 만들었는지 알 수 없다.

지켜야 하는 것
    - 1024×500, **투명도 없음**(RGB). 플레이가 알파를 거부한다.
    - 글꼴은 tools/.fontcache/ 의 Jua·Gothic A1 (둘 다 SIL OFL — 재배포 가능).
      없으면 `python tools/embed_fonts.py` 를 한 번 돌리면 받아진다.
    - ⚠ **이모지를 쓰지 않는다.** 아이폰 이모지는 애플 저작권이고, 시스템마다 그림이
      달라 결과를 예측할 수 없다. 도형은 전부 직접 그린다.
    - ⚠ **가장자리는 잘릴 수 있다.** 중요한 것은 안쪽 80% 에 둔다.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, 'tools', '.fontcache')
OUT  = os.path.join(ROOT, 'store-assets', 'feature-graphic-1024x500.png')

W, H  = 1024, 500
BG    = (0xF2, 0xF1, 0xF8)   # --bg
INK   = (0x2E, 0x2B, 0x3A)   # --ink
MINT  = (0x7F, 0xD1, 0xB9)   # --a  쿵
CORAL = (0xFF, 0x8F, 0xA3)   # --b  짝
MUTE  = (0xDC, 0xDA, 0xE8)   # --mute
SUB   = (0x6B, 0x67, 0x7C)   # 본문 보조 (먹색을 옅게 한 것과 같은 결)

S = 4   # 4배로 그리고 줄인다 — PIL 은 안티에일리어싱이 없어 곡선이 계단진다


def build():
    jua = os.path.join(FONT, 'Jua-Regular.ttf')
    g1b = os.path.join(FONT, 'GothicA1-Bold.ttf')
    for f in (jua, g1b):
        if not os.path.exists(f):
            raise SystemExit(f'글꼴이 없다: {f}\n먼저 `python tools/embed_fonts.py` 를 돌릴 것.')

    img = Image.new('RGB', (W * S, H * S), BG)
    d = ImageDraw.Draw(img, 'RGBA')

    # 배경 — 두 사람 색을 아주 옅게. 얼굴과 겹치면 썸네일에서 뭉개지므로 구석으로 뺀다.
    d.ellipse([-160 * S, -210 * S, 300 * S, 130 * S], fill=MINT + (46,))
    d.ellipse([760 * S, 392 * S, 1200 * S, 732 * S], fill=CORAL + (40,))

    def face(cx, cy, r, rgb):
        """앱의 calm 표정 — 눈은 짧은 곡선 두 개, 입은 작은 미소."""
        d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=rgb)
        ew, eo, ey = r * 0.30, r * 0.34, cy - r * 0.12
        for sx in (-1, 1):
            ex = cx + sx * eo
            d.arc([(ex - ew / 2) * S, (ey - ew * 0.55) * S,
                   (ex + ew / 2) * S, (ey + ew * 0.55) * S],
                  200, 340, fill=INK, width=max(1, int(r * 0.11 * S)))
        mw, my = r * 0.42, cy + r * 0.34
        d.arc([(cx - mw / 2) * S, (my - mw * 0.5) * S,
               (cx + mw / 2) * S, (my + mw * 0.5) * S],
              20, 160, fill=INK, width=max(1, int(r * 0.10 * S)))

    f_name = ImageFont.truetype(jua, 54 * S)

    def pill(cx, cy, rgb, name):
        """앱 첫 화면의 .who 알약 그대로 — 흰 바탕에 얼굴과 이름을 묶는다.
        얼굴만 두면 배경색과 붙어 썸네일에서 안 보인다."""
        r = 40
        l, t, rr, b = d.textbbox((0, 0), name, font=f_name)
        tw, th = (rr - l) / S, (b - t) / S
        pw, ph = 2 * r + 22 + tw + 40, 2 * r + 26
        x0, y0 = cx - pw / 2, cy - ph / 2
        d.rounded_rectangle([x0 * S, y0 * S, (x0 + pw) * S, (y0 + ph) * S],
                            radius=ph / 2 * S, fill=(255, 255, 255),
                            outline=MUTE, width=int(2.5 * S))
        face(x0 + 13 + r, cy, r, rgb)
        d.text(((x0 + 13 + 2 * r + 22) * S - l, cy * S - t - th * S / 2),
               name, font=f_name, fill=INK)

    def center(txt, font, top, fill):
        l, t, rr, b = d.textbbox((0, 0), txt, font=font)
        d.text(((W * S - (rr - l)) / 2 - l, top * S - t), txt, font=font, fill=fill)

    center('쿵짝', ImageFont.truetype(jua, 180 * S), 48, INK)
    center('둘이서, 폰 하나로', ImageFont.truetype(g1b, 42 * S), 252, SUB)

    pill(300, 356, MINT, '쿵')
    pill(724, 356, CORAL, '짝')

    # 맨 아래 한 줄. 알약과 40px, 아래 가장자리와 40px 이상 띄운다(잘림 대비).
    f_small = ImageFont.truetype(g1b, 26 * S)
    txt = '미니게임 10개 · 완전 오프라인'
    l, t, rr, b = d.textbbox((0, 0), txt, font=f_small)
    d.text((W * S / 2 - (rr - l) / 2 - l, 448 * S - t - (b - t) / 2),
           txt, font=f_small, fill=(0x8B, 0x87, 0x9C))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.resize((W, H), Image.LANCZOS).save(OUT)
    print(f'{OUT}  ({W}×{H}, RGB)')


if __name__ == '__main__':
    build()
