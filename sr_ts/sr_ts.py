import os
import tempfile
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment

def generate_reply_text(user_text):
    """
    Placeholder for your logic or LLM integration.
    Currently acts as a simple echo/acknowledgment.
    """
    return f"I heard you say: {user_text}. This is a working prototype."

def process_audio_pipeline(input_ogg_path):
    """
    Takes an input .ogg file, converts it to text, generates a reply,
    converts the reply to speech, and returns the path to the new audio file.
    """
    temp_wav = None
    output_mp3 = None
    
    try:
        # 1. Convert Telegram's .ogg to .wav (required for SpeechRecognition)
        audio = AudioSegment.from_ogg(input_ogg_path)
        
        # Use tempfile to prevent file storage leaks
        fd, temp_wav = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        audio.export(temp_wav, format="wav")
        
        # 2. Speech-to-Text (STT)
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            audio_data = recognizer.record(source)
            try:
                user_text = recognizer.recognize_google(audio_data)
                print(f"[STT] User said: {user_text}")
            except sr.UnknownValueError:
                user_text = "Sorry, I could not understand the audio."
            except sr.RequestError as e:
                user_text = "API error during speech recognition."
                print(f"[Error] {e}")

        # 3. Generate Reply Logic
        reply_text = generate_reply_text(user_text)
        print(f"[Logic] Reply: {reply_text}")

        # 4. Text-to-Speech (TTS)
        tts = gTTS(text=reply_text, lang='en')
        fd_out, output_mp3 = tempfile.mkstemp(suffix=".mp3")
        os.close(fd_out)
        tts.save(output_mp3)

        return output_mp3, reply_text

    finally:
        # Clean up intermediate .wav file to free memory/disk space
        if temp_wav and os.path.exists(temp_wav):
            os.remove(temp_wav)
