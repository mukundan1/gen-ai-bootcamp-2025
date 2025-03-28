"""
Japanese Vocabulary Extractor
---------------------------
Parses Japanese lyrics to extract vocabulary with detailed breakdowns:
- Kanji/kana components
- Romaji readings
- Part of speech
- English meanings (via dictionary lookup)
"""

from typing import List, Dict
import fugashi
import jaconv
import json
from pathlib import Path

class JapaneseVocabExtractor:
    def __init__(self):
        # Initialize Fugashi for morphological analysis
        self.tagger = fugashi.Tagger()
        # Load kanji dictionary (you'll need to implement this)
        self.kanji_dict = self._load_kanji_dict()
        
    def _load_kanji_dict(self) -> Dict:
        """Load kanji definitions from dictionary file"""
        dict_path = Path(__file__).parent / "data" / "kanji_dict.json"
        if dict_path.exists():
            return json.loads(dict_path.read_text(encoding='utf-8'))
        return {}

    def _break_down_word(self, word: str) -> List[Dict]:
        """Break down word into individual kanji/kana components"""
        parts = []
        for char in word:
            romaji = jaconv.kana2romaji(char) if char.isalpha() else []
            parts.append({
                "kanji": char,
                "romaji": list(romaji) if romaji else []
            })
        return parts

    async def extract_vocabulary(self, text: str) -> List[Dict]:
        """Extract vocabulary with detailed breakdowns from Japanese text"""
        words = self.tagger.parse(text)
        vocabulary = []
        
        for word in words:
            # Only process content words
            if word.feature.pos1 in ['名詞', '動詞', '形容詞', '副詞']:
                entry = {
                    "kanji": word.surface,
                    "romaji": jaconv.kata2romaji(word.feature.pronunciation or word.surface),
                    "english": self.kanji_dict.get(word.surface, ""),
                    "parts": self._break_down_word(word.surface),
                    "pos": word.feature.pos1
                }
                vocabulary.append(entry)
        
        return vocabulary


# Create singleton instance
extractor = JapaneseVocabExtractor()

async def extract_vocabulary(lyrics: str) -> List[Dict]:
    """Main interface for vocabulary extraction"""
    return await extractor.extract_vocabulary(lyrics)