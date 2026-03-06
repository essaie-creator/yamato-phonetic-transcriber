"""
Core phonetic transcription engine using SpeechBrain, Phonemizer, and ONNX.
"""

import re
from typing import Optional, List, Union
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
        low_resource: bool = True
    ):
        """
        Initialize the phonetic transcriber.
        
        Args:
            language: Language code ('en', 'es', 'fr', 'ja', 'ht')
            use_onnx: Whether to use ONNX runtime for optimization
            low_resource: Enable low-resource mode optimizations
        """
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported: {list(SUPPORTED_LANGUAGES.keys())}"
            )
        
        self.language = language
        self.lang_config = SUPPORTED_LANGUAGES[language]
        self.use_onnx = use_onnx and ONNX_AVAILABLE
        self.low_resource = low_resource
        
        self._phonemizer = None
        self._asr_model = None
        self._onnx_session = None
        
        if low_resource and LOW_RESOURCE_MODE['lazy_load']:
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
        sample_rate: Optional[int] = None
    ) -> str:
        """
        Transcribe audio file to phonemes using ASR.
        
        Args:
            audio_path: Path to audio file (WAV, FLAC, etc.)
            sample_rate: Override sample rate if needed
            
        Returns:
            Phonetic transcription of spoken content
        """
        if not SPEECHBRAIN_AVAILABLE:
            raise ImportError(
                "SpeechBrain not installed. Please install with: pip install speechbrain"
            )
        
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Load ASR model (lazy loading)
        if self._asr_model is None:
            self._load_asr_model()
        
        # Transcribe audio to text
        text = self._asr_model.transcribe_file(str(audio_path))
        
        # Convert text to phonemes
        return self.text_to_phonemes(text)
    
    def _load_asr_model(self):
        """Load SpeechBrain ASR model for audio transcription."""
        # Use a lightweight ASR model suitable for low-resource environments
        try:
            from speechbrain.inference.ASR import EncoderASR
            
            # Select appropriate model based on language
            if self.language == 'en':
                model_name = "speechbrain/asr-whisper-tiny.en-common_voice_en"
            elif self.language == 'es':
                model_name = "speechbrain/asr-whisper-tiny-common_voice_es"
            elif self.language == 'fr':
                model_name = "speechbrain/asr-whisper-tiny-common_voice_fr"
            elif self.language == 'ja':
                model_name = "speechbrain/asr-whisper-tiny-common_voice_ja"
            else:
                # Default to English for unsupported languages
                model_name = "speechbrain/asr-whisper-tiny.en-common_voice_en"
                print(f"Warning: Using English ASR for {self.language}")
            
            self._asr_model = EncoderASR.from_hparams(
                source=model_name,
                savedir=f"/tmp/sb_{self.language}_asr"
            )
        except Exception as e:
            print(f"Warning: Failed to load ASR model: {e}")
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
