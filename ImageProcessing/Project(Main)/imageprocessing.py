import os
import base64
import io
from PIL import Image
from groq import Groq

os.environ["GROQ_API_KEY"] = "GROQ API KEY"
client = Groq()

image_path = "ImageProcessing/Project(Main)/images/image.png"
output_text_path = "ImageProcessing/Project(Main)/analysis_output.txt"

prompt = (
    "Designation: Medical Professional , Task : This is an image of a rash , "
    "Analyze the visual characteristics of the rash and provide a detailed "
    "description of its appearance, including color, texture, size, and any other notable features. "
    "Additionally, suggest possible causes or conditions that could be associated with "
    "this type of rash based on its visual presentation."
)

def compress_image_to_base64(path, max_dim=1024, quality=85):
    with Image.open(path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

def analyze_rash_groq():
    os.makedirs(os.path.dirname(output_text_path), exist_ok=True)

    print("Compressing image for Groq payload...")
    base64_image = compress_image_to_base64(image_path)

    print("Sending request to Groq (Qwen 3.8 27B Vision)...")
    
    # Model ID updated to Groq's active vision model
    stream = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        temperature=0.2,
        max_completion_tokens=1024,
        stream=True,
    )

    print(f"\n--- Streamed Output (Saving to {output_text_path}) ---\n")
    
    with open(output_text_path, "w", encoding="utf-8") as f:
        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            print(content, end="", flush=True)
            f.write(content)

    print(f"\n\n--- Done! Analysis saved to {output_text_path} ---")

if __name__ == "__main__":
    analyze_rash_groq()