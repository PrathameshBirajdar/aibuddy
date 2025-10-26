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
                    "error": "Groq API key not configured."
                }, status=500)

            print(f"✅ API Key loaded: {GROQ_API_KEY[:15]}...")
            print(f"📤 User message: {user_message}")

            # Prepare request
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "user", 
                        "content": user_message
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1024
            }

            print(f"🌐 Sending to: {GROQ_API_URL}")
            print(f"📦 Payload: {json.dumps(payload, indent=2)}")

            # Send to Groq API
            response = requests.post(
                GROQ_API_URL, 
                headers=headers, 
                json=payload, 
                timeout=30
            )

            # Log response
            print(f"📥 Status Code: {response.status_code}")
            print(f"📥 Response: {response.text[:500]}")

            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ Groq API Error: {error_detail}")
                
                # Try to parse error message
                try:
                    error_json = response.json()
                    error_message = error_json.get("error", {}).get("message", "Unknown error")
                except:
                    error_message = error_detail[:200]
                
                return JsonResponse({
                    "error": f"Groq API error: {error_message}"
                }, status=400)

            # Parse response
            result = response.json()
            reply = result.get("choices", [{}])[0].get("message", {}).get("content", "Hmm, I don't know yet.")
            
            print(f"✅ Reply: {reply[:100]}...")
            return JsonResponse({"response": reply})

        except json.JSONDecodeError as e:
            print(f"❌ JSON Error: {str(e)}")
            return JsonResponse({"error": "Invalid JSON in request"}, status=400)
        except requests.exceptions.Timeout:
            print("❌ Timeout error")
            return JsonResponse({"error": "Request timed out"}, status=504)
        except Exception as e:
            print(f"❌ Unexpected Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                "error": f"Server error: {str(e)}"
            }, status=500)