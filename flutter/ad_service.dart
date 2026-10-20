import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

/// 배너 광고 1곳(게임 화면 아래). 안드로이드 앱에서만 켠다 — 게임 본체는 웹뷰라 웹판에는 광고가 없다.
///
/// 진짜 광고 단위 ID 는 ADMIN 이 소담 AdMob 에 만들어 전달한다. 받기 전까지는 테스트 ID 만 쓴다.
/// 개발·시험은 늘 테스트 ID — 진짜 광고를 내 손으로 누르면 계정이 정지된다.
class AdService {
  static const bool adsEnabled = true;

  static const _testBannerId = 'ca-app-pub-3940256099942544/9214589741';
  // TODO(ADMIN): 진짜 배너 단위 ID 를 받으면 여기에 넣는다. 그전에는 제출하지 않는다.
  static const _releaseBannerId = _testBannerId;

  static bool get supported =>
      adsEnabled && !kIsWeb && defaultTargetPlatform == TargetPlatform.android;

  static String get bannerUnitId =>
      kReleaseMode ? _releaseBannerId : _testBannerId;

  static bool _initialized = false;
  static final Completer<void> _ready = Completer<void>();
  static Future<void> get ready => _ready.future;

  /// 동의(UMP) → 초기화. 실패해도 앱은 그냥 뜬다(광고만 안 나온다).
  static Future<void> init() async {
    if (!supported || _initialized) return;
    _initialized = true;
    try {
      final done = Completer<void>();
      ConsentInformation.instance.requestConsentInfoUpdate(
        ConsentRequestParameters(),
        () {
          ConsentForm.loadAndShowConsentFormIfRequired((err) {
            if (err != null) debugPrint('동의 폼 오류: ${err.message}');
            if (!done.isCompleted) done.complete();
          });
        },
        (err) {
          debugPrint('동의 정보 갱신 실패: ${err.message}');
          if (!done.isCompleted) done.complete();
        },
      );
      await done.future.timeout(const Duration(seconds: 8), onTimeout: () {});
    } catch (e) {
      debugPrint('동의 절차 건너뜀: $e');
    }
    try {
      await MobileAds.instance.initialize();
    } catch (e) {
      debugPrint('광고 초기화 실패: $e');
    }
    if (!_ready.isCompleted) _ready.complete();
  }
}
