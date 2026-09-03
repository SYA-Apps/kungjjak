# 릴리스 빌드에서 R8 이 지우면 안 되는 것들.
#
# 왜 필요한가: R8 은 «아무도 안 부르는 코드» 를 지워 앱을 줄인다. 그런데 어떤
# 라이브러리는 클래스를 «이름 문자열» 로 찾아 쓴다(리플렉션). 그 경우 R8 눈에는
# 안 쓰이는 것으로 보여 지워 버리고, 앱은 그 기능을 쓸 때 터진다.
# 🚨 디버그 빌드는 R8 이 안 돌아 멀쩡하다 — 릴리스로 바꾸기 전까지 안 드러난다.
#
# ⚠️ 쿵짝도 R8 이 돈다. `app/build/app/outputs/mapping/release/mapping.txt` 가
#    생기는 것이 증거다. «게임이 웹이니 R8 과 무관하다» 고 생각하면 안 된다 —
#    WebView 를 띄우는 네이티브 껍데기가 R8 사정권에 있다.

# ── Flutter 플러그인 공통 (모든 앱 필수) ──────────────────────────────────
# 플러그인은 GeneratedPluginRegistrant 가 «이름으로» 등록한다.
# 쿵짝의 webview_flutter 도 여기에 걸린다.
-keep class io.flutter.plugins.** { *; }
-keep class io.flutter.plugin.** { *; }
-dontwarn io.flutter.embedding.**

# ── 안 쓰는 것은 넣지 않았다 ──────────────────────────────────────────────
# 광고(google_mobile_ads) · ML Kit · Room/WorkManager · flutter_local_notifications
# 규칙은 쿵짝에 해당 없어 뺐다. 나중에 그런 라이브러리를 붙이면
# C:\SYA\playbook\templates\proguard-rules.pro 에서 그 구간을 가져올 것.
# (학원비서는 androidx.work 규칙이 없어 «켜자마자» 죽은 전례가 있다)
