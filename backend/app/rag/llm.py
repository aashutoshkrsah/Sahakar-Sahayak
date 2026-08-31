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

def ask_sarvam(question, top_k=5):

    # Retrieve relevant government document context
    context = build_context(
        question,
        top_k=top_k
    )

    prompt = f"""
You are Sahakar Sahayak, an agricultural government-scheme assistant.

Answer the farmer's question using ONLY the information provided
in the government document context below.

Do not invent information.

If the answer is not present in the context, say:
"I could not find this information in the available government documents."

Keep the answer simple and easy for a farmer to understand.

At the end, provide the source document and page number.

--------------------------------
GOVERNMENT DOCUMENT CONTEXT
--------------------------------

{context}

--------------------------------
FARMER QUESTION
--------------------------------

{question}

--------------------------------
ANSWER
--------------------------------
"""

    response = client.chat.completions(
        model="sarvam-105b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# ---------------------------------
# Test
# ---------------------------------

if __name__ == "__main__":

    questions = [
    "What is PM-KISAN?",
    "How much money does a farmer receive under PM-KISAN?",
    "Who is eligible for PM-KISAN?",
    "Who is excluded from PM-KISAN?",
    "How are PM-KISAN benefits transferred?",
    "Are income tax payers eligible for PM-KISAN?",
    "How many installments are provided under PM-KISAN?"
]

    for question in questions:

        print("\n" + "=" * 60)
        print("QUESTION")
        print("=" * 60)

        print(question)

        print("\n" + "=" * 60)
        print("SARVAM ANSWER")
        print("=" * 60)

        try:

            answer = ask_sarvam(question)

            print(answer)

        except Exception as e:

            print("ERROR:")
            print(e)