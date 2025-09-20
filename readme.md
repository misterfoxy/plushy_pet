# Plushy Pet

- Uses whisper for local Speech-to-Text to take audio input from the user
- Uses Llama2 with a Modelfile for LLM prompts
- Uses pyttsx3 for Text-to-Speech output of the response from the LLM

## Download & Install

- Download through github
- run docker-compose

## Developing on Plushy Pet

- Update the Modelfile
- run `docker exec -it ollama bash`
- run `cd /models`
- run `ollama create plushy-pet -f Modelfile`