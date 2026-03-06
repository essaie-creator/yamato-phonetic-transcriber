import streamlit as st
import os
import tempfile
from yamato_transcriber import PhoneticTranscriber

st.set_page_config(page_title="Yamato Phonetic Transcriber", page_icon="🎙️")

st.title("🎙️ Yamato Phonetic Transcriber")
st.markdown("""
Upload an audio file to automatically detect the language and transcribe it phonetically.
Supports: English, Spanish, French, Japanese, Haitian Creole.
""")

uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "flac"])

if uploaded_file is not None:
    st.audio(uploaded_file)
    
    if st.button("Transcribe Audio"):
        with st.spinner("Detecting language and transcribing..."):
            # Save uploaded file to a temporary location
            file_extension = os.path.splitext(uploaded_file.name)[1] or ".wav"
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                # Initialize transcriber with auto-detection enabled
                transcriber = PhoneticTranscriber(
                    language='en',  # Default fallback
                    auto_detect_language=True,
                    low_resource=True
                )
                
                # Transcribe audio (automatically detects language)
                phonemes, detected_lang = transcriber.audio_to_phonemes(tmp_path)
                
                st.success(f"Transcription Complete! Detected Language: {detected_lang}")
                st.text_area("Phonetic Output:", value=phonemes, height=200)
                
                # Show detected language info
                lang_info = transcriber.get_language_info()
                st.info(f"**Language:** {lang_info['name']} | **Script:** {lang_info['script']}")
                
                # Download button
                st.download_button(
                    label="Download Transcription",
                    data=phonemes,
                    file_name=f"transcription_{detected_lang}.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"Error during transcription: {str(e)}")
                st.info("Tip: Make sure you have installed all dependencies: `pip install speechbrain phonemizer`")
            finally:
                # Cleanup temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
