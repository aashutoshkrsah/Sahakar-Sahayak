import speech_recognition as sr
from gtts import gTTS
import os
import base64
from pydub import AudioSegment

print("Loading lightweight Speech Engine...")

def convert_audio_to_text(audio_file_path):
    """
    Takes ANY audio file, converts it to WAV, and gets text using Google STT.
    """
    recognizer = sr.Recognizer()
    wav_path = "temp_converted.wav"
    
    try:
        # Trap 1 Fix: Force convert whatever frontend sends into a clean .wav file
        audio = AudioSegment.from_file(audio_file_path)
        audio.export(wav_path, format="wav")
        
        # Now read the clean wav file
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            
        # Using Indian English accent for better regional recognition
        text = recognizer.recognize_google(audio_data, language="en-IN")
        
        # Clean up the temp file
        if os.path.exists(wav_path):
            os.remove(wav_path)
            
        return text.strip(), "en"
        
    except sr.UnknownValueError:
        if os.path.exists(wav_path): os.remove(wav_path)
        return "Sorry, the audio was not clear enough.", "en"
    except Exception as e:
        if os.path.exists(wav_path): os.remove(wav_path)
        return f"STT Error: {e}", "en"


def convert_text_to_audio(text_string, lang_code):
    """
    Converts LLM text to spoken audio.
    """
    try:
        supported_langs = ["hi", "kn", "en"]
        safe_lang = lang_code if lang_code in supported_langs else "en"
        
        tts = gTTS(text=text_string, lang=safe_lang, slow=False)
        temp_filename = "server_response.mp3"
        tts.save(temp_filename)
        
        with open(temp_filename, "rb") as audio_file:
            encoded_audio = base64.b64encode(audio_file.read()).decode('utf-8')
            
        os.remove(temp_filename)
        return encoded_audio
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return None