import sys
import os
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, UploadFile, File, HTTPException
from data_ingestion.api_agent import DataIngestionAPIAgent
from data_ingestion.scrap_agent import ScraperAgent
from agents.voice_agent import text_to_speech, speech_to_text
from agents.rag_agent import indexed_docs, rag_agent
from agents.analysis_agent import AnalyticsAgent
from agents.language_agent import generate_narrative
from config import ALPHA_VANTAGE_API_KEY, SEC_API_KEY, TECH_STOCKS, NEWS_SITE
import os
import uuid
import uvicorn
import traceback

app = FastAPI()

@app.post('/process_query')
async def process_query(query: str = None, audio: UploadFile = File(None)):
    try:
        # Handle voice input
        if audio:
            audio_path = f"temp_audio_{uuid.uuid4()}.wav"
            with open(audio_path, 'wb') as f:
                f.write(await audio.read())
            query = speech_to_text(audio_path)
            os.remove(audio_path)
            if not query or "error" in query.lower():
                raise HTTPException(status_code=400, detail=f"STT failed: {query}")

        if not query:
            raise HTTPException(status_code=400, detail="No query provided")

        # Fetch and analyze data
        api_data = DataIngestionAPIAgent(ALPHA_VANTAGE_API_KEY).fetch_stock_data(TECH_STOCKS)
        data_analysis = AnalyticsAgent(api_data).analysis()
        scrape_data = ScraperAgent(SEC_API_KEY, NEWS_SITE).doc_combined(TECH_STOCKS)
        indexed_emb = indexed_docs(scrape_data)
        rag = rag_agent(query, indexed_emb, k=5)
        
        # Generate narrative
        narrative, sources = generate_narrative(query, rag, data_analysis)
        
        # Generate speech
        output_file = os.path.join(os.getcwd(), f"output_{uuid.uuid4()}.mp3")
        speech_path = text_to_speech(narrative, output_file)
        if not speech_path:
            raise HTTPException(status_code=500, detail="TTS failed")

        return {'response': narrative, 'audio': speech_path, 'sources': sources}

    except Exception as e:
        traceback.print_exc()  # Add this line to print full stack trace
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        # Clean up audio files
        for file in os.listdir():
            if file.startswith('temp_audio') and file.endswith('.wav'):
                try:
                    os.remove(file)
                except:
                    pass

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
