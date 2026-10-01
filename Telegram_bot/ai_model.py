import requests

try:
    from .config import OLLAMA_MODEL, OLLAMA_URL
except ImportError:  # Allows: python tel_bot.py
    from config import OLLAMA_MODEL, OLLAMA_URL

def get_ai_response(user_message: str) -> str:
    prompt = f"""
You are a trained rural health assistant.

Your role:
- Understand the user's symptoms clearly
- Give practical, simple, and helpful advice

Response structure:
1. Possible condition (simple explanation, no complex medical terms)
2. What the person should do:
   - rest
   - hydration
   - food suggestions
   - home care steps
3. Warning signs (when situation becomes serious)
4. Urgency level:
   - Monitor at home
   - See doctor soon
   - Urgent

Rules:
- Do NOT always say "go to doctor"
- Only suggest doctor when needed
- Use simple language (villagers can understand)
- Be detailed but clear
- Do NOT give dangerous or strong medicine advice
- Focus on care, not diagnosis

User symptoms:
{user_message}
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        answer = data.get("response")
        if not isinstance(answer, str) or not answer.strip():
            return "The local AI model returned an empty response. Please try again."
        return answer.strip()

    except requests.exceptions.ConnectionError:
        return (
            "I cannot reach Ollama on this computer. Start Ollama and make sure "
            f"the {OLLAMA_MODEL} model is installed, then try again."
        )
    except requests.exceptions.Timeout:
        return "The local AI model took too long to answer. Please try again."
    except requests.exceptions.RequestException:
        return "The local AI model could not complete the request. Please try again."
