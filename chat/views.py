# chat/views.py
import json
import requests
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    data = json.loads(request.body)
    user_message = data.get("message", "")

    if not user_message:
        return JsonResponse({"error": "Empty message"}, status=400)

    # ✅ Correct Groq-style payload
    payload = {
        "model": "llama3-8b-8192",  # or the model you selected in Groq dashboard
        "messages": [
            {"role": "system", "content": "You are AI Buddy, a friendly chatbot."},
            {"role": "user", "content": user_message}
        ]
    }

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(settings.GROQ_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        reply = data["choices"][0]["message"]["content"]  # ✅ Groq's format
        return JsonResponse({"reply": reply})
    except Exception as e:
        return JsonResponse({"error": "External API error", "detail": str(e)}, status=502)
