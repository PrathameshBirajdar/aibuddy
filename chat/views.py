# aibuddy/chat/views.py
import os
import json
import requests
from dotenv import load_dotenv
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Load .env if present
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, "..", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Chat popup HTML
def chat_page(request):
    """Render the chat popup UI (template: chat/chat_page.html)."""
    return render(request, "chat/chat_page.html")

# API used by JS to get model response
@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    user_message = (payload.get("message") or "").strip()
    kid_name = payload.get("name", "Buddy")
    learning_context = payload.get("context", "general")  # e.g. english, math, gk, alphabets, numbers

    if not user_message:
        return JsonResponse({"error": "Message cannot be empty"}, status=400)

    # Build system prompt for the model depending on context
    system_prompt = f"You are AI Buddy, a friendly playful teacher for a child named {kid_name}. Speak in simple sentences, use emojis and encourage learning."

    if learning_context == "alphabets":
        system_prompt += " Teach letters A-Z with short examples like 'A for Apple 🍎'. Ask simple follow-ups."
    elif learning_context == "numbers":
        system_prompt += " Teach counting and simple arithmetic with step-by-step hints."
    elif learning_context == "animals":
        system_prompt += " Teach animal names and sounds with fun facts and small quizzes."
    elif learning_context == "english":
        system_prompt += " Help the child learn English words, rhymes and simple pronunciation tips."
    elif learning_context == "math":
        system_prompt += " Provide simple math practice, step-by-step explanation for sums appropriate for kids."
    elif learning_context == "gk":
        system_prompt += " Provide short, kid-friendly general knowledge facts and short quiz questions."
    elif learning_context == "quiz":
        system_prompt += " Ask a short multiple-choice quiz question appropriate for children."
    elif learning_context == "stories":
        system_prompt += " Tell a short moral story for young children with a clear moral."

    # Request payload
    request_payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 512
    }

    if not GROQ_API_KEY:
        return JsonResponse({"error": "Server misconfiguration: missing API key"}, status=500)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=request_payload, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        # Don't leak internal details to client; log on server and return friendly message
        print("Network/Groq error:", str(e))
        return JsonResponse({"error": "Connection error. Please try again later."}, status=502)

    try:
        result = resp.json()
    except ValueError:
        return JsonResponse({"error": "Invalid response from AI service"}, status=502)

    if "error" in result:
        err_msg = result["error"].get("message", "Model error")
        print("Model error:", result)
        return JsonResponse({"error": err_msg}, status=400)

    # OpenAI/Groq response shape: choices[0].message.content
    try:
        message_text = result["choices"][0]["message"]["content"]
    except Exception as e:
        print("Unexpected model shape:", result, e)
        return JsonResponse({"error": "Unexpected response from AI"}, status=502)

    return JsonResponse({"response": message_text})
