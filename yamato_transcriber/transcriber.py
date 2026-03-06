"""
Core phonetic transcription engine using SpeechBrain, Phonemizer, and ONNX.
"""

import re
from typing import Optional, List, Union, Tuple
from pathlib import Path

try:
    from phonemizer import phonemize
    from phonemizer.backend import EspeakBackend
    PHONEMIZER_AVAILABLE = True
except ImportError:
    PHONEMIZER_AVAILABLE = False

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

try:
    import torch
    import speechbrain as sb
    SPEECHBRAIN_AVAILABLE = True
except ImportError:
    SPEECHBRAIN_AVAILABLE = False

from .config import (
    SUPPORTED_LANGUAGES,
    PHONEMIZER_BACKEND,
    ONNX_CONFIG,
    LOW_RESOURCE_MODE
)


class PhoneticTranscriber:
    """
    Multilingual phonetic transcriber for low-resource environments.
    
    Supports text-to-phoneme conversion and audio-to-phoneme transcription
    using SpeechBrain, Phonemizer, and ONNX runtime.
    """
    
    def __init__(
        self,
        language: str = 'en',
        use_onnx: bool = True,
        low_resource: bool = True,
        auto_detect_language: bool = False
    ):
        """
        Initialize the phonetic transcriber.
        
        Args:
            language: Language code ('en', 'es', 'fr', 'ja', 'ht')
            use_onnx: Whether to use ONNX runtime for optimization
            low_resource: Enable low-resource mode optimizations
            auto_detect_language: Enable automatic language detection from audio
        """
        if not auto_detect_language and language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported: {list(SUPPORTED_LANGUAGES.keys())}"
            )
        
        self.language = language
        self.lang_config = SUPPORTED_LANGUAGES.get(language, SUPPORTED_LANGUAGES['en'])
        self.use_onnx = use_onnx and ONNX_AVAILABLE
        self.low_resource = low_resource
        self.auto_detect_language = auto_detect_language
        
        self._phonemizer = None
        self._asr_model = None
        self._onnx_session = None
        
        if low_resource and LOW_RESOURCE_MODE['lazy_load'] and not auto_detect_language:
            self._load_phonemizer()
    
    def _load_phonemizer(self):
        """Load the phonemizer backend for the configured language."""
        if not PHONEMIZER_AVAILABLE:
            raise ImportError(
                "phonemizer package not installed. "
                "Please install with: pip install phonemizer"
            )
        
        try:
            self._phonemizer = EspeakBackend(
                language=self.lang_config['phonemizer_lang'],
                preserve_punctuation=True,
                with_stress=False
            )
        except Exception as e:
            # Fallback for unsupported languages (e.g., Haitian Creole)
            if self.language == 'ht':
                print(f"Warning: Haitian Creole not fully supported, using French rules")
                self._phonemizer = EspeakBackend(
                    language='fr-fr',
                    preserve_punctuation=True,
                    with_stress=False
                )
            else:
                raise RuntimeError(f"Failed to load phonemizer: {e}")
    
    def text_to_phonemes(
        self,
        text: str,
        ipa: bool = True,
        word_separator: str = ' '
    ) -> str:
        """
        Convert text to phonetic transcription.
        
        Args:
            text: Input text to transcribe
            ipa: Return IPA format (True) or ARPABET (False)
            word_separator: Separator between words in output
            
        Returns:
            Phonetic transcription string
        """
        if self._phonemizer is None:
            self._load_phonemizer()
        
        # Normalize input
        text = self._normalize_text(text)
        
        # Phonemize
        phonemes = phonemize(
            text,
            backend=PHONEMIZER_BACKEND,
            language=self.lang_config['phonemizer_lang'],
            preserve_punctuation=True,
            strip=True
        )
        
        # Clean up output
        phonemes = self._clean_phonemes(phonemes, word_separator)
        
        return phonemes
    
    def audio_to_phonemes(
        self,
        audio_path: Union[str, Path],
        sample_rate: Optional[int] = None,
        detect_language: bool = None
    ) -> Tuple[str, str]:
        """
        Transcribe audio file to phonemes using ASR with optional language detection.
        
        Args:
            audio_path: Path to audio file (WAV, FLAC, etc.)
            sample_rate: Override sample rate if needed
            detect_language: If True, auto-detect language from audio. 
                           If None, uses instance's auto_detect_language setting.
        
        Returns:
            Tuple of (phonetic transcription, detected language code)
        """
        if not SPEECHBRAIN_AVAILABLE:
            raise ImportError(
                "SpeechBrain not installed. Please install with: pip install speechbrain"
            )
        
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Determine if we should detect language
        should_detect = detect_language if detect_language is not None else self.auto_detect_language
        
        # Detect language from audio if requested
        detected_lang = self.language
        if should_detect:
            self.log_message("Detecting language from audio...")
            detected_lang = self._detect_language_from_audio(audio_path)
            self.log_message(f"Detected language: {detected_lang}")
            
            # Update language config for detected language
            if detected_lang in SUPPORTED_LANGUAGES:
                self.lang_config = SUPPORTED_LANGUAGES[detected_lang]
                self.language = detected_lang
            else:
                self.log_message(f"Detected language '{detected_lang}' not supported, using English")
                detected_lang = 'en'
        
        # Load ASR model (lazy loading) - now using detected language
        if self._asr_model is None or (should_detect and detected_lang != self.language):
            self._load_asr_model(language_override=detected_lang if should_detect else None)
        
        # Transcribe audio to text
        text = self._asr_model.transcribe_file(str(audio_path))
        self.log_message(f"Transcribed text: {text}")
        
        # Convert text to phonemes
        phonemes = self.text_to_phonemes(text)
        
        return phonemes, detected_lang
    
    def _detect_language_from_audio(self, audio_path: Path) -> str:
        """
        Detect the language spoken in an audio file.
        
        Uses a lightweight language identification model.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            ISO 639-1 language code ('en', 'es', 'fr', 'ja', 'ht')
        """
        try:
            # Try to use SpeechBrain's language identification model
            from speechbrain.inference.classifiers import EncoderClassifier
            
            # Load a lightweight language ID model
            classifier = EncoderClassifier.from_hparams(
                source="speechbrain/lang-id-commonlanguage_ecapa",
                savedir="/tmp/sb_langid"
            )
            
            # Get language prediction
            prediction = classifier.classify_file(str(audio_path))
            
            # Map common language codes to our supported codes
            lang_mapping = {
                'eng': 'en',
                'english': 'en',
                'spa': 'es',
                'spanish': 'es',
                'fra': 'fr',
                'french': 'fr',
                'jpn': 'ja',
                'japanese': 'ja',
                'hat': 'ht',
                'haitian': 'ht'
            }
            
            # Get the predicted language code
            if isinstance(prediction, list) and len(prediction) > 0:
                pred_code = prediction[0].lower()
            else:
                pred_code = str(prediction).lower()
            
            # Map to our supported languages
            for key, value in lang_mapping.items():
                if key in pred_code:
                    return value
            
            # Default fallback based on common patterns
            if 'en' in pred_code or 'eng' in pred_code:
                return 'en'
            elif 'es' in pred_code or 'spa' in pred_code:
                return 'es'
            elif 'fr' in pred_code or 'fra' in pred_code:
                return 'fr'
            elif 'ja' in pred_code or 'jpn' in pred_code:
                return 'ja'
            elif 'ht' in pred_code or 'hat' in pred_code:
                return 'ht'
            
            # If no match, return English as default
            return 'en'
            
        except Exception as e:
            self.log_message(f"Language detection failed: {e}, using default language")
            return self.language
    
    def log_message(self, message: str):
        """Log a message (can be overridden for GUI integration)."""
        if self.low_resource:
            pass  # Silent in low-resource mode
        else:
            print(f"[Yamato] {message}")
    
    def _load_asr_model(self, language_override: str = None):
        """Load SpeechBrain ASR model for audio transcription.
        
        Args:
            language_override: Override the instance language for model loading
        """
        # Use a lightweight ASR model suitable for low-resource environments
        try:
            from speechbrain.inference.ASR import EncoderASR
            
            # Use overridden language if provided, otherwise use instance language
            lang = language_override if language_override else self.language
            
            # Select appropriate model based on language
            if lang == 'en':
                model_name = "speechbrain/asr-whisper-tiny.en-common_voice_en"
            elif lang == 'es':
                model_name = "speechbrain/asr-whisper-tiny-common_voice_es"
            elif lang == 'fr':
                model_name = "speechbrain/asr-whisper-tiny-common_voice_fr"
            elif lang == 'ja':
                model_name = "speechbrain/asr-whisper-tiny-common_voice_ja"
            else:
                # Default to English for unsupported languages
                model_name = "speechbrain/asr-whisper-tiny.en-common_voice_en"
                self.log_message(f"Warning: Using English ASR for {lang}")
            
            self._asr_model = EncoderASR.from_hparams(
                source=model_name,
                savedir=f"/tmp/sb_{lang}_asr"
            )
        except Exception as e:
            self.log_message(f"Warning: Failed to load ASR model: {e}")
            self._asr_model = None
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for phonemization."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Handle special cases for different languages
        if self.language == 'ja':
            # Japanese text may need special preprocessing
            pass
        elif self.language == 'ht':
            # Haitian Creole normalization
            text = text.lower()
        
        return text
    
    def _clean_phonemes(self, phonemes: str, separator: str) -> str:
        """Clean and format phoneme output."""
        # Remove extra spaces
        phonemes = re.sub(r'\s+', ' ', phonemes.strip())
        
        # Replace word boundaries with separator
        phonemes = phonemes.replace('  ', separator)
        
        return phonemes
    
    def batch_transcribe(
        self,
        texts: List[str],
        output_format: str = 'ipa'
    ) -> List[str]:
        """
        Batch transcribe multiple texts.
        
        Args:
            texts: List of texts to transcribe
            output_format: Output format ('ipa', 'arpabet')
            
        Returns:
            List of phonetic transcriptions
        """
        results = []
        for text in texts:
            try:
                result = self.text_to_phonemes(text, ipa=(output_format == 'ipa'))
                results.append(result)
            except Exception as e:
                print(f"Error transcribing '{text}': {e}")
                results.append("")
        
        return results
    
    def get_language_info(self) -> dict:
        """Get information about the current language configuration."""
        return {
            'code': self.language,
            'name': self.lang_config['name'],
            'script': self.lang_config['script'],
            'phonemizer_lang': self.lang_config['phonemizer_lang']
        }
