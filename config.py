"""VELOCITY JAPANESE - language pack, brand and motion design constants."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

OUTPUT_DIR = BASE_DIR / "output"
LESSONS_DIR = OUTPUT_DIR / "lessons"
HISTORY_DIR = OUTPUT_DIR / "history"
SCENE_DIR = BASE_DIR / "scene"

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# ---------------------------------------------------------------- brand

BRAND = "VELOCITY HEBREW"
BRAND_LOCKUP_TOP = "VELOCITY"
BRAND_LOCKUP_BOTTOM = "HEBREW"
HANDLE = "@velocityhebrew"
MASCOT_NAME = "Velo"

# ==== LANGUAGE PACK START ====
LANGUAGE = {
    "code": "he",
    "name": "Hebrew",
    "native_name": "עברית",
    "history_key": "hebrew",
    "english_voice": "en-US-AvaNeural",
    "english_fallback_voice": "en-US-GuyNeural",
    "native_voice": "he-IL-HilaNeural",
    "native_fallback_voice": "he-IL-AvriNeural",
    "native_engine": "edge",
    "native_lang_code": "he",
    "english_rate": "-4%",
    "native_rate": "-20%",
    "english_pitch": "+0Hz",
    "native_pitch": "+0Hz",
    "native_label": "עברית",
    "translit_label": "SAY IT LIKE",
    "flag": "il",
    "greeting": "שלום!",
    "encouragement": "מעולה!",
    "rtl": True,
    "char_tiles": False,
    "script_font": "",
    "glyphs": "אבגדהוזחטיכלמנסעפצקרשתךםןףץ",
}
# ==== LANGUAGE PACK END ====

AI_MODEL = os.getenv("AI_MODEL", "gemini-fast")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")

# ---------------------------------------------------------------- timing (seconds)

INTRO_DURATION = 4.0
OUTRO_DURATION = 5.2
EN_CARD_IN = 0.55
GAP_EN_NATIVE = 0.5
NATIVE_CARD_LEAD = 0.35
GAP_BEFORE_REPEAT = 0.8
TAIL_HOLD = 1.4
MAX_REEL_DURATION = 88.0

# ---------------------------------------------------------------- palette

INK = "#3C3C3C"
MUTED = "#8A8A8A"
CREAM = "#FFF8E7"
GREEN = "#58CC02"
GREEN_DARK = "#46A302"
GREEN_DEEP = "#3D8F00"
BLUE = "#1CB0F6"
PURPLE = "#A560E8"
ORANGE = "#FF7A00"
RED = "#FF4B4B"
YELLOW = "#F5A700"
TEAL = "#00A889"
PINK = "#E056A0"

PALETTE = [GREEN, BLUE, PURPLE, ORANGE, RED, YELLOW, TEAL, PINK]

# ---------------------------------------------------------------- categories
# (english, native, icon, accent)

# ==== CATEGORY TABLE START ====
CATEGORY_TABLE = [
    ("Greetings", "ברכות", "hand", "#1CB0F6"),
    ("Basic Phrases", "ביטויים בסיסיים", "chat", "#58CC02"),
    ("Common Expressions", "ביטויים נפוצים", "chat", "#1CB0F6"),
    ("Travel", "טיולים", "plane", "#1CB0F6"),
    ("Restaurant", "מסעדה", "fork", "#FF7A00"),
    ("Shopping", "קניות", "bag", "#E056A0"),
    ("Emergency", "חירום", "siren", "#FF4B4B"),
    ("Family Terms", "מונחי משפחה", "heart", "#E056A0"),
    ("Numbers", "מספרים", "hash", "#A560E8"),
    ("Time", "זמן", "clock", "#00A889"),
    ("Motivation", "מוטיבציה", "rocket", "#A560E8"),
    ("Love", "אהבה", "heart", "#FF4B4B"),
    ("Success", "הצלחה", "trophy", "#F5A700"),
    ("Wisdom", "חוכמה", "book", "#A560E8"),
    ("Happiness", "אושר", "smile", "#F5A700"),
    ("Self Improvement", "שיפור עצמי", "leaf", "#58CC02"),
    ("Gratitude", "הכרת תודה", "heart", "#FF7A00"),
    ("Friendship", "חברות", "users", "#00A889"),
    ("Hope", "תקווה", "sun", "#FF7A00"),
    ("Creativity", "יצירתיות", "palette", "#E056A0"),
    ("Inner Peace", "שלווה פנימית", "lotus", "#00A889"),
    ("Confidence", "ביטחון עצמי", "shield", "#1CB0F6"),
    ("Perseverance", "התמדה", "mountain", "#FF7A00"),
    ("Inspiration", "השראה", "sparkles", "#A560E8"),
    ("Positive Life", "חיים חיוביים", "sun", "#58CC02"),
    ("Courage", "אומץ", "shield", "#FF4B4B"),
    ("Kindness", "טוב לב", "heart", "#E056A0"),
    ("Patience", "סבלנות", "hourglass", "#00A889"),
    ("Forgiveness", "סליחה", "hands", "#FF7A00"),
    ("Strength", "כוח", "dumbbell", "#FF4B4B"),
    ("Joy", "שמחה", "smile", "#F5A700"),
    ("Balance", "איזון", "scale", "#00A889"),
    ("Growth", "צמיחה", "sprout", "#58CC02"),
    ("Purpose", "מטרה", "target", "#A560E8"),
    ("Mindfulness", "קשיבות", "lotus", "#00A889"),
    ("Daily Routine", "שגרה יומית", "calendar", "#1CB0F6"),
    ("Weather", "מזג אוויר", "cloud", "#1CB0F6"),
    ("Feelings", "רגשות", "smile", "#E056A0"),
    ("Food", "אוכל", "fork", "#FF7A00"),
    ("Health", "בריאות", "heart", "#58CC02"),
    ("Work", "עבודה", "briefcase", "#1CB0F6"),
    ("Technology", "טכנולוגיה", "chip", "#A560E8"),
    ("Nature", "טבע", "leaf", "#58CC02"),
    ("Animals", "בעלי חיים", "paw", "#FF7A00"),
    ("Colors", "צבעים", "palette", "#E056A0"),
    ("Directions", "כיוונים", "compass", "#1CB0F6"),
    ("Body Parts", "חלקי גוף", "hand", "#00A889"),
    ("Clothes", "בגדים", "shirt", "#E056A0"),
    ("Music", "מוזיקה", "music", "#A560E8"),
    ("Sports", "ספורט", "ball", "#FF7A00"),
    ("Holidays", "חגים", "gift", "#FF4B4B"),
    ("Education", "חינוך", "book", "#1CB0F6"),
    ("Culture", "תרבות", "globe", "#00A889"),
    ("Finance", "כספים", "coin", "#58CC02"),
    ("Relationships", "מערכות יחסים", "users", "#E056A0"),
]
# ==== CATEGORY TABLE END ====

CATEGORIES = [c[0] for c in CATEGORY_TABLE]
CATEGORIES_NATIVE = {c[0]: c[1] for c in CATEGORY_TABLE}
CATEGORY_META = {c[0]: {"native": c[1], "icon": c[2], "accent": c[3]} for c in CATEGORY_TABLE}
MAX_RECENT_CATEGORIES = 25

# ==== HASHTAGS START ====
HASHTAGS = [
    "#learnhebrew",
    "#hebrewlessons",
    "#hebrewforbeginners",
    "#languagelearning",
    "#hebrewvocabulary",
    "#velocityhebrew",
    "#dailyhebrew",
    "#hebrew",
    "#learnlanguages",
    "#speakhebrew",
    "#bilingual",
    "#languagetips",
]
# ==== HASHTAGS END ====
