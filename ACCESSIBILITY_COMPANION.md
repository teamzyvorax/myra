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


## Open any Android app by voice

The companion now checks launchable installed apps by their visible app name. If it cannot find a matching installed app, it opens Google Play Store search for that name (or the Play Store web search if the Play Store app is unavailable).

Examples:
- `open app Instagram`
- `open app WhatsApp`
- `open app Spotify`
- `ऐप खोलो Snapchat`

The Android manifest queries launchable activities only; it does not request unrestricted access to every installed package. The Play Store opens a search result page; MYRA does not silently install apps. You choose the app and tap Install yourself.
