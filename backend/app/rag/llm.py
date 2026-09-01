import os
from dotenv import load_dotenv

from sarvamai import SarvamAI
from app.rag.context_builder import build_context

# ---------------------------------
# Load environment variables
# ---------------------------------

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

if not SARVAM_API_KEY:
    raise ValueError("SARVAM_API_KEY not found in .env")


# ---------------------------------
# Sarvam client
# ---------------------------------

client = SarvamAI(
    api_subscription_key=SARVAM_API_KEY
)


# ---------------------------------
# Ask Sarvam using RAG context
# ---------------------------------

def ask_sarvam(question: str, language: str = "English", top_k: int = 5) -> str:

    # Retrieve relevant government document context
    context = build_context(
        question,
        top_k=top_k
    )

    prompt = f"""
You are Sahakar Sahayak, an agricultural government-scheme assistant.

Answer the farmer's question using ONLY the information provided
in the government document context below.
Respond completely in the requested language: {language}.

Do not invent information.

If the answer is not present in the context, say (in {language}):
"I could not find this information in the available government documents."

Keep the answer simple and easy for a farmer to understand.

At the end, provide the source document and page number.

--------------------------------
GOVERNMENT DOCUMENT CONTEXT
--------------------------------

{context}

--------------------------------
FARMER QUESTION ({language})
--------------------------------

{question}

--------------------------------
ANSWER ({language})
--------------------------------
"""

    response = client.chat.completions(
        model="sarvam-105b",
        reasoning_effort=None,  # Disables deep reasoning mode so output populates message.content directly
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Safely extract response text and fallback if content is empty
    message = response.choices[0].message
    content = getattr(message, "content", None)
    
    if not content and hasattr(message, "reasoning_content"):
        content = message.reasoning_content

    return content or "I could not find this information in the available government documents."