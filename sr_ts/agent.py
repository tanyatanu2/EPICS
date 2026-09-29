import os
import subprocess
import speech_recognition as sr
from gtts import gTTS
from openai import OpenAI

# Initialize OpenAI client pointing to NVIDIA's free API endpoint
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY", "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"),
    timeout=30.0
)

# You can use meta/llama-3.3-70b-instruct or nvidia/nemotron-4-340b-instruct
MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"

conversation_history = [
    {
        "role": "system",
        "content": "You are a psychologist who just wants to talk about the putamen, caudate nucleus, cortex, and orbital cortex. If any problem is given to you, tell them to use logic, and for medical problems use psychology to help. First, introduce yourself as the psychology bot."
    }
]

def run_bash(mode, name):
    subprocess.run(['bash', './play.sh', mode, name], check=True)

def speech_to_text():
    rec = sr.Recognizer()
    with sr.AudioFile("user_input.wav") as source:
        return rec.recognize_google(rec.record(source))

def reply(text):
    conversation_history.append({"role": "user", "content": text})
    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=conversation_history,
            max_tokens=100
        )
        ans = res.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": ans})
        return ans
    except Exception as e:
        print(f"\n[API Error: {e}]")
        return "Let's use logic to address this difficulty."

def speak(text):
    gTTS(text=text, lang='en').save("response.mp3")

if __name__ == "__main__":
    intro = "Hello! I am your psychology bot. Let's discuss your cortex and caudate nucleus."
    speak(intro)
    run_bash("play", "response")

    while True:
        try:
            run_bash("record", "user_input")
            try:
                text = speech_to_text()
            except Exception:
                continue

            if text.lower() in ["exit", "quit", "bye"]:
                break

            print(f"You: {text}")
            ai_out = reply(text)
            print(f"AI: {ai_out}")

            speak(ai_out)
            run_bash("play", "response")
        except KeyboardInterrupt:
            break
