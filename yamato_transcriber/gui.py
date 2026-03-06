"""
Tkinter-based Graphical User Interface for Yamato Phonetic Transcriber.

Provides a user-friendly interface for non-technical users with:
- Text input and phonetic transcription
- Audio file upload and transcription
- Progress indicators
- Verbose logging
- Configuration management
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from .transcriber import PhoneticTranscriber
    from .config import SUPPORTED_LANGUAGES
except ImportError:
    from transcriber import PhoneticTranscriber
    from config import SUPPORTED_LANGUAGES


class ConfigManager:
    """Manages user configuration stored in ~/.yamato_config.yaml or ~/.yamato_config.json"""
    
    DEFAULT_CONFIG = {
        'default_language': 'en',
        'output_format': 'ipa',
        'word_separator': ' ',
        'verbose': False,
        'low_resource_mode': True,
        'use_onnx': True,
        'recent_files': [],
        'window_geometry': '800x600',
        'audio_sample_rate': None,
        'max_recent_files': 5
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            home = Path.home()
            # Try YAML first, fallback to JSON
            self.config_path = home / '.yamato_config.json'
        else:
            self.config_path = Path(config_path)
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults."""
        if not self.config_path.exists():
            return self.DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**self.DEFAULT_CONFIG, **config}
        except Exception as e:
            logging.warning(f"Failed to load config: {e}, using defaults")
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value."""
        self.config[key] = value
        self.save_config()
    
    def add_recent_file(self, filepath: str):
        """Add file to recent files list."""
        recent = self.config.get('recent_files', [])
        if filepath in recent:
            recent.remove(filepath)
        recent.insert(0, filepath)
        # Keep only max_recent_files
        max_files = self.config.get('max_recent_files', 5)
        self.config['recent_files'] = recent[:max_files]
        self.save_config()


class VerboseLogger(logging.Handler):
    """Custom logging handler that updates GUI text widget."""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.setLevel(logging.DEBUG)
    
    def emit(self, record):
        """Log message to text widget."""
        msg = self.format(record)
        try:
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')
        except Exception:
            pass


class YamatoGUI:
    """Main GUI application for Yamato Phonetic Transcriber."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Yamato Phonetic Transcriber v1.0.0")
        self.root.minsize(800, 600)
        
        # Initialize configuration
        self.config_manager = ConfigManager()
        
        # Initialize transcriber (lazy loading)
        self.transcriber: Optional[PhoneticTranscriber] = None
        
        # Setup logging
        self.setup_logging()
        
        # Build UI
        self.build_menu()
        self.build_ui()
        
        # Load saved window geometry
        geometry = self.config_manager.get('window_geometry', '800x600')
        self.root.geometry(geometry)
        
        # Save geometry on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.log_message("Yamato Phonetic Transcriber initialized")
        self.log_message(f"Configuration loaded from: {self.config_manager.config_path}")
    
    def setup_logging(self):
        """Setup logging system."""
        self.logger = logging.getLogger('yamato_gui')
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def log_message(self, message: str, level: int = logging.INFO):
        """Log message to both console and verbose widget if available."""
        self.logger.log(level, message)
        if hasattr(self, 'verbose_text'):
            try:
                self.verbose_text.configure(state='normal')
                timestamp = datetime.now().strftime('%H:%M:%S')
                self.verbose_text.insert(tk.END, f"[{timestamp}] {message}\n")
                self.verbose_text.see(tk.END)
                self.verbose_text.configure(state='disabled')
            except Exception:
                pass
    
    def build_menu(self):
        """Build application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Text File...", command=self.open_text_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Open Audio File...", command=self.open_audio_file, accelerator="Ctrl+A")
        file_menu.add_separator()
        file_menu.add_command(label="Save Transcription...", command=self.save_transcription, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close, accelerator="Alt+F4")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear Input", command=self.clear_input)
        edit_menu.add_command(label="Clear Output", command=self.clear_output)
        edit_menu.add_command(label="Clear All", command=self.clear_all)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="REPL Mode", command=self.open_repl)
        tools_menu.add_command(label="Batch Processing", command=self.open_batch_processor)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_checkbutton(label="Verbose Mode", command=self.toggle_verbose, 
                                       variable=tk.BooleanVar(value=self.config_manager.get('verbose')))
        settings_menu.add_command(label="Configure...", command=self.open_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Supported Languages", command=self.show_languages)
        
        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_text_file())
        self.root.bind('<Control-a>', lambda e: self.open_audio_file())
        self.root.bind('<Control-s>', lambda e: self.save_transcription())
    
    def build_ui(self):
        """Build main user interface."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Language selection
        lang_frame = ttk.LabelFrame(main_frame, text="Language Settings", padding="5")
        lang_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        lang_frame.columnconfigure(1, weight=1)
        
        ttk.Label(lang_frame, text="Language:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.language_var = tk.StringVar(value=self.config_manager.get('default_language', 'en'))
        self.language_combo = ttk.Combobox(lang_frame, textvariable=self.language_var, 
                                           values=list(SUPPORTED_LANGUAGES.keys()), width=10)
        self.language_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(lang_frame, text="Format:").grid(row=0, column=2, sticky=tk.W, padx=10)
        self.format_var = tk.StringVar(value=self.config_manager.get('output_format', 'ipa'))
        format_combo = ttk.Combobox(lang_frame, textvariable=self.format_var, 
                                    values=['ipa', 'arpabet'], width=10)
        format_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(lang_frame, text="Separator:").grid(row=0, column=4, sticky=tk.W, padx=10)
        self.separator_var = tk.StringVar(value=self.config_manager.get('word_separator', ' '))
        separator_entry = ttk.Entry(lang_frame, textvariable=self.separator_var, width=5)
        separator_entry.grid(row=0, column=5, sticky=tk.W, padx=5)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input", padding="5")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=8)
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input buttons
        input_btn_frame = ttk.Frame(input_frame)
        input_btn_frame.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        ttk.Button(input_btn_frame, text="📁 Open Text", command=self.open_text_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(input_btn_frame, text="🎤 Open Audio", command=self.open_audio_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(input_btn_frame, text="🗑 Clear", command=self.clear_input).pack(side=tk.LEFT, padx=2)
        
        # Transcribe button with progress
        transcribe_frame = ttk.Frame(main_frame)
        transcribe_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.transcribe_btn = ttk.Button(transcribe_frame, text="▶ Transcribe", command=self.start_transcription)
        self.transcribe_btn.pack(side=tk.LEFT, padx=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(transcribe_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.status_label = ttk.Label(transcribe_frame, text="Ready", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="5")
        output_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=8)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Output buttons
        output_btn_frame = ttk.Frame(output_frame)
        output_btn_frame.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        ttk.Button(output_btn_frame, text="💾 Save", command=self.save_transcription).pack(side=tk.LEFT, padx=2)
        ttk.Button(output_btn_frame, text="📋 Copy", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=2)
        ttk.Button(output_btn_frame, text="🗑 Clear", command=self.clear_output).pack(side=tk.LEFT, padx=2)
        
        # Verbose logging panel (collapsible)
        verbose_frame = ttk.LabelFrame(main_frame, text="Verbose Log", padding="5")
        verbose_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        verbose_frame.columnconfigure(0, weight=1)
        verbose_frame.rowconfigure(0, weight=1)
        
        self.verbose_text = scrolledtext.ScrolledText(verbose_frame, wrap=tk.WORD, height=6, state='disabled')
        self.verbose_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Show/hide verbose based on config
        if not self.config_manager.get('verbose', False):
            verbose_frame.grid_remove()
    
    def toggle_verbose(self):
        """Toggle verbose logging visibility."""
        verbose_frame = self.root.nametowidget('.!frame.!labelframe4')
        if verbose_frame.winfo_ismapped():
            verbose_frame.grid_remove()
            self.config_manager.set('verbose', False)
        else:
            verbose_frame.grid()
            self.config_manager.set('verbose', True)
        self.log_message("Verbose mode toggled")
    
    def open_text_file(self):
        """Open text file for transcription."""
        filepath = filedialog.askopenfilename(
            title="Open Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.input_text.delete('1.0', tk.END)
                self.input_text.insert('1.0', content)
                self.config_manager.add_recent_file(filepath)
                self.log_message(f"Loaded text file: {filepath}")
                self.status_label.config(text=f"Loaded: {Path(filepath).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")
                self.log_message(f"Error opening file: {e}", logging.ERROR)
    
    def open_audio_file(self):
        """Open audio file for transcription."""
        filepath = filedialog.askopenfilename(
            title="Open Audio File",
            filetypes=[
                ("Audio files", "*.wav *.flac *.mp3 *.ogg *.m4a"),
                ("WAV files", "*.wav"),
                ("FLAC files", "*.flac"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            self.input_text.delete('1.0', tk.END)
            self.input_text.insert('1.0', f"[AUDIO FILE]: {filepath}")
            self.audio_filepath = filepath
            self.config_manager.add_recent_file(filepath)
            self.log_message(f"Loaded audio file: {filepath}")
            self.status_label.config(text=f"Audio ready: {Path(filepath).name}")
    
    def start_transcription(self):
        """Start transcription in background thread."""
        self.transcribe_btn.config(state='disabled')
        self.progress_var.set(0)
        self.status_label.config(text="Processing...")
        
        # Run transcription in background thread
        thread = threading.Thread(target=self.transcribe_worker, daemon=True)
        thread.start()
    
    def transcribe_worker(self):
        """Worker method for transcription (runs in background thread)."""
        try:
            self.log_message("Starting transcription...")
            
            # Get input
            input_content = self.input_text.get('1.0', tk.END).strip()
            
            if not input_content:
                self.root.after(0, lambda: messagebox.showwarning("Warning", "No input provided"))
                self.root.after(0, lambda: self.status_label.config(text="Error: No input"))
                return
            
            # Check if audio file
            is_audio = input_content.startswith("[AUDIO FILE]:")
            
            # Initialize transcriber if needed
            if self.transcriber is None:
                self.root.after(0, lambda: self.status_label.config(text="Loading model..."))
                self.log_message("Initializing transcriber...")
                
                try:
                    self.transcriber = PhoneticTranscriber(
                        language=self.language_var.get(),
                        use_onnx=self.config_manager.get('use_onnx', True),
                        low_resource=self.config_manager.get('low_resource_mode', True)
                    )
                    self.log_message("Transcriber initialized successfully")
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to initialize transcriber: {e}"))
                    self.root.after(0, lambda: self.status_label.config(text="Error initializing"))
                    self.log_message(f"Transcriber initialization failed: {e}", logging.ERROR)
                    return
            
            # Update language if changed
            if self.transcriber.language != self.language_var.get():
                self.log_message(f"Changing language to {self.language_var.get()}")
                self.transcriber = PhoneticTranscriber(
                    language=self.language_var.get(),
                    use_onnx=self.config_manager.get('use_onnx', True),
                    low_resource=self.config_manager.get('low_resource_mode', True)
                )
            
            # Perform transcription
            self.root.after(0, lambda: self.progress_var.set(50))
            self.log_message("Performing transcription...")
            
            if is_audio:
                audio_path = input_content.replace("[AUDIO FILE]:", "").strip()
                result = self.transcriber.audio_to_phonemes(audio_path)
            else:
                result = self.transcriber.text_to_phonemes(
                    input_content,
                    ipa=(self.format_var.get() == 'ipa'),
                    word_separator=self.separator_var.get()
                )
            
            # Update UI with result
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.output_text.delete('1.0', tk.END))
            self.root.after(0, lambda: self.output_text.insert('1.0', result))
            self.root.after(0, lambda: self.status_label.config(text="Completed"))
            self.log_message("Transcription completed successfully")
            
        except FileNotFoundError as e:
            self.root.after(0, lambda: messagebox.showerror("File Not Found", str(e)))
            self.root.after(0, lambda: self.status_label.config(text="Error: File not found"))
            self.log_message(f"File not found: {e}", logging.ERROR)
        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            self.root.after(0, lambda: self.status_label.config(text="Error"))
            self.log_message(error_msg, logging.ERROR)
        finally:
            self.root.after(0, lambda: self.transcribe_btn.config(state='normal'))
    
    def save_transcription(self):
        """Save transcription to file."""
        content = self.output_text.get('1.0', tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "No transcription to save")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="Save Transcription",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log_message(f"Saved transcription to: {filepath}")
                messagebox.showinfo("Success", f"Transcription saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
                self.log_message(f"Error saving file: {e}", logging.ERROR)
    
    def copy_to_clipboard(self):
        """Copy transcription to clipboard."""
        content = self.output_text.get('1.0', tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.status_label.config(text="Copied to clipboard")
            self.log_message("Transcription copied to clipboard")
    
    def clear_input(self):
        """Clear input text."""
        self.input_text.delete('1.0', tk.END)
        if hasattr(self, 'audio_filepath'):
            del self.audio_filepath
        self.log_message("Input cleared")
    
    def clear_output(self):
        """Clear output text."""
        self.output_text.delete('1.0', tk.END)
        self.log_message("Output cleared")
    
    def clear_all(self):
        """Clear all text fields."""
        self.clear_input()
        self.clear_output()
        self.log_message("All fields cleared")
    
    def open_repl(self):
        """Open interactive REPL mode window."""
        repl_window = tk.Toplevel(self.root)
        repl_window.title("REPL Mode - Interactive Transcription")
        repl_window.geometry("600x400")
        
        frame = ttk.Frame(repl_window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        repl_window.columnconfigure(0, weight=1)
        repl_window.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        ttk.Label(frame, text="Interactive REPL Mode - Type text and press Enter").grid(row=0, column=0)
        
        repl_output = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=15, state='disabled')
        repl_output.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        repl_input = ttk.Entry(frame)
        repl_input.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Create local transcriber for REPL
        local_transcriber = None
        
        def process_repl_input(event=None):
            nonlocal local_transcriber
            text = repl_input.get().strip()
            if not text:
                return
            
            if text.lower() in ['quit', 'exit', 'q']:
                repl_window.destroy()
                return
            
            try:
                if local_transcriber is None:
                    local_transcriber = PhoneticTranscriber(
                        language=self.language_var.get(),
                        use_onnx=self.config_manager.get('use_onnx', True),
                        low_resource=self.config_manager.get('low_resource_mode', True)
                    )
                
                result = local_transcriber.text_to_phonemes(
                    text,
                    ipa=(self.format_var.get() == 'ipa'),
                    word_separator=self.separator_var.get()
                )
                
                repl_output.configure(state='normal')
                repl_output.insert(tk.END, f"> {text}\n< {result}\n\n")
                repl_output.see(tk.END)
                repl_output.configure(state='disabled')
                
            except Exception as e:
                repl_output.configure(state='normal')
                repl_output.insert(tk.END, f"Error: {e}\n\n")
                repl_output.see(tk.END)
                repl_output.configure(state='disabled')
            
            repl_input.delete(0, tk.END)
        
        repl_input.bind('<Return>', process_repl_input)
        repl_input.focus()
        
        ttk.Button(frame, text="Close", command=repl_window.destroy).grid(row=3, column=0, pady=(10, 0))
    
    def open_batch_processor(self):
        """Open batch processing dialog."""
        batch_window = tk.Toplevel(self.root)
        batch_window.title("Batch Processing")
        batch_window.geometry("700x500")
        
        frame = ttk.Frame(batch_window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        batch_window.columnconfigure(0, weight=1)
        batch_window.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        
        ttk.Label(frame, text="Batch Process Multiple Texts").grid(row=0, column=0)
        
        # Input file selection
        input_file_var = tk.StringVar()
        ttk.Label(frame, text="Input File:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        input_frame = ttk.Frame(frame)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Entry(input_frame, textvariable=input_file_var).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(input_frame, text="Browse...", command=lambda: input_file_var.set(
            filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        )).grid(row=0, column=1)
        
        # Output file selection
        output_file_var = tk.StringVar()
        ttk.Label(frame, text="Output File:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        
        output_frame = ttk.Frame(frame)
        output_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Entry(output_frame, textvariable=output_file_var).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse...", command=lambda: output_file_var.set(
            filedialog.asksaveasfilename(defaultextension=".txt")
        )).grid(row=0, column=1)
        
        # Progress
        batch_progress = ttk.Progressbar(frame, mode='indeterminate')
        batch_progress.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(20, 0))
        
        status_label = ttk.Label(frame, text="")
        status_label.grid(row=6, column=0, pady=(5, 0))
        
        def run_batch():
            input_path = input_file_var.get()
            output_path = output_file_var.get()
            
            if not input_path or not output_path:
                messagebox.showwarning("Warning", "Please select both input and output files")
                return
            
            try:
                batch_progress.start()
                status_label.config(text="Processing...")
                
                # Read input
                with open(input_path, 'r', encoding='utf-8') as f:
                    texts = [line.strip() for line in f if line.strip()]
                
                # Initialize transcriber
                transcriber = PhoneticTranscriber(
                    language=self.language_var.get(),
                    use_onnx=self.config_manager.get('use_onnx', True),
                    low_resource=self.config_manager.get('low_resource_mode', True)
                )
                
                # Process batch
                results = transcriber.batch_transcribe(texts, output_format=self.format_var.get())
                
                # Write output
                with open(output_path, 'w', encoding='utf-8') as f:
                    for original, result in zip(texts, results):
                        f.write(f"{original}\t{result}\n")
                
                batch_progress.stop()
                status_label.config(text=f"Completed: {len(results)} items")
                messagebox.showinfo("Success", f"Batch processing completed!\nProcessed {len(results)} items")
                self.log_message(f"Batch processed {len(results)} items")
                
            except Exception as e:
                batch_progress.stop()
                status_label.config(text="Error")
                messagebox.showerror("Error", f"Batch processing failed: {e}")
                self.log_message(f"Batch processing error: {e}", logging.ERROR)
        
        ttk.Button(frame, text="Start Batch Processing", command=run_batch).grid(row=7, column=0, pady=(20, 0))
        ttk.Button(frame, text="Close", command=batch_window.destroy).grid(row=8, column=0, pady=(5, 0))
    
    def open_settings(self):
        """Open settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.resizable(False, False)
        
        frame = ttk.Frame(settings_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        settings_window.columnconfigure(0, weight=1)
        settings_window.rowconfigure(0, weight=1)
        
        row = 0
        
        # Default language
        ttk.Label(frame, text="Default Language:").grid(row=row, column=0, sticky=tk.W, pady=5)
        lang_var = tk.StringVar(value=self.config_manager.get('default_language', 'en'))
        lang_combo = ttk.Combobox(frame, textvariable=lang_var, values=list(SUPPORTED_LANGUAGES.keys()))
        lang_combo.grid(row=row, column=1, sticky=tk.W, padx=10)
        row += 1
        
        # Output format
        ttk.Label(frame, text="Output Format:").grid(row=row, column=0, sticky=tk.W, pady=5)
        format_var = tk.StringVar(value=self.config_manager.get('output_format', 'ipa'))
        format_combo = ttk.Combobox(frame, textvariable=format_var, values=['ipa', 'arpabet'])
        format_combo.grid(row=row, column=1, sticky=tk.W, padx=10)
        row += 1
        
        # Word separator
        ttk.Label(frame, text="Word Separator:").grid(row=row, column=0, sticky=tk.W, pady=5)
        sep_var = tk.StringVar(value=self.config_manager.get('word_separator', ' '))
        ttk.Entry(frame, textvariable=sep_var, width=5).grid(row=row, column=1, sticky=tk.W, padx=10)
        row += 1
        
        # Low resource mode
        low_res_var = tk.BooleanVar(value=self.config_manager.get('low_resource_mode', True))
        ttk.Checkbutton(frame, text="Low Resource Mode", variable=low_res_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Use ONNX
        onnx_var = tk.BooleanVar(value=self.config_manager.get('use_onnx', True))
        ttk.Checkbutton(frame, text="Use ONNX Optimization", variable=onnx_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Max recent files
        ttk.Label(frame, text="Max Recent Files:").grid(row=row, column=0, sticky=tk.W, pady=5)
        recent_var = tk.IntVar(value=self.config_manager.get('max_recent_files', 5))
        ttk.Spinbox(frame, from_=1, to=20, textvariable=recent_var, width=5).grid(row=row, column=1, sticky=tk.W, padx=10)
        row += 1
        
        def save_settings():
            self.config_manager.set('default_language', lang_var.get())
            self.config_manager.set('output_format', format_var.get())
            self.config_manager.set('word_separator', sep_var.get())
            self.config_manager.set('low_resource_mode', low_res_var.get())
            self.config_manager.set('use_onnx', onnx_var.get())
            self.config_manager.set('max_recent_files', recent_var.get())
            self.language_var.set(lang_var.get())
            self.format_var.set(format_var.get())
            self.separator_var.set(sep_var.get())
            messagebox.showinfo("Success", "Settings saved!")
            settings_window.destroy()
        
        ttk.Button(frame, text="Save", command=save_settings).grid(row=row, column=0, pady=(20, 0))
        ttk.Button(frame, text="Cancel", command=settings_window.destroy).grid(row=row, column=1, pady=(20, 0))
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About Yamato Phonetic Transcriber",
            "Yamato Phonetic Transcriber v1.0.0\n\n"
            "A lightweight multilingual phonetic transcription application.\n\n"
            "Features:\n"
            "• Text-to-phoneme conversion\n"
            "• Audio-to-phoneme transcription\n"
            "• Support for 5 languages\n"
            "• Low-resource optimized\n"
            "• ONNX runtime acceleration\n\n"
            "License: MIT"
        )
    
    def show_languages(self):
        """Show supported languages dialog."""
        lang_info = ""
        for code, info in SUPPORTED_LANGUAGES.items():
            lang_info += f"{code}: {info['name']} ({info['script']})\n"
        
        messagebox.showinfo("Supported Languages", lang_info)
    
    def on_close(self):
        """Handle window close event."""
        # Save window geometry
        self.config_manager.set('window_geometry', self.root.geometry())
        self.root.destroy()


def launch_gui():
    """Launch the GUI application."""
    root = tk.Tk()
    
    # Set application icon (if available)
    try:
        root.iconbitmap('yamato_icon.ico')
    except Exception:
        pass
    
    app = YamatoGUI(root)
    root.mainloop()


if __name__ == '__main__':
    launch_gui()
