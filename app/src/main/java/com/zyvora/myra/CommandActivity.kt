package com.zyvora.myra

import android.app.Activity
import android.os.Bundle
import android.widget.Toast

class CommandActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val command = intent.getStringExtra("command").orEmpty()
        val text = intent.getStringExtra("text").orEmpty()
        val allowed = setOf("scroll_up", "scroll_down", "back", "like", "open_comments", "lock_screen", "type_comment")
        if (command !in allowed) {
            Toast.makeText(this, "Command not allowed", Toast.LENGTH_SHORT).show()
        } else if (command == "type_comment") {
            Toast.makeText(this, "Text is entered only into a focused comment field. Review and post manually.", Toast.LENGTH_LONG).show()
            MyraAccessibilityService.typeIntoFocusedField(text.take(500))
        } else {
            MyraAccessibilityService.perform(command)
        }
        finish()
    }
}
