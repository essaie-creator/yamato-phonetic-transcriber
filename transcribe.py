#!/usr/bin/env python3
"""
Command-line interface for Yamato Phonetic Transcriber.

Usage:
    python transcribe.py --text "Hello world" --lang en
    python transcribe.py --audio input.wav --lang es
    python transcribe.py --input-file texts.txt --output-file output.txt --lang fr
    python transcribe.py --gui  # Launch graphical interface
"""

import argparse
import sys
from pathlib import Path

from yamato_transcriber import PhoneticTranscriber, SUPPORTED_LANGUAGES, launch_gui


def main():
    parser = argparse.ArgumentParser(
        description='Yamato Phonetic Transcriber - Multilingual phonetic transcription',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --text "Hello world" --lang en
  %(prog)s --audio speech.wav --lang es
  %(prog)s --input-file texts.txt --output-file transcriptions.txt --lang fr
  %(prog)s --list-languages
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        '--text', '-t',
        type=str,
        help='Text to transcribe'
    )
    input_group.add_argument(
        '--audio', '-a',
        type=str,
        help='Audio file path to transcribe'
    )
    input_group.add_argument(
        '--input-file', '-i',
        type=str,
        help='File containing texts to transcribe (one per line)'
    )
    
    # Language selection
    parser.add_argument(
        '--lang', '-l',
        type=str,
        default='auto',
        choices=['auto'] + list(SUPPORTED_LANGUAGES.keys()),
        help='Language code or "auto" for automatic detection from audio (default: auto)'
    )
    
    # Output options
    parser.add_argument(
        '--output-file', '-o',
        type=str,
        help='Output file path (default: stdout)'
    )
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['ipa', 'arpabet'],
        default='ipa',
        help='Output format (default: ipa)'
    )
    parser.add_argument(
        '--separator', '-s',
        type=str,
        default=' ',
        help='Word separator in output (default: space)'
    )
    
    # Utility options
    parser.add_argument(
        '--list-languages',
        action='store_true',
        help='List supported languages and exit'
    )
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='%(prog)s 1.0.0'
    )
    parser.add_argument(
        '--no-onnx',
        action='store_true',
        help='Disable ONNX optimization'
    )
    parser.add_argument(
        '--no-low-resource',
        action='store_true',
        help='Disable low-resource mode'
    )
    parser.add_argument(
        '--gui', '-g',
        action='store_true',
        help='Launch graphical user interface'
    )
    
    args = parser.parse_args()
    
    # Launch GUI if requested
    if args.gui:
        launch_gui()
        return 0
    
    # List languages if requested
    if args.list_languages:
        print("Supported Languages:")
        print("-" * 40)
        for code, info in SUPPORTED_LANGUAGES.items():
            print(f"  {code:4} - {info['name']:20} ({info['script']})")
        return 0
    
    # Initialize transcriber
    try:
        # Determine if auto-detection is enabled
        auto_detect = (args.lang == 'auto')
        language = 'en' if auto_detect else args.lang
        
        transcriber = PhoneticTranscriber(
            language=language,
            use_onnx=not args.no_onnx,
            low_resource=not args.no_low_resource,
            auto_detect_language=auto_detect
        )
    except Exception as e:
        print(f"Error initializing transcriber: {e}", file=sys.stderr)
        return 1
    
    # Prepare output
    output_file = None
    output_handle = sys.stdout
    
    if args.output_file:
        try:
            output_file = Path(args.output_file)
            output_handle = output_file.open('w', encoding='utf-8')
        except Exception as e:
            print(f"Error opening output file: {e}", file=sys.stderr)
            return 1
    
    try:
        # Process text input
        if args.text:
            result = transcriber.text_to_phonemes(
                args.text,
                ipa=(args.format == 'ipa'),
                word_separator=args.separator
            )
            output_handle.write(result + '\n')
        
        # Process audio input
        elif args.audio:
            result, detected_lang = transcriber.audio_to_phonemes(args.audio)
            if auto_detect:
                output_handle.write(f"[Detected Language: {detected_lang}] {result}\n")
            else:
                output_handle.write(result + '\n')
        
        # Process batch file input
        elif args.input_file:
            input_path = Path(args.input_file)
            if not input_path.exists():
                print(f"Input file not found: {input_path}", file=sys.stderr)
                return 1
            
            texts = []
            with input_path.open('r', encoding='utf-8') as f:
                texts = [line.strip() for line in f if line.strip()]
            
            results = transcriber.batch_transcribe(texts, output_format=args.format)
            
            for original, transcription in zip(texts, results):
                output_handle.write(f"{original}\t{transcription}\n")
        
        else:
            parser.print_help()
            return 1
    
    except Exception as e:
        print(f"Error during transcription: {e}", file=sys.stderr)
        return 1
    
    finally:
        if output_file and output_handle:
            output_handle.close()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
