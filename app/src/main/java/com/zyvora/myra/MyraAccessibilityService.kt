package com.zyvora.myra

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.graphics.Path
import android.os.Build
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.widget.Toast

class MyraAccessibilityService : AccessibilityService() {
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {}
    override fun onInterrupt() {}
    override fun onServiceConnected() { instance = this }

    private fun findText(root: AccessibilityNodeInfo?, labels: List<String>): AccessibilityNodeInfo? {
        if (root == null) return null
        for (label in labels) {
            val hits = root.findAccessibilityNodeInfosByText(label)
            hits.firstOrNull { it.isVisibleToUser && it.isEnabled }?.let { return it }
        }
        return null
    }

    private fun clickNode(node: AccessibilityNodeInfo?): Boolean {
        var current = node
        while (current != null) {
            if (current.isClickable && current.isEnabled) return current.performAction(AccessibilityNodeInfo.ACTION_CLICK)
            current = current.parent
        }
        return false
    }

    private fun scroll(down: Boolean) {
        val root = rootInActiveWindow ?: return
        val candidates = mutableListOf<AccessibilityNodeInfo>()
        fun walk(node: AccessibilityNodeInfo?) {
            if (node == null) return
            if (node.isScrollable) candidates.add(node)
            for (i in 0 until node.childCount) walk(node.getChild(i))
        }
        walk(root)
        val target = candidates.firstOrNull()
        if (target != null) target.performAction(if (down) AccessibilityNodeInfo.ACTION_SCROLL_FORWARD else AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD)
        else {
            val path = Path().apply {
                val x = resources.displayMetrics.widthPixels / 2f
                val y1 = resources.displayMetrics.heightPixels * if (down) .78f else .25f
                val y2 = resources.displayMetrics.heightPixels * if (down) .25f else .78f
                moveTo(x, y1); lineTo(x, y2)
            }
            val gesture = GestureDescription.Builder().addStroke(GestureDescription.StrokeDescription(path, 0, 350)).build()
            dispatchGesture(gesture, null, null)
        }
    }

    private fun run(command: String) {
        when (command) {
            "scroll_down" -> scroll(true)
            "scroll_up" -> scroll(false)
            "back" -> performGlobalAction(GLOBAL_ACTION_BACK)
            "lock_screen" -> {
                if (Build.VERSION.SDK_INT >= 28) performGlobalAction(GLOBAL_ACTION_LOCK_SCREEN)
                else Toast.makeText(this, "Screen lock needs Android 9 or newer", Toast.LENGTH_SHORT).show()
            }
            "like" -> {
                val node = findText(rootInActiveWindow, listOf("Like", "like", "पसंद"))
                if (!clickNode(node)) Toast.makeText(this, "Like button not found. Open a video first.", Toast.LENGTH_SHORT).show()
            }
            "open_comments" -> {
                val node = findText(rootInActiveWindow, listOf("Comments", "comments", "टिप्पणियाँ", "कमेन्ट"))
                if (!clickNode(node)) Toast.makeText(this, "Comments control not found on this screen.", Toast.LENGTH_SHORT).show()
            }
        }
    }

    companion object {
        @Volatile private var instance: MyraAccessibilityService? = null
        fun perform(command: String) { instance?.run(command) }
        fun typeIntoFocusedField(value: String) {
            val service = instance ?: return
            val node = service.rootInActiveWindow?.findFocus(AccessibilityNodeInfo.FOCUS_INPUT) ?: return
            val args = Bundle().apply { putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, value) }
            node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
        }
    }
}
