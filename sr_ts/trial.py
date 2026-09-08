import os
from groq import Groq
from deepgram import(
        DeepgramClient,
        SpeakOptions,
        )


GROQ_API_KEY = os.getenv("GROQ_API_KEY","replace the text with your key")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY","replace the text with your key")

groq_client = Groq(api_key = GROQ_API_KEY)
deepgram_client = DeepgramClient(api_key = DEEPGRAM_API_KEY)


def speech_to_text(audio_file:str)->str:


    with open(audio_file_path,"rb") as file:
        translation = groq_client.audio.transcriptions.create(
                file=(audio_file,file.read()),
                model="whisper-large-v3",
                response_format="text"
                )
    return translation.strip()

def text_to_speech(text_prompt:str,output_filename:str = "output.mp3"):
    try:
        options = SpeakOptions(
                model="aura-asteria-en",
                encoding="mp3"
                )
        response = deepgram_client.speak.v("1").save(
                output_filename,
                {"text": text_prompt},
                options
                )
    except Exception as e:
        print("Failed to do\n")


if __name__ == "__main__":
    sample_text = "Hello this the first trial the this epic project you guys can try and also you can check weither groq speech to text is working or not. BYE"
    text_to_speech(sample_text,"first_text.mp3")



