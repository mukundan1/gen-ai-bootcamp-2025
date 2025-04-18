from fastapi import APIRouter, HTTPException
from lib.db import get_db_connection
import os

router = APIRouter()

# Only enable these endpoints in development/testing
ENABLE_RESET = os.getenv("ENABLE_RESET", "false").lower() == "true"

@router.post("/reset/all", tags=["Reset"])
async def reset_all_data():
    """
    Reset all data in the database. Only available in development/testing.
    """
    if not ENABLE_RESET:
        raise HTTPException(
            status_code=403,
            detail="Reset endpoints are disabled in production"
        )
    
    with get_db_connection() as conn:
        # Delete data in reverse order of dependencies
        conn.execute("DELETE FROM word_reviews")
        conn.execute("DELETE FROM word_review_items")
        conn.execute("DELETE FROM study_sessions")
        conn.execute("DELETE FROM study_activities")
        conn.execute("DELETE FROM words")
        conn.execute("DELETE FROM groups")
        
        # Reset auto-increment counters
        conn.execute("DELETE FROM sqlite_sequence")
        
        return {"message": "All data has been reset"}

@router.post("/reset/study-data", tags=["Reset"])
async def reset_study_data():
    """
    Reset only study-related data, preserving words and groups.
    """
    if not ENABLE_RESET:
        raise HTTPException(
            status_code=403,
            detail="Reset endpoints are disabled in production"
        )
    
    with get_db_connection() as conn:
        # Delete study-related data
        conn.execute("DELETE FROM word_reviews")
        conn.execute("DELETE FROM word_review_items")
        conn.execute("DELETE FROM study_sessions")
        conn.execute("DELETE FROM study_activities")
        
        # Reset auto-increment counters for affected tables
        conn.execute("""
            DELETE FROM sqlite_sequence 
            WHERE name IN (
                'word_reviews', 
                'word_review_items', 
                'study_sessions', 
                'study_activities'
            )
        """)
        
        return {"message": "Study data has been reset"}

@router.post("/reset/seed", tags=["Reset"])
async def seed_test_data():
    """
    Seed the database with test data. Only available in development/testing.
    """
    if not ENABLE_RESET:
        raise HTTPException(
            status_code=403,
            detail="Reset endpoints are disabled in production"
        )
    
    with get_db_connection() as conn:
        # Create test groups
        conn.execute("""
            INSERT INTO groups (name, description) VALUES 
            ('Beginner Japanese', 'Basic Japanese vocabulary and phrases'),
            ('Intermediate Japanese', 'Common Japanese expressions and grammar')
        """)
        
        # Create test words
        conn.execute("""
            INSERT INTO words (japanese, english, parts, romaji, reading, word_type, jlpt_level, group_id) VALUES 
            ('私', 'I/me', '{"type":"pronoun","usage":"subject"}', 'watashi', 'わたし', 'pronoun', 5, 1),
            ('あなた', 'you', '{"type":"pronoun","usage":"subject"}', 'anata', 'あなた', 'pronoun', 5, 1),
            ('彼ら', 'they/them', '{"type":"pronoun","usage":"subject"}', 'karera', 'かれら', 'pronoun', 4, 1),
            ('私たち', 'we/us', '{"type":"pronoun","usage":"subject"}', 'watashitachi', 'わたしたち', 'pronoun', 5, 1),
            ('彼', 'he/him', '{"type":"pronoun","usage":"subject"}', 'kare', 'かれ', 'pronoun', 5, 1),
            ('走る', 'run', '{"type":"verb","tense":"present"}', 'hashiru', 'はしる', 'verb', 4, 2),
            ('歩く', 'walk', '{"type":"verb","tense":"present"}', 'aruku', 'あるく', 'verb', 5, 2),
            ('話す', 'talk', '{"type":"verb","tense":"present"}', 'hanasu', 'はなす', 'verb', 5, 2),
            ('食べる', 'eat', '{"type":"verb","tense":"present"}', 'taberu', 'たべる', 'verb', 5, 2),
            ('寝る', 'sleep', '{"type":"verb","tense":"present"}', 'neru', 'ねる', 'verb', 5, 2)
        """)
        
        # Create test study activities
        conn.execute("""
            INSERT INTO study_activities (name, group_id, created_at) VALUES 
            ('Vocabulary Review', 1, datetime('now')),
            ('Grammar Practice', 2, datetime('now'))
        """)
        
        # Create test study sessions
        conn.execute("""
            INSERT INTO study_sessions (study_activity_id, group_id, created_at) VALUES 
            (1, 1, datetime('now')),
            (2, 2, datetime('now'))
        """)
        
        # Add words to review items
        conn.execute("""
            INSERT INTO word_review_items (study_session_id, word_id) 
            SELECT 1, id FROM words WHERE group_id = 1
            UNION
            SELECT 2, id FROM words WHERE group_id = 2
        """)
        
        # Add some word reviews
        conn.execute("""
            INSERT INTO word_reviews (word_id, study_session_id, correct, created_at)
            SELECT 
                word_id, 
                study_session_id, 
                CASE WHEN RANDOM() > 0.3 THEN TRUE ELSE FALSE END,
                datetime('now', '-' || RANDOM() * 10 || ' minutes')
            FROM word_review_items
        """)
        
        return {"message": "Test data has been seeded"} 