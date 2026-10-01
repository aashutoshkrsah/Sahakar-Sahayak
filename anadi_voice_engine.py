import speech_recognition as sr
from gtts import gTTS
import os
import base64
import requests
import uuid
from pydub import AudioSegment
import time  # (added) timings for the [VOICE-IN] / [VOICE-OUT] log lines

print("=======================================================")
print("🎙️ INITIATING TRIPLE-TIER VOICE ENGINE (SARVAM -> BHASHINI -> GOOGLE) 🎙️")
print("=======================================================")

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "").strip()
BHASHINI_USER_ID = os.getenv("BHASHINI_USER_ID", "455ebbb51e-8be8-41c7-b1c4-97139e071887")
BHASHINI_API_KEY = os.getenv("BHASHINI_API_KEY", "GNSK-fU7d1X0zBT20yFRch9YBUCeZ93goVEcN1LcC1cWND_oI2FGQLqjpv6g0nEM")
BHASHINI_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

def get_google_lang_code(lang_code):
    """Maps frontend dropdown codes to Google's exact STT regional codes."""
    mapping = {"en": "en-IN", "hi": "hi-IN", "kn": "kn-IN"}
    return mapping.get(lang_code, "en-IN")


# ------------------------------------------------------------------------------
# (added) One-line voice logs. In Render -> Logs, search for:
#   VOICE-IN   who heard the user (speech -> text) and exactly what it heard
#   VOICE-OUT  who read the answer aloud (text -> speech)
#   VOICE      both
# Only these log lines were added; the engines, their order and the keys are unchanged.
# ------------------------------------------------------------------------------
def _vlog(tag, trace_id, message):
    print(f"[{tag} {trace_id}] {message}", flush=True)


def _short(text, limit=200):
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[:limit] + "..."


# ==============================================================================
# SPEECH-TO-TEXT (LISTENING): TRIPLE TIER FALLBACK
# ==============================================================================
def convert_audio_to_text(audio_file_path, lang_code="en"):
    trace_id = str(uuid.uuid4())[:8].upper()
    safe_lang = lang_code if lang_code in ["en", "hi", "kn"] else "en"
    google_lang = get_google_lang_code(safe_lang)
    wav_path = f"temp_stt_{trace_id}.wav"
    
    print(f"\n==================================================================")
    print(f"🎙️ STT INITIATED | Trace ID: {trace_id} | Target Lang: {safe_lang}")
    print(f"==================================================================")
    _t0 = time.perf_counter()
    try:
        _size_kb = round(os.path.getsize(audio_file_path) / 1024)
    except Exception:
        _size_kb = "?"
    _vlog("VOICE-IN", trace_id, f"🎙️ listening started | website language: {lang_code} | audio {_size_kb} KB | order: SARVAM -> BHASHINI -> GOOGLE")

    try:
        audio = AudioSegment.from_file(audio_file_path)
        audio.export(wav_path, format="wav")
    except Exception as e:
        print(f"[SYSTEM] ❌ FATAL ERROR processing audio file: {e}")
        _vlog("VOICE-IN", trace_id, f"💥 could not read the recording ({type(e).__name__}) -- nothing was sent to Sarvam / Bhashini / Google")
        return "", lang_code

    # ----------------------------------------------------------------------
    # TIER 1: SARVAM (Saaras v4 - Handles mixed Hindi+Kannada Native)
    # ----------------------------------------------------------------------
    print(f"\n▶️ [TIER 1] EXECUTING SARVAM STT (Model: saaras:v4 | Auto-Detect)")
    _t = time.perf_counter()
    try:
        url = "https://api.sarvam.ai/speech-to-text"
        headers = {"api-subscription-key": SARVAM_API_KEY}
        with open(wav_path, "rb") as f:
            files = {'file': ('audio.wav', f, 'audio/wav')}
            # 'unknown' forces Sarvam to auto-detect mixed languages mid-sentence
            data = {'model': 'saaras:v4', 'language_code': 'unknown'}
            response = requests.post(url, headers=headers, files=files, data=data, timeout=12)
            
        if response.status_code == 200:
            result = response.json()
            transcript = result.get("transcript", "").strip()
            detected_lang = result.get("language_code", "unknown")
            print(f"✅ [TIER 1 SUCCESS] Request {trace_id} processed.")
            print(f"🎯 RESOLVED BY: SARVAM AI | Detected Lang: {detected_lang} | Text: '{transcript}'")
            _vlog("VOICE-IN", trace_id, f"✅ heard by SARVAM in {time.perf_counter() - _t:.1f}s (total {time.perf_counter() - _t0:.1f}s) | detected: {detected_lang} | text: '{_short(transcript)}'" + ("" if transcript else " | ⚠️ Sarvam heard no words"))
            if os.path.exists(wav_path): os.remove(wav_path)
            return transcript, lang_code
        else:
            print(f"❌ [TIER 1 FAILED] Sarvam Rejected. HTTP {response.status_code}: {response.text}")
            _vlog("VOICE-IN", trace_id, f"❌ SARVAM failed in {time.perf_counter() - _t:.1f}s (HTTP {response.status_code}) -> trying BHASHINI")
    except Exception as e:
        print(f"❌ [TIER 1 FAILED] Sarvam connection error: {e}")
        _vlog("VOICE-IN", trace_id, f"❌ SARVAM failed in {time.perf_counter() - _t:.1f}s ({type(e).__name__}) -> trying BHASHINI")

    # ----------------------------------------------------------------------
    # TIER 2: BHASHINI (Government DPI Fallback)
    # ----------------------------------------------------------------------
    print(f"\n▶️ [TIER 2] EXECUTING BHASHINI STT (Dhruva ASR | Lang: {safe_lang})")
    _t = time.perf_counter()
    try:
        headers = {
            "Authorization": BHASHINI_API_KEY,
            "userID": BHASHINI_USER_ID,
            "Content-Type": "application/json"
        }
        with open(wav_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode("utf-8")
        payload = {
            "pipelineTasks": [{"taskType": "asr", "config": {"language": {"sourceLanguage": safe_lang}}}],
            "inputData": {"audio": [{"audioContent": audio_base64}]}
        }
        response = requests.post(BHASHINI_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            bhashini_text = response.json()["pipelineResponse"][0]["output"][0]["source"].strip()
            print(f"✅ [TIER 2 SUCCESS] Request {trace_id} processed.")
            print(f"🎯 RESOLVED BY: BHASHINI DHRUVA | Text: '{bhashini_text}'")
            _vlog("VOICE-IN", trace_id, f"✅ heard by BHASHINI in {time.perf_counter() - _t:.1f}s (total {time.perf_counter() - _t0:.1f}s) | language: {safe_lang} | text: '{_short(bhashini_text)}'")
            if os.path.exists(wav_path): os.remove(wav_path)
            return bhashini_text, safe_lang
        else:
            print(f"❌ [TIER 2 FAILED] Bhashini Rejected. HTTP {response.status_code}: {response.text}")
            _vlog("VOICE-IN", trace_id, f"❌ BHASHINI failed in {time.perf_counter() - _t:.1f}s (HTTP {response.status_code}) -> trying GOOGLE")
    except Exception as e:
        print(f"❌ [TIER 2 FAILED] Bhashini connection error: {e}")
        _vlog("VOICE-IN", trace_id, f"❌ BHASHINI failed in {time.perf_counter() - _t:.1f}s ({type(e).__name__}) -> trying GOOGLE")

    # ----------------------------------------------------------------------
    # TIER 3: GOOGLE (Unbreakable Final Fallback)
    # ----------------------------------------------------------------------
    print(f"\n▶️ [TIER 3] EXECUTING GOOGLE STT (Google Cloud | Lang: {google_lang})")
    _t = time.perf_counter()
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language=google_lang).strip()
        print(f"✅ [TIER 3 SUCCESS] Request {trace_id} processed.")
        print(f"🎯 RESOLVED BY: GOOGLE CLOUD | Text: '{text}'")
        _vlog("VOICE-IN", trace_id, f"✅ heard by GOOGLE in {time.perf_counter() - _t:.1f}s (total {time.perf_counter() - _t0:.1f}s) | language: {google_lang} | text: '{_short(text)}'")
        if os.path.exists(wav_path): os.remove(wav_path)
        return text, safe_lang
    except sr.UnknownValueError:
        print(f"❌ [TIER 3 FAILED] Google could not understand audio noise.")
        _vlog("VOICE-IN", trace_id, f"❌ GOOGLE could not make out any words ({time.perf_counter() - _t:.1f}s)")
    except Exception as e:
        print(f"❌ [TIER 3 FAILED] Google connection error: {e}")
        _vlog("VOICE-IN", trace_id, f"❌ GOOGLE failed in {time.perf_counter() - _t:.1f}s ({type(e).__name__})")

    # ----------------------------------------------------------------------
    # TOTAL FAILURE STATE
    # ----------------------------------------------------------------------
    if os.path.exists(wav_path): os.remove(wav_path)
    print(f"\n💥 [CRITICAL] ALL STT TIERS FAILED FOR REQUEST {trace_id}")
    _vlog("VOICE-IN", trace_id, f"💥 nobody could hear it -- Sarvam, Bhashini and Google all failed (total {time.perf_counter() - _t0:.1f}s); the user gets an empty result")
    return "", safe_lang


# ==============================================================================
# LISTENING FIX: farm words that speech-to-text often mishears
# ==============================================================================
import re as _re

_HEARD_FIXES = [
    # "mandi prices" heard as "Monday prices" (they sound alike in Indian English)
    (_re.compile(r"\bmonday(?=\s+(?:prices?|rates?|bhav|bhaav|bhaw|market|yard|ka|ke|ki|me|mein|mai)\b)", _re.I), "mandi"),
    (_re.compile(r"\bmondays(?=\s+(?:prices?|rates?)\b)", _re.I), "mandi"),
    (_re.compile(r"\bmandy(?=\s+(?:prices?|rates?|bhav|bhaav|market|yard)\b)", _re.I), "mandi"),
    (_re.compile(r"\bkis+aa?n\b", _re.I), "Kisan"),
]


def fix_heard_words(text, trace_id="-"):
    """Correct a few farm words the speech-to-text step often mishears (e.g. 'Monday prices' -> 'mandi prices')."""
    fixed = text or ""
    for pattern, repl in _HEARD_FIXES:
        fixed = pattern.sub(repl, fixed)
    if fixed != (text or ""):
        _vlog("VOICE-IN", trace_id, f"🛠️ farm-word fix: {_short(text, 120)!r} -> {_short(fixed, 120)!r}")
    return fixed


# ==============================================================================
# TEXT-TO-SPEECH (SPEAKING)
#   English / Hindi / Kannada:  SARVAM (Bulbul, Indian voices) -> BHASHINI (unchanged) -> GOOGLE (Indian accent)
#   Nepali:                     GOOGLE (real Nepali voice) -> BHASHINI Hindi voice -> SARVAM Hindi voice
#                               (Sarvam and Bhashini have no Nepali voice; Nepali uses the same letters as Hindi)
# SARVAM_TTS_API_KEY = a separate Sarvam key just for the voice (falls back to SARVAM_API_KEY).
# ==============================================================================
SARVAM_TTS_API_KEY = (os.getenv("SARVAM_TTS_API_KEY", "") or "").strip() or SARVAM_API_KEY
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"
SARVAM_TTS_SPEAKER = os.getenv("SARVAM_TTS_SPEAKER", "priya").strip().lower()
SARVAM_TTS_LANG = {"en": "en-IN", "hi": "hi-IN", "kn": "kn-IN"}
SARVAM_TTS_MAX = 2400          # Sarvam bulbul:v3 takes up to 2,500 characters per request

# Only for the BACKUP voices in English mode (Bhashini / Google read English spelling literally):
# the words are spelled the way they sound. The text on screen and the text sent to Sarvam never change.
_PRONOUNCE = {
    "mandi": "mundee", "mandis": "mundees", "kisan": "kisaan", "krishi": "krishee",
    "yojana": "yojnaa", "bima": "beema", "fasal": "fussal", "samman": "summaan", "nidhi": "nidhee",
}
_PRONOUNCE_RE = _re.compile(r"\b(" + "|".join(_PRONOUNCE) + r")\b", _re.I)


def _for_backup_voice(text, lang):
    if lang != "en":
        return text
    return _PRONOUNCE_RE.sub(lambda m: _PRONOUNCE[m.group(1).lower()], text)


def _chunks(text, limit=SARVAM_TTS_MAX):
    """Split long answers at sentence ends so each piece fits one Sarvam request."""
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return [text]
    parts, cur = [], ""
    for sent in _re.split(r"(?<=[.!?।])\s+", text):
        while len(sent) > limit:                       # a very long sentence: hard cut
            parts.append(sent[:limit]); sent = sent[limit:]
        if len(cur) + len(sent) + 1 > limit:
            parts.append(cur); cur = sent
        else:
            cur = f"{cur} {sent}".strip()
    if cur:
        parts.append(cur)
    return [p for p in parts if p.strip()]


def _sarvam_tts(text, lang):
    """Sarvam Bulbul voice -> base64 MP3. Raises on failure."""
    if not SARVAM_TTS_API_KEY:
        raise RuntimeError("no SARVAM_TTS_API_KEY / SARVAM_API_KEY")
    code = SARVAM_TTS_LANG[lang]
    headers = {"api-subscription-key": SARVAM_TTS_API_KEY, "Content-Type": "application/json"}
    pieces = []
    for chunk in _chunks(text):
        body = {"text": chunk, "language_code": code, "model": "bulbul:v3", "speaker": SARVAM_TTS_SPEAKER,
                "output_audio_codec": "mp3"}
        r = requests.post(SARVAM_TTS_URL, headers=headers, json=body, timeout=15)
        if r.status_code in (400, 422):                 # older API shape, kept as a safety net
            r = requests.post(SARVAM_TTS_URL, headers=headers, timeout=15,
                              json={"inputs": [chunk], "target_language_code": code, "speaker": "anushka",
                                    "model": "bulbul:v2"})
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
        audios = (r.json() or {}).get("audios") or []
        if not audios:
            raise RuntimeError("no audio in Sarvam's reply")
        pieces.append(base64.b64decode("".join(audios)))
    if len(pieces) == 1:
        return base64.b64encode(pieces[0]).decode("utf-8")
    if all(p[:3] == b"ID3" or p[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2") for p in pieces):
        return base64.b64encode(b"".join(pieces)).decode("utf-8")   # MP3 pieces can simply be joined
    import io                                                         # WAV pieces: join properly
    joined = AudioSegment.empty()
    for p in pieces:
        joined += AudioSegment.from_file(io.BytesIO(p))
    out = io.BytesIO()
    joined.export(out, format="mp3")
    return base64.b64encode(out.getvalue()).decode("utf-8")


def _bhashini_tts(text, lang):
    """Bhashini (Dhruva) voice -- request exactly as before (same keys, female voice). Raises on failure."""
    headers = {
        "Authorization": BHASHINI_API_KEY,
        "userID": BHASHINI_USER_ID,
        "Content-Type": "application/json"
    }
    payload = {
        "pipelineTasks": [{"taskType": "tts", "config": {"language": {"sourceLanguage": lang}, "gender": "female"}}],
        "inputData": {"input": [{"source": text}]}
    }
    response = requests.post(BHASHINI_URL, headers=headers, json=payload, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:200]}")
    return response.json()["pipelineResponse"][0]["audio"][0]["audioContent"]


def _google_tts(text, lang, trace_id):
    """Google voice (gTTS). English uses the Indian accent (tld co.in). Raises on failure."""
    temp_filename = f"temp_tts_{trace_id}.mp3"
    try:
        tts = gTTS(text=text, lang=lang, tld="co.in", slow=False) if lang == "en" else gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_filename)
        with open(temp_filename, "rb") as audio_file:
            return base64.b64encode(audio_file.read()).decode('utf-8')
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


def convert_text_to_audio(text_string, lang_code="en"):
    trace_id = str(uuid.uuid4())[:8].upper()
    lang = lang_code if lang_code in ["en", "hi", "kn", "ne"] else "en"
    if lang == "ne":
        order = [("GOOGLE", lambda: _google_tts(text_string, "ne", trace_id), "Nepali voice"),
                 ("BHASHINI", lambda: _bhashini_tts(text_string, "hi"), "Hindi voice (same letters as Nepali)"),
                 ("SARVAM", lambda: _sarvam_tts(text_string, "hi"), "Hindi voice (same letters as Nepali)")]
    else:
        backup_text = _for_backup_voice(text_string, lang)
        order = [("SARVAM", lambda: _sarvam_tts(text_string, lang), f"Bulbul · {SARVAM_TTS_SPEAKER}"),
                 ("BHASHINI", lambda: _bhashini_tts(backup_text, lang), "Dhruva · female"),
                 ("GOOGLE", lambda: _google_tts(backup_text, lang, trace_id), "gTTS" + (" · Indian accent" if lang == "en" else ""))]

    print(f"\n==================================================================")
    print(f"🗣️ TTS INITIATED | Trace ID: {trace_id} | Target Lang: {lang}")
    print(f"==================================================================")
    _t0 = time.perf_counter()
    _vlog("VOICE-OUT", trace_id, f"🔊 speaking started | language: {lang} | {len(text_string or '')} characters | "
                                 f"order: {' -> '.join(name for name, _, _ in order)}")
    for i, (name, speak, detail) in enumerate(order):
        _t = time.perf_counter()
        print(f"\n▶️ [TIER {i + 1}] EXECUTING {name} TTS ({detail} | Lang: {lang})")
        try:
            audio = speak()
            if not audio:
                raise RuntimeError("empty audio")
            print(f"✅ [TIER {i + 1} SUCCESS] Request {trace_id} processed.")
            print(f"🎯 RESOLVED BY: {name}")
            _vlog("VOICE-OUT", trace_id, f"✅ spoken by {name} ({detail}) in {time.perf_counter() - _t:.1f}s "
                                         f"(total {time.perf_counter() - _t0:.1f}s)")
            return audio
        except Exception as e:
            nxt = order[i + 1][0] if i + 1 < len(order) else None
            print(f"❌ [TIER {i + 1} FAILED] {name}: {str(e)[:200]}")
            _vlog("VOICE-OUT", trace_id, f"❌ {name} failed in {time.perf_counter() - _t:.1f}s ({type(e).__name__}: {str(e)[:120]})")
            if nxt:
                _vlog("VOICE-OUT", trace_id, f"🔀 HANDOVER [voice] {name} failed → {nxt} takes charge")

    print(f"\n💥 [CRITICAL] ALL TTS TIERS FAILED FOR REQUEST {trace_id}")
    _vlog("VOICE-OUT", trace_id, "💥 nobody could read it aloud -- every voice failed; no audio is played")
    return None
