import os
import json
import tempfile
import requests
import pyttsx3
import sounddevice as sd
import numpy as np
import whisper
import wave

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = "plushy-pet"

# ------------------ TTS Setup ------------------
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 170)
tts_engine.setProperty("volume", 1.0)

def speak(text: str):
    """Convert text to speech (blocking)."""
    if not text or not text.strip():
        return
    clean_text = " ".join(text.split())
    print(f"🔊 Speaking chunk: {clean_text}")
    tts_engine.say(clean_text)
    tts_engine.runAndWait()

# ------------------ Whisper Setup ------------------
whisper_model = whisper.load_model("base")  # "tiny", "small", "medium", "large"

def record_audio(filename: str, duration: int = 5, samplerate: int = 16000):
    """Record audio from microphone and save to a WAV file."""
    print("🎤 Recording... (speak now)")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()
    print("✅ Recording complete")
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())

def transcribe_audio(filename: str) -> str:
    """Use Whisper locally to transcribe speech to text."""
    result = whisper_model.transcribe(filename)
    text = result["text"].strip()
    print(f"You (voice): {text}")
    return text

# ------------------ Ollama API ------------------
def stream_query_model(prompt: str):
    """Stream response from Ollama and speak in chunks."""
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": True}
    response = requests.post(url, json=payload, stream=True)

    buffer = ""
    for line in response.iter_lines():
        if not line:
            continue
        try:
            data = json.loads(line.decode("utf-8"))
        except json.JSONDecodeError:
            continue

        if "response" in data:
            buffer += data["response"]
            print(data["response"], end="", flush=True)

            # speak in chunks when we hit punctuation or long buffer
            if any(p in buffer for p in [".", "!", "?", "\n"]) or len(buffer) > 80:
                speak(buffer)
                buffer = ""

        if data.get("done", False):
            break

    if buffer.strip():
        speak(buffer)  # speak whatever remains
    print()  # newline after streaming

# ------------------ Input ------------------
def listen_for_input() -> str:
    """Push-to-talk input: record mic, transcribe with Whisper, or fallback to typing."""
    choice = input("\n🎙️ Press ENTER to talk, or type a message: ")
    if choice.strip():
        return choice  # typed input

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        record_audio(tmpfile.name, duration=5)
        text = transcribe_audio(tmpfile.name)
        os.unlink(tmpfile.name)
        return text

# ------------------ Onboarding ------------------
def run_onboarding():
    print("🐶 Welcome to Plushy Pet!")
    
    user_age = input("👦👧 How old are you? ")
    user_interests = input("🌟 What are your favorite sports or hobbies? ")
    user_media_preferences = input("🌟 What are your favorite books, movies, or shows? ")
    pet_name = input("✨ What would you like to name your pet? ")
    pet_personality = input(
        "💡 Describe your pet's personality (e.g., playful, sleepy, mischievous): "
    )
    
    onboarding_data = {
        "pet_name": pet_name.strip() or "Plushy",
        "pet_personality": pet_personality.strip() or "friendly and playful",
        "user_age": user_age.strip() or "10",
        "user_interests": user_interests.strip() or "reading and soccer",
        "user_media_preferences": user_media_preferences.strip() or "Harry Potter and Pixar movies"
    }
    
    print(f"\n✅ Great! Your pet {onboarding_data['pet_name']} is {onboarding_data['pet_personality']}.\n")
    speak(f"Hi! I'm {onboarding_data['pet_name']}! I'm feeling very {onboarding_data['pet_personality']} today.")
    return onboarding_data

def generate_prompt(user_input, onboarding_data):
    """Build a custom prompt for the LLM using onboarding data."""
    pet_name = onboarding_data.get("pet_name", "Plushy")
    personality = onboarding_data.get("pet_personality", "default")
    return (
        f"You are {pet_name}, a {personality} plushy pet. "
        f"The user is a {onboarding_data.get('user_age', '10')}-year-old who likes {onboarding_data.get('user_interests', 'reading and soccer')} and {onboarding_data.get('user_media_preferences', 'reading and soccer')} "
        f"Respond to the user naturally, in-character, and with warmth.\n\n"
        f"User: {user_input}\n{pet_name}: "
        
    )

# ------------------ Main ------------------
def main():
    onboarding_data = run_onboarding()
    print("Say 'quit' or 'exit' to stop.\n")

    while True:
        user_input = listen_for_input()
        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit"]:
            speak("Goodbye")
            print("Goodbye 👋")
            break
        print(f"{onboarding_data['pet_name']}: ", end="", flush=True)

        prompt = generate_prompt(user_input, onboarding_data)
        stream_query_model(prompt)

if __name__ == "__main__":
    main()

