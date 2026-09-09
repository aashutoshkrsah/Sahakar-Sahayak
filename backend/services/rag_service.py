import os
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    if os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    genai = None
    model = None


def get_answer(query: str, language: str = "en", intent: str = "general") -> dict:
    if model is None:
        return {
            "answer": "Sahakar Sahayak assistant is active. Please configure GEMINI_API_KEY to enable full generative responses."
        }

    try:
        lang_instructions = {
            "kn": "Please respond in Kannada (ಕನ್ನಡ).",
            "hi": "Please respond in Hindi (हिंदी).",
            "ne": "Please respond in Nepali (नेपाली).",
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