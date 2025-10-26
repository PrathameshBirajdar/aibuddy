import os
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@method_decorator(csrf_exempt, name="dispatch")
class ChatAPIView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()
            if not user_message:
                return JsonResponse({"error": "Empty message."}, status=400)

            if not GROQ_API_KEY:
                return JsonResponse({
                    "error": "API key missing. Please configure GROQ_API_KEY on Render."
                }, status=500)

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are AI Buddy, a kind learning assistant for children."},
                    {"role": "user", "content": user_message},
                ],
            }

            response = requests.post(GROQ_API_URL, headers=headers, json=payload)
            if response.status_code != 200:
                return JsonResponse({"error": "Groq API error."}, status=response.status_code)

            reply = response.json()["choices"][0]["message"]["content"]
            return JsonResponse({"response": reply})

        except Exception as e:
            return JsonResponse({"error": f"Server error: {e}"}, status=500)
