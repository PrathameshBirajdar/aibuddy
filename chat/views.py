import os
import json
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
from django.conf import settings

# Get API key from settings
GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_API_URL = settings.GROQ_API_URL

# Add to views.py
def test_groq(request):
    """Test endpoint to verify Groq API configuration"""
    return JsonResponse({
        "api_key_present": bool(GROQ_API_KEY),
        "api_key_prefix": GROQ_API_KEY[:10] if GROQ_API_KEY else None,
        "api_url": GROQ_API_URL
    })

# ✅ Main chat UI page
def chat_ui(request):
    """Renders the chatbot popup template"""
    return render(request, "chat/chat_page.html")

@method_decorator(csrf_exempt, name="dispatch")
class ChatAPIView(View):
    def post(self, request):
        try:
            # Parse request
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"error": "Empty message."}, status=400)

            # Check API key
            if not GROQ_API_KEY:
                print("❌ GROQ_API_KEY is missing!")
                return JsonResponse({
                    "error": "Groq API key not configured. Please check environment variables."
                }, status=500)

            print(f"📤 Sending to Groq: {user_message[:50]}...")

            # Prepare request
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are AI Buddy — a friendly, educational chatbot for children."
                    },
                    {
                        "role": "user", 
                        "content": user_message
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1024
            }

            # Log the request (without exposing full API key)
            print(f"🔑 Using API Key: {GROQ_API_KEY[:10]}...")
            print(f"🌐 API URL: {GROQ_API_URL}")

            # Send to Groq API
            response = requests.post(
                GROQ_API_URL, 
                headers=headers, 
                json=payload, 
                timeout=25
            )

            # Log response status
            print(f"📥 Groq Response Status: {response.status_code}")

            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ Groq API Error: {error_detail}")
                return JsonResponse({
                    "error": f"Groq API error ({response.status_code})",
                    "detail": error_detail
                }, status=400)

            # Parse response
            result = response.json()
            reply = result.get("choices", [{}])[0].get("message", {}).get("content", "Hmm, I don't know yet.")
            
            print(f"✅ Reply: {reply[:50]}...")
            return JsonResponse({"response": reply})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in request"}, status=400)
        except requests.exceptions.Timeout:
            return JsonResponse({"error": "Request timed out"}, status=504)
        except Exception as e:
            print(f"❌ Server Error: {str(e)}")
            return JsonResponse({
                "error": f"Server error: {str(e)}"
            }, status=500)