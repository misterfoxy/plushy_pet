import os
import json
import requests

# If you're running Python inside docker-compose, keep this.
# If you're running Python on your Mac, change to "http://localhost:11434"
OLLAMA_HOST = "http://ollama:11434"
MODEL_NAME = "plushy-pet"

def query_model(prompt: str):
    """Send a prompt to the LLM running in Ollama and stream the response."""
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {"model": MODEL_NAME, "prompt": prompt}

    with requests.post(url, json=payload, stream=True) as response:
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    if "response" in data:
                        # Print without newline and flush so it appears instantly
                        print(data["response"], end="", flush=True)
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
    print()  # final newline at end of response

def main():
    print("🐶 Plushy Pet is ready! Type 'quit' to exit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye 👋")
            break
        print("Pet: ", end="", flush=True)
        query_model(user_input)

if __name__ == "__main__":
    main()