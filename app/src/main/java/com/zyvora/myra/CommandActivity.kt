package com.zyvora.myra

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.Toast

class CommandActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val command = intent.getStringExtra("command").orEmpty()
        val text = intent.getStringExtra("text").orEmpty()
        val allowed = setOf("scroll_up", "scroll_down", "back", "like", "open_comments", "lock_screen", "type_comment", "open_app", "camera")
        when {
            command !in allowed -> Toast.makeText(this, "Command not allowed", Toast.LENGTH_SHORT).show()
            command == "camera" -> startActivity(Intent(this, CameraActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
            command == "open_app" -> openInstalledAppOrStore(text)
            command == "type_comment" -> {
                Toast.makeText(this, "Text entered only in a focused field. Review and post manually.", Toast.LENGTH_LONG).show()
                MyraAccessibilityService.typeIntoFocusedField(text.take(500))
            }
            else -> MyraAccessibilityService.perform(command)
        }
        finish()
    }

    private fun openInstalledAppOrStore(rawName: String) {
        val name = rawName.trim().take(80)
        if (name.isBlank()) return
        val launcher = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
        val matches = packageManager.queryIntentActivities(launcher, 0)
        val wanted = name.lowercase()
        val match = matches.firstOrNull { it.loadLabel(packageManager).toString().trim().lowercase() == wanted }
            ?: matches.firstOrNull {
                val label = it.loadLabel(packageManager).toString().trim().lowercase()
                label.contains(wanted) || wanted.contains(label)
            }
        if (match != null) {
            val launch = packageManager.getLaunchIntentForPackage(match.activityInfo.packageName)
            if (launch != null) { launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK); startActivity(launch); return }
        }
        val market = Intent(Intent.ACTION_VIEW, Uri.parse("market://search?q=" + Uri.encode(name)))
        try { startActivity(market) } catch (_: Exception) {
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://play.google.com/store/search?q=" + Uri.encode(name) + "&c=apps")))
        }
    }
}
