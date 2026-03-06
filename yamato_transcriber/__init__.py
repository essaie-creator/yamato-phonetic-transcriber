"""
Yamato Phonetic Transcriber - Multilingual phonetic transcription for low-resource environments.
"""

from .transcriber import PhoneticTranscriber
from .config import SUPPORTED_LANGUAGES

try:
    from .gui import launch_gui
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    def launch_gui():
        raise ImportError("GUI dependencies not installed. Install tkinter to use the GUI.")

__version__ = "1.0.0"
__all__ = ["PhoneticTranscriber", "SUPPORTED_LANGUAGES", "launch_gui", "GUI_AVAILABLE"]
