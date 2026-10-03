# Store listing — English (en-US) · 해외판 초안

미국 · 영국 · 캐나다 · 호주에 처음 열 때 콘솔 「스토어 등록정보 → 번역 추가 → English (United States) – en-US」 에 넣을 글.
한국어판(`docs/스토어-등록정보.md`)과 같은 사실만 적었다. 2026-10-03 초안.

## ⚠ 넣기 전에

- 🚨 **앱 이름은 넣기 직전에 사용자에게 최종 문구를 확인받는다**(공통 규칙). 아래 후보 셋 중에서 고른다
- 🔒 **1.0.1(+3) 검토가 끝난 뒤에** 넣는다 — 검토 중에 등록정보를 바꾸면 검토가 다시 돈다
- 상표명 금지(«like ○○» 도 안 된다) · 과장 금지(«best», «#1») · 영구 약속 금지(«no ads ever» 대신 «currently no ads»)
- 글자 수는 `python tools/check_store_text.py` 와 같은 기준으로 센다(이름 30 · 짧은 설명 80 · 자세한 설명 4000)

---

## App name (30 characters max) — 후보 셋

| | 이름 | 글자 수 | 느낌 |
|---|---|---|---|
| 1 | `Kungjjak - 2 Player Mini Games` | 30 | 검색어 «2 player» · «mini games» 가 둘 다 들어간다(추천) |
| 2 | `Kungjjak - Party Games for Two` | 30 | «party games» 로 찾는 사람에게 |
| 3 | `Kungjjak - Duel Games for Two` | 29 | 마주 앉아 겨루는 느낌 |

> 「Kungjjak」 은 로마자 표기라 영어권 사람은 뜻을 모른다. 그래서 뒤의 설명이 사실상 이름 역할을 한다 —
> 사람들이 실제로 치는 말(«2 player games», «two player games»)을 앞에 둔다.

## Short description (80 characters max)

```
10 mini games for two, played face to face on one phone. No internet needed.
```

## Full description (4000 characters max)

```
All you need is one phone.

Put the phone between you and sit face to face. The screen splits in two, and the top half
is turned around so the person across from you sees it the right way up. Each player just
taps their own side.

The first to reach the target score wins. Choose 5, 10, 15 or 20 points.

Can't decide what to play? Pick "Random" and you'll switch to a different game after every point.


■ 10 mini games

⚡ Flash - Tap first when the light turns yellow
🎨 Color Trap - Pick the ink color, not the word
🔺 Trio - 3 cards, each trait all same or all different
🔍 Spot the Match - Exactly one picture is on both discs
🍒 Exactly Five - Same picture, and the counts add up to 5
🔄 Flip-Flop - Tap only on this round's color
🎯 Odd One Out - One tile is a slightly different shade
💣 Pass the Bomb - Pass it on before it blows
👊 Tap Race - Tap more in 5 seconds
🚩 Dots and Boxes - Draw lines, claim the boxes

Each game is marked Easy, Normal or Hard. Some test your reflexes, others make you think.


■ Nothing else needed

· Works without an internet connection. On a plane, on the subway.
· No account, no sign-in.
· Asks for no permissions at all.
· Currently no ads.
· Nothing to buy inside the app.
· Collects no personal information.

The current version works without the internet permission.


■ Good for

· Waiting for your food across the table
· Standing in line
· Deciding who pays
· Settling a quick contest

A round takes from a few seconds to a few minutes.


■ Good to know

· You need two people. It can't be played alone.
· Hold the phone upright (portrait), not sideways.
· Intended for ages 13 and over.
· The app follows your phone's language (English or Korean). You can switch on the first screen.

Privacy policy: https://sya-apps.github.io/kungjjak/privacy-en.html
Try it in your browser first: https://sya-apps.github.io/kungjjak/
```

## 콘솔 칸

| 칸 | 값 |
|---|---|
| 개인정보처리방침 URL | 앱 하나에 하나뿐이라 **한국어 주소 그대로** 둔다(`…/privacy.html`). 영어 방침은 자세한 설명 끝 링크로 안내한다 |
| 카테고리 · 태그 · 연락처 | 한국어판과 같다(국가마다 따로 없다) |
| 국가 | 대한민국 + **미국 · 영국 · 캐나다 · 호주**(콘솔 「국가/지역」 · ADMIN 과 같이) |

📌 방침 주소를 영어 쪽으로 바꾸지 않는 이유 — 콘솔의 방침 URL 은 언어마다 따로 못 넣는다. 한국어 방침이 심사와 연결돼 있어 그대로 두고,
영어 방침은 그 안 내용과 똑같은 사실이라 링크만 더한다. (원하면 나중에 한 페이지에 두 언어를 합칠 수 있다 — 그건 다음 판에)

## 영어 스크린샷 찍는 법

- 🚫 **아이폰으로 찍지 않는다** — 애플 이모지 그림이 들어간다(저작권). 안드로이드(Noto 이모지)로만
- 앱의 웹뷰는 **폰 언어를 따른다** → 둘 중 하나:
  1. **에뮬레이터**(`reading_log_pixel`)의 시스템 언어를 English (US) 로 두고 앱을 깔아 찍는다 — S8 설정을 안 건드려도 된다(권장)
  2. S8 언어를 잠깐 영어로 바꿨다가 되돌린다(차례표 `s8_lock.py` 로 잡고 · 끝나면 한국어로 꼭 되돌리기)
- 웹으로 미리 볼 때는 `https://sya-apps.github.io/kungjjak/?lang=en` (언어를 강제로 연다)
- 한국어판과 **같은 장면 8장**(메뉴 · 번쩍 · 색깔 함정 · 삼총사 · 같은 그림 찾기 · 폭탄 · 땅따먹기 · 결과)을 같은 크기로 → `store-assets/screenshots-en/`
- 크기 맞추기는 `tools/prep_screenshots.py` 를 그대로 쓴다
