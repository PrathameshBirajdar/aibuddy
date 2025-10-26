import os
import json
import requests
from dotenv import load_dotenv
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# ====================================
# ✅ Environment Setup
# ====================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env")

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print("✅ Loaded .env file")
else:
    print("⚠️ No .env file found — relying on system environment variables")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")

if GROQ_API_KEY:
    print(f"✅ GROQ_API_KEY loaded: {GROQ_API_KEY[:10]}...")
else:
    print("❌ GROQ_API_KEY not found!")

print(f"✅ GROQ_API_URL: {GROQ_API_URL}")

# ====================================
# 🔹 Chat Page
# ====================================
def chat_page(request):
    """Render chat popup UI"""
    return render(request, "chat/chat_page.html")


# ====================================
# 🔹 Chat API Endpoint
# ====================================
@csrf_exempt
def chat_api(request):
    """Handles chat messages sent from frontend to Groq API"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        print(f"📤 User message: {user_message}")

        # =========================
        # 🧠 Model Handling
        # =========================
        model_name = "llama-3.3-70b-versatile"  # ✅ Primary model
        fallback_model = "llama-3.3-8b-instant"  # ✅ Backup if Groq changes support

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": user_message}],
            "temperature": 0.7,
            "max_tokens": 1024
        }

        print(f"🌐 Sending request to: {GROQ_API_URL}")
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response_data = response.json()

        # =========================
        # ⚠️ Handle errors
        # =========================
        if response.status_code != 200 or "error" in response_data:
            err_msg = response_data.get("error", {}).get("message", "Unknown Groq error")
            print(f"❌ Groq API Error: {err_msg}")

            # Fallback if model is deprecated or invalid
            if "model" in err_msg.lower():
                print("⚠️ Switching to fallback model:", fallback_model)
                payload["model"] = fallback_model
                response = requests.post(GROQ_API_URL, headers=headers, json=payload)
                response_data = response.json()

            else:
                return JsonResponse({"error": err_msg}, status=400)

        # =========================
        # ✅ Success: Return reply
        # =========================
        message = response_data["choices"][0]["message"]["content"]
        print(f"🤖 Model reply: {message[:100]}...")
        return JsonResponse({"response": message})

    except json.JSONDecodeError:
        print("❌ JSON decode error")
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        return JsonResponse({"error": "Network request failed"}, status=500)

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
