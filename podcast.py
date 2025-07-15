import os
import requests
import argparse
from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv()

groq_api_key = os.getenv('API_KEY_GROQ')
eleven_labs_api_key = os.getenv('ELABS_API_KEY')

if not groq_api_key or not eleven_labs_api_key:
    raise EnvironmentError("Missing API keys. Check your .env file.")

api_base_groq = "https://api.groq.com/openai/v1/chat/completions"
llm_model = "llama3-8b-8192"

api_base_eleven_labs = "https://api.elevenlabs.io/v1/text-to-speech/"
voice_ids = ["21m00Tcm4TlvDq8ikWAM", "UgBBYS2sOqTuMpoF3BR0"]

def get_script_from_llm(prompt):
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    messages = [{"role": "user", "content": prompt}]
    payload = {
        "model": llm_model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800
    }

    print("\nCalling LLM API...")
    try:
        response = requests.post(api_base_groq, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        print("LLM API call failed:", str(e))
        return None

def speech_to_text(text, voice_id, file_name):
    headers = {
        "xi-api-key": eleven_labs_api_key,
        "Content-Type": "application/json"
    }
    url = f"{api_base_eleven_labs}{voice_id}"
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.7, "similarity_boost": 0.75}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        with open(file_name, 'wb') as f:
            f.write(response.content)
        return file_name
    except Exception as e:
        print(f"TTS failed for line '{text[:30]}...':", str(e))
        return None

def generate_conversation(script_text, output_file):
    print("\nParsing script and generating audio...")
    lines = [line.strip() for line in script_text.strip().split('\n') if line.strip()]
    audio_segments = []

    for i, line in enumerate(lines):
        voice_id = voice_ids[i % 2]
        temp_filename = f"line_{i}.mp3"
        if speech_to_text(line, voice_id, temp_filename):
            segment = AudioSegment.from_mp3(temp_filename)
            audio_segments.append(segment + AudioSegment.silent(duration=300))
            os.remove(temp_filename)

    final_audio = sum(audio_segments)
    final_audio.export(output_file, format="wav")
    print(f"Final podcast saved as: {output_file}")

def main():
    print("Starting AI Podcast Generation...")
    parser = argparse.ArgumentParser(description="Generate a 6-line podcast with AI voices")
    parser.add_argument("--output", default="conversation.wav", help="Output audio file name")
    parser.add_argument("--transcript", default="script.txt", help="File to save the generated script")
    args = parser.parse_args()

    prompt = """
    Write a short podcast conversation about a trending topic in artificial intelligence or technology.
    The conversation must be exactly 6 lines long:
    - 3 lines for the host
    - 3 lines for the guest
    Do not include any names or speaker labels. Simply return the 6 lines of dialogue, one per line, in natural conversation order (host, guest, host, guest, host, guest). Do not add any introductions, titles, or explanations.
    """

    script = get_script_from_llm(prompt)
    if script:
        with open(args.transcript, "w", encoding="utf-8") as f:
            f.write(script)
        generate_conversation(script, args.output)
    else:
        print("Failed to get script.")

if __name__ == "__main__":
    main()
