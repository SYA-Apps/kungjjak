// 쿵짝 — Flutter WebView 래퍼
// 게임 본체는 assets/web/index.html 하나. Flutter는 껍데기 역할만 한다.
//
// 이 파일을 flutter 프로젝트의 lib/main.dart 로 덮어쓸 것.
// 자세한 절차는 flutter/README.md 참고.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:webview_flutter/webview_flutter.dart';

// web/index.html 의 :root 변수와 같은 값을 쓴다. 한쪽만 바꾸면 색이 어긋난다.
const kBg   = Color(0xFFF2F1F8); // --bg   앱 배경색
const kInk  = Color(0xFF2E2B3A); // --ink  글자
const kMint = Color(0xFF7FD1B9); // --a    쿵

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
  runApp(const KungjjakApp());
}

class KungjjakApp extends StatelessWidget {
  const KungjjakApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '쿵짝',
      debugShowCheckedModeBanner: false,
      // ⚠ ThemeData() 를 그냥 두면 머티리얼 기본 '보라'가 대화상자 버튼에 나온다.
      // 게임 화면은 WebView 라 안 물들지만 Flutter 위젯(대화상자)은 물든다.
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: kBg,
        colorScheme: ColorScheme.fromSeed(
          seedColor: kMint,
          surface: Colors.white,
          onSurface: kInk,
        ),
      ),
      home: const GameView(),
    );
  }
}

class GameView extends StatefulWidget {
  const GameView({super.key});

  @override
  State<GameView> createState() => _GameViewState();
}

class _GameViewState extends State<GameView> {
  late final WebViewController _web;

  @override
  void initState() {
    super.initState();
    _web = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(kBg)
      ..loadFlutterAsset('assets/web/index.html');
  }

  /// 메뉴 화면에 있는지 확인. 뒤로가기 동작을 결정하는 데 쓴다.
  Future<bool> _isAtMenu() async {
    try {
      final r = await _web.runJavaScriptReturningResult(
        "document.getElementById('menu').classList.contains('on')",
      );
      return r.toString().contains('true');
    } catch (_) {
      return true;
    }
  }

  Future<bool> _askExit() async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        backgroundColor: Colors.white,
        // M3 는 흰 배경 위에 seed 색 틴트를 얇게 덧입힌다 — 흰색을 흰색으로 두려면 꺼야 한다.
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22)),
        title: const Text(
          '쿵짝을 끝낼까요?',
          style: TextStyle(color: kInk, fontSize: 20, fontWeight: FontWeight.w700),
        ),
        actionsPadding: const EdgeInsets.fromLTRB(14, 4, 14, 14),
        actions: [
          // '계속하기' 가 기본 행동이라 진하게 둔다. 실수로 끝내는 쪽이 손해가 크다.
          TextButton(
            onPressed: () => Navigator.pop(c, false),
            style: TextButton.styleFrom(foregroundColor: kInk),
            child: const Text('계속하기',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
          ),
          // 보조 글자는 먹색 55% — web 의 .hint(opacity:.5) 와 같은 결.
          TextButton(
            onPressed: () => Navigator.pop(c, true),
            style: TextButton.styleFrom(
                foregroundColor: kInk.withValues(alpha: 0.55)),
            child: const Text('끝내기', style: TextStyle(fontSize: 16)),
          ),
        ],
      ),
    );
    return ok ?? false;
  }

  @override
  Widget build(BuildContext context) {
    // Flutter 버전에 따라 onPopInvokedWithResult / onPopInvoked 로 이름이 다르다.
    // 컴파일 에러가 나면 아래 콜백 이름을 바꿀 것.
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) async {
        if (didPop) return;
        if (await _isAtMenu()) {
          if (await _askExit()) SystemNavigator.pop();
        } else {
          // 게임 중이면 메뉴로 돌아간다 (셸의 '게임 고르기' 버튼을 누른 것과 같다)
          await _web.runJavaScript("document.getElementById('toMenu').click()");
        }
      },
      child: Scaffold(
        backgroundColor: kBg,
        body: SafeArea(child: WebViewWidget(controller: _web)),
      ),
    );
  }
}
