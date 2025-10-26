import os
import json
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator

# Load from Render env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")

# ✅ Main chat UI page (integrated with main project design)
def chat_ui(request):
    """Renders the chatbot popup template — used with main project's design"""
    return render(request, "chat/chat_page.html")

@method_decorator(csrf_exempt, name="dispatch")
class ChatAPIView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"error": "Empty message."}, status=400)

            if not GROQ_API_KEY:
                return JsonResponse({"error": "Groq API key missing."}, status=500)

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are AI Buddy — a friendly, educational chatbot for children."},
                    {"role": "user", "content": user_message}
                ]
            }

            # Send to Groq API
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=25)

            if response.status_code != 200:
                print("Groq API Error:", response.text)
                return JsonResponse({"error": f"Groq API error ({response.status_code})."}, status=400)

            result = response.json()
            reply = result.get("choices", [{}])[0].get("message", {}).get("content", "Hmm, I don’t know yet.")
            return JsonResponse({"response": reply})

        except Exception as e:
            print("Server Error:", str(e))
            return JsonResponse({"error": f"Server error: {e}"}, status=500)
