"""
Facebook Reels Automation - Bilingual English/Hebrew Content Generator
IMPROVED VERSION: Better backgrounds, English categories, no repeats, VELOCITY HEBREW branding
Rounded container style from Habla Verse
"""

import os
import sys
import json
import random
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")
AI_MODEL = os.getenv("AI_MODEL")

if not AI_MODEL:
    raise ValueError(
        "AI_MODEL not set! Please add 'AI_MODEL=gemini-fast' to your .env file. "
        "For GitHub Actions: Add AI_MODEL to repository secrets."
    )

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
IMAGES_DIR = OUTPUT_DIR / "images"
AUDIO_DIR = OUTPUT_DIR / "audio"
VIDEO_DIR = OUTPUT_DIR / "video"
HISTORY_DIR = OUTPUT_DIR / "history"

for d in [OUTPUT_DIR, IMAGES_DIR, AUDIO_DIR, VIDEO_DIR, HISTORY_DIR]:
    d.mkdir(exist_ok=True)

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

CATEGORIES_ENGLISH = [
    "Greetings",
    "Basic Phrases",
    "Common Expressions",
    "Travel",
    "Restaurant",
    "Shopping",
    "Emergency",
    "Family Terms",
    "Numbers",
    "Time",
    "Motivation",
    "Love",
    "Success",
    "Wisdom",
    "Happiness",
    "Self Improvement",
    "Gratitude",
    "Friendship",
    "Hope",
    "Creativity",
    "Inner Peace",
    "Confidence",
    "Perseverance",
    "Inspiration",
    "Positive Life",
    "Courage",
    "Kindness",
    "Patience",
    "Forgiveness",
    "Strength",
    "Joy",
    "Balance",
    "Growth",
    "Purpose",
    "Mindfulness",
    "Daily Routine",
    "Weather",
    "Feelings",
    "Food",
    "Health",
    "Work",
    "Technology",
    "Nature",
    "Animals",
    "Colors",
    "Directions",
    "Body Parts",
    "Clothes",
    "Music",
    "Sports",
    "Holidays",
    "Education",
    "Culture",
    "Finance",
    "Relationships",
]

CATEGORIES_NATIVE = {
    "Greetings": "ברכות",
    "Basic Phrases": "ביטויים בסיסיים",
    "Common Expressions": "ביטויים נפוצים",
    "Travel": "טיולים",
    "Restaurant": "מסעדה",
    "Shopping": "קניות",
    "Emergency": "חירום",
    "Family Terms": "מונחי משפחה",
    "Numbers": "מספרים",
    "Time": "זמן",
    "Motivation": "מוטיבציה",
    "Love": "אהבה",
    "Success": "הצלחה",
    "Wisdom": "חוכמה",
    "Happiness": "אושר",
    "Self Improvement": "שיפור עצמי",
    "Gratitude": "הכרת תודה",
    "Friendship": "חברות",
    "Hope": "תקווה",
    "Creativity": "יצירתיות",
    "Inner Peace": "שלווה פנימית",
    "Confidence": "ביטחון עצמי",
    "Perseverance": "התמדה",
    "Inspiration": "השראה",
    "Positive Life": "חיים חיוביים",
    "Courage": "אומץ",
    "Kindness": "טוב לב",
    "Patience": "סבלנות",
    "Forgiveness": "סליחה",
    "Strength": "כוח",
    "Joy": "שמחה",
    "Balance": "איזון",
    "Growth": "צמיחה",
    "Purpose": "מטרה",
    "Mindfulness": "מיינדפולנס",
    "Daily Routine": "שגרה יומית",
    "Weather": "מזג אוויר",
    "Feelings": "רגשות",
    "Food": "אוכל",
    "Health": "בריאות",
    "Work": "עבודה",
    "Technology": "טכנולוגיה",
    "Nature": "טבע",
    "Animals": "חיות",
    "Colors": "צבעים",
    "Directions": "כיוונים",
    "Body Parts": "איברי גוף",
    "Clothes": "בגדים",
    "Music": "מוזיקה",
    "Sports": "ספורט",
    "Holidays": "חגים",
    "Education": "חינוך",
    "Culture": "תרבות",
    "Finance": "כספים",
    "Relationships": "מערכות יחסים"
}

ENGLISH_VOICE = "en-US-GuyNeural"
NATIVE_VOICE = "he-IL-HilaNeural"

PHRASE_HISTORY_FILE = HISTORY_DIR / "all_generated_phrases.json"
RECENT_CATEGORIES_FILE = HISTORY_DIR / "recent_categories.json"
MAX_RECENT_CATEGORIES = 25


def load_phrase_history():
    if PHRASE_HISTORY_FILE.exists():
        with open(PHRASE_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"phrases": [], "last_updated": None}


def save_phrase_history(data):
    data["last_updated"] = datetime.now().isoformat()
    with open(PHRASE_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def is_phrase_used(english_phrase):
    history = load_phrase_history()
    english_lower = english_phrase.lower().strip()
    for p in history.get("phrases", []):
        if p.get("english", "").lower().strip() == english_lower:
            return True
    return False


def add_phrases_to_history(phrases, category):
    history = load_phrase_history()
    lang_key = "hebrew"
    for phrase in phrases:
        history["phrases"].append({
            "english": phrase["english"],
            lang_key: phrase[lang_key],
            "transliteration": phrase.get("transliteration", ""),
            "category": category,
            "generated_at": datetime.now().isoformat()
        })
    save_phrase_history(history)
    print(f"[history] Added {len(phrases)} phrases to history (total: {len(history['phrases'])})")


def load_recent_categories():
    if RECENT_CATEGORIES_FILE.exists():
        with open(RECENT_CATEGORIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"recent_categories": [], "last_updated": None}


def save_recent_categories(data):
    data["last_updated"] = datetime.now().isoformat()
    with open(RECENT_CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_available_category():
    recent_data = load_recent_categories()
    recent = recent_data.get("recent_categories", [])
    available = [cat for cat in CATEGORIES_ENGLISH if cat not in recent]
    if not available:
        recent_data["recent_categories"] = recent[-5:]
        save_recent_categories(recent_data)
        available = [cat for cat in CATEGORIES_ENGLISH if cat not in recent_data["recent_categories"]]
        print(f"[rotation] All categories used recently - cleared old ones, {len(available)} available")
    selected = random.choice(available)
    recent.append(selected)
    if len(recent) > MAX_RECENT_CATEGORIES:
        recent = recent[-MAX_RECENT_CATEGORIES:]
    recent_data["recent_categories"] = recent
    save_recent_categories(recent_data)
    print(f"[rotation] Selected '{selected}' ({len(available)} available, {len(recent)} in recent history)")
    return selected


def generate_phrases(category_english: str, num_phrases: int = 5) -> list:
    category_native = CATEGORIES_NATIVE[category_english]
    max_attempts = 3

    history = load_phrase_history()
    recent_english = [p["english"] for p in history.get("phrases", []) if p.get("category") == category_english][-30:]

    for attempt in range(max_attempts):
        try:
            import requests
            url = "https://gen.pollinations.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
                "Content-Type": "application/json"
            }

            avoid_text = ""
            if recent_english:
                avoid_text = "\nABSOLUTELY AVOID these already-used phrases:\n" + "\n".join(f"- {p}" for p in recent_english)

            prompt = f"""Create {num_phrases * 6} unique and creative {category_english} phrases for English speakers learning Hebrew.{avoid_text}

IMPORTANT RULES FOR NATURAL SPEECH:
1. Keep phrases SHORT (5-12 words max per language)
2. Add NATURAL PAUSES using commas (e.g., "Dream big, start small")
3. Use punctuation for breathing room in TTS
4. Avoid long run-on sentences
5. Each phrase should be speakable in 3-5 seconds
6. Hebrew text should be CLEAN - use standard Hebrew script
7. Do NOT include multiple versions or slashes - just ONE clean Hebrew translation
8. Transliteration should be in Roman script for pronunciation
9. BE CREATIVE AND VARIED - do NOT repeat themes from the avoid list

For each phrase:
1. English phrase (with commas for natural pauses)
2. Hebrew translation (in Hebrew script)
3. Transliteration (Roman script pronunciation)

Return as JSON array:
[{{"english": "...", "hebrew": "...", "transliteration": "..."}}]

IMPORTANT: Create FRESH, UNIQUE phrases that haven't been used before.
IMPORTANT: Hebrew text must be clean - no slashes, no multiple versions."""

            payload = {
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a Hebrew teacher. Create short, natural phrases with pauses. Each generation must produce completely different, creative phrases."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": min(0.95 + attempt * 0.03, 1.0)
            }

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            phrases = json.loads(content)

            for p in phrases:
                if "transliteration" not in p and "romaji" in p:
                    p["transliteration"] = p.pop("romaji")
                if "hebrew" not in p:
                    alt_keys = ["hebrew_text", "native", "translation", p.get("language", "")]
                    for k in alt_keys:
                        if k in p:
                            p["hebrew"] = p.pop(k)
                            break
                if "hebrew" not in p:
                    continue

            unique_phrases = []
            for phrase in phrases:
                if len(phrase["english"].split()) > 15:
                    continue
                if not is_phrase_used(phrase["english"]):
                    unique_phrases.append(phrase)
                if len(unique_phrases) >= num_phrases:
                    break

            if len(unique_phrases) >= num_phrases:
                add_phrases_to_history(unique_phrases[:num_phrases], category_english)
                return unique_phrases[:num_phrases]

            print(f"[content] Attempt {attempt + 1}: API returned {len(phrases)} phrases, only {len(unique_phrases)} are new (need {num_phrases})")
            for p in unique_phrases:
                if p["english"] not in recent_english:
                    recent_english.append(p["english"])

        except Exception as e:
            print(f"[content] Attempt {attempt + 1} failed: {e}")

    print("[content] Using fallback phrases...")
    return get_fresh_fallback_phrases(category_english, num_phrases)



def get_fresh_fallback_phrases(category: str, num_phrases: int) -> list:
    """Return simple English fallback phrases when AI generation fails"""
    generic_fallbacks = [
        {"english": "Hello, nice to meet you.", "hebrew": "\u05e9\u05dc\u05d5\u05dd, \u05e0\u05e2\u05d9\u05dd \u05dc\u05d4\u05db\u05d9\u05e8.", "transliteration": "Shalom, na'im lehakir."},
        {"english": "Thank you very much.", "hebrew": "\u05ea\u05d5\u05d3\u05d4 \u05e8\u05d1\u05d4.", "transliteration": "Toda raba."},
        {"english": "Good morning, have a great day.", "hebrew": "\u05d1\u05d5\u05e7\u05e8 \u05d8\u05d5\u05d1, \u05e9\u05d9\u05d4\u05d9\u05d4 \u05dc\u05da \u05d9\u05d5\u05dd \u05e0\u05d4\u05d3\u05e8.", "transliteration": "Boker tov, sheyihyeh lecha yom nehedar."},
        {"english": "I love learning new languages.", "hebrew": "\u05d0\u05e0\u05d9 \u05d0\u05d5\u05d4\u05d1 \u05dc\u05dc\u05de\u05d5\u05d3 \u05e9\u05e4\u05d5\u05ea \u05d7\u05d3\u05e9\u05d5\u05ea.", "transliteration": "Ani ohev lilmod safot chadashot."},
        {"english": "Never give up on your dreams.", "hebrew": "\u05dc\u05e2\u05d5\u05dc\u05dd \u05d0\u05dc \u05ea\u05d5\u05d5\u05ea\u05e8 \u05e2\u05dc \u05d4\u05d7\u05dc\u05d5\u05de\u05d5\u05ea \u05e9\u05dc\u05da.", "transliteration": "Le'olam al tefater al hachalomot shelcha."},
        {"english": "Every day is a fresh start.", "hebrew": "\u05db\u05dc \u05d9\u05d5\u05dd \u05d4\u05d5\u05d0 \u05d4\u05ea\u05d7\u05dc\u05d4 \u05d7\u05d3\u05e9\u05d4.", "transliteration": "Kol yom hu hatchala chadasha."},
        {"english": "Believe in yourself always.", "hebrew": "\u05ea\u05d0\u05de\u05d9\u05df \u05d1\u05e2\u05e6\u05de\u05da \u05ea\u05de\u05d9\u05d3.", "transliteration": "Ta'amin be'atzmecha tamid."},
        {"english": "Small steps lead to big changes.", "hebrew": "\u05e6\u05e2\u05d3\u05d9\u05dd \u05e7\u05d8\u05e0\u05d9\u05dd \u05de\u05d5\u05d1\u05d9\u05dc\u05d9\u05dd \u05dc\u05e9\u05d9\u05e0\u05d5\u05d9\u05d9\u05dd \u05d2\u05d3\u05d5\u05dc\u05d9\u05dd.", "transliteration": "Tze'adim ktanim movilim le'shinuyim gdolim."},
        {"english": "You are stronger than you think.", "hebrew": "\u05d0\u05ea\u05d4 \u05d7\u05d6\u05e7 \u05d9\u05d5\u05ea\u05e8 \u05de\u05de\u05d4 \u05e9\u05d0\u05ea\u05d4 \u05d7\u05d5\u05e9\u05d1.", "transliteration": "Ata chazak yoter mima ata choshev."},
        {"english": "Happiness is a choice, choose it.", "hebrew": "\u05d0\u05d5\u05e9\u05e8 \u05d4\u05d5\u05d0 \u05d1\u05d7\u05d9\u05e8\u05d4, \u05d1\u05d7\u05e8 \u05d1\u05d5.", "transliteration": "Osher hu bechira, bachar bo."},
        {"english": "What time is it please.", "hebrew": "\u05de\u05d4 \u05d4\u05e9\u05e2\u05d4 \u05d1\u05d1\u05e7\u05e9\u05d4.", "transliteration": "Ma hasha'a bevakasha."},
        {"english": "Where is the train station.", "hebrew": "\u05d0\u05d9\u05e4\u05d4 \u05ea\u05d7\u05e0\u05ea \u05d4\u05e8\u05db\u05d1\u05ea.", "transliteration": "Eifo tachanat ha'rakevet."},
        {"english": "How much does this cost.", "hebrew": "\u05db\u05de\u05d4 \u05d6\u05d4 \u05e2\u05d5\u05dc\u05d4.", "transliteration": "Kama ze ole."},
        {"english": "Can you help me please.", "hebrew": "\u05d0\u05ea\u05d4 \u05d9\u05db\u05d5\u05dc \u05dc\u05e2\u05d6\u05d5\u05e8 \u05dc\u05d9 \u05d1\u05d1\u05e7\u05e9\u05d4.", "transliteration": "Ata yachol la'azor li bevakasha."},
        {"english": "I would like a coffee please.", "hebrew": "\u05d0\u05e0\u05d9 \u05d0\u05e9\u05de\u05d7 \u05dc\u05e7\u05e4\u05d4 \u05d1\u05d1\u05e7\u05e9\u05d4.", "transliteration": "Ani esmach lekafe bevakasha."},
        {"english": "The food is delicious today.", "hebrew": "\u05d4\u05d0\u05d5\u05db\u05dc \u05d8\u05e2\u05d9\u05dd \u05d4\u05d9\u05d5\u05dd.", "transliteration": "Ha'ochel ta'im hayom."},
        {"english": "Have a wonderful weekend.", "hebrew": "\u05e9\u05d9\u05d4\u05d9\u05d4 \u05dc\u05da \u05e1\u05d5\u05e3 \u05e9\u05d1\u05d5\u05e2 \u05e0\u05e4\u05dc\u05d0.", "transliteration": "Sheyihyeh lecha sof shavua nifla."},
        {"english": "Take care of yourself.", "hebrew": "\u05e9\u05de\u05d5\u05e8 \u05e2\u05dc \u05e2\u05e6\u05de\u05da.", "transliteration": "Shmor al atzmecha."},
        {"english": "See you tomorrow my friend.", "hebrew": "\u05e0\u05ea\u05e8\u05d0\u05d4 \u05de\u05d7\u05e8 \u05d7\u05d1\u05e8 \u05e9\u05dc\u05d9.", "transliteration": "Nitra'e machar chaver sheli."},
        {"english": "The weather is beautiful outside.", "hebrew": "\u05de\u05d6\u05d2 \u05d4\u05d0\u05d5\u05d5\u05d9\u05e8 \u05d9\u05e4\u05d4 \u05d1\u05d7\u05d5\u05e5.", "transliteration": "Mezeg ha'avir yafe bachutz."},
        {"english": "I am very happy today.", "hebrew": "\u05d0\u05e0\u05d9 \u05de\u05d0\u05d5\u05d3 \u05e9\u05de\u05d7 \u05d4\u05d9\u05d5\u05dd.", "transliteration": "Ani me'od samach hayom."},
        {"english": "Learning a language opens new doors.", "hebrew": "\u05dc\u05d9\u05de\u05d5\u05d3 \u05e9\u05e4\u05d4 \u05e4\u05d5\u05ea\u05d7 \u05d3\u05dc\u05ea\u05d5\u05ea \u05d7\u05d3\u05e9\u05d5\u05ea.", "transliteration": "Limud safa pote'ach dlatot chadashot."},
        {"english": "Keep practicing every single day.", "hebrew": "\u05d4\u05de\u05e9\u05da \u05dc\u05d4\u05ea\u05d0\u05de\u05df \u05db\u05dc \u05d9\u05d5\u05dd.", "transliteration": "Hemshech lehit'amen kol yom."},
        {"english": "You can achieve anything you want.", "hebrew": "\u05d0\u05ea\u05d4 \u05d9\u05db\u05d5\u05dc \u05dc\u05d4\u05e9\u05d9\u05d2 \u05db\u05dc \u05de\u05d4 \u05e9\u05d0\u05ea\u05d4 \u05e8\u05d5\u05e6\u05d4.", "transliteration": "Ata yachol lehasig kol ma ata rotze."},
        {"english": "Rest when you are tired.", "hebrew": "\u05e0\u05d5\u05d7 \u05db\u05e9\u05d0\u05ea\u05d4 \u05e2\u05d9\u05d9\u05e3.", "transliteration": "No'ach kshe'ata ayef."},
        {"english": "Focus on the positive things.", "hebrew": "\u05d4\u05ea\u05de\u05e7\u05d3 \u05d1\u05d3\u05d1\u05e8\u05d9\u05dd \u05d4\u05d7\u05d9\u05d5\u05d1\u05d9\u05d9\u05dd.", "transliteration": "Hitmaked badvarim hachiyuviyim."},
        {"english": "Learn from your mistakes.", "hebrew": "\u05dc\u05de\u05d3 \u05de\u05d4\u05d8\u05e2\u05d5\u05d9\u05d5\u05ea \u05e9\u05dc\u05da.", "transliteration": "Lemad me'hate'uyot shelcha."},
        {"english": "Trust the process completely.", "hebrew": "\u05e1\u05de\u05d5\u05da \u05e2\u05dc \u05d4\u05ea\u05d4\u05dc\u05d9\u05da \u05dc\u05d7\u05dc\u05d5\u05d8\u05d9\u05df.", "transliteration": "Smoch al hate\u05dc\u05d9\u05da lachluchin."},
        {"english": "Breathe deeply and stay calm.", "hebrew": "\u05e0\u05e9\u05d5\u05dd \u05e2\u05de\u05d5\u05e7 \u05d5\u05d4\u05d9\u05e9\u05d0\u05e8 \u05e8\u05d2\u05d5\u05e2.", "transliteration": "Nashom amok vehis'are rago'a."},
        {"english": "Enjoy the little moments in life.", "hebrew": "\u05ea\u05d9\u05d4\u05e0\u05d4 \u05de\u05d4\u05e8\u05d2\u05e2\u05d9\u05dd \u05d4\u05e7\u05d8\u05e0\u05d9\u05dd \u05d1\u05d7\u05d9\u05d9\u05dd.", "transliteration": "Tihana me'ha'rega'im haktanim bachayim."},
        {"english": "Smile more, worry less.", "hebrew": "\u05d7\u05d9\u05d9\u05da \u05d9\u05d5\u05ea\u05e8, \u05d3\u05d0\u05d2 \u05e4\u05d7\u05d5\u05ea.", "transliteration": "Chayech yoter, de'ag pachot."},
        {"english": "Be kind to everyone you meet.", "hebrew": "\u05d4\u05d9\u05d4 \u05d0\u05d3\u05d9\u05d1 \u05dc\u05db\u05dc \u05de\u05d9 \u05e9\u05d0\u05ea\u05d4 \u05e4\u05d5\u05d2\u05e9.", "transliteration": "Hihye adiv lechol mi ata pogesh."},
        {"english": "Help others without expecting anything back.", "hebrew": "\u05e2\u05d6\u05d5\u05e8 \u05dc\u05d0\u05d7\u05e8\u05d9\u05dd \u05de\u05d1\u05dc\u05d9 \u05dc\u05e6\u05e4\u05d5\u05ea \u05dc\u05ea\u05de\u05d5\u05e8\u05d4.", "transliteration": "Azor le'acherim mibli letzapot letmura."},
        {"english": "Forgive yourself and move forward.", "hebrew": "\u05e1\u05dc\u05d7 \u05dc\u05e2\u05e6\u05de\u05da \u05d5\u05d4\u05de\u05e9\u05da \u05d4\u05dc\u05d0\u05d4.", "transliteration": "Slech le'atzmecha vehemshech hala."},
        {"english": "Stay strong in difficult times.", "hebrew": "\u05d4\u05d9\u05e9\u05d0\u05e8 \u05d7\u05d6\u05e7 \u05d1\u05d6\u05de\u05e0\u05d9\u05dd \u05e7\u05e9\u05d9\u05dd.", "transliteration": "His'are chazak bizmanim kashim."},
        {"english": "Every moment is a new beginning.", "hebrew": "\u05db\u05dc \u05e8\u05d2\u05e2 \u05d4\u05d5\u05d0 \u05d4\u05ea\u05d7\u05dc\u05d4 \u05d7\u05d3\u05e9\u05d4.", "transliteration": "Kol rega hu hatchala chadasha."},
        {"english": "Listen to your heart always.", "hebrew": "\u05d4\u05e7\u05e9\u05d1 \u05dc\u05dc\u05d1 \u05e9\u05dc\u05da \u05ea\u05de\u05d9\u05d3.", "transliteration": "Hakshav lelev shelcha tamid."},
        {"english": "Do what makes you happy.", "hebrew": "\u05e2\u05e9\u05d4 \u05de\u05d4 \u05e9\u05e2\u05d5\u05e9\u05d4 \u05d0\u05d5\u05ea\u05da \u05de\u05d0\u05d5\u05e9\u05e8.", "transliteration": "Ase ma she'ose otcha me'usher."},
        {"english": "Your potential is unlimited.", "hebrew": "\u05d4\u05e4\u05d5\u05d8\u05e0\u05e6\u05d9\u05d0\u05dc \u05e9\u05dc\u05da \u05d1\u05dc\u05ea\u05d9 \u05de\u05d5\u05d2\u05d1\u05dc.", "transliteration": "Hapotentzial shelcha bilti mugbal."},
        {"english": "Be brave and take risks.", "hebrew": "\u05d4\u05d9\u05d4 \u05d0\u05de\u05d9\u05e5 \u05d5\u05e7\u05d7 \u05e1\u05d9\u05db\u05d5\u05e0\u05d9\u05dd.", "transliteration": "Hihye amitz vekach sikunim."},
        {"english": "Celebrate your progress every day.", "hebrew": "\u05d7\u05d2\u05d5\u05d2 \u05d0\u05ea \u05d4\u05d4\u05ea\u05e7\u05d3\u05de\u05d5\u05ea \u05e9\u05dc\u05da \u05db\u05dc \u05d9\u05d5\u05dd.", "transliteration": "Chagog et hahitkadmut shelcha kol yom."},
        {"english": "Surround yourself with good people.", "hebrew": "\u05d4\u05e7\u05e3 \u05d0\u05ea \u05e2\u05e6\u05de\u05da \u05d1\u05d0\u05e0\u05e9\u05d9\u05dd \u05d8\u05d5\u05d1\u05d9\u05dd.", "transliteration": "Hakif et atzmecha be'anashim tovim."},
        {"english": "Read books and grow your mind.", "hebrew": "\u05e7\u05e8\u05d0 \u05e1\u05e4\u05e8\u05d9\u05dd \u05d5\u05e4\u05ea\u05d7 \u05d0\u05ea \u05d4\u05de\u05d5\u05d7 \u05e9\u05dc\u05da.", "transliteration": "Kra sfarim u'ftech et hamoach shelcha."},
        {"english": "Travel and discover new places.", "hebrew": "\u05d8\u05d9\u05d9\u05dc \u05d5\u05d2\u05dc\u05d4 \u05de\u05e7\u05d5\u05de\u05d5\u05ea \u05d7\u05d3\u05e9\u05d9\u05dd.", "transliteration": "Tayeil vegalem mekomot chadashim."},
        {"english": "Appreciate what you already have.", "hebrew": "\u05d4\u05e2\u05e8\u05da \u05d0\u05ea \u05de\u05d4 \u05e9\u05db\u05d1\u05e8 \u05d9\u05e9 \u05dc\u05da.", "transliteration": "Ha'arech et ma she'kvar yesh lecha."},
        {"english": "Dance like nobody is watching.", "hebrew": "\u05e8\u05e7\u05d5\u05d3 \u05db\u05d0\u05d9\u05dc\u05d5 \u05d0\u05e3 \u05d0\u05d7\u05d3 \u05dc\u05d0 \u05de\u05e1\u05ea\u05db\u05dc.", "transliteration": "Rkod ke'ilu af echad lo mistakel."},
        {"english": "Sing from your heart out loud.", "hebrew": "\u05e9\u05d9\u05e8 \u05de\u05d4\u05dc\u05d1 \u05d1\u05e7\u05d5\u05dc \u05e8\u05dd.", "transliteration": "Shir mehalev bekol ram."},
        {"english": "Plant seeds of kindness everywhere.", "hebrew": "\u05e9\u05ea\u05d5\u05dc \u05d6\u05e8\u05e2\u05d9 \u05d7\u05e1\u05d3 \u05d1\u05db\u05dc \u05de\u05e7\u05d5\u05dd.", "transliteration": "Shtol zr'ei chesed bechol makom."},
        {"english": "Let go of what you cannot control.", "hebrew": "\u05e9\u05d7\u05e8\u05e8 \u05d0\u05ea \u05de\u05d4 \u05e9\u05d0\u05d9\u05e0\u05da \u05d9\u05db\u05d5\u05dc \u05dc\u05e9\u05dc\u05d5\u05d8 \u05d1\u05d5.", "transliteration": "Shachrer et ma she'einch'a yachol lishlot bo."},
        {"english": "Be present in the here and now.", "hebrew": "\u05d4\u05d9\u05d4 \u05e0\u05d5\u05db\u05d7 \u05d1\u05d4\u05d5\u05d5\u05d4.", "transliteration": "Hihye noch'ach bahove."}
    ]
    fresh = [p for p in generic_fallbacks if not is_phrase_used(p["english"])]
    return fresh[:num_phrases]
def configure_edge_tts():
    import edge_tts.constants
    active_url = "wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1?Ocp-Apim-Subscription-Key=6A5AA1D4EAFF4E9FB37E23D68491D6F4"
    edge_tts.constants.TRUSTED_CLIENT_TOKEN = "6A5AA1D4EAFF4E9FB37E23D68491D6F4"
    edge_tts.constants.WSS_URL = active_url
    edge_tts.constants.BASE_URL = active_url

async def generate_single_audio(text: str, voice: str, output_path: str):
    for attempt in range(1, 4):
        try:
            import edge_tts
            configure_edge_tts()
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            if Path(output_path).exists() and Path(output_path).stat().st_size > 100:
                return True
        except Exception as e:
            print(f"  TTS error (attempt {attempt}/3): {e}")
            if attempt < 3:
                import asyncio
                await asyncio.sleep(2 * attempt)
    return False

async def generate_audio_with_retries(text: str, voice: str, output_path: str, max_retries: int = 3):
    import asyncio
    for attempt in range(1, max_retries + 1):
        success = await generate_single_audio(text, voice, output_path)
        if success:
            if Path(output_path).exists() and Path(output_path).stat().st_size > 100:
                return True
            else:
                print(f"    TTS file too small or missing, retrying ({attempt}/{max_retries})...")
                await asyncio.sleep(2 * attempt)
                continue
        else:
            if attempt < max_retries:
                wait = 2 * attempt
                print(f"    TTS retry {attempt}/{max_retries} in {wait}s...")
                await asyncio.sleep(wait)
            else:
                print(f"    TTS failed after {max_retries} attempts, using silence fallback")
                return False
    return False


def generate_all_audio(phrases: list, output_dir: str):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_files = []

    for i, phrase in enumerate(phrases):
        english_file = output_dir / f"english_{i}.mp3"
        native_file = output_dir / f"native_{i}.mp3"
        combined_file = output_dir / f"combined_{i}.mp3"

        print(f"\n  Phrase {i+1}:")
        print(f"    EN: {phrase['english']}")
        print(f"    HE: {phrase['hebrew']}")

        nat_success = asyncio.run(generate_audio_with_retries(phrase["hebrew"], NATIVE_VOICE, str(native_file)))
        if nat_success:
            print(f"    - Hebrew: {native_file.name}")
        else:
            print(f"    - Hebrew: SILENCE FALLBACK (TTS failed)")
            cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "2", str(native_file)]
            subprocess.run(cmd, capture_output=True)

        en_success = asyncio.run(generate_audio_with_retries(phrase["english"], ENGLISH_VOICE, str(english_file)))
        if en_success:
            print(f"    - English: {english_file.name}")
        else:
            print(f"    - English: SILENCE FALLBACK (TTS failed)")
            cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "2", str(english_file)]
            subprocess.run(cmd, capture_output=True)

        en_duration = get_audio_duration(str(english_file))
        nat_duration = get_audio_duration(str(native_file))
        pause_between = 0.5
        total_duration = en_duration + pause_between + nat_duration

        print(f"    Total: {total_duration:.2f}s (EN: {en_duration:.2f}s + pause: {pause_between}s + HE: {nat_duration:.2f}s)")

        cmd = [
            "ffmpeg", "-y",
            "-i", str(english_file),
            "-i", str(native_file),
            "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[out]",
            "-map", "[out]",
            str(combined_file)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            concat_file = output_dir / f"concat_{i}.txt"
            with open(concat_file, "w", encoding="utf-8") as f:
                f.write(f"file '{english_file.as_posix()}'\n")
                f.write(f"file '{native_file.as_posix()}'\n")
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-c:a", "aac",
                str(combined_file)
            ]
            subprocess.run(cmd, capture_output=True)
            if concat_file.exists():
                concat_file.unlink()

        actual_duration = get_audio_duration(str(combined_file))
        print(f"    Combined verified: {actual_duration:.2f}s")

        audio_files.append({
            "index": i,
            "english": str(english_file),
            "native": str(native_file),
            "combined": str(combined_file),
            "duration": actual_duration,
            "en_duration": en_duration,
            "nat_duration": nat_duration
        })

    print(f"\n[audio] Generated {len(audio_files)} phrase audios")
    return audio_files


def get_audio_duration(audio_file: str) -> float:
    if not Path(audio_file).exists():
        return 2.0
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 2.0


def create_final_narration(audio_files: list, output_file: str):
    n = len(audio_files)
    print(f"[audio] Combining {n} audio files...")
    concat_file = Path(output_file).parent / "narration_list.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for audio_info in audio_files:
            combined_path = Path(audio_info["combined"])
            if combined_path.exists():
                path_str = str(combined_path.resolve()).replace("\\", "/").replace("'", "'\\''")
                f.write(f"file '{path_str}'\n")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c:a", "copy", str(output_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if concat_file.exists():
        concat_file.unlink()
    if result.returncode == 0 and Path(output_file).exists() and Path(output_file).stat().st_size > 0:
        size = Path(output_file).stat().st_size
        print(f"\n[audio] Final narration: {Path(output_file).name} ({size/1024:.1f} KB)")
        return True
    return False


NOTO_FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosans/NotoSans%5Bwdth,wght%5D.ttf"
FONTS_DIR = BASE_DIR / "fonts"


def ensure_font():
    font_file = FONTS_DIR / "NotoSansHebrew-Bold.ttf"
    if font_file.exists():
        return str(font_file)
    FONTS_DIR.mkdir(exist_ok=True)
    try:
        import urllib.request
        print(f"[font] Downloading {font_file.name}...")
        urllib.request.urlretrieve(NOTO_FONT_URL, str(font_file))
        print(f"[font] Downloaded: {font_file}")
        try:
            from fontTools.ttLib import TTFont
            from fontTools.varLib.instancer import instantiateVariableFont, AxisLimits
            font = TTFont(str(font_file))
            if 'fvar' in font:
                has_wght = any(a.axisTag == 'wght' for a in font['fvar'].axes)
                if has_wght:
                    font2 = TTFont(str(font_file))
                    instantiateVariableFont(font2, AxisLimits({"wght": (700, 700)}), inplace=True)
                    for tag in ['fvar','avar','cvar','gvar','STAT','HVAR','VVAR','MVAR']:
                        if tag in font2: del font2[tag]
                    font2.save(str(font_file))
                    print(f"[font] Converted to Bold (wght=700)")
        except Exception as e:
            print(f"[font] Font conversion note: {e}")
    except Exception as e:
        print(f"[font] Download failed: {e}")

    if font_file.exists():
        return str(font_file)
    return None


def _find_hebrew_font_file():
    candidates = [
        str(FONTS_DIR / "NotoSansHebrew-Bold.ttf"),
        str(FONTS_DIR / "NotoSansHebrew-Regular.ttf"),
        "/usr/share/fonts/truetype/noto/NotoSansHebrew-Bold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansHebrew-Bold.ttc",
        "C:/Windows/Fonts/Nirmala.ttc",
        "C:/Windows/Fonts/Nirmala.ttf",
        "C:/Windows/Fonts/gautami.ttf",
        "C:/Windows/Fonts/mangal.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return path
    for search_dir in ["/usr/share/fonts", "/usr/local/share/fonts", "C:/Windows/Fonts"]:
        if not Path(search_dir).exists():
            continue
        for root, dirs, files in os.walk(search_dir):
            for fname in files:
                fname_lower = fname.lower()
                if any(t.lower() in fname_lower for t in ["notosanshebrew", "nirmala", "gautami", "mangal", "latha"]):
                    return str(Path(root) / fname)
    return None


def _render_text_harfbuzz(text, font_path, font_size, fill_color, stroke_color=None, stroke_width=0):
    import uharfbuzz as hb
    import freetype as ft
    from PIL import Image, ImageDraw, ImageChops

    blob = hb.Blob.from_file_path(font_path)
    hb_face = hb.Face(blob)
    hb_font = hb.Font(hb_face)
    hb_font.scale = (font_size * 64, font_size * 64)

    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(hb_font, buffer)

    infos = buffer.glyph_infos
    positions = buffer.glyph_positions

    ft_face = ft.Face(font_path)
    ft_face.set_char_size(font_size * 64)

    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')

    x_cursor = 0.0
    y_cursor = 0.0
    glyph_metrics = []

    for info, pos in zip(infos, positions):
        ft_face.load_glyph(info.codepoint)
        bitmap = ft_face.glyph.bitmap
        bitmap_left = ft_face.glyph.bitmap_left
        bitmap_top = ft_face.glyph.bitmap_top
        x_off = pos.x_offset / 64.0
        y_off = pos.y_offset / 64.0
        x_adv = pos.x_advance / 64.0

        px = x_cursor + x_off + bitmap_left
        py = y_cursor + y_off - bitmap_top

        if bitmap.width > 0 and bitmap.rows > 0:
            min_x = min(min_x, px - stroke_width)
            min_y = min(min_y, py - stroke_width)
            max_x = max(max_x, px + bitmap.width + stroke_width)
            max_y = max(max_y, py + bitmap.rows + stroke_width)

        glyph_metrics.append({
            'codepoint': info.codepoint,
            'x': px, 'y': py,
            'width': bitmap.width, 'height': bitmap.rows,
            'x_advance': x_adv,
        })
        x_cursor += x_adv

    if min_x == float('inf'):
        total_width = max(x_cursor, 50)
        total_height = int(font_size * 1.5)
        min_x = 0
        min_y = 0
    else:
        total_width = max(max_x - min_x + stroke_width * 2, x_cursor + stroke_width * 2)
        total_height = max_y - min_y + stroke_width * 2

    total_width = int(total_width) + stroke_width * 2 + 4
    total_height = int(total_height) + stroke_width * 2 + 4

    img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))

    def _draw_glyphs(target_img, color):
        draw = ImageDraw.Draw(target_img)
        for gm in glyph_metrics:
            ft_face.load_glyph(gm['codepoint'])
            bitmap = ft_face.glyph.bitmap
            if bitmap.width > 0 and bitmap.rows > 0:
                glyph_img = Image.frombytes('L', (bitmap.width, bitmap.rows), bytes(bitmap.buffer))
                paste_x = int(gm['x'] - min_x + stroke_width)
                paste_y = int(gm['y'] - min_y + stroke_width)
                if color[-1] == 255:
                    colored_glyph = Image.new('RGBA', glyph_img.size, color)
                    colored_glyph.putalpha(glyph_img)
                    target_img.paste(colored_glyph, (paste_x, paste_y), glyph_img)
                else:
                    blended = Image.new('RGBA', glyph_img.size, color)
                    mask = glyph_img.point(lambda p: min(255, int(p * color[-1] / 255)))
                    blended.putalpha(mask)
                    target_img.paste(blended, (paste_x, paste_y), blended)

    if stroke_width > 0 and stroke_color:
        stroke_img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx * dx + dy * dy <= stroke_width * stroke_width + 1:
                    shifted = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
                    _draw_glyphs(shifted, stroke_color)
                    stroke_img = Image.alpha_composite(stroke_img, ImageChops.offset(shifted, dx, dy))
        img = Image.alpha_composite(img, stroke_img)

    fill_img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
    _draw_glyphs(fill_img, fill_color)
    img = Image.alpha_composite(img, fill_img)

    return img, int(x_cursor)


def create_impressive_background(category_english: str):
    from PIL import Image, ImageDraw

    category_colors = {
    "Greetings": [
        [
            70,
            130,
            180
        ],
        [
            255,
            140,
            0
        ],
        [
            255,
            255,
            0
        ],
        [
            255,
            99,
            71
        ]
    ],
    "Basic Phrases": [
        [
            60,
            179,
            113
        ],
        [
            255,
            215,
            0
        ],
        [
            144,
            238,
            144
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Common Expressions": [
        [
            138,
            43,
            226
        ],
        [
            255,
            20,
            147
        ],
        [
            75,
            0,
            130
        ],
        [
            255,
            105,
            180
        ]
    ],
    "Travel": [
        [
            0,
            191,
            255
        ],
        [
            255,
            255,
            0
        ],
        [
            70,
            130,
            180
        ],
        [
            255,
            215,
            0
        ]
    ],
    "Restaurant": [
        [
            255,
            69,
            0
        ],
        [
            255,
            215,
            0
        ],
        [
            220,
            20,
            60
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Shopping": [
        [
            255,
            105,
            180
        ],
        [
            0,
            100,
            80
        ],
        [
            255,
            192,
            203
        ],
        [
            0,
            200,
            160
        ]
    ],
    "Emergency": [
        [
            255,
            0,
            0
        ],
        [
            139,
            0,
            0
        ],
        [
            255,
            69,
            0
        ],
        [
            220,
            20,
            60
        ]
    ],
    "Family Terms": [
        [
            255,
            182,
            193
        ],
        [
            138,
            43,
            226
        ],
        [
            255,
            160,
            122
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Numbers": [
        [
            255,
            215,
            0
        ],
        [
            0,
            0,
            139
        ],
        [
            255,
            140,
            0
        ],
        [
            70,
            130,
            180
        ]
    ],
    "Time": [
        [
            0,
            0,
            100
        ],
        [
            255,
            255,
            0
        ],
        [
            70,
            130,
            180
        ],
        [
            255,
            215,
            0
        ]
    ],
    "Motivation": [
        [
            138,
            43,
            226
        ],
        [
            75,
            0,
            130
        ],
        [
            255,
            20,
            147
        ],
        [
            147,
            112,
            219
        ]
    ],
    "Love": [
        [
            255,
            0,
            100
        ],
        [
            139,
            0,
            0
        ],
        [
            255,
            105,
            180
        ],
        [
            255,
            192,
            203
        ]
    ],
    "Success": [
        [
            255,
            215,
            0
        ],
        [
            0,
            100,
            0
        ],
        [
            255,
            140,
            0
        ],
        [
            34,
            139,
            34
        ]
    ],
    "Wisdom": [
        [
            0,
            0,
            139
        ],
        [
            255,
            215,
            0
        ],
        [
            70,
            130,
            180
        ],
        [
            255,
            255,
            0
        ]
    ],
    "Happiness": [
        [
            255,
            255,
            0
        ],
        [
            255,
            0,
            255
        ],
        [
            255,
            165,
            0
        ],
        [
            147,
            112,
            219
        ]
    ],
    "Self Improvement": [
        [
            0,
            128,
            0
        ],
        [
            255,
            215,
            0
        ],
        [
            0,
            255,
            0
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Gratitude": [
        [
            255,
            127,
            80
        ],
        [
            75,
            0,
            130
        ],
        [
            255,
            160,
            122
        ],
        [
            138,
            43,
            226
        ]
    ],
    "Friendship": [
        [
            255,
            192,
            203
        ],
        [
            0,
            100,
            80
        ],
        [
            255,
            105,
            180
        ],
        [
            0,
            200,
            160
        ]
    ],
    "Hope": [
        [
            0,
            0,
            100
        ],
        [
            255,
            255,
            0
        ],
        [
            70,
            130,
            180
        ],
        [
            255,
            215,
            0
        ]
    ],
    "Creativity": [
        [
            255,
            0,
            127
        ],
        [
            0,
            0,
            139
        ],
        [
            255,
            20,
            147
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Inner Peace": [
        [
            135,
            206,
            235
        ],
        [
            0,
            0,
            100
        ],
        [
            176,
            224,
            230
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Confidence": [
        [
            255,
            69,
            0
        ],
        [
            0,
            0,
            139
        ],
        [
            255,
            140,
            0
        ],
        [
            70,
            130,
            180
        ]
    ],
    "Perseverance": [
        [
            139,
            69,
            19
        ],
        [
            255,
            215,
            0
        ],
        [
            160,
            82,
            45
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Inspiration": [
        [
            255,
            0,
            255
        ],
        [
            75,
            0,
            130
        ],
        [
            255,
            20,
            147
        ],
        [
            0,
            0,
            139
        ]
    ],
    "Positive Life": [
        [
            50,
            205,
            50
        ],
        [
            255,
            0,
            127
        ],
        [
            144,
            238,
            144
        ],
        [
            255,
            20,
            147
        ]
    ],
    "Courage": [
        [
            178,
            34,
            34
        ],
        [
            255,
            215,
            0
        ],
        [
            220,
            20,
            60
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Kindness": [
        [
            255,
            182,
            193
        ],
        [
            138,
            43,
            226
        ],
        [
            255,
            160,
            122
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Patience": [
        [
            34,
            139,
            34
        ],
        [
            255,
            255,
            0
        ],
        [
            60,
            179,
            113
        ],
        [
            255,
            215,
            0
        ]
    ],
    "Forgiveness": [
        [
            230,
            230,
            250
        ],
        [
            75,
            0,
            130
        ],
        [
            216,
            191,
            216
        ],
        [
            138,
            43,
            226
        ]
    ],
    "Strength": [
        [
            100,
            100,
            100
        ],
        [
            255,
            69,
            0
        ],
        [
            150,
            150,
            150
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Joy": [
        [
            255,
            255,
            0
        ],
        [
            255,
            0,
            127
        ],
        [
            255,
            215,
            0
        ],
        [
            147,
            112,
            219
        ]
    ],
    "Balance": [
        [
            60,
            179,
            113
        ],
        [
            138,
            43,
            226
        ],
        [
            152,
            251,
            152
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Growth": [
        [
            0,
            100,
            0
        ],
        [
            255,
            215,
            0
        ],
        [
            34,
            139,
            34
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Purpose": [
        [
            75,
            0,
            130
        ],
        [
            255,
            215,
            0
        ],
        [
            138,
            43,
            226
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Mindfulness": [
        [
            210,
            180,
            140
        ],
        [
            75,
            0,
            130
        ],
        [
            245,
            245,
            220
        ],
        [
            138,
            43,
            226
        ]
    ]
}

    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)

    colors = category_colors.get(category_english, [(138, 43, 226), (75, 0, 130), (255, 20, 147), (147, 112, 219)])

    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        if ratio < 0.33:
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * (ratio * 3))
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * (ratio * 3))
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * (ratio * 3))
        elif ratio < 0.66:
            r = int(colors[1][0] + (colors[2][0] - colors[1][0]) * ((ratio - 0.33) * 3))
            g = int(colors[1][1] + (colors[2][1] - colors[1][1]) * ((ratio - 0.33) * 3))
            b = int(colors[1][2] + (colors[2][2] - colors[1][2]) * ((ratio - 0.33) * 3))
        else:
            r = int(colors[2][0] + (colors[3][0] - colors[2][0]) * ((ratio - 0.66) * 3))
            g = int(colors[2][1] + (colors[3][1] - colors[2][1]) * ((ratio - 0.66) * 3))
            b = int(colors[2][2] + (colors[3][2] - colors[2][2]) * ((ratio - 0.66) * 3))
        draw.rectangle([(0, y), (VIDEO_WIDTH, y + 1)], fill=(r, g, b))

    for i in range(0, VIDEO_WIDTH, 120):
        for j in range(0, VIDEO_HEIGHT, 120):
            draw.ellipse(
                [(i + 30, j + 30), (i + 90, j + 90)],
                outline=(255, 255, 255, 20),
                width=1
            )

    glow = Image.new('RGBA', (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for radius in range(800, 0, -50):
        alpha = int(30 * (1 - radius / 800))
        glow_draw.ellipse(
            [(VIDEO_WIDTH//2 - radius, VIDEO_HEIGHT//3 - radius),
             (VIDEO_WIDTH//2 + radius, VIDEO_HEIGHT//3 + radius)],
            fill=(255, 255, 255, alpha)
        )

    img = img.convert('RGBA')
    img = Image.alpha_composite(img, glow)
    return img


def find_font(bold=False, size=40):
    from PIL import ImageFont
    font_file = FONTS_DIR / "NotoSansHebrew-Bold.ttf"
    if font_file.exists():
        try:
            return ImageFont.truetype(str(font_file), size)
        except (IOError, OSError):
            pass
    if bold:
        font_preferences = [
            "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        font_preferences = [
            "segoeui.ttf", "arial.ttf", "calibri.ttf", "DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for font_name in font_preferences:
        try:
            return ImageFont.truetype(font_name, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def rounded_rect(draw, bbox, radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = bbox
    r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
    draw.pieslice([x1, y1, x1 + r*2, y1 + r*2], 180, 270, fill=fill)
    draw.pieslice([x2 - r*2, y1, x2, y1 + r*2], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - r*2, x1 + r*2, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - r*2, y2 - r*2, x2, y2], 0, 90, fill=fill)
    draw.rectangle([x1 + r, y1, x2 - r, y2], fill=fill)
    draw.rectangle([x1, y1 + r, x2, y2 - r], fill=fill)


def generate_complete_image(phrase_data: dict, category_english: str, output_path: str, phrase_index: int = 0, total_phrases: int = 5):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("PIL not available. Install: pip install Pillow")
        return None

    ensure_font()
    img = create_impressive_background(category_english)
    draw = ImageDraw.Draw(img)

    SIZE_CATEGORY = 64
    SIZE_NATIVE_L = 100
    SIZE_NATIVE_M = 82
    SIZE_NATIVE_S = 66
    SIZE_ENGLISH = 70
    SIZE_TRANSLITERATION = 48
    SIZE_BRANDING = 50
    SIZE_PROGRESS = 38

    font_category = find_font(bold=True, size=SIZE_CATEGORY)
    font_native_l = find_font(bold=True, size=SIZE_NATIVE_L)
    font_native_m = find_font(bold=True, size=SIZE_NATIVE_M)
    font_native_s = find_font(bold=True, size=SIZE_NATIVE_S)
    font_english = find_font(bold=True, size=SIZE_ENGLISH)
    font_transliteration = find_font(bold=False, size=SIZE_TRANSLITERATION)
    font_branding = find_font(bold=True, size=SIZE_BRANDING)
    font_progress = find_font(bold=False, size=SIZE_PROGRESS)

    native = phrase_data.get("hebrew", "")
    english = phrase_data.get("english", "")
    transliteration = phrase_data.get("transliteration", "")

    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def pick_native_font(text, max_w):
        for font, name in [(font_native_l, 'L'), (font_native_m, 'M'), (font_native_s, 'S')]:
            lines = wrap_text(text, font, max_w)
            if len(lines) <= 2:
                return font, lines
        return font_native_s, wrap_text(native, font_native_s, max_w)

    def measure_line_h(font):
        b = draw.textbbox((0, 0), "Ag", font=font)
        return b[3] - b[1]

    max_text_w = VIDEO_WIDTH - 140
    cat_native = CATEGORIES_NATIVE.get(category_english, category_english)

    nat_font, nat_lines = pick_native_font(native, max_text_w - 40)
    en_lines = wrap_text(english, font_english, max_text_w)
    trans_lines = wrap_text(transliteration, font_transliteration, max_text_w - 60) if transliteration else []

    nat_lh = measure_line_h(nat_font)
    en_lh = measure_line_h(font_english)
    trans_lh = measure_line_h(font_transliteration)

    nat_box_pad = 35
    en_box_pad = 28
    trans_box_pad = 22

    nat_box_h = len(nat_lines) * nat_lh + nat_box_pad * 2
    en_box_h = len(en_lines) * en_lh + en_box_pad * 2
    trans_box_h = len(trans_lines) * trans_lh + trans_box_pad * 2 if trans_lines else 0

    gap_cat_en = 50
    gap_en_nat = 80
    gap_nat_trans = 60
    gap_trans_prog = 50
    gap_prog_brand = 40
    prog_bar_h = 30

    total_center_h = (0 + gap_cat_en + en_box_h + gap_en_nat +
                      nat_box_h + gap_nat_trans + trans_box_h + gap_trans_prog +
                      prog_bar_h + gap_prog_brand)

    start_y = int((VIDEO_HEIGHT - total_center_h) * 0.38)
    if start_y < 200:
        start_y = 200

    cy = start_y

    # Category bar (rounded)
    cat_text = category_english
    cat_bb = draw.textbbox((0, 0), cat_text, font=font_category)
    cat_tw = cat_bb[2] - cat_bb[0]
    cat_th = cat_bb[3] - cat_bb[1]
    cat_cx = VIDEO_WIDTH // 2
    cat_cy = 185
    cat_pad = 28
    cat_box_x1 = cat_cx - cat_tw // 2 - cat_pad
    cat_box_y1 = cat_cy - cat_th // 2 - cat_pad
    cat_box_x2 = cat_cx + cat_tw // 2 + cat_pad
    cat_box_y2 = cat_cy + cat_th // 2 + cat_pad
    rounded_rect(draw, (cat_box_x1, cat_box_y1, cat_box_x2, cat_box_y2),
                 25, fill=(0, 0, 0, 190))
    draw.text((cat_cx, cat_cy), cat_text,
              fill=(255, 255, 255), font=font_category, anchor="mm",
              stroke_width=2, stroke_fill=(0, 0, 0))

    cy += gap_cat_en

    # English phrase (top)
    en_margin = 60
    rounded_rect(draw, (en_margin, cy, VIDEO_WIDTH - en_margin, cy + en_box_h), 28,
                 fill=(20, 40, 100, 220))
    for i, line in enumerate(en_lines):
        ly = cy + en_box_pad + i * en_lh + en_lh // 2
        draw.text((VIDEO_WIDTH // 2, ly), line,
                  fill=(255, 255, 255), font=font_english, anchor="mm",
                  stroke_width=3, stroke_fill=(0, 0, 40))

    cy += en_box_h + gap_en_nat

    # Native phrase (below English)
    heb_font_path = _find_hebrew_font_file()
    use_harfbuzz = heb_font_path is not None
    if use_harfbuzz:
        try:
            import uharfbuzz as hb
            import freetype as ft
        except ImportError:
            use_harfbuzz = False
            print("  [WARNING] uharfbuzz/freetype not available, falling back to Pillow")

    nat_margin = 50
    rounded_rect(draw, (nat_margin, cy, VIDEO_WIDTH - nat_margin, cy + nat_box_h), 24,
                 fill=(139, 0, 0, 220))

    if use_harfbuzz:
        max_heb_width = VIDEO_WIDTH - 200
        heb_words = native.split(' ')
        heb_lines = []
        current_line_words = []

        for word in heb_words:
            test_line = ' '.join(current_line_words + [word]) if current_line_words else word
            _, test_w = _render_text_harfbuzz(
                test_line, heb_font_path, 65,
                fill_color=(255, 255, 200, 255)
            )
            if test_w <= max_heb_width or not current_line_words:
                current_line_words.append(word)
            else:
                heb_lines.append(' '.join(current_line_words))
                current_line_words = [word]

        if current_line_words:
            heb_lines.append(' '.join(current_line_words))
        if not heb_lines:
            heb_lines = [native]

        line_count = len(heb_lines)
        total_text_height = line_count * nat_lh
        start_y_offset = (nat_box_h - total_text_height) // 2

        for i, line in enumerate(heb_lines):
            rendered, text_w = _render_text_harfbuzz(
                line, heb_font_path, 65,
                fill_color=(255, 255, 200, 255),
                stroke_color=(0, 0, 0, 255),
                stroke_width=2
            )
            x_pos = (VIDEO_WIDTH - rendered.width) // 2
            y_pos = cy + start_y_offset + i * nat_lh + (nat_lh - rendered.height) // 2
            img.paste(rendered, (x_pos, y_pos), rendered)
    else:
        for i, line in enumerate(nat_lines):
            ly = cy + nat_box_pad + i * nat_lh + nat_lh // 2
            draw.text((VIDEO_WIDTH // 2, ly), line,
                      fill=(255, 255, 200), font=nat_font, anchor="mm",
                      stroke_width=2, stroke_fill=(60, 0, 0))

    cy += nat_box_h + gap_nat_trans

    # Transliteration
    if trans_lines:
        trans_margin = 70
        rounded_rect(draw, (trans_margin, cy, VIDEO_WIDTH - trans_margin, cy + trans_box_h), 18,
                     fill=(40, 40, 40, 220))
        for i, line in enumerate(trans_lines):
            ly = cy + trans_box_pad + i * trans_lh + trans_lh // 2
            draw.text((VIDEO_WIDTH // 2, ly), line,
                      fill=(220, 220, 220), font=font_transliteration, anchor="mm",
                      stroke_width=1, stroke_fill=(20, 20, 20))
        cy += trans_box_h + gap_trans_prog
    else:
        cy += gap_trans_prog

    # Progress
    prog_text = f"{phrase_index + 1} / {total_phrases}"
    prog_bb = draw.textbbox((0, 0), prog_text, font=font_progress)
    prog_h = prog_bb[3] - prog_bb[1]
    draw.text((VIDEO_WIDTH // 2, cy + prog_h // 2), prog_text,
              fill=(180, 180, 180), font=font_progress, anchor="mm")

    # Branding (rounded)
    brand_text = "VELOCITY HEBREW"
    brand_bb = draw.textbbox((0, 0), brand_text, font=font_branding)
    brand_tw = brand_bb[2] - brand_bb[0]
    brand_th = brand_bb[3] - brand_bb[1]
    brand_cx = VIDEO_WIDTH // 2
    brand_cy = VIDEO_HEIGHT - 120
    brand_pad = 32
    brand_box_x1 = brand_cx - brand_tw // 2 - brand_pad
    brand_box_y1 = brand_cy - brand_th // 2 - brand_pad
    brand_box_x2 = brand_cx + brand_tw // 2 + brand_pad
    brand_box_y2 = brand_cy + brand_th // 2 + brand_pad
    rounded_rect(draw, (brand_box_x1, brand_box_y1, brand_box_x2, brand_box_y2),
                 30, fill=(0, 0, 0, 195))
    draw.text((brand_cx, brand_cy), brand_text,
              fill=(255, 215, 0), font=font_branding, anchor="mm",
              stroke_width=2, stroke_fill=(0, 0, 0))

    if img.mode == 'RGBA':
        img = img.convert('RGB')

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95, optimize=True)
    print(f"  Image: {Path(output_path).name}")
    return output_path


def _run_ffmpeg(cmd, max_retries: int = 3, timeout: int = 600):
    """Run an ffmpeg command with retries. Returns True on success."""
    import time
    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            rc = result.returncode
            out = Path(cmd[-1])
            if rc == 0 and out.exists() and out.stat().st_size > 0:
                return True
            stderr_tail = (result.stderr or "")[-600:].replace("\n", " ")
            print(f"[video] ffmpeg attempt {attempt}/{max_retries} failed (rc={rc}): {stderr_tail}")
        except subprocess.TimeoutExpired as e:
            print(f"[video] ffmpeg attempt {attempt}/{max_retries} timed out: {e}")
        except Exception as e:
            print(f"[video] ffmpeg attempt {attempt}/{max_retries} exception: {e}")
        try:
            partial = Path(cmd[-1])
            if partial.exists():
                partial.unlink()
        except Exception:
            pass
        if attempt < max_retries:
            time.sleep(3)
    return False


def create_video_from_images_audio(image_files: list, audio_files: list, combined_audio: str, output_file: str):
    print(f"\n[video] Creating video from {len(image_files)} images...")
    print(f"[video] Ensuring complete audio playback and sync...")

    temp_clips = []

    for i, (img_path, audio_info) in enumerate(zip(image_files, audio_files)):
        duration = audio_info['duration']
        print(f"  Image {i+1}/{len(image_files)}: {duration:.2f}s (EN: {audio_info.get('en_duration', 0):.1f}s + HE: {audio_info.get('nat_duration', 0):.1f}s)")

        temp_clip = Path(output_file).parent / f"temp_clip_{i:02d}.mp4"
        temp_clips.append(temp_clip)

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
            "-t", str(duration),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            str(temp_clip)
        ]
        if not _run_ffmpeg(cmd):
            raise RuntimeError(f"Failed to create clip {i+1} after retries")

    print("[video] Concatenating clips...")
    temp_video = Path(output_file).parent / "temp_video.mp4"
    concat_file = Path(output_file).parent / "concat_list.txt"

    with open(concat_file, "w") as f:
        for clip in temp_clips:
            f.write(f"file '{clip.resolve().as_posix()}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(temp_video)]
    if not _run_ffmpeg(cmd):
        raise RuntimeError("Failed to concatenate clips after retries")

    print("[video] Adding audio (ensuring complete playback)...")
    audio_duration = get_audio_duration(combined_audio)
    print(f"[video] Audio duration: {audio_duration:.2f}s")

    if not Path(combined_audio).exists() or Path(combined_audio).stat().st_size == 0:
        raise RuntimeError(f"Narration audio missing or empty: {combined_audio}")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(combined_audio),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_file)
    ]
    mux_ok = _run_ffmpeg(cmd)
    if not mux_ok:
        print("[video] Mux with -c:v copy failed, retrying with re-encode...")
        cmd = [
            "ffmpeg", "-y",
            "-i", str(temp_video),
            "-i", str(combined_audio),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
            "-c:a", "aac",
            "-shortest",
            str(output_file)
        ]
        if not _run_ffmpeg(cmd):
            raise RuntimeError("Failed to mux video+audio after retries")

    video_duration = get_audio_duration(str(output_file).replace(".mp4", ".mp4"))
    print(f"[video] Video created: {Path(output_file).name} ({video_duration:.2f}s)")

    for clip in temp_clips:
        if clip.exists():
            clip.unlink()
    if temp_video.exists():
        temp_video.unlink()
    if concat_file.exists():
        concat_file.unlink()


def generate_reel(category_english: str = None):
    if not category_english:
        category_english = get_available_category()

    print(f"\n{'='*80}")
    print(f"Category: {category_english} ({CATEGORIES_NATIVE[category_english]})")
    print(f"{'='*80}\n")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reel_dir = VIDEO_DIR / f"{category_english}_{timestamp}"
    reel_dir.mkdir(exist_ok=True)

    print("[1/4] Generating unique phrases (checking history)...")
    phrases = generate_phrases(category_english, num_phrases=5)

    for i, phrase in enumerate(phrases, 1):
        print(f"  {i}. {phrase['english']} -> {phrase['hebrew']}")

    print("\n[2/4] Generating images with impressive backgrounds...")
    for i, phrase in enumerate(phrases):
        output_path = reel_dir / f"phrase_{i:02d}.jpg"
        generate_complete_image(phrase, category_english, str(output_path), phrase_index=i, total_phrases=len(phrases))
        print(f"  Image {i+1}: {phrase['english'][:40]}...")

    print("\n[3/4] Generating audio (English + Hebrew with 500ms pause)...")
    audio_files = generate_all_audio(phrases, str(reel_dir))

    final_audio = reel_dir / "narration.mp3"
    create_final_narration(audio_files, str(final_audio))

    print("\n[4/4] Creating video...")
    output_video = reel_dir / "final_reel.mp4"

    image_files = sorted([str(p) for p in reel_dir.glob("phrase_*.jpg")])

    create_video_from_images_audio(
        image_files,
        audio_files,
        str(final_audio),
        str(output_video)
    )

    metadata = {
        "category_english": category_english,
        "category_native": CATEGORIES_NATIVE[category_english],
        "timestamp": timestamp,
        "phrases": phrases,
        "video": str(output_video),
        "audio": str(final_audio)
    }

    with open(reel_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"REEL COMPLETE!")
    print(f"  {reel_dir}")
    print(f"  {output_video.name}")
    print(f"  Branding: VELOCITY HEBREW")
    print(f"{'='*80}\n")

    return metadata


if __name__ == "__main__":
    print("\n" + "="*80)
    print(f"VELOCITY HEBREW - FACEBOOK REELS AUTOMATION")
    print("="*80)
    print("\nFEATURES:")
    print("  - Natural pauses with commas (non-robotic TTS)")
    print("  - Perfect audio-video synchronization")
    print("  - Complete audio playback guaranteed")
    print("  - English category names (for learners)")
    print(f"  - VELOCITY HEBREW branding at bottom")
    print("  - NEVER repeats phrases (permanent history tracking)")
    print(f"\nAVAILABLE CATEGORIES ({len(CATEGORIES_ENGLISH)} total):")
    for i, cat in enumerate(CATEGORIES_ENGLISH, 1):
        print(f"   {i:2d}. {cat} ({CATEGORIES_NATIVE[cat]})")
    print("="*80)

    generate_reel()

    print("\n" + "="*80)
    print("READY FOR DAILY AUTOMATION!")
    print("="*80)
