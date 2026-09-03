import java.util.Properties

plugins {
    id("com.android.application")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

// ── 릴리스 서명 키 ────────────────────────────────────────────────────────
// 스토어에 올리는 빌드는 «업로드 키» 로 서명해야 한다. 비밀번호를 git 에 올릴 수
// 없으므로 android/key.properties 라는 별도 파일에서 읽는다(.gitignore 가 막아 둔다).
// key.properties 가 없으면 디버그 키로 서명한다 — 키를 안 만든 PC 에서도
// `flutter run --release` 가 그냥 돌게 하려는 것이다. 없다고 빌드가 깨지지 않는다.
val keystoreProperties = Properties()
val keystorePropertiesFile = rootProject.file("key.properties")
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(keystorePropertiesFile.inputStream())
}

android {
    namespace = "com.syaapps.kungjjak"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    defaultConfig {
        // TODO: Specify your own unique Application ID (https://developer.android.com/studio/build/application-id.html).
        applicationId = "com.syaapps.kungjjak"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = flutter.minSdkVersion
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    signingConfigs {
        create("release") {
            if (keystorePropertiesFile.exists()) {
                keyAlias = keystoreProperties["keyAlias"] as String
                keyPassword = keystoreProperties["keyPassword"] as String
                storeFile = keystoreProperties["storeFile"]?.let { file(it) }
                storePassword = keystoreProperties["storePassword"] as String
            }
        }
    }

    buildTypes {
        release {
            // key.properties 가 있으면 업로드 키로, 없으면 디버그 키로.
            // 🚨 디버그 키로 만든 AAB 는 Play Console 이 거부한다.
            //    «빌드가 성공했다» 와 «제출할 수 있다» 는 다르다.
            // ⚠️ 디버그→업로드 키로 처음 바꾸면 서명이 달라져, 폰에 깔린 기존
            //    릴리스 위에 덮어 설치가 안 된다. 먼저 지우고 새로 깔아야 한다.
            signingConfig = if (keystorePropertiesFile.exists()) {
                signingConfigs.getByName("release")
            } else {
                signingConfigs.getByName("debug")
            }

            // R8 이 리플렉션으로 찾는 클래스를 지워 릴리스에서만 터지는 일이 있다.
            // 지우면 안 되는 것은 proguard-rules.pro 에 적었다.
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}
