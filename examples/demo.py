"""
Example usage of the Yamato Phonetic Transcriber.
"""

from yamato_transcriber import PhoneticTranscriber, SUPPORTED_LANGUAGES


def main():
    print("=" * 60)
    print("Yamato Phonetic Transcriber - Demo")
    print("=" * 60)
    
    # List supported languages
    print("\nSupported Languages:")
    for code, info in SUPPORTED_LANGUAGES.items():
        print(f"  {code}: {info['name']} ({info['script']})")
    
    # English example
    print("\n" + "-" * 60)
    print("English (en):")
    transcriber_en = PhoneticTranscriber(language='en')
    text_en = "Hello world, this is a test."
    phonemes_en = transcriber_en.text_to_phonemes(text_en)
    print(f"  Text:     {text_en}")
    print(f"  Phonemes: {phonemes_en}")
    
    # Spanish example
    print("\n" + "-" * 60)
    print("Spanish (es):")
    transcriber_es = PhoneticTranscriber(language='es')
    text_es = "Hola mundo, esto es una prueba."
    phonemes_es = transcriber_es.text_to_phonemes(text_es)
    print(f"  Text:     {text_es}")
    print(f"  Phonemes: {phonemes_es}")
    
    # French example
    print("\n" + "-" * 60)
    print("French (fr):")
    transcriber_fr = PhoneticTranscriber(language='fr')
    text_fr = "Bonjour le monde, ceci est un test."
    phonemes_fr = transcriber_fr.text_to_phonemes(text_fr)
    print(f"  Text:     {text_fr}")
    print(f"  Phonemes: {phonemes_fr}")
    
    # Japanese example
    print("\n" + "-" * 60)
    print("Japanese (ja):")
    transcriber_ja = PhoneticTranscriber(language='ja')
    text_ja = "こんにちは世界、これはテストです。"
    phonemes_ja = transcriber_ja.text_to_phonemes(text_ja)
    print(f"  Text:     {text_ja}")
    print(f"  Phonemes: {phonemes_ja}")
    
    # Haitian Creole example
    print("\n" + "-" * 60)
    print("Haitian Creole (ht):")
    transcriber_ht = PhoneticTranscriber(language='ht')
    text_ht = "Bonjou mond, sa a se yon tès."
    phonemes_ht = transcriber_ht.text_to_phonemes(text_ht)
    print(f"  Text:     {text_ht}")
    print(f"  Phonemes: {phonemes_ht}")
    
    # Batch processing example
    print("\n" + "-" * 60)
    print("Batch Processing (English):")
    texts = [
        "The quick brown fox",
        "Jumps over the lazy dog",
        "Phonetic transcription is useful"
    ]
    results = transcriber_en.batch_transcribe(texts)
    for text, result in zip(texts, results):
        print(f"  {text:35} -> {result}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
