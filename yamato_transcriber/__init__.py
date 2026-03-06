"""
Yamato Phonetic Transcriber - Multilingual phonetic transcription for low-resource environments.
"""

from .transcriber import PhoneticTranscriber
from .config import SUPPORTED_LANGUAGES

__version__ = "1.0.0"
__all__ = ["PhoneticTranscriber", "SUPPORTED_LANGUAGES"]
