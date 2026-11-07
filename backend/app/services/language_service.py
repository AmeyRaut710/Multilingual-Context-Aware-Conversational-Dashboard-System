import re
from typing import Tuple, Dict, Any, List, Optional

class LanguageService:
    # Devanagari Unicode range: \u0900-\u097F
    DEV_MARATHI_KEYWORDS = [
        "करा", "दाखवा", "बदला", "तयार करा", "तयार", "आहे", "नुसार", "नूसार", 
        "एकूण", "मधील", "कमी", "जास्त", "चा", "ची", "चे", "साठी", "वरून", "तक्ता", 
        "वृत्तालेख", "स्तंभ", "रेषा", "बेरीज", "सरासरी", "किमान", "कमाल", "सर्वोच्च", "सर्वात"
    ]
    DEV_HINDI_KEYWORDS = [
        "बनाओ", "दिखाओ", "करो", "में", "का", "की", "के", "कुल", "सहित", "हटाओ", 
        "बदलो", "शीर्ष", "औसत", "जोड़", "कम", "ज्यादा", "के अनुसार", "आलेख", "पाई", "रेखा"
    ]
    
    LATIN_MARATHI_KEYWORDS = [
        "kara", "kar", "dakhva", "dakhav", "badla", "tayar", "ekun", "nusar", 
        "madhe", "cha", "chi", "che", "sathi", "varun", "sarvat", "berij", 
        "sarasari", "jast", "kami", "banva", "kadha"
    ]
    LATIN_HINDI_KEYWORDS = [
        "banao", "dikhao", "karo", "badlo", "hatao", "ka", "ki", "ke", "mein", 
        "kul", "sabse", "liye", "aur", "pe", "jyada", "kam", "ausat", "jod"
    ]

    @classmethod
    def detect_language(cls, text: str) -> str:
        """
        Detects whether input is English, Hindi, Marathi, Hinglish, or Marathi-English.
        """
        text_lower = text.lower().strip()
        has_devanagari = bool(re.search(r'[\u0900-\u097F]', text))

        if has_devanagari:
            # Check for distinctive Marathi words in Devanagari
            marathi_score = sum(1 for kw in cls.DEV_MARATHI_KEYWORDS if kw in text)
            hindi_score = sum(1 for kw in cls.DEV_HINDI_KEYWORDS if kw in text)
            
            if marathi_score > hindi_score:
                return "Marathi"
            elif hindi_score > 0:
                return "Hindi"
            else:
                # Default Devanagari to Hindi if equal/indeterminate
                return "Hindi"
        else:
            # Check Latin transliterations
            tokens = re.findall(r'\b\w+\b', text_lower)
            marathi_latin_score = sum(1 for tok in tokens if tok in cls.LATIN_MARATHI_KEYWORDS)
            hindi_latin_score = sum(1 for tok in tokens if tok in cls.LATIN_HINDI_KEYWORDS)

            if marathi_latin_score > 0 and marathi_latin_score >= hindi_latin_score:
                return "Marathi-English"
            elif hindi_latin_score > 0:
                return "Hinglish"
            else:
                return "English"

    @classmethod
    def extract_chart_type(cls, text: str) -> Tuple[str, Optional[str]]:
        """
        Extract canonical chart type from multilingual text.
        Returns (canonical_type, matched_token)
        """
        text_lower = text.lower()
        
        # Specific compound types first
        if any(w in text_lower for w in ["horizontal bar", "horizontal", "aadva bar", "आडवा बार"]):
            return "horizontal_bar", "horizontal bar"
        if any(w in text_lower for w in ["stacked bar", "stacked", "स्टैक्ड"]):
            return "stacked_bar", "stacked bar"
        if any(w in text_lower for w in ["grouped bar", "grouped", "ग्रुप"]):
            return "grouped_bar", "grouped bar"
        if any(w in text_lower for w in ["donut", "doughnut", "डोनट"]):
            return "donut", "donut"
        if any(w in text_lower for w in ["pie chart", "pie", "पाई", "वृत्तालेख"]):
            return "pie", "pie"
        if any(w in text_lower for w in ["scatter plot", "scatter", "स्कैटर", "बिंदू"]):
            return "scatter", "scatter"
        if any(w in text_lower for w in ["histogram", "hist", "हिस्टोग्राम"]):
            return "histogram", "histogram"
        if any(w in text_lower for w in ["area chart", "area", "एरिया", "क्षेत्र"]):
            return "area", "area"
        if any(w in text_lower for w in ["box plot", "box", "बॉक्स"]):
            return "box", "box"
        if any(w in text_lower for w in ["heatmap", "heat map", "हीटमैप"]):
            return "heatmap", "heatmap"
        if any(w in text_lower for w in ["line chart", "line", "लाइन", "रेखा", "रेषा"]):
            return "line", "line"
        if any(w in text_lower for w in ["bar chart", "bar", "बार", "स्तंभ"]):
            return "bar", "bar"
            
        return "bar", None  # default fallback if needed

    @classmethod
    def extract_aggregation(cls, text: str) -> Tuple[str, Optional[str]]:
        """
        Extract canonical aggregation (sum, avg, count, min, max).
        """
        text_lower = text.lower()
        
        # Avg
        if any(w in text_lower for w in ["average", "avg", "mean", "औसत", "सरासरी", "ausat", "sarasari"]):
            return "avg", "average"
        # Min
        if any(w in text_lower for w in ["minimum", "min", "lowest", "न्यूनतम", "कमीत कमी", "kamit kami", "sabse kam", "sarvat kami"]):
            return "min", "minimum"
        # Max
        if any(w in text_lower for w in ["maximum", "max", "highest", "अधिकतम", "जास्तीत जास्त", "sarvat jast", "sabse jyada", "jastit jast"]):
            return "max", "maximum"
        # Count
        if any(w in text_lower for w in ["count", "number of", "total orders", "orders", "संख्या", "गिनती", "sankhya", "ginti", "moza"]):
            return "count", "count"
        # Sum / Total
        if any(w in text_lower for w in ["total", "sum", "कुल", "एकूण", "ekun", "kul", "jod", "बेरीज", "berij"]):
            return "sum", "total"

        return "sum", None

    @classmethod
    def extract_top_n(cls, text: str) -> Tuple[Optional[int], Optional[str]]:
        """
        Extract top or bottom N values.
        Supports digits ("top 5") and word numerals ("top five", "पाच", "पांच").
        """
        text_lower = text.lower()
        
        # Check for bottom / lowest
        is_bottom = any(w in text_lower for w in ["bottom", "lowest", "sabse kam", "sarvat kami", "तळाशी"])
        
        # Regex for digits e.g. "top 5", "top 10", "5 top"
        m = re.search(r'(?:top|bottom|first|last|शीर्ष|पहिले|सर्वात जास्त|सर्वात कमी|sabse jyada|sabse kam)\s*(\d+)', text_lower)
        if not m:
            m = re.search(r'(\d+)\s*(?:top|bottom|products|regions|categories|items)', text_lower)
        
        # Number words mapping
        word_to_num = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "एक": 1, "दोन": 2, "तीन": 3, "चार": 4, "पाच": 5, "सहा": 6, "सात": 7, "आठ": 8, "नऊ": 9, "दहा": 10,
            "दो": 2, "पांच": 5, "दस": 10
        }

        if m:
            n = int(m.group(1))
            return n, "asc" if is_bottom else "desc"
        
        for w, num in word_to_num.items():
            if f"top {w}" in text_lower or f"bottom {w}" in text_lower or f"शीर्ष {w}" in text_lower or f"पहिले {w}" in text_lower:
                return num, "asc" if is_bottom else "desc"

        return None, None

    @classmethod
    def extract_time_group(cls, text: str) -> Optional[str]:
        """Extract time dimension grouping: month, quarter, year, day."""
        text_lower = text.lower()
        if any(w in text_lower for w in ["month", "monthly", "महीने", "महिना", "mahina", "mahinyacha", "मासिक"]):
            return "month"
        if any(w in text_lower for w in ["quarter", "quarterly", "त्रैमासिक"]):
            return "quarter"
        if any(w in text_lower for w in ["year", "yearly", "annual", "annually", "साल", "वर्ष", "varsha", "varshik"]):
            return "year"
        if any(w in text_lower for w in ["day", "daily", "दैनिक", "roj", "din"]):
            return "day"
        return None

language_service = LanguageService()
