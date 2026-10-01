"""
Small talk: "hi", "what is your name?", "who are you?", "thank you", "bye" get a friendly built-in reply
in the user's language -- no document search and no AI call (so they are never answered from a PDF by mistake).

Only SHORT messages that are clearly small talk are caught; anything mentioning farming, schemes, loans,
societies etc. goes through the normal answer path.
"""
import re

from backend.services.reqlog import log

MAX_LEN = 60

_GREETING = re.compile(
    r"^\s*(hi+|hello+|hey+|hii+|namaste|namaskar(a|am)?|namaskaara|vanakkam|good\s+(morning|afternoon|evening|night)|"
    r"नमस्ते|नमस्कार|प्रणाम|ನಮಸ್ಕಾರ|ನಮಸ್ತೆ|हेलो|हलो)[\s!.,?]*(sir|madam|ji|bhai|there|sahayak)?[\s!.,?]*$", re.I)
_THANKS = re.compile(
    r"^\s*(thanks?|thank\s*you|thank\s*u|thx|ok(ay)?\s*thanks?|dhanyavaa?d|shukriya|dhanyawad|धन्यवाद|शुक्रिया|"
    r"ಧನ್ಯವಾದ(ಗಳು)?|धन्यवाद छ)[\s!.,]*(sir|madam|ji|so much|a lot|very much)?[\s!.,]*$", re.I)
_BYE = re.compile(r"^\s*(bye+|good\s*bye|see\s*you|alvida|अलविदा|फिर मिलेंगे|ಹೋಗಿ ಬರುತ್ತೇನೆ|बिदा)[\s!.,]*$", re.I)
_WHO = re.compile(
    r"(what('?s| is)\s+your\s+name|who\s+are\s+you(?=[\s?!.]*$)|your\s+name\??$|"
    r"what\s+can\s+you\s+do(?=[\s?!.]*$)|what\s+do\s+you\s+do(?=[\s?!.]*$)|how\s+are\s+you(?=[\s?!.]*$)|"
    r"are\s+you\s+(a\s+)?(bot|robot|human|ai)|introduce\s+yourself|aap\s+kaun|tum\s+kaun|aapka\s+naam|tumhara\s+naam|"
    r"आप कौन|तुम कौन|आपका नाम|तुम्हारा नाम|आप क्या कर सकते|ನೀನು ಯಾರು|ನೀವು ಯಾರು|ನಿಮ್ಮ ಹೆಸರು|ನಿನ್ನ ಹೆಸರು|"
    r"तपाईं को हो|तिमी को हौ|तपाईंको नाम|तिम्रो नाम)", re.I)

INTRO = {
    "en": "Namaste! I am Sahakar Sahayak, a helper for farmers and cooperative society members. You can ask me about "
          "PM-KISAN, crop insurance (PMFBY), Kisan Credit Card loans, cooperative society rules, elections, audits, "
          "and mandi prices — in English, Hindi, Kannada or Nepali, by typing or by voice.",
    "hi": "नमस्ते! मैं सहकार सहायक हूँ — किसानों और सहकारी समितियों के सदस्यों का सहायक। आप मुझसे पीएम-किसान, फसल बीमा "
          "(PMFBY), किसान क्रेडिट कार्ड ऋण, सहकारी समिति के नियम, चुनाव, ऑडिट और मंडी भाव के बारे में पूछ सकते हैं — "
          "हिंदी, अंग्रेज़ी, कन्नड़ या नेपाली में, लिखकर या बोलकर।",
    "kn": "ನಮಸ್ಕಾರ! ನಾನು ಸಹಕಾರ ಸಹಾಯಕ — ರೈತರು ಮತ್ತು ಸಹಕಾರ ಸಂಘದ ಸದಸ್ಯರ ಸಹಾಯಕ. ಪಿಎಂ-ಕಿಸಾನ್, ಬೆಳೆ ವಿಮೆ (PMFBY), "
          "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ ಸಾಲ, ಸಹಕಾರ ಸಂಘದ ನಿಯಮಗಳು, ಚುನಾವಣೆ, ಲೆಕ್ಕಪರಿಶೋಧನೆ ಮತ್ತು ಮಂಡಿ ಬೆಲೆಗಳ ಬಗ್ಗೆ ಕೇಳಬಹುದು — "
          "ಕನ್ನಡ, ಇಂಗ್ಲಿಷ್, ಹಿಂದಿ ಅಥವಾ ನೇಪಾಳಿಯಲ್ಲಿ, ಬರೆದು ಅಥವಾ ಮಾತನಾಡಿ.",
    "ne": "नमस्ते! म सहकार सहायक हुँ — किसान र सहकारी संस्थाका सदस्यहरूको सहयोगी। तपाईं मलाई पीएम-किसान, बाली बीमा "
          "(PMFBY), किसान क्रेडिट कार्ड ऋण, सहकारी संस्थाका नियम, चुनाव, लेखापरीक्षण र मण्डी भाउबारे सोध्न सक्नुहुन्छ — "
          "नेपाली, हिन्दी, अंग्रेजी वा कन्नडमा, लेखेर वा बोलेर।",
}
THANKS = {
    "en": "You're welcome! Ask me anytime about farmer schemes or your cooperative society. 🙏",
    "hi": "आपका स्वागत है! किसान योजनाओं या अपनी सहकारी समिति के बारे में कभी भी पूछिए। 🙏",
    "kn": "ಸ್ವಾಗತ! ರೈತ ಯೋಜನೆಗಳು ಅಥವಾ ನಿಮ್ಮ ಸಹಕಾರ ಸಂಘದ ಬಗ್ಗೆ ಯಾವಾಗ ಬೇಕಾದರೂ ಕೇಳಿ. 🙏",
    "ne": "स्वागत छ! किसान योजना वा तपाईंको सहकारी संस्थाबारे जुनसुकै बेला सोध्नुहोस्। 🙏",
}
BYE = {
    "en": "Goodbye! Wishing you a good harvest. 🌾",
    "hi": "फिर मिलेंगे! आपकी फसल अच्छी हो। 🌾",
    "kn": "ಮತ್ತೆ ಸಿಗೋಣ! ನಿಮ್ಮ ಬೆಳೆ ಚೆನ್ನಾಗಿರಲಿ. 🌾",
    "ne": "फेरि भेटौंला! तपाईंको बाली राम्रो होस्। 🌾",
}


def _kind(text: str):
    t = (text or "").strip()
    if not t or len(t) > MAX_LEN:
        return None
    from backend.services.rag_service import _FARM_WORDS
    if _FARM_WORDS.search(t):
        return None
    if _THANKS.match(t):
        return "thanks"
    if _BYE.match(t):
        return "bye"
    if _GREETING.match(t) or _WHO.search(t):
        return "intro"
    return None


def small_talk(text: str, language: str):
    """A full /query result for small talk, or None for a real question."""
    kind = _kind(text)
    if not kind:
        return None
    replies = {"intro": INTRO, "thanks": THANKS, "bye": BYE}[kind]
    from backend.services.rag_service import _build_search_report
    report = _build_search_report([], {})
    report["used_documents"] = False
    log("SMALLTALK", f"👋 small talk ({kind}) -- friendly built-in reply, no search, no AI")
    return {
        "answer": replies.get(language, replies["en"]), "language": language, "intent": "small_talk",
        "sources": [], "confidence": 0.0, "answer_source": "general", "trust_level": "general",
        "answered_by": "built_in", "search_report": report, "action_url": None, "qr_code_base64": None,
        "helplines": [], "prices": None,
    }
