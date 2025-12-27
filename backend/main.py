from fastapi import FastAPI, UploadFile, File, Query, Form
from fastapi.staticfiles import StaticFiles
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
from langdetect import detect
import uuid
import os
import io

# 🔹 Set full path to your ffmpeg.exe and ffprobe.exe
AudioSegment.converter = r"C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffprobe.exe"

app = FastAPI(
    title="TranslaAI - Language Translation API",
    version="1.1.0"
)

# Serve audio files
app.mount("/audio", StaticFiles(directory="."), name="audio")

# -----------------------------
# Language Maps
# -----------------------------
LANGUAGE_MAP = {
    "english": "en", "en": "en",
    "french": "fr", "fr": "fr",
    "spanish": "es", "es": "es",
    "portuguese": "pt", "pt": "pt",
    "german": "de", "de": "de",
    "italian": "it", "it": "it",
    "arabic": "ar", "ar": "ar",
    "hindi": "hi", "hi": "hi",
    "malayalam": "ml", "ml": "ml",
    "tamil": "ta", "ta": "ta",
    "telugu": "te", "te": "te",
    "kannada": "kn", "kn": "kn",
    "marathi": "mr", "mr": "mr",
    "bengali": "bn", "bn": "bn",
    "urdu": "ur", "ur": "ur",
    "chinese": "zh-cn",
    "japanese": "ja", "ja": "ja",
    "korean": "ko", "ko": "ko",
    "russian": "ru", "ru": "ru",
    "turkish": "tr", "tr": "tr",
    "indonesian": "id", "id": "id",
    "dutch": "nl", "nl": "nl",
    "polish": "pl", "pl": "pl",
    "thai": "th", "th": "th",
    "vietnamese": "vi", "vi": "vi"
}

LANG_CODE_TO_NAME = {v: k.title() for k, v in LANGUAGE_MAP.items() if len(v) > 1}

# -----------------------------
# Helpers
# -----------------------------
def get_language_code(lang: str) -> str:
    lang = lang.lower().strip()
    if lang not in LANGUAGE_MAP:
        raise ValueError("Unsupported language")
    return LANGUAGE_MAP[lang]

def get_language_name(code: str) -> str:
    return LANG_CODE_TO_NAME.get(code, code)

# -----------------------------
# TEXT TRANSLATION
# -----------------------------
@app.post("/translate")
def translate_text(
    text: str = Form(...),
    target_language: str = Query(...)
):
    target_code = get_language_code(target_language)

    try:
        detected_code = detect(text)
        detected_name = get_language_name(detected_code)
    except:
        detected_name = "Unknown"

    translated_text = GoogleTranslator(
        source="auto",
        target=target_code
    ).translate(text)

    audio_file = f"speech_{uuid.uuid4()}.mp3"
    gTTS(translated_text, lang=target_code).save(audio_file)

    return {
        "detected_language": f"{detected_name} (Auto-detected)",
        "translated_text": translated_text,
        "audio_file": audio_file
    }

# -----------------------------
# VOICE FILE TRANSLATION
# -----------------------------
@app.post("/translate-voice")
async def translate_voice(
    audio: UploadFile = File(...),
    target_language: str = Query(...)
):
    target_code = get_language_code(target_language)
    detected_name = "Unknown"
    recognized_text = ""

    try:
        audio_bytes = await audio.read()
        temp_wav = f"input_{uuid.uuid4()}.wav"

        # Convert audio to WAV
        audio_segment = AudioSegment.from_file(
            io.BytesIO(audio_bytes),
            format=audio.filename.split(".")[-1]
        )
        audio_segment.set_channels(1).set_frame_rate(16000).export(temp_wav, format="wav")

        # Speech recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            audio_data = recognizer.record(source)
            try:
                recognized_text = recognizer.recognize_google(audio_data)
                # Detect spoken language
                detected_code = detect(recognized_text)
                detected_name = get_language_name(detected_code)
            except sr.UnknownValueError:
                recognized_text = ""
                detected_name = "Unknown"

        os.remove(temp_wav)

        # Translate if there is recognized text, else just empty translation
        translated_text = ""
        output_audio = ""
        if recognized_text:
            translated_text = GoogleTranslator(
                source="auto",
                target=target_code
            ).translate(recognized_text)

            output_audio = f"speech_{uuid.uuid4()}.mp3"
            gTTS(translated_text, lang=target_code).save(output_audio)

        return {
            "detected_language": f"{detected_name} (Auto-detected)",
            "recognized_text": recognized_text,
            "translated_text": translated_text,
            "audio_file": output_audio
        }

    except Exception as e:
        return {
            "detected_language": "Unknown",
            "recognized_text": "",
            "translated_text": "",
            "audio_file": "",
            "error": f"Voice translation failed: {str(e)}"
        }
