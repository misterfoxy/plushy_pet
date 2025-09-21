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

# --- Text-to-Speech setup ---
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 170)
tts_engine.setProperty("volume", 1.0)

# --- Whisper setup (offline) ---
whisper_model = whisper.load_model("base")  # "tiny", "small", "medium", "large"

def speak(text: str):
    """Convert text to speech (blocking)."""
    if not text or not text.strip():
        return
    clean_text = " ".join(text.split())
    print(f"🔊 Speaking chunk: {clean_text}")
    tts_engine.say(clean_text)
    tts_engine.runAndWait()

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

def main():
    print("🐶 Plushy Pet is ready! Say 'quit' or 'exit' to stop.")
    speak("Hello there! Let's talk.")

    while True:
        user_input = listen_for_input()
        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit"]:
            speak("Goodbye")
            print("Goodbye 👋")
            break
        print("Pet: ", end="", flush=True)
        stream_query_model(user_input)

if __name__ == "__main__":
    main()



# import os
# import json
# import requests
# import pyttsx3
# import speech_recognition as sr

# OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
# MODEL_NAME = "plushy-pet"

# # --- Text-to-Speech engine setup ---
# tts_engine = pyttsx3.init()
# tts_engine.setProperty("rate", 170)
# tts_engine.setProperty("volume", 1.0)

# def speak(text: str):
#     """Convert text to spoken audio."""
#     tts_engine.say(text)
#     tts_engine.runAndWait()

# def query_model(prompt: str) -> str:
#     """Send a prompt to the LLM running in Ollama and return the response text."""
#     url = f"{OLLAMA_HOST}/api/generate"
#     payload = {"model": MODEL_NAME, "prompt": prompt}
#     response = requests.post(url, json=payload, stream=True)

#     output = ""
#     for line in response.iter_lines():
#         if line:
#             data = line.decode("utf-8")
#             if '"response":"' in data:
#                 part = data.split('"response":"')[1].split('"')[0]
#                 output += part
#     return output.strip()

# def listen_for_input() -> str:
#     """Capture voice input and return transcribed text using Whisper (offline)."""
#     recognizer = sr.Recognizer()

#     try:
#         with sr.Microphone() as source:
#             print("\n🎤 Listening... (say something or type 'quit' to exit)")
#             recognizer.adjust_for_ambient_noise(source)
#             audio = recognizer.listen(source)

#         # Use Whisper model locally (choose: tiny, base, small, medium, large)
#         text = recognizer.recognize_whisper(audio, model="base")
#         print(f"You (voice): {text}")
#         return text
#     except OSError:
#         # No mic detected, fallback to typing
#         return input("\nYou (typed): ")
#     except sr.UnknownValueError:
#         print("❌ Sorry, I couldn't understand that. Try again.")
#         return ""
#     except Exception as e:
#         print(f"⚠️ Whisper error: {e}, falling back to typing.")
#         return input("\nYou (typed): ")

# def main():
#     print("🐶 Plushy Pet is ready! Say 'quit' or 'exit' to stop.")

#     while True:
#         user_input = listen_for_input()
#         if not user_input:
#             continue

#         if user_input.lower() in ["quit", "exit"]:
#             print("Goodbye 👋")
#             speak("Goodbye")
#             break

#         reply = query_model(user_input)
#         print(f"Pet: {reply}")
#         speak(reply)

# if __name__ == "__main__":
#     main()

# # # --- Text-to-Speech engine setup ---
# # tts_engine = pyttsx3.init()
# # tts_engine.setProperty("rate", 170)   # speaking speed (default ~200)
# # tts_engine.setProperty("volume", 1.0) # 0.0 to 1.0

# # def speak(text: str):
# #     """Convert text to spoken audio."""
# #     tts_engine.say(text)
# #     tts_engine.runAndWait()

# # def query_model(prompt: str) -> str:
# #     """Send a prompt to the LLM running in Ollama and return the response text."""
# #     url = f"{OLLAMA_HOST}/api/generate"
# #     payload = {"model": MODEL_NAME, "prompt": prompt}
# #     response = requests.post(url, json=payload, stream=True)

# #     output = ""
# #     for line in response.iter_lines():
# #         if line:
# #             data = line.decode("utf-8")
# #             if '"response":"' in data:
# #                 part = data.split('"response":"')[1].split('"')[0]
# #                 output += part
# #     return output.strip()

# # def main():
# #     print("🐶 Plushy Pet is ready! Type 'quit' to exit.")
# #     while True:
# #         user_input = input("\nYou: ")
# #         if user_input.lower() in ["quit", "exit"]:
# #             print("Goodbye 👋")
# #             speak("Goodbye")
# #             break

# #         reply = query_model(user_input)
# #         print(f"Pet: {reply}")
# #         speak(reply)

# # if __name__ == "__main__":
# #     main()



# # OG VERSION BELOW
# # def query_model(prompt: str):
# #     """Send a prompt to the LLM running in Ollama and stream the response."""
# #     url = f"{OLLAMA_HOST}/api/generate"
# #     payload = {"model": MODEL_NAME, "prompt": prompt}

# #     with requests.post(url, json=payload, stream=True) as response:
# #         for line in response.iter_lines():
# #             if line:
# #                 try:
# #                     data = json.loads(line.decode("utf-8"))
# #                     if "response" in data:
# #                         # Print without newline and flush so it appears instantly
# #                         print(data["response"], end="", flush=True)
# #                     if data.get("done", False):
# #                         break
# #                 except json.JSONDecodeError:
# #                     continue
# #     print()  # final newline at end of response

# # def main():
# #     print("🐶 Plushy Pet is ready! Type 'quit' to exit.")
# #     while True:
# #         user_input = input("\nYou: ")
# #         if user_input.lower() in ["quit", "exit"]:
# #             print("Goodbye 👋")
# #             break
# #         print("Pet: ", end="", flush=True)
# #         query_model(user_input)

# # if __name__ == "__main__":
# #     main()