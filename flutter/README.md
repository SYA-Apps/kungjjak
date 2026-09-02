# Flutter 래핑 절차

게임 본체는 `web/index.html` 하나다. Flutter는 그걸 WebView로 띄우는 껍데기일 뿐이다.
**게임 로직은 절대 Dart로 옮기지 말 것.** 웹과 앱이 같은 파일을 공유해야 관리가 된다.

✅ **2026-09-02 에 이 절차대로 실제로 빌드·설치까지 했다** (Flutter 3.44.6 · Android SDK 36,
갤럭시 S8). 그때 걸린 것들을 각 단계에 적어 두었으니 **그대로 따라가면 된다.**

---

## 1. 프로젝트 생성

```bash
cd ~/작업폴더/kungjjak
flutter create --org com.syaapps --project-name kungjjak --platforms=android app
```

`--org`를 넣으면 `applicationId`가 `com.syaapps.kungjjak`으로 잡힌다.
(기본값 `com.example`은 Play 스토어가 거부한다)

지금은 안드로이드만 만든다. iOS는 사파리 웹으로 먼저 가고, 나중에 필요할 때
`flutter create --platforms=ios .`로 추가하면 된다.

⚠ **만들자마자 `test/widget_test.dart` 를 지운다.** `flutter create` 가 넣어 주는 이 파일은
사라질 카운터 앱(`MyApp`)을 참조해서, main.dart 를 갈아끼우면 `flutter analyze` 가
에러를 뱉는다. 우리 앱에는 위젯 테스트가 필요 없다.

```bash
rm -rf app/test
```

---

## 2. 게임 파일 넣기

```bash
mkdir -p app/assets
cp -r web app/assets/web
```

결과: `app/assets/web/index.html`, `app/assets/web/icons/...`

⚠ `web/`을 수정하면 **매번 다시 복사**해야 한다.
자주 할 거면 심볼릭 링크로 걸어도 된다: `ln -s ../../web app/assets/web`

---

## 3. main.dart 교체

```bash
cp flutter/main.dart app/lib/main.dart
```

---

## 3-2. 앱 아이콘 (빠뜨리기 쉽다)

⚠ **안 하면 홈 화면에 Flutter 기본 파란 새가 뜬다.** `flutter create` 가 넣어 둔
`ic_launcher.png` 를 밀도별로 덮어써야 한다.

```bash
python - <<'EOF'
from PIL import Image
src = Image.open('web/icons/icon-512.png').convert('RGBA')
for d, s in {'mdpi':48,'hdpi':72,'xhdpi':96,'xxhdpi':144,'xxxhdpi':192}.items():
    src.resize((s, s), Image.LANCZOS).save(
        f'app/android/app/src/main/res/mipmap-{d}/ic_launcher.png')
EOF
```

---

## 4. pubspec.yaml 수정

`app/pubspec.yaml`에서 두 군데:

```yaml
dependencies:
  flutter:
    sdk: flutter
  webview_flutter: ^4.10.0      # ← 추가

flutter:
  uses-material-design: true
  assets:                        # ← 추가
    - assets/web/
    - assets/web/icons/
```

```bash
cd app && flutter pub get
```

---

## 5. 안드로이드 설정

### 앱 이름
`app/android/app/src/main/AndroidManifest.xml`

```xml
<application android:label="쿵짝" ... >
```

### 화면 꺼짐 방지 (중요)
대결 도중 화면이 꺼지면 안 된다.
`app/android/app/src/main/kotlin/.../MainActivity.kt`

```kotlin
import android.os.Bundle
import android.view.WindowManager
import io.flutter.embedding.android.FlutterActivity

class MainActivity : FlutterActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
    }
}
```

### target API — **손댈 것 없다**
Flutter 3.44 의 기본값이 이미 `compileSdk 36 · targetSdk 36 · minSdk 24` 다.
`build.gradle.kts` 는 `flutter.targetSdkVersion` 을 그대로 쓰므로 건드리지 않는다.
(예전 이 문서에 `minSdk 23` 이라고 적혀 있었는데, 굳이 낮출 이유가 없다 —
안드로이드 6 은 점유율이 미미하고 낮출수록 플러그인 호환 문제만 생긴다.)

### 인터넷 권한 — **이미 없다**
Flutter 는 `INTERNET` 을 `src/debug` 와 `src/profile` 매니페스트에만 넣는다.
**릴리스 빌드에는 처음부터 안 들어간다.** 지울 것이 없다.

설치 후 실제로 확인하는 법:

```bash
adb shell dumpsys package com.syaapps.kungjjak | grep -A4 "requested permissions"
```

Flutter 내부용 `DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION` 하나만 나오면 맞다.

### 🎨 머티리얼 기본 보라 — 실제로 당했다

`ThemeData()` 를 비워 두면 **머티리얼 3 의 기본 시드색(보라)** 이 Flutter 위젯에 나온다.
게임 화면은 WebView 라 안 물들지만 그 위에 뜨는 **종료 확인 창 버튼이 보라색**이 됐다.

`main.dart` 에서 테마를 민트 시드로 잡고, M3 가 흰 배경에 시드색을 얇게 덧입히는 것도
`surfaceTintColor: Colors.transparent` 로 껐다. 이미 반영돼 있으니 그대로 쓰면 된다.

---

## 6. 실행과 빌드

```bash
flutter analyze                     # 먼저 돌린다. 에러 0 이어야 한다
flutter build apk --release         # 실기기 확인용 → build/app/outputs/flutter-apk/app-release.apk
flutter build appbundle --release   # 스토어 제출용 → build/app/outputs/bundle/release/app-release.aab
```

설치는 `adb install -r <apk 경로>`.

📌 APK 가 **42MB** 로 나오는데 놀라지 말 것 — 모든 CPU 아키텍처가 다 든 범용 APK 다.
**스토어에 올리는 AAB 는 Play 가 기기별로 쪼개 주므로 훨씬 작게 내려간다.**

⚠ `web/` 을 고쳤으면 **2번(파일 복사)을 다시 하고** 빌드해야 한다. 안 하면 옛 게임이 나간다.

---

## 7. 서명 키 — **가장 되돌릴 수 없는 단계**

🔑 **이 키를 잃어버리면 앱을 영영 업데이트할 수 없다.** 새 키로 서명하면 Play 가
같은 앱으로 인정하지 않아, 사용자를 두고 새 앱으로 다시 시작해야 한다.
**만들기 전에 어디에 백업할지부터 정한다.**

백업 위치로 **원드라이브는 피한다** — 동기화 충돌이나 계정 사고로 같이 날아간다.
USB 메모리나 종이에 적어 둔 복원 정보처럼 **PC 와 운명이 갈리는 곳**이 좋다.

### 7-1. 키 만들기 (사람이 직접 — 비밀번호를 물어본다)

```bash
keytool -genkey -v -keystore "$USERPROFILE/kungjjak-upload.jks"   -storetype JKS -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```

비밀번호 두 번(키스토어·키)과 이름·조직을 물어본다.
**조직 정보에 개인 메일·본명을 넣지 않는다** — 서명서에 남는다. `SYA` 로 통일한다.

### 7-2. `app/android/key.properties` 만들기

```properties
storePassword=위에서_정한_비밀번호
keyPassword=위에서_정한_비밀번호
keyAlias=upload
storeFile=C:/Users/<사용자>/kungjjak-upload.jks
```

⚠ **이 파일은 절대 커밋하지 않는다.** `app/` 전체가 `.gitignore` 에 들어 있어 지금은
안전하지만, 나중에 `app/` 을 커밋하게 되면 `key.properties` 와 `*.jks` 를 따로 막을 것.

### 7-3. `app/android/app/build.gradle.kts` 에서 참조

```kotlin
import java.util.Properties
import java.io.FileInputStream

val keystoreProperties = Properties()
val keystorePropertiesFile = rootProject.file("key.properties")
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(FileInputStream(keystorePropertiesFile))
}

android {
    signingConfigs {
        create("release") {
            keyAlias = keystoreProperties["keyAlias"] as String
            keyPassword = keystoreProperties["keyPassword"] as String
            storeFile = file(keystoreProperties["storeFile"] as String)
            storePassword = keystoreProperties["storePassword"] as String
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")   // ← debug 에서 바꾼다
        }
    }
}
```

기본 상태는 `signingConfig = signingConfigs.getByName("debug")` 다. **이대로 빌드한 AAB 는
Play Console 이 거부한다.**

### 7-4. 서명이 바뀌었는지 확인

```bash
keytool -printcert -jarfile build/app/outputs/bundle/release/app-release.aab
```

소유자가 `CN=Android Debug` 가 아니라 7-1 에서 넣은 이름으로 나와야 한다.

---

## 확인할 것

`web/` 자체의 확인 항목은 `docs/출시체크리스트.md` 0번에 있다. 여기는 **앱에만 있는 것**만.

- [x] 앱이 오프라인에서 도는지 — **구조적으로 보장된다.** `file:///android_asset/` 에서
      로드되고 INTERNET 권한이 아예 없다. 글꼴도 HTML 안에 base64 로 박혀 있다
- [x] 뒤로가기: 게임 중 → 메뉴 ✅ / 메뉴 → 종료 확인 창 ✅ (2026-09-02 S8)
- [x] 앱 아이콘이 쿵짝 아이콘인지 (Flutter 기본 새가 아닌지)
- [x] 종료 확인 창 색이 팔레트인지 (머티리얼 보라가 아닌지)
- [ ] 화면이 꺼지지 않는지 — 코드는 넣었으나 **사람이 몇 분 두고 봐야 확인된다**
- [ ] 소리가 나는지 (WebView는 사용자 조작 후에만 오디오 허용)
- [ ] 세로 고정이 되는지 (폰을 눕혀 볼 것)
- [ ] **낡은 웹뷰**에서 깨지지 않는지 — 크롬이 웹뷰를 대신하고 있으면 위험이 안 드러난다.
      `adb shell cmd webviewupdate set-webview-implementation com.google.android.webview`
      로 바꿔 한 번 볼 것 (확인 뒤 `com.android.chrome` 으로 되돌린다)
