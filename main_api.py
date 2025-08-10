from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
import podcast
import json

load_dotenv()

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Podcast Generator API"}

@app.post("/generate_podcast")
async def generate_podcast(request: Request):
    try:
        body = await request.json()
        
        topic = body.get("topic")
        output_audio = body.get("output_audio", "podcast.wav")
        output_script = body.get("output_script", "script.txt")
        
        if not topic:
            return {"error": "topic is required"}
        
        if not os.getenv('API_KEY_GROQ') or not os.getenv('ELABS_API_KEY'):
            return {"error": "Missing API keys"}
        
        result = podcast.generate_podcast(
            topic=topic,
            output_audio_filename=output_audio,
            output_script_filename=output_script
        )
        
        return {
            "success": True,
            "script_file": result["script_path"],
            "audio_file": result["audio_path"],
            "topic": topic
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
