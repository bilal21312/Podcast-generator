import os
import requests
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

def get_script_from_llm(prompt, model=None, provider=None):
    """
    Generate podcast script from LLM
    
    Args:
        prompt (str): The prompt for the LLM
        model (str, optional): LLM model to use
        provider (str, optional): LLM provider (currently only Groq supported)
    
    Returns:
        str: Generated script text or None if failed
    """
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    messages = [{"role": "user", "content": prompt}]
    payload = {
        "model": model or llm_model,
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
    """
    Convert text to speech using Eleven Labs API
    
    Args:
        text (str): Text to convert to speech
        voice_id (str): Eleven Labs voice ID
        file_name (str): Output filename
    
    Returns:
        str: Filename if successful, None if failed
    """
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

def parse_script_to_segments(script_text):
    """
    Parses the raw script text into a list of dialogue lines.
    
    Args:
        script_text (str): Raw script text from LLM
    
    Returns:
        list: List of dialogue lines
    """
    # Split into lines and clean them
    lines = [line.strip() for line in script_text.strip().split('\n') if line.strip()]
    
    print(f"Parsed {len(lines)} lines from script:")
    for i, line in enumerate(lines):
        print(f"Line {i+1}: {line}")
    
    # Simple: just count lines and skip obvious intro
    dialogue_lines = []
    for line in lines:
        if not line.startswith("Here is") and not line.startswith("This is"):
            dialogue_lines.append(line)
    
    print(f"Found {len(dialogue_lines)} dialogue lines")
    
    if len(dialogue_lines) != 6:
        raise ValueError(f"Error: Expected exactly 6 lines, but got {len(dialogue_lines)}. Here's what was received:\n{script_text}")
    
    return dialogue_lines

def generate_and_combine_audio_from_segments(dialogue_segments, host_voice_id=None, guest_voice_id=None, output_audio_path="conversation.wav"):
    """
    Generate and combine audio from dialogue segments
    
    Args:
        dialogue_segments (list): List of dialogue lines
        host_voice_id (str, optional): Voice ID for host
        guest_voice_id (str, optional): Voice ID for guest
        output_audio_path (str): Output audio file path
    
    Returns:
        str: Path to generated audio file
    """
    print("\nParsing script and generating audio...")
    
    host_voice = host_voice_id or voice_ids[0]
    guest_voice = guest_voice_id or voice_ids[1]
    
    audio_segments = []

    for i, line in enumerate(dialogue_segments):
        voice_id = host_voice if i % 2 == 0 else guest_voice
        temp_filename = f"line_{i}.mp3"
        if speech_to_text(line, voice_id, temp_filename):
            segment = AudioSegment.from_mp3(temp_filename)
            audio_segments.append(segment + AudioSegment.silent(duration=300))
            os.remove(temp_filename)

    final_audio = sum(audio_segments)
    final_audio.export(output_audio_path, format="wav")
    print(f"Podcast saved as: {output_audio_path}")
    return output_audio_path

def generate_podcast_script_text(topic, llm_model=None, llm_provider=None):
    """
    Generates podcast script text using LLM.
    
    Args:
        topic (str): Podcast topic
        llm_model (str): LLM model to use
        llm_provider (str): LLM provider to use
    
    Returns:
        str: Generated script text
    """
    prompt = f"Write a podcast conversation about {topic}. Return exactly 6 lines of dialogue. No labels, no names, no extra text. Just 6 lines of conversation."
    
    print(f"Generating script for topic: {topic}")
    script_text = get_script_from_llm(prompt, llm_model, llm_provider)
    print(f"Generated script:\n{script_text}")
    
    return script_text

def generate_podcast(topic, output_audio_filename="conversation.wav", output_script_filename="script.txt", 
                     host_voice_id=None, guest_voice_id=None, llm_model=None, llm_provider=None):
    """
    Complete podcast generation pipeline
    
    Args:
        topic (str): Podcast topic
        output_audio_filename (str): Output audio filename
        output_script_filename (str): Output script filename
        host_voice_id (str, optional): Host voice ID
        guest_voice_id (str, optional): Guest voice ID
        llm_model (str, optional): LLM model
        llm_provider (str, optional): LLM provider
    
    Returns:
        dict: Dictionary with script_path and audio_path
    """
    print("Starting AI Podcast Generation.....")
    
    script = generate_podcast_script_text(topic, llm_model, llm_provider)
    if not script:
        raise Exception("Failed to generate script from LLM")
    
    with open(output_script_filename, "w", encoding="utf-8") as f:
        f.write(script)
    
    dialogue_segments = parse_script_to_segments(script)
    
    audio_path = generate_and_combine_audio_from_segments(
        dialogue_segments, host_voice_id, guest_voice_id, output_audio_filename
    )
    
    return {
        "script_path": output_script_filename,
        "audio_path": audio_path
    }
