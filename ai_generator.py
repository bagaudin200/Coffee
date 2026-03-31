import os
import json
import traceback
import re
from openai import OpenAI
import google.generativeai as genai

# Mock data for testing
MOCK_PREVIEW = {
    "audience_summary": "Ваша аудитория — это ценители качественного кофе и уютной атмосферы. В основном это фрилансеры и студенты.",
    "branding_concept": "Концепция 'Уютный уголок': минимализм, натуральные материалы и акцент на качестве зерна.",
    "content_preview": "Пост: 'История нашего зерна — от плантации до вашей чашки'."
}

MOCK_FULL = {
    "target_audience": [
        {"segment": "Фрилансеры", "description": "Люди, работающие удаленно", "pain_points": "Нужен быстрый Wi-Fi и тишина", "value_prop": "Рабочая зона и безлимитный фильтр-кофе"}
    ],
    "branding": {
        "concept": "Уютный уголок",
        "visual_style": "Скандинавский минимализм",
        "colors": ["#F5F5DC", "#4B3621"],
        "tone_of_voice": "Дружелюбный и экспертный"
    },
    "content_plan": {
        "pillars": ["Процессы", "Люди", "Атмосфера"],
        "posts": [
            {"day": 1, "topic": "Знакомство с бариста", "type": "Фото + Текст", "hook": "Кто готовит ваш идеальный латте?"}
        ],
        "hashtags": ["#кофе", "#кофейня", "#бариста"],
        "kpis": ["Охват", "Вовлеченность"]
    }
}

def clean_json_response(text: str) -> dict:
    """Clean JSON response from AI (remove markdown code blocks if present)."""
    # Remove markdown code blocks like ```json ... ```
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}. Raw text: {text}")
        raise e

def generate_strategy_openai(system_prompt: str, user_prompt: str, preview_only: bool) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPEN_API_KEY")
    if not api_key:
        raise ValueError("No OpenAI API key found.")
    
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=2000 if preview_only else 4000
    )
    return clean_json_response(response.choices[0].message.content)

def generate_strategy_gemini(system_prompt: str, user_prompt: str) -> dict:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("No Google API key found.")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    full_prompt = f"{system_prompt}\n\n{user_prompt}\n\nОТВЕТЬ ТОЛЬКО В ФОРМАТЕ JSON."
    
    response = model.generate_content(full_prompt)
    return clean_json_response(response.text)

def generate_strategy(data: dict, preview_only: bool = True) -> dict:
    # 1. ABSOLUTE TEST MODE (Priority 1)
    # Check if ANY field contains "TEST"
    all_values = " ".join([str(v) for v in data.values()]).upper()
    if "TEST" in all_values:
        print("!!! TEST MODE ACTIVATED !!! Returning mock data immediately.")
        return MOCK_PREVIEW if preview_only else MOCK_FULL

    # 2. Normal AI Generation
    system_prompt = "Ты эксперт по маркетингу кофеен. Отвечай только в формате JSON."
    user_prompt = f"Создай {'превью' if preview_only else 'полную'} стратегию для кофейни: {json.dumps(data, ensure_ascii=False)}"
    
    # Try OpenAI
    if os.environ.get("OPENAI_API_KEY") or os.environ.get("OPEN_API_KEY"):
        try:
            return generate_strategy_openai(system_prompt, user_prompt, preview_only)
        except Exception as e:
            print(f"OpenAI error: {str(e)}")
            if not os.environ.get("GOOGLE_API_KEY"):
                raise e
    
    # Fallback to Gemini
    if os.environ.get("GOOGLE_API_KEY"):
        try:
            return generate_strategy_gemini(system_prompt, user_prompt)
        except Exception as e:
            print(f"Gemini error: {str(e)}")
            raise e
            
    raise ValueError("No valid AI API keys found. Use 'TEST' in the form to skip AI.")
