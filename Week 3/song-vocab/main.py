from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from agent import SongLyricsAgent
from utils.logger import setup_logger

logger = setup_logger("api")

app = FastAPI(title="Japanese Lyrics Vocabulary Extractor")

class MessageRequest(BaseModel):
    message_request: str

class VocabularyItem(BaseModel):
    kanji: str
    romaji: str
    english: str
    parts: List[Dict[str, any]]
    pos: str

class LyricsResponse(BaseModel):
    song_id: str

@app.post("/api/agent", response_model=LyricsResponse)
async def get_lyrics(request: MessageRequest) -> LyricsResponse:
    logger.info(f"Received request for lyrics: {request.message_request}")
    try:
        agent = SongLyricsAgent()
        logger.info("Created SongLyricsAgent instance")
        
        song_id = await agent.run(request.message_request)
        logger.info(f"Successfully processed request, got song_id: {song_id}")
        
        return LyricsResponse(song_id=song_id)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application starting up...")
    
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI application shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)