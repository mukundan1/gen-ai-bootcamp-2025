"""
Japanese Lyrics Web Search
------------------------
Specialized search tool for finding Japanese song lyrics
using SERP API with optimized query construction.
"""

from serpapi import GoogleSearch
from typing import List
import os
from dotenv import load_dotenv
from utils.logger import setup_logger

logger = setup_logger("search_web")

load_dotenv()

async def search_web(query: str) -> List[str]:
    """
    Search for Japanese lyrics using SERP API.
    Optimizes query for Japanese lyrics sites.
    """
    logger.info(f"Searching for: {query}")
    
    try:
        api_key = os.getenv("SERP_API_KEY")
        if not api_key:
            logger.error("SERP_API_KEY not found in environment variables")
            raise ValueError("SERP_API_KEY not configured")
            
        params = {
            "engine": "google",
            "q": f"{query} 日本語 歌詞",
            "api_key": api_key,
            "num": 5
        }
        
        logger.debug(f"Search params: {params}")
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "organic_results" in results:
            urls = [result["link"] for result in results["organic_results"]]
            logger.info(f"Found {len(urls)} results")
            logger.debug(f"URLs found: {urls}")
            return urls
            
        logger.warning("No organic results found in search response")
        return []
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        raise