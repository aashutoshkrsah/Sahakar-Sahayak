import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

def get_answer(query: str, language: str = "en", intent: str = "general") -> dict:
    try:
        lang_instructions = {
            "kn": "Please respond in Kannada (ಕನ್ನಡ).",
            "hi": "Please respond in Hindi (हिंदी).",
            "en": "Please respond in English."
        }
        instruction = lang_instructions.get(language, "Please respond in English.")
        
        full_prompt = (
            f"You are Sahakar Sahayak, a helpful assistant for cooperative schemes and citizen queries. "
            f"{instruction}\n"
            f"User Intent: {intent}\n"
            f"User Query: {query}"
        )

        response = model.generate_content(full_prompt)
        answer_text = response.text if response and response.text else "No response generated."
        
        return {"answer": answer_text}
    except Exception as e:
        return {"answer": f"AI Connection Error: {str(e)}"}