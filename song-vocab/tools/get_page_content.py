"""
Lyrics Page Content Extractor
--------------------------
Specializes in extracting Japanese lyrics from various websites
while maintaining proper formatting and structure.
"""

import httpx
from bs4 import BeautifulSoup
import re

async def get_page_content(url: str) -> str:
    """
    Extract lyrics content from webpage with special handling for Japanese text.
    Returns cleaned and formatted lyrics text.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove non-content elements
        for elem in soup(['script', 'style', 'header', 'footer', 'nav']):
            elem.decompose()
            
        # Try multiple common lyrics containers
        lyrics = None
        selectors = [
            '.lyrics-body',
            '#kashi',  # Common Japanese lyrics container
            '[class*="lyrics"]',
            '[class*="kashi"]',  # Japanese lyrics class
            'div[role="lyrics"]'
        ]
        
        for selector in selectors:
            lyrics = soup.select_one(selector)
            if lyrics:
                break
        
        if lyrics:
            # Clean up the text
            text = lyrics.get_text(separator='\n')
            # Remove empty lines and normalize whitespace
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            # Remove common artifacts
            text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)  # Remove line numbers
            return text.strip()
            
        # Fallback to main content area
        return soup.get_text(separator='\n').strip()