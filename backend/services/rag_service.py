import os
import google.generativeai as genai

# Your Gemini API key
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Using Gemini 1.5 Flash for fast, ChatGPT-like responses
model = genai.GenerativeModel('gemini-1.5-flash')

def get_answer(query: str):
    try:
        response = model.generate_content(query)
        return response.text
    except Exception as e:
        return f"AI Connection Error: {str(e)}"