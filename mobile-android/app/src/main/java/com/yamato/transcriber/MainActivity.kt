package com.yamato.transcriber

import android.Manifest
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.*
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.google.android.material.snackbar.Snackbar
import com.permissionx.guolindev.PermissionX
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {
    
    private lateinit var languageSpinner: Spinner
    private lateinit var inputEditText: EditText
    private lateinit var outputTextView: TextView
    private lateinit var transcribeButton: Button
    private lateinit var recordButton: Button
    private lateinit var clearInputButton: Button
    private lateinit var copyButton: Button
    private lateinit var saveButton: Button
    private lateinit var openFileButton: Button
    private lateinit var progressBar: ProgressBar
    private lateinit var statusText: TextView
    
    private var audioFilePath: String? = null
    private val languageCodes = arrayOf("en", "es", "fr", "ja", "ht")
    
    // Permission request launcher
    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.all { it.value }
        if (allGranted) {
            startRecording()
        } else {
            showPermissionDeniedMessage()
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        setSupportActionBar(findViewById(R.id.toolbar))
        
        initViews()
        setupListeners()
        loadConfig()
    }
    
    private fun initViews() {
        languageSpinner = findViewById(R.id.language_spinner)
        inputEditText = findViewById(R.id.input_edittext)
        outputTextView = findViewById(R.id.output_textview)
        transcribeButton = findViewById(R.id.transcribe_button)
        recordButton = findViewById(R.id.record_button)
        clearInputButton = findViewById(R.id.clear_input_button)
        copyButton = findViewById(R.id.copy_button)
        saveButton = findViewById(R.id.save_button)
        openFileButton = findViewById(R.id.open_file_button)
        progressBar = findViewById(R.id.progress_bar)
        statusText = findViewById(R.id.status_text)
    }
    
    private fun setupListeners() {
        transcribeButton.setOnClickListener {
            startTranscription()
        }
        
        recordButton.setOnClickListener {
            checkPermissionsAndRecord()
        }
        
        clearInputButton.setOnClickListener {
            inputEditText.text.clear()
            audioFilePath = null
        }
        
        copyButton.setOnClickListener {
            copyToClipboard()
        }
        
        saveButton.setOnClickListener {
            saveTranscription()
        }
        
        openFileButton.setOnClickListener {
            openFilePicker()
        }
    }
    
    private fun checkPermissionsAndRecord() {
        val permissions = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            arrayOf(
                Manifest.permission.RECORD_AUDIO,
                Manifest.permission.READ_MEDIA_AUDIO
            )
        } else {
            arrayOf(
                Manifest.permission.RECORD_AUDIO,
                Manifest.permission.WRITE_EXTERNAL_STORAGE
            )
        }
        
        PermissionX.init(this)
            .permissions(*permissions)
            .onExplainRequestReason { scope, deniedList ->
                scope.showRequestReasonDialog(deniedList, 
                    getString(R.string.microphone_permission_rationale),
                    "Allow", "Deny")
            }
            .request { allGranted, _, _ ->
                if (allGranted) {
                    startRecording()
                } else {
                    showPermissionDeniedMessage()
                }
            }
    }
    
    private fun startRecording() {
        Snackbar.make(findViewById(android.R.id.content), 
            "Recording started...", Snackbar.LENGTH_LONG).show()
        // TODO: Implement audio recording
    }
    
    private fun showPermissionDeniedMessage() {
        Snackbar.make(findViewById(android.R.id.content), 
            getString(R.string.permission_required), Snackbar.LENGTH_LONG).show()
    }
    
    private fun startTranscription() {
        val inputText = inputEditText.text.toString().trim()
        
        if (inputText.isEmpty() && audioFilePath == null) {
            Snackbar.make(findViewById(android.R.id.content), 
                getString(R.string.no_input), Snackbar.LENGTH_SHORT).show()
            return
        }
        
        // Disable button and show progress
        transcribeButton.isEnabled = false
        progressBar.isIndeterminate = true
        statusText.text = getString(R.string.processing)
        
        lifecycleScope.launch {
            try {
                val selectedLanguage = languageCodes[languageSpinner.selectedItemPosition]
                
                val result = withContext(Dispatchers.IO) {
                    // TODO: Call transcription engine
                    // For now, return placeholder
                    "/həˈloʊ wɜrld/"
                }
                
                outputTextView.text = result
                statusText.text = getString(R.string.success)
                
            } catch (e: Exception) {
                statusText.text = getString(R.string.error)
                Snackbar.make(findViewById(android.R.id.content), 
                    "${getString(R.string.transcription_failed)}: ${e.message}", 
                    Snackbar.LENGTH_LONG).show()
            } finally {
                transcribeButton.isEnabled = true
                progressBar.isIndeterminate = false
            }
        }
    }
    
    private fun copyToClipboard() {
        val text = outputTextView.text.toString()
        if (text.isNotEmpty()) {
            val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val clip = ClipData.newPlainText("Phonetic Transcription", text)
            clipboard.setPrimaryClip(clip)
            
            Snackbar.make(findViewById(android.R.id.content), 
                getString(R.string.copied_to_clipboard), Snackbar.LENGTH_SHORT).show()
        }
    }
    
    private fun saveTranscription() {
        val text = outputTextView.text.toString()
        if (text.isNotEmpty()) {
            // TODO: Implement file saving
            Snackbar.make(findViewById(android.R.id.content), 
                getString(R.string.saved_to_file), Snackbar.LENGTH_SHORT).show()
        }
    }
    
    private fun openFilePicker() {
        // TODO: Implement file picker
        Snackbar.make(findViewById(android.R.id.content), 
            "File picker not yet implemented", Snackbar.LENGTH_SHORT).show()
    }
    
    private fun loadConfig() {
        // Load saved preferences
        val prefs = getSharedPreferences("yamato_config", Context.MODE_PRIVATE)
        val savedLanguage = prefs.getString("default_language", "en")
        
        val languageIndex = languageCodes.indexOf(savedLanguage)
        if (languageIndex >= 0) {
            languageSpinner.setSelection(languageIndex)
        }
    }
    
    private fun saveConfig() {
        val prefs = getSharedPreferences("yamato_config", Context.MODE_PRIVATE)
        with(prefs.edit()) {
            putString("default_language", languageCodes[languageSpinner.selectedItemPosition])
            apply()
        }
    }
    
    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.main_menu, menu)
        return true
    }
    
    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_settings -> {
                // TODO: Open settings
                true
            }
            R.id.action_batch -> {
                // TODO: Open batch processing
                true
            }
            R.id.action_about -> {
                showAboutDialog()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
    
    private fun showAboutDialog() {
        AlertDialog.Builder(this)
            .setTitle(R.string.app_name)
            .setMessage("${getString(R.string.version)}\n\nMultilingual phonetic transcription for Android")
            .setPositiveButton("OK", null)
            .show()
    }
    
    override fun onPause() {
        super.onPause()
        saveConfig()
    }
}
