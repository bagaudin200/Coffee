import os
import json
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
    # Use gpt-4o-mini as it's very stable and supports JSON mode well
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

def generate_strategy_gemini(system_prompt: str, user_prompt: str) -> dict:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("No Google API key found.")
    
    genai.configure(api_key=api_key)
    # Use a more robust way to call Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')
    full_prompt = f"{system_prompt}\n\n{user_prompt}\n\nОТВЕТЬ ТОЛЬКО В ФОРМАТЕ JSON."
    
    response = model.generate_content(
        full_prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)

def generate_strategy(data: dict, preview_only: bool = True) -> dict:
    system_prompt = PREVIEW_SYSTEM_PROMPT if preview_only else FULL_SYSTEM_PROMPT
    user_prompt = build_user_prompt(data)
    
    # Try OpenAI first (most stable)
    if os.environ.get("OPENAI_API_KEY") or os.environ.get("OPEN_API_KEY"):
        try:
            print("Attempting generation with OpenAI...")
            return generate_strategy_openai(system_prompt, user_prompt, preview_only)
        except Exception as e:
            print(f"OpenAI error: {str(e)}")
            if not os.environ.get("GOOGLE_API_KEY"):
                raise e
    
    # Fallback to Gemini
    if os.environ.get("GOOGLE_API_KEY"):
        try:
            print("Attempting generation with Gemini...")
            return generate_strategy_gemini(system_prompt, user_prompt)
        except Exception as e:
            print(f"Gemini error: {str(e)}")
            raise e
            
    raise ValueError("No valid AI API keys found in environment variables.")
