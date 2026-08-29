# Flutter 래핑 절차

게임 본체는 `web/index.html` 하나다. Flutter는 그걸 WebView로 띄우는 껍데기일 뿐이다.
**게임 로직은 절대 Dart로 옮기지 말 것.** 웹과 앱이 같은 파일을 공유해야 관리가 된다.

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

### target API
`app/android/app/build.gradle.kts` (또는 `.gradle`)

```
targetSdk = 36
minSdk = 23
```

2026년 8월 기준 신규 앱은 target API 36이 필요하다.

### 인터넷 권한
**필요 없다.** 게임은 완전 오프라인이다.
`AndroidManifest.xml`에 `INTERNET` 권한이 있으면 지우는 게 낫다.
(권한이 적을수록 심사와 데이터 안전 신고가 간단해진다)

---

## 6. 실행과 빌드

```bash
flutter run                      # 실기기 연결 후 (갤럭시 A23)
flutter build appbundle --release   # → build/app/outputs/bundle/release/app-release.aab
```

---

## 7. 서명 키

```bash
keytool -genkey -v -keystore ~/kungjjak-upload.jks \
  -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```

`app/android/key.properties` 생성 후 `build.gradle`에서 참조.

⚠ **이 키를 잃어버리면 앱을 영영 업데이트할 수 없다.**
`.gitignore`가 커밋을 막아두었으니, 원드라이브가 아닌 별도의 안전한 곳에 백업할 것.

---

## 확인할 것

- [ ] 앱이 오프라인(기내모드)에서 정상 실행되는지 — 글꼴 CDN 때문에 깨질 수 있다
- [ ] 뒤로가기: 게임 중 → 메뉴, 메뉴 → 종료 확인 창
- [ ] 화면이 꺼지지 않는지
- [ ] 소리가 나는지 (WebView는 사용자 조작 후에만 오디오 허용)
- [ ] 세로 고정이 되는지
