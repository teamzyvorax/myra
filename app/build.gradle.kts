plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "com.zyvora.myra"
    compileSdk = 35
    defaultConfig {
        applicationId = "com.zyvora.myra"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
    }
}
