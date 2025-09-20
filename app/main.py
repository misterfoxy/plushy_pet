import os
import json
import requests
import pyttsx3
import speech_recognition as sr

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = "plushy-pet"

# --- Text-to-Speech engine setup ---
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 170)   # speaking speed (default ~200)
tts_engine.setProperty("volume", 1.0) # 0.0 to 1.0

def speak(text: str):
    """Convert text to spoken audio."""
    tts_engine.say(text)
    tts_engine.runAndWait()

def query_model(prompt: str) -> str:
    """Send a prompt to the LLM running in Ollama and return the response text."""
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {"model": MODEL_NAME, "prompt": prompt}
    response = requests.post(url, json=payload, stream=True)

    output = ""
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8")
            if '"response":"' in data:
                part = data.split('"response":"')[1].split('"')[0]
                output += part
    return output.strip()

def main():
    print("🐶 Plushy Pet is ready! Type 'quit' to exit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye 👋")
            speak("Goodbye")
            break

        reply = query_model(user_input)
        print(f"Pet: {reply}")
        speak(reply)

if __name__ == "__main__":
    main()

# def query_model(prompt: str):
#     """Send a prompt to the LLM running in Ollama and stream the response."""
#     url = f"{OLLAMA_HOST}/api/generate"
#     payload = {"model": MODEL_NAME, "prompt": prompt}

#     with requests.post(url, json=payload, stream=True) as response:
#         for line in response.iter_lines():
#             if line:
#                 try:
#                     data = json.loads(line.decode("utf-8"))
#                     if "response" in data:
#                         # Print without newline and flush so it appears instantly
#                         print(data["response"], end="", flush=True)
#                     if data.get("done", False):
#                         break
#                 except json.JSONDecodeError:
#                     continue
#     print()  # final newline at end of response

# def main():
#     print("🐶 Plushy Pet is ready! Type 'quit' to exit.")
#     while True:
#         user_input = input("\nYou: ")
#         if user_input.lower() in ["quit", "exit"]:
#             print("Goodbye 👋")
#             break
#         print("Pet: ", end="", flush=True)
#         query_model(user_input)

# if __name__ == "__main__":
#     main()