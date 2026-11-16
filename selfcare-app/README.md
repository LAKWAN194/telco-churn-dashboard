# selfcare-app

A Jetpack Compose self-care app for subscribers: balance, bundles, an offer inbox,
and an offline cache. The skeleton builds and shows a placeholder home screen; the
real screens are designed in `docs/retention-loop/design/selfcare-app.md` (week 4).

Open this folder in Android Studio, or from a terminal with the Android SDK set up
(`ANDROID_HOME`, SDK platform 37) and JDK 17 or later:

```bash
./gradlew assembleDebug testDebugUnitTest lintDebug   # build, unit tests, lint
./gradlew connectedDebugAndroidTest                   # Compose UI tests, on a device or emulator
```

| | |
| --- | --- |
| Android Gradle Plugin | 9.4.1 (compiles Kotlin itself) |
| Kotlin and Compose compiler | 2.4.20 |
| Compose BOM | 2026.09.00 |
| Min / target / compile SDK | 26 / 36 / 37 |

Lint currently reports 5 expected warnings: no app icon yet, `targetSdk` below the newest
API (your choice in ADR-015), the backup policy (`allowBackup` versus
`dataExtractionRules`, a decision for an app holding personal data), and two newer tool
versions (pinned versions are at least two weeks old on purpose).
