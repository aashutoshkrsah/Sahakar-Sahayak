import whisper
from gtts import gTTS
import os
import base64

# The script will automatically download the 'base' model from the internet here!
print("Loading Speech Engine...")
try:
    stt_model = whisper.load_model("base")
except Exception as e:
    print(f"Warning: Could not load Whisper model. Error: {e}")

def convert_audio_to_text(audio_file_path):
    """
    Takes an audio file, detects if it's Hindi, English, or Kannada, 
    and returns the text string and language code.
    """
    try:
        result = stt_model.transcribe(audio_file_path)
        return result["text"].strip(), result["language"]
    except Exception as e:
        return f"Error understanding audio: {e}", "en"

def convert_text_to_audio(text_string, lang_code):
    """
    Takes Vinutha's LLM answer and converts it into a spoken audio file (base64).
    """
    try:
        # gTTS supports 'hi' (Hindi), 'kn' (Kannada), and 'en' (English)
        supported_langs = ["hi", "kn", "en"]
        safe_lang = lang_code if lang_code in supported_langs else "en"
        
        # Generate the voice
        tts = gTTS(text=text_string, lang=safe_lang, slow=False)
        temp_filename = "server_response.mp3"
        tts.save(temp_filename)
        
        # Convert audio to a string so Aashutosh's frontend can play it
        with open(temp_filename, "rb") as audio_file:
            encoded_audio = base64.b64encode(audio_file.read()).decode('utf-8')
            
        # Clean up the file so the server doesn't get cluttered
        os.remove(temp_filename)
        return encoded_audio
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return None
