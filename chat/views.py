import os
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

# ✅ Auto-detect Render environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

if os.getenv("RENDER") != "true" and not GROQ_API_KEY:
    print("⚠️ Running locally — Groq API disabled.")

@method_decorator(csrf_exempt, name="dispatch")
class ChatAPIView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get("message", "").strip()

            if not message:
                return JsonResponse({"error": "Message cannot be empty"}, status=400)

            if not GROQ_API_KEY:
                return JsonResponse({
                    "error": "Groq API key not configured. Please set it in Render Environment Variables."
                }, status=500)

            # ✅ Call Groq API
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama3-8b-8192",  # or whichever model you're using
                "messages": [
                    {"role": "system", "content": "You are AI Buddy, a helpful learning assistant for kids."},
                    {"role": "user", "content": message}
                ]
            }

            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=20)
            if response.status_code != 200:
                return JsonResponse({"error": f"Groq API error: {response.text}"}, status=500)

            result = response.json()
            reply = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return JsonResponse({"response": reply})

        except Exception as e:
            return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)
