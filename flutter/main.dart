// 쿵짝 — Flutter WebView 래퍼
// 게임 본체는 assets/web/index.html 하나. Flutter는 껍데기 역할만 한다.
//
// 이 파일을 flutter 프로젝트의 lib/main.dart 로 덮어쓸 것.
// 자세한 절차는 flutter/README.md 참고.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:webview_flutter/webview_flutter.dart';

const kBg = Color(0xFFF2F1F8); // 앱 배경색. web/index.html 의 --bg 와 같아야 한다

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
      theme: ThemeData(scaffoldBackgroundColor: kBg),
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
        title: const Text('쿵짝을 끝낼까요?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(c, false),
            child: const Text('계속하기'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(c, true),
            child: const Text('끝내기'),
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
