CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    japanese TEXT NOT NULL,
    english TEXT NOT NULL,
    parts JSON,
    romaji TEXT,
    reading TEXT,
    word_type TEXT,
    jlpt_level INTEGER CHECK (jlpt_level BETWEEN 1 AND 5)
);