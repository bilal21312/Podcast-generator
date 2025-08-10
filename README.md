# Simple Podcast Generator API

A FastAPI service that generates AI podcasts using your existing `podcast.py` module. Simple and straightforward.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your `.env` file:**
   ```env
   API_KEY_GROQ=your_groq_api_key_here
   ELABS_API_KEY=your_elevenlabs_api_key_here
   ```

3. **Run the API:**
   ```bash
   uvicorn main_api:app --reload
   ```

4. **Test the API:**
   - Go to http://127.0.0.1:8000/docs (Swagger UI)
   - Or use the endpoint directly

## Test the API

### Using Swagger UI (/docs)

1. **Start your API:**
   ```bash
   uvicorn main_api:app --reload
   ```

2. **Open Swagger UI:**
   - Go to http://127.0.0.1:8000/docs in your browser
   - You'll see the interactive API documentation

3. **What you'll see automatically:**
   - **Endpoint list**: All available API endpoints
   - **Request format**: Shows exactly what JSON to send
   - **Parameters**: Lists all required and optional fields
   - **Response examples**: Shows what the API will return
   - **Try it out button**: Interactive testing interface

4. **Test the endpoint:**
   - Find the `POST /generate_podcast` endpoint
   - Click on it to expand
   - Click the "Try it out" button

5. **Fill in the request:**
   ```json
   {
     "topic": "artificial intelligence",
     "output_audio": "test_podcast.wav",
     "output_script": "test_script.txt"
   }
   ```

6. **Execute:**
   - Click "Execute" button
   - See the response and status code
   - Check your folder for generated files

**Note:** Swagger UI automatically generates the documentation from your FastAPI code, so it will always show the current API structure and parameters!

### Using curl (Command Line)

```bash
curl -X POST "http://127.0.0.1:8000/generate_podcast" \
     -H "Content-Type: application/json" \
     -d '{"topic": "cybersecurity"}'
```

### Using Postman

1. Create a new POST request
2. URL: `http://127.0.0.1:8000/generate_podcast`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
     "topic": "machine learning"
   }
   ```

## API Endpoints

### Generate Podcast
- **POST** `/generate_podcast`
- **Request Body (JSON):**
  ```json
  {
    "topic": "artificial intelligence",
    "output_audio": "my_podcast.wav",
    "output_script": "my_script.txt"
  }
  ```

**Parameters:**
- `topic` (required): What the podcast should be about
- `output_audio` (optional): Audio filename (default: "podcast.wav")
- `output_script` (optional): Script filename (default: "script.txt")

### Example Request
```bash
curl -X POST "http://127.0.0.1:8000/generate_podcast" \
     -H "Content-Type: application/json" \
     -d '{"topic": "cybersecurity"}'
```

### Example Response
```json
{
  "success": true,
  "script_file": "script.txt",
  "audio_file": "podcast.wav",
  "topic": "cybersecurity"
}
```

## How It Works

1. **Send a POST request** with your podcast topic
2. **The API generates** exactly 6 lines of dialogue (no labels, no extra text)
3. **Creates audio** using Eleven Labs text-to-speech
4. **Returns file paths** for both script and audio

## What You Get

- **Script file**: A text file with exactly 6 lines of podcast dialogue
- **Audio file**: A WAV file with the conversation converted to speech
- **Simple format**: Just dialogue lines, no speaker labels or extra text

## Requirements

- Python 3.7+
- FFmpeg (for audio processing)
- Groq API key (for script generation)
- Eleven Labs API key (for text-to-speech)

That's it! Simple and straightforward.
