"""쿵짝 앱 아이콘 생성.
민트/코랄 캐릭터 둘이 마주 보는 구도. 앱 팔레트를 그대로 쓴다.
python3 tools/make_icons.py 로 실행.
"""
from PIL import Image, ImageDraw
import os

BG    = (242, 241, 248)
INK   = (46, 43, 58)
MINT  = (127, 209, 185)
CORAL = (255, 143, 163)

S = 1024                      # 원본 해상도
OUT = os.path.join(os.path.dirname(__file__), '..', 'web', 'icons')


def draw_face(d, cx, cy, r, color, look):
    """둥근 캐릭터 하나. look 은 눈이 향하는 방향(-1 왼쪽 / +1 오른쪽)."""
    d.ellipse([cx - r, cy - r * 0.93, cx + r, cy + r * 0.93], fill=color)

    ex, ey = r * 0.34, r * 0.13
    er = r * 0.115
    off = look * r * 0.05                      # 서로를 바라보게 눈동자를 살짝 옮긴다
    for sx in (-1, 1):
        x = cx + sx * ex + off
        d.ellipse([x - er, cy - ey - er, x + er, cy - ey + er], fill=INK)

    # 웃는 입
    mw, my = r * 0.30, cy + r * 0.34
    d.arc([cx - mw, my - r * 0.20, cx + mw, my + r * 0.22],
          start=15, end=165, fill=INK, width=int(r * 0.11))


def build(size):
    img = Image.new('RGB', (S, S), BG)
    d = ImageDraw.Draw(img)

    r = S * 0.195
    cy = S * 0.50
    draw_face(d, S * 0.285, cy, r, MINT,  look=+1)   # 왼쪽 캐릭터가 오른쪽을 본다
    draw_face(d, S * 0.715, cy, r, CORAL, look=-1)

    # 두 사람 사이의 경계선 — 화면을 나눠 쓴다는 컨셉
    d.line([(S * 0.5, S * 0.16), (S * 0.5, S * 0.84)],
           fill=(220, 218, 232), width=int(S * 0.018))

    return img.resize((size, size), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    # Play 스토어 512, PWA 192/512, 사파리 홈화면 180
    for size, name in [(512, 'icon-512.png'),
                       (192, 'icon-192.png'),
                       (180, 'apple-touch-icon.png')]:
        p = os.path.join(OUT, name)
        build(size).save(p, optimize=True)
        print('생성:', os.path.relpath(p), f'{size}x{size}')

    # 마스크 대응(안드로이드 적응형 아이콘) — 여백을 더 준 버전
    img = Image.new('RGB', (S, S), BG)
    d = ImageDraw.Draw(img)
    r = S * 0.150
    draw_face(d, S * 0.325, S * 0.5, r, MINT,  look=+1)
    draw_face(d, S * 0.675, S * 0.5, r, CORAL, look=-1)
    p = os.path.join(OUT, 'icon-maskable-512.png')
    img.resize((512, 512), Image.LANCZOS).save(p, optimize=True)
    print('생성:', os.path.relpath(p), '512x512 (maskable)')


if __name__ == '__main__':
    main()
