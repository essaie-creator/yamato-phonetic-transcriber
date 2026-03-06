"""
Configuration for supported languages and phonemizer settings.
"""

SUPPORTED_LANGUAGES = {
    'en': {
        'name': 'English',
        'phonemizer_lang': 'en-us',
        'script': 'Latin'
    },
    'es': {
        'name': 'Spanish',
        'phonemizer_lang': 'es',
        'script': 'Latin'
    },
    'fr': {
        'name': 'French',
        'phonemizer_lang': 'fr-fr',
        'script': 'Latin'
    },
    'ja': {
        'name': 'Japanese',
        'phonemizer_lang': 'ja',
        'script': 'Kana/Kanji'
    },
    'ht': {
        'name': 'Haitian Creole',
        'phonemizer_lang': 'ht',  # Falls back to French-based rules
        'script': 'Latin'
    }
}

# Phonemizer backend options
PHONEMIZER_BACKEND = 'espeak'

# ONNX model configurations
ONNX_CONFIG = {
    'quantized': True,
    'execution_providers': ['CPUExecutionProvider'],
    'intra_op_num_threads': 2,
    'inter_op_num_threads': 1
}

# Low-resource mode settings
LOW_RESOURCE_MODE = {
    'lazy_load': True,
    'cache_models': False,
    'max_audio_length': 300  # seconds
}
