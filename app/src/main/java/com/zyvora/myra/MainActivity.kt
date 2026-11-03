package com.zyvora.myra

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val layout = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER; setPadding(28, 32, 28, 32) }
        layout.addView(TextView(this).apply {
            text = "MYRA COMPANION\n\nCamera Vision: photo scan, live object recognition and spoken results. Screen Control uses Accessibility permission."
            textSize = 18f
        })
        layout.addView(Button(this).apply { text = "OPEN CAMERA VISION"; setOnClickListener { startActivity(Intent(this@MainActivity, CameraActivity::class.java)) } })
        layout.addView(Button(this).apply { text = "ENABLE ACCESSIBILITY"; setOnClickListener { startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) } })
        layout.addView(Button(this).apply { text = "TEST SCROLL DOWN"; setOnClickListener { MyraAccessibilityService.perform("scroll_down") } })
        setContentView(layout)
    }
}
