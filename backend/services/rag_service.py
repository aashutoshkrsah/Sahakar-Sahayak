import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

if os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Updated to the exact model identifier specified by the error message
model = genai.GenerativeModel('gemini-3.6-flash')

def get_answer(query: str, language: str = "en", intent: str = "general") -> dict:
    try:
        lang_instructions = {
            "kn": "Please respond in Kannada (ಕನ್ನಡ).",
            "hi": "Please respond in Hindi (हिंदी).",
            "en": "Please respond in English."
        }
        instruction = lang_instructions.get(language, "Please respond in English.")
        
        full_prompt = (
            f"You are Sahakar Sahayak, a helpful assistant for cooperative schemes. "
            f"{instruction}\n"
            f"User Intent: {intent}\n"
            f"User Query: {query}"
        )

        response = model.generate_content(full_prompt)
        answer_text = response.text if response and response.text else "No response generated."
        
        return {"answer": answer_text}
    except Exception as e:
        return {"answer": f"AI Error: {str(e)}"}