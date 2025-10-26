from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests, os, json
from dotenv import load_dotenv

load_dotenv()

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        user_message = data.get("message", "")

        groq_api_key = os.getenv("GROQ_API_KEY")
        groq_url = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")

        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "llama-3.1-70b-versatile",
            "messages": [{"role": "user", "content": user_message}],
        }

        response = requests.post(groq_url, headers=headers, json=payload)
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            return JsonResponse({"response": answer})
        else:
            return JsonResponse({"error": "Groq API request failed"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
