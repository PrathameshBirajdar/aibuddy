# aibuddy/chat/views.py
import os
import json
import requests
from dotenv import load_dotenv
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# ======================================================
# 🔹 Environment Setup
# ======================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, "..", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


# ======================================================
# 🔹 Chat Page Renderer
# ======================================================
def chat_page(request):
    return render(request, "chat/chat_page.html")


# ======================================================
# 🔹 Chat + Quiz API (with memory)
# ======================================================
@csrf_exempt
def chat_api(request):
    """AI Buddy with image generation, quiz + memory tracking."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    user_message = (payload.get("message") or "").strip()
    kid_name = payload.get("name", "Buddy")
    learning_context = payload.get("context", "general")

    if not user_message:
        return JsonResponse({"error": "Message cannot be empty"}, status=400)

    # ✅ Initialize quiz memory in session
    session = request.session
    if "quiz_stats" not in session:
        session["quiz_stats"] = {"total": 0, "correct": 0, "current_answer": None}
        session.save()

    quiz_stats = session["quiz_stats"]

    # ======================================================
    # 🧠 Check if user answered a quiz question
    # ======================================================
    if learning_context == "quiz_followup":
        user_answer = user_message.strip().lower()
        correct_answer = (quiz_stats.get("current_answer") or "").lower()

        if not correct_answer:
            return JsonResponse({"response": "Let’s start a new quiz! Ask me a question 🧠"})

        quiz_stats["total"] += 1
        if user_answer == correct_answer:
            quiz_stats["correct"] += 1
            response_text = f"✅ Correct, {kid_name}! Great job! 🎉"
        else:
            response_text = f"❌ Oops! The correct answer was **{correct_answer}**."

        # If the quiz session has 5 questions, show summary
        if quiz_stats["total"] >= 5:
            score = quiz_stats["correct"]
            response_text += f"\n🏅 You scored {score}/5! Let's take a break or start a new quiz!"
            quiz_stats["total"] = 0
            quiz_stats["correct"] = 0

        quiz_stats["current_answer"] = None
        session["quiz_stats"] = quiz_stats
        session.save()

        return JsonResponse({"response": response_text})

    # ======================================================
    # 🎓 Build AI Prompt Based on Learning Context
    # ======================================================
    system_prompt = (
        f"You are AI Buddy, a friendly and patient teacher for a child named {kid_name}. "
        "Explain in fun and encouraging ways using emojis.\n"
        "If the child asks for a picture (like 'show me a lion'), reply with 'GENERATE_IMAGE: description'.\n"
        "If they want a quiz, respond as: 'QUIZ: question? answer=correct_option options=[A,B,C,D]'.\n"
        "Otherwise, just chat normally.\n"
        "Avoid markdown or code format."
    )

    if learning_context == "ask_me_anything":
        system_prompt += " Encourage curiosity about any topic (science, space, animals, etc.)."
    elif learning_context == "math":
        system_prompt += " Teach basic math (addition, subtraction, etc.) with examples."
    elif learning_context == "english":
        system_prompt += " Help with simple English grammar, spelling, or meanings."
    elif learning_context == "gk":
        system_prompt += " Ask short general knowledge questions for kids."
    elif learning_context == "animals":
        system_prompt += " Teach animal facts and ask small quiz questions."
    elif learning_context == "numbers":
        system_prompt += " Teach counting and arithmetic playfully."

    # ======================================================
    # 🔹 Send request to AI
    # ======================================================
    req_data = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.8,
        "max_tokens": 512,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=req_data, timeout=30)
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as e:
        print("❌ Groq error:", e)
        return JsonResponse({"error": "AI service is currently unreachable."}, status=502)

    # ======================================================
    # 🔹 Interpret AI Response
    # ======================================================
    reply = result["choices"][0]["message"]["content"].strip()

    # 🎨 Image generation
    if reply.startswith("GENERATE_IMAGE:"):
        desc = reply.replace("GENERATE_IMAGE:", "").strip()
        img_url = f"https://image.pollinations.ai/prompt/{desc.replace(' ', '%20')}"
        return JsonResponse({
            "response": f"Here’s {desc}! 🖼️",
            "image": img_url
        })

    # 🧠 Quiz question with correct answer
    if reply.startswith("QUIZ:"):
        try:
            main_part = reply.replace("QUIZ:", "").strip()
            question, rest = main_part.split("answer=")
            question = question.strip()
            answer_part, options_part = rest.split("options=")
            correct_answer = answer_part.strip()
            options = [opt.strip() for opt in options_part.strip("[]").split(",")]

            # Store correct answer in session
            quiz_stats["current_answer"] = correct_answer
            session["quiz_stats"] = quiz_stats
            session.save()

            return JsonResponse({
                "response": f"🤔 {question}",
                "quiz_options": options
            })

        except Exception as e:
            print("⚠️ Quiz parse error:", e)
            return JsonResponse({"response": reply})

    # Regular chat
    return JsonResponse({"response": reply})
