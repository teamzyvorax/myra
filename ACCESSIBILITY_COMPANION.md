# MYRA Accessibility Companion

Android companion app source for MYRA Termux. It uses Android AccessibilityService only after the device owner explicitly enables this service in Android Settings.

## Supported commands
- Scroll up / down (scrollable view first, gesture fallback)
- Back
- Like (best-effort visible YouTube accessibility label)
- Open comments (best-effort visible YouTube accessibility label)
- Type comment into an already focused field (does not submit)
- Lock screen (Android 9+; cannot unlock the device)

YouTube interface labels vary by app version, language and device. Like/comments may not be discoverable on every screen. The app does not bypass sign-in, age gates, DRM, screen locks, or YouTube restrictions. It never posts a comment automatically.

## Build
Open this repository in Android Studio, sync Gradle, then choose Build > Build APK(s). Java 17 and Android SDK Platform 35 are required. This repository contains source files, not a prebuilt APK.

## Enable
Install the debug APK, open MYRA Companion, tap ENABLE ACCESSIBILITY, then explicitly enable MYRA Screen Control in Android Accessibility settings.

## Termux bridge (after install)
Launch a command with:
am start -n com.zyvora.myra/.CommandActivity --es command scroll_down

For comment text:
am start -n com.zyvora.myra/.CommandActivity --es command type_comment --es text "Your comment"

Review and manually post comments in YouTube. Accessibility access is powerful. Enable it only if you trust this app, and disable it in Android Settings when not needed.
