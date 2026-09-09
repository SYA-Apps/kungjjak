"""쿵짝 앱 아이콘 생성.
python3 tools/make_icons.py 로 실행.

구도 — **아이콘 전체를 위아래로 반 가른다.** 위 민트(쿵)는 얼굴이 거꾸로, 아래
코랄(짝)은 바로 놓이고, 가운데 잉크색 선이 둘을 나눈다. 여백 없이 꽉 채운다.
앱 실제 화면이 상하 분할이고 위쪽 절반이 180도 돌아가 있는 것을 그대로 옮긴 것이라,
아이콘과 화면이 같은 말을 한다.

⚠ **배경 여백을 두지 말 것.** 크림 배경 안에 폰을 그린 판(2026-09-09 오전)은 여백이
아이콘 면적의 3분의 1을 먹어서, 스토어 목록 크기(48px)로 줄이면 그림이 너무 작아졌다.
꽉 채우면 두 색이 그대로 목록에서 읽힌다.

⚠ **안드로이드 적응형 아이콘은 가운데 72/108(≈66.7%)만 보인다.** 그래서 안드로이드용
두 레이어는 그만큼 축소해 그린다(`SAFE`). 배경은 어차피 꽉 차므로 상관없지만,
**얼굴이 그 밖으로 나가면 런처 모양에 따라 잘린다.**

⚠ RGBA 로 저장한다 — Play Console 이 앱 아이콘을 32비트 PNG(알파 포함)로 요구한다.
그림 자체는 불투명하고(알파 255) 채널만 갖는다 — 아이폰 홈화면 아이콘은
실제로 투명하면 검게 나오기 때문이다.
"""
from PIL import Image, ImageDraw
import os

INK   = (46, 43, 58)
MINT  = (127, 209, 185)
CORAL = (255, 143, 163)

S = 1024                      # 원본 해상도
OUT = os.path.join(os.path.dirname(__file__), '..', 'web', 'icons')

FACE_R   = 0.25               # 얼굴 반지름 (사각형 아이콘 기준)
FACE_GAP = 0.265              # 가운데선에서 얼굴 중심까지
DIV_W    = 0.030              # 가르는 선 두께

SAFE     = 72 / 108.0         # 적응형 아이콘에서 실제로 보이는 비율
MASKABLE = 0.777              # 웹 maskable 안전지대(반지름 40%)에 맞추는 배율
                              # (FACE_GAP + FACE_R) * 0.777 = 0.40


def _marks(d, cx, cy, r):
    """눈 두 개와 웃는 입."""
    ex, ey, er = r * 0.36, r * 0.16, r * 0.105
    for sx in (-1, 1):
        x = cx + sx * ex
        d.ellipse([x - er, cy - ey - er, x + er, cy - ey + er], fill=INK)
    mw, my = r * 0.30, cy + r * 0.36
    d.arc([cx - mw, my - r * 0.20, cx + mw, my + r * 0.22],
          start=15, end=165, fill=INK, width=int(r * 0.13))


def compose(scale=1.0, bg=True, faces=True, divider=True):
    """scale = 그림 요소를 줄이는 배율(배경은 언제나 꽉 찬다).
    bg/faces/divider 를 꺼서 안드로이드 적응형의 두 레이어를 따로 뽑는다."""
    img = Image.new('RGBA', (S, S), (MINT + (255,)) if bg else (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if bg:
        d.rectangle([0, S * 0.5, S, S], fill=CORAL + (255,))
    if divider:
        w = S * DIV_W * scale
        d.rectangle([0, S * 0.5 - w / 2, S, S * 0.5 + w / 2], fill=INK + (255,))
    if faces:
        r, gap = S * FACE_R * scale, S * FACE_GAP * scale
        t = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        _marks(ImageDraw.Draw(t), S * 0.5, S * 0.5 - gap, r)      # 위 = 맞은편 사람
        img.alpha_composite(t.rotate(180, center=(S * 0.5, S * 0.5 - gap)))
        _marks(d, S * 0.5, S * 0.5 + gap, r)                      # 아래 = 내 쪽
    return img


def save(img, name, size):
    p = os.path.join(OUT, name)
    img.resize((size, size), Image.LANCZOS).save(p, optimize=True)
    print('생성:', os.path.relpath(p), f'{size}x{size}')


def main():
    os.makedirs(OUT, exist_ok=True)

    # Play 스토어 512, PWA 192/512, 사파리 홈화면 180
    square = compose()
    for size, name in [(512, 'icon-512.png'),
                       (192, 'icon-192.png'),
                       (180, 'apple-touch-icon.png')]:
        save(square, name, size)

    # 웹 maskable — 잘려도 얼굴이 남도록 안전지대 안으로 줄인다
    save(compose(MASKABLE), 'icon-maskable-512.png', 512)

    # 안드로이드 적응형 두 레이어. 배경에 가르는 선을 넣어야 끝까지 이어진다
    # (앞면에 넣으면 보이는 영역 밖에서 끊긴다).
    save(compose(SAFE, faces=False), 'icon-background-432.png', 432)
    save(compose(SAFE, bg=False, divider=False), 'icon-foreground-432.png', 432)


if __name__ == '__main__':
    main()
