"""
Song Lyrics Agent
---------------
Orchestrates the process of finding and processing Japanese song lyrics.
"""

from typing import List, Dict
import ollama
from pathlib import Path
import json
import re
from datetime import datetime
from tools.search_web import search_web
from tools.get_page_content import get_page_content
from tools.extract_vocabulary import extract_vocabulary
from utils.logger import setup_logger

logger = setup_logger("agent")

class SongLyricsAgent:
    """Main agent class that coordinates the lyrics and vocabulary extraction process."""
    
    def __init__(self):
        logger.info("Initializing SongLyricsAgent")
        self.model = ollama.Mistral()
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Load the agent's instruction prompt from file."""
        try:
            prompt_path = Path(__file__).parent / "prompts" / "lyrics-agent.md"
            logger.debug(f"Loading prompt from: {prompt_path}")
            return prompt_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to load prompt template: {e}")
            raise

    def _generate_song_id(self, title: str) -> str:
        """Generate a URL-safe unique identifier for the song."""
        clean_title = re.sub(r'[^\w\s-]', '', title.lower())
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"song_{clean_title}_{timestamp}"

    async def _save_results(self, song_id: str, lyrics: str, vocabulary: List[Dict]) -> None:
        """Save lyrics and vocabulary to files."""
        logger.info(f"Saving results for song_id: {song_id}")
        try:
            output_dir = Path(__file__).parent / "outputs"
            output_dir.mkdir(exist_ok=True)
            
            # Save lyrics
            lyrics_path = output_dir / "lyrics" / f"{song_id}.txt"
            lyrics_path.parent.mkdir(exist_ok=True)
            lyrics_path.write_text(lyrics, encoding='utf-8')
            logger.debug(f"Saved lyrics to {lyrics_path}")
            
            # Save vocabulary
            vocab_path = output_dir / "vocabulary" / f"{song_id}.json"
            vocab_path.parent.mkdir(exist_ok=True)
            vocab_path.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=2), encoding='utf-8')
            logger.debug(f"Saved vocabulary to {vocab_path}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}", exc_info=True)
            raise

    async def run(self, user_request: str) -> str:
        """Execute the lyrics extraction and vocabulary analysis pipeline."""
        logger.info(f"Processing request: {user_request}")
        
        try:
            # Search for lyrics
            logger.info("Searching for lyrics...")
            search_results = await search_web(user_request)
            if not search_results:
                logger.error("No search results found")
                raise Exception("No lyrics found")
            
            # Get page content
            logger.info(f"Fetching content from {search_results[0]}")
            lyrics = await get_page_content(search_results[0])
            
            # Extract vocabulary
            logger.info("Extracting vocabulary")
            vocabulary = await extract_vocabulary(lyrics)
            
            # Generate and save results
            song_id = self._generate_song_id(user_request)
            await self._save_results(song_id, lyrics, vocabulary)
            
            return song_id
            
        except Exception as e:
            logger.error(f"Error in agent execution: {str(e)}", exc_info=True)
            raise