import streamlit as st
import requests
import pyperclip

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="TranslaAI", layout="wide")
st.title("🌍 TranslaAI - Your AI Translation Assistant")
st.subheader("Translate text or voice instantly across multiple languages")

# -------------------------
# Supported languages
# -------------------------
LANGUAGES = [
    "english", "french", "spanish", "portuguese",
    "arabic", "hindi", "malayalam", "tamil",
    "german", "italian", "japanese", "korean",
    "telugu", "kannada", "marathi", "bengali",
    "urdu", "chinese", "turkish", "indonesian",
    "dutch", "polish", "thai", "vietnamese", "russian"
]

# -------------------------
# Language row like Google Translate
# -------------------------
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Detected Language**")
    detected_lang_box = st.empty()
with col2:
    target_language = st.selectbox("Translate to", LANGUAGES)

st.divider()

# -------------------------
# Input method
# -------------------------
input_type = st.radio("Input method", ["Text", "Voice"], horizontal=True)

# -------------------------
# TEXT TRANSLATION
# -------------------------
if input_type == "Text":
    text_input = st.text_area("Enter text", height=150)
    if st.button("Translate"):
        if not text_input.strip():
            st.warning("Please enter text")
        else:
            response = requests.post(
                f"{BACKEND_URL}/translate",
                params={"target_language": target_language},
                data={"text": text_input}
            )

            if response.status_code == 200:
                result = response.json()
                detected_lang_box.markdown(f"**{result.get('detected_language', 'Unknown')}**")

                st.subheader("Translated Text")
                st.success(result.get("translated_text", ""))

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Copy"):
                        pyperclip.copy(result.get("translated_text", ""))
                        st.toast("Copied!")

                with col_b:
                    audio_file = result.get("audio_file")
                    if audio_file:
                        st.audio(f"{BACKEND_URL}/audio/{audio_file}")

            else:
                st.error("Translation failed")

# -------------------------
# VOICE FILE TRANSLATION
# -------------------------
else:
    audio_file = st.file_uploader(
        "Upload voice (MP3 or WAV)",
        type=["mp3", "wav"]
    )

    if st.button("Translate Voice"):
        if audio_file is None:
            st.warning("Please upload an audio file")
        else:
            files = {"audio": audio_file}
            response = requests.post(
                f"{BACKEND_URL}/translate-voice",
                params={"target_language": target_language},
                files=files
            )

            if response.status_code == 200:
                result = response.json()

                detected_lang_box.markdown(f"**{result.get('detected_language', 'Unknown')}**")

                st.subheader("Recognized Text")
                recognized_text = result.get("recognized_text", "")
                if recognized_text:
                    st.info(recognized_text)
                else:
                    st.info("Could not recognize speech")

                st.subheader("Translated Text")
                translated_text = result.get("translated_text", "")
                if translated_text:
                    st.success(translated_text)
                else:
                    st.warning("Translation not available")

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Copy"):
                        pyperclip.copy(translated_text)
                        st.toast("Copied!")

                with col_b:
                    audio_file = result.get("audio_file")
                    if audio_file:
                        st.audio(f"{BACKEND_URL}/audio/{audio_file}")

            else:
                st.error("Voice translation failed")
