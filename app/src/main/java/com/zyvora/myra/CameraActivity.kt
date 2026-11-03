package com.zyvora.myra

import android.Manifest
import android.app.Activity
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import com.google.mlkit.vision.label.ImageLabeling
import com.google.mlkit.vision.label.defaults.ImageLabelerOptions
import java.io.File
import java.util.Locale
import java.util.concurrent.Executors

class CameraActivity : Activity(), TextToSpeech.OnInitListener {
    private lateinit var previewView: PreviewView
    private lateinit var status: TextView
    private lateinit var tts: TextToSpeech
    private var imageCapture: ImageCapture? = null
    private var liveMode = false
    private var lastSpoken = ""
    private var lastAnalysisAt = 0L
    private val cameraExecutor = Executors.newSingleThreadExecutor()
    private val recognizer by lazy { TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS) }
    private val labeler by lazy { ImageLabeling.getClient(ImageLabelerOptions.DEFAULT_OPTIONS) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        tts = TextToSpeech(this, this)
        buildUi()
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) startCamera()
        else ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.CAMERA), 41)
    }

    private fun buildUi() {
        val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(16, 24, 16, 16); setBackgroundColor(0xFF10131B.toInt()) }
        root.addView(TextView(this).apply { text = "MYRA CAMERA VISION"; textSize = 22f; setTextColor(0xFF69E6FF.toInt()); gravity = Gravity.CENTER; setPadding(0, 8, 0, 16) })
        previewView = PreviewView(this).apply { layoutParams = LinearLayout.LayoutParams(-1, 0, 1f) }
        status = TextView(this).apply { text = "Camera permission ka intezar..."; textSize = 16f; setTextColor(0xFFFFFFFF.toInt()); setPadding(8, 14, 8, 14) }
        root.addView(previewView)
        root.addView(ScrollView(this).apply { addView(status) }, LinearLayout.LayoutParams(-1, 130))
        root.addView(Button(this).apply { text = "TAKE PHOTO + READ / DESCRIBE"; setOnClickListener { captureAndAnalyze() } })
        root.addView(Button(this).apply { text = "START LIVE VISION"; setOnClickListener { liveMode = !liveMode; text = if (liveMode) "STOP LIVE VISION" else "START LIVE VISION"; status.text = if (liveMode) "Live vision on. Main objects identify kar rahi hoon." else "Live vision paused."; if (!liveMode) speak("Live vision paused.") } })
        setContentView(root)
    }

    override fun onInit(result: Int) { if (result == TextToSpeech.SUCCESS) tts.language = Locale.getDefault() }

    private fun startCamera() {
        val future = ProcessCameraProvider.getInstance(this)
        future.addListener({
            val provider = future.get()
            val preview = Preview.Builder().build().also { it.setSurfaceProvider(previewView.surfaceProvider) }
            imageCapture = ImageCapture.Builder().build()
            val analysis = ImageAnalysis.Builder().setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST).build()
            analysis.setAnalyzer(cameraExecutor) { proxy -> analyzeLiveFrame(proxy) }
            try {
                provider.unbindAll()
                provider.bindToLifecycle(this, CameraSelector.DEFAULT_BACK_CAMERA, preview, imageCapture, analysis)
                status.text = "Camera ready. Photo lo ya Live Vision start karo."
            } catch (e: Exception) { status.text = "Camera start nahi hua: ${e.localizedMessage}" }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun captureAndAnalyze() {
        val capture = imageCapture ?: run { status.text = "Camera abhi ready nahi hai."; return }
        val file = File(cacheDir, "myra-camera-${System.currentTimeMillis()}.jpg")
        capture.takePicture(ImageCapture.OutputFileOptions.Builder(file).build(), ContextCompat.getMainExecutor(this), object : ImageCapture.OnImageSavedCallback {
            override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                status.text = "Photo captured. Object aur text scan ho raha hai..."
                val image = try { InputImage.fromFilePath(this@CameraActivity, android.net.Uri.fromFile(file)) } catch (e: Exception) { status.text = "Photo read nahi hui."; return }
                analyzeStill(image)
            }
            override fun onError(exception: ImageCaptureException) { status.text = "Photo capture failed: ${exception.message}" }
        })
    }

    private fun analyzeStill(image: InputImage) {
        var labelsDone = false
        var textDone = false
        var labelsText = "Objects: none recognized"
        var ocrText = "Text: nothing readable"
        fun finish() {
            if (labelsDone && textDone) {
                val result = "$labelsText. $ocrText"
                status.text = result
                speak(result)
            }
        }
        labeler.process(image).addOnSuccessListener { labels ->
            labelsText = if (labels.isEmpty()) "Objects: none recognized" else "Objects: " + labels.take(6).joinToString(", ") { "${it.text} (${(it.confidence * 100).toInt()}%)" }
        }.addOnFailureListener { labelsText = "Object scan unavailable" }.addOnCompleteListener { labelsDone = true; finish() }
        recognizer.process(image).addOnSuccessListener { result ->
            if (result.text.isNotBlank()) ocrText = "Readable text: " + result.text.take(1200)
        }.addOnFailureListener { ocrText = "Text scan unavailable" }.addOnCompleteListener { textDone = true; finish() }
    }

    private fun analyzeLiveFrame(proxy: ImageProxy) {
        if (!liveMode || System.currentTimeMillis() - lastAnalysisAt < 1800) { proxy.close(); return }
        lastAnalysisAt = System.currentTimeMillis()
        val media = proxy.image
        if (media == null) { proxy.close(); return }
        val image = InputImage.fromMediaImage(media, proxy.imageInfo.rotationDegrees)
        labeler.process(image).addOnSuccessListener { labels ->
            if (!liveMode) return@addOnSuccessListener
            val description = labels.take(4).joinToString(", ") { it.text }
            if (description.isNotBlank() && description != lastSpoken) {
                lastSpoken = description
                runOnUiThread { status.text = "Live objects: $description"; speak("I can see $description") }
            }
        }.addOnFailureListener { runOnUiThread { status.text = "Live analysis error. Try again." } }.addOnCompleteListener { proxy.close() }
    }

    private fun speak(message: String) { if (::tts.isInitialized) tts.speak(message.take(1200), TextToSpeech.QUEUE_FLUSH, null, "myra-vision") }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 41 && grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED) startCamera()
        else status.text = "Camera permission required. Android Settings se allow karo."
    }

    override fun onDestroy() {
        super.onDestroy()
        cameraExecutor.shutdown()
        if (::tts.isInitialized) tts.shutdown()
        if (::recognizer.isInitialized) recognizer.close()
        if (::labeler.isInitialized) labeler.close()
    }
}
