import os
import json
import traceback
from openai import OpenAI
import google.generativeai as genai

# System prompts for AI
PREVIEW_SYSTEM_PROMPT = """Ты — эксперт по маркетингу кофеен. 
Твоя задача — создать краткое превью маркетинговой стратегии на основе брифа.
Ответ должен быть СТРОГО в формате JSON со следующими полями:
{
  "audience_summary": "Краткое описание ЦА (2-3 предложения)",
  "branding_concept": "Основная идея бренда (1-2 предложения)",
  "content_preview": "Пример одной идеи для поста"
}"""

FULL_SYSTEM_PROMPT = """Ты — ведущий маркетолог для кофейного бизнеса. 
Создай подробную маркетинговую стратегию.
Ответ должен быть СТРОГО в формате JSON со следующей структурой:
{
  "target_audience": [
    {"segment": "Название", "description": "Описание", "pain_points": "Боли", "value_prop": "Решение"}
  ],
  "branding": {
    "concept": "Идея",
    "visual_style": "Стиль",
    "colors": ["Цвет1", "Цвет2"],
    "tone_of_voice": "Голос бренда"
  },
  "content_plan": {
    "pillars": ["Рубрика1", "Рубрика2"],
    "posts": [
      {"day": 1, "topic": "Тема", "type": "Тип", "hook": "Заголовок"}
    ],
    "hashtags": ["#тег1", "#тег2"],
    "kpis": ["Метрика1", "Метрика2"]
  }
}"""

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

def build_user_prompt(data: dict) -> str:
    return f"""
Бриф кофейни:
- Название/Локация: {data.get('location', 'Не указано')}
- Клиенты: {data.get('target_customers', 'Не указано')}
- Конкуренты: {data.get('competitors', 'Не указано')}
- Соцсети: {data.get('social_media', 'Не указано')}
- Доп. инфо: {data.get('additional_info', 'Не указано')}
"""

def generate_strategy_openai(system_prompt: str, user_prompt: str, preview_only: bool) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPEN_API_KEY")
    if not api_key:
        raise ValueError("No OpenAI API key found.")
    
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"CRITICAL OpenAI Error: {str(e)}")
        print(traceback.format_exc())
        raise e

def generate_strategy_gemini(system_prompt: str, user_prompt: str) -> dict:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("No Google API key found.")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_prompt = f"{system_prompt}\n\n{user_prompt}\n\nОТВЕТЬ ТОЛЬКО В ФОРМАТЕ JSON."
        
        response = model.generate_content(
            full_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"CRITICAL Gemini Error: {str(e)}")
        print(traceback.format_exc())
        raise e

def generate_strategy(data: dict, preview_only: bool = True) -> dict:
    # TEST MODE: If location contains "TEST", return mock data
    location = str(data.get('location', '')).upper()
    if "TEST" in location:
        print("TEST MODE ACTIVATED: Returning mock data.")
        return MOCK_PREVIEW if preview_only else MOCK_FULL

    system_prompt = PREVIEW_SYSTEM_PROMPT if preview_only else FULL_SYSTEM_PROMPT
    user_prompt = build_user_prompt(data)
    
    # Try OpenAI first
    if os.environ.get("OPENAI_API_KEY") or os.environ.get("OPEN_API_KEY"):
        try:
            print("Attempting generation with OpenAI...")
            return generate_strategy_openai(system_prompt, user_prompt, preview_only)
        except Exception as e:
            print(f"OpenAI error caught in main generator: {str(e)}")
            if not os.environ.get("GOOGLE_API_KEY"):
                raise e
    
    # Fallback to Gemini
    if os.environ.get("GOOGLE_API_KEY"):
        try:
            print("Attempting generation with Gemini...")
            return generate_strategy_gemini(system_prompt, user_prompt)
        except Exception as e:
            print(f"Gemini error caught in main generator: {str(e)}")
            raise e
            
    raise ValueError("No valid AI API keys found. Please check Railway variables.")
