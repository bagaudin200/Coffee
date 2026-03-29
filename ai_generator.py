import os
import json
from openai import OpenAI
import google.generativeai as genai

# Initialize OpenAI client
openai_client = OpenAI()

# Initialize Gemini if API key is present
google_api_key = os.environ.get("GOOGLE_API_KEY")
if google_api_key:
    genai.configure(api_key=google_api_key)

PREVIEW_SYSTEM_PROMPT = """Ты — эксперт по маркетингу кофеен. Тебе дают краткий бриф о кофейне, и ты создаёшь КРАТКОЕ превью маркетинговой стратегии.
Отвечай ТОЛЬКО валидным JSON без markdown-блоков, без пояснений.
Структура ответа строго такая:
{
  "audience_preview": {
    "primary_segment": "название основного сегмента",
    "age_range": "возрастной диапазон",
    "key_needs": ["потребность 1", "потребность 2", "потребность 3"],
    "pain_points": ["боль 1", "боль 2"]
  },
  "branding_preview": {
    "brand_archetype": "архетип бренда",
    "color_palette": ["цвет1", "цвет2", "цвет3"],
    "brand_voice": "описание голоса бренда",
    "tagline": "слоган кофейни"
  },
  "content_teaser": {
    "top_content_ideas": ["идея 1", "идея 2", "идея 3"],
    "best_posting_times": "лучшее время для постов",
    "recommended_platforms": ["платформа 1", "платформа 2"]
  },
  "strategy_summary": "краткое резюме стратегии в 2-3 предложениях"
}"""

FULL_SYSTEM_PROMPT = """Ты — эксперт по маркетингу кофеен с 10-летним опытом. Создай ПОЛНУЮ детальную маркетинговую стратегию на основе брифа.
Отвечай ТОЛЬКО валидным JSON без markdown-блоков, без пояснений.
Структура ответа строго такая:
{
  "audience_analysis": {
    "primary_segment": {
      "name": "название сегмента",
      "age_range": "возраст",
      "gender_split": "соотношение полов",
      "income_level": "уровень дохода",
      "lifestyle": "описание образа жизни",
      "values": ["ценность 1", "ценность 2", "ценность 3"],
      "coffee_habits": "привычки потребления кофе",
      "decision_factors": ["фактор 1", "фактор 2", "фактор 3"]
    },
    "secondary_segment": {
      "name": "название сегмента",
      "age_range": "возраст",
      "description": "описание",
      "opportunity": "возможность для бизнеса"
    },
    "customer_journey": {
      "awareness": "как узнают о кофейне",
      "consideration": "что влияет на выбор",
      "purchase": "триггеры покупки",
      "loyalty": "что удерживает клиентов"
    },
    "pain_points": ["боль 1", "боль 2", "боль 3", "боль 4"],
    "key_insights": ["инсайт 1", "инсайт 2", "инсайт 3"]
  },
  "branding": {
    "brand_archetype": "архетип",
    "brand_personality": ["черта 1", "черта 2", "черта 3", "черта 4"],
    "color_palette": {
      "primary": "основной цвет + HEX",
      "secondary": "вторичный цвет + HEX",
      "accent": "акцентный цвет + HEX",
      "background": "фоновый цвет + HEX",
      "rationale": "обоснование выбора палитры"
    },
    "typography": {
      "heading_font": "шрифт для заголовков",
      "body_font": "шрифт для текста",
      "rationale": "обоснование"
    },
    "brand_voice": {
      "tone": "тон коммуникации",
      "style": "стиль",
      "do": ["делать 1", "делать 2", "делать 3"],
      "dont": ["не делать 1", "не делать 2"]
    },
    "tagline": "слоган",
    "visual_concepts": ["концепция 1", "концепция 2", "концепция 3"],
    "logo_direction": "направление для логотипа",
    "interior_mood": "атмосфера интерьера"
  },
  "content_plan": {
    "strategy_overview": "общее описание контент-стратегии",
    "platforms": {
      "instagram": {
        "priority": "высокий/средний/низкий",
        "posting_frequency": "частота постинга",
        "content_mix": "соотношение типов контента",
        "best_times": ["время 1", "время 2"]
      },
      "vkontakte": {
        "priority": "высокий/средний/низкий",
        "posting_frequency": "частота постинга",
        "content_mix": "соотношение типов контента",
        "best_times": ["время 1", "время 2"]
      },
      "telegram": {
        "priority": "высокий/средний/низкий",
        "posting_frequency": "частота постинга",
        "content_mix": "соотношение типов контента",
        "best_times": ["время 1"]
      }
    },
    "content_pillars": [
      {"name": "пиллар 1", "description": "описание", "percentage": "процент контента"},
      {"name": "пиллар 2", "description": "описание", "percentage": "процент контента"},
      {"name": "пиллар 3", "description": "описание", "percentage": "процент контента"},
      {"name": "пиллар 4", "description": "описание", "percentage": "процент контента"}
    ],
    "monthly_calendar": [
      {"week": 1, "theme": "тема недели", "posts": [
        {"day": "Понедельник", "platform": "Instagram", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"},
        {"day": "Среда", "platform": "VK", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"},
        {"day": "Пятница", "platform": "Instagram", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"},
        {"day": "Суббота", "platform": "Telegram", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"}
      ]},
      {"week": 2, "theme": "тема недели", "posts": [
        {"day": "Понедельник", "platform": "Instagram", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"},
        {"day": "Вторник", "platform": "VK", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"},
        {"day": "Четверг", "platform": "Instagram", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"},
        {"day": "Воскресенье", "platform": "Telegram", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"}
      ]},
      {"week": 3, "theme": "тема недели", "posts": [
        {"day": "Понедельник", "platform": "Instagram", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"},
        {"day": "Среда", "platform": "VK", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"},
        {"day": "Пятница", "platform": "Instagram", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"},
        {"day": "Суббота", "platform": "Telegram", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"}
      ]},
      {"week": 4, "theme": "тема недели", "posts": [
        {"day": "Понедельник", "platform": "Instagram", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"},
        {"day": "Среда", "platform": "VK", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"},
        {"day": "Пятница", "platform": "Instagram", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"},
        {"day": "Воскресенье", "platform": "Telegram", "type": "тип поста", "idea": "идея поста", "caption_hook": "цепляющее начало"}
      ]}
    ],
    "hashtag_strategy": {
      "branded": ["хэштег1", "хэштег2"],
      "niche": ["хэштег1", "хэштег2", "хэштег3"],
      "local": ["хэштег1", "хэштег2", "хэштег3"],
      "trending": ["хэштег1", "хэштег2"]
    },
    "engagement_tactics": ["тактика 1", "тактика 2", "тактика 3", "тактика 4"]
  },
  "quick_wins": ["быстрая победа 1", "быстрая победа 2", "быстрая победа 3"],
  "kpis": [
    {"metric": "метрика 1", "target": "цель", "timeframe": "срок"},
    {"metric": "метрика 2", "target": "цель", "timeframe": "срок"},
    {"metric": "метрика 3", "target": "цель", "timeframe": "срок"}
  ]
}"""

def build_user_prompt(data: dict) -> str:
    return f"""Бриф кофейни:
- Название: {data.get('coffee_name', 'Не указано')}
- Город/Район: {data.get('location', 'Не указано')}
- Тип заведения: {data.get('coffee_type', 'Не указано')}
- Целевая аудитория (по мнению владельца): {data.get('target_audience', 'Не указано')}
- Ценовой диапазон: {data.get('price_range', 'Не указано')}
- Уникальность/Особенности: {data.get('unique_features', 'Не указано')}
- Конкуренты поблизости: {data.get('competitors', 'Не указано')}
- Текущие соцсети: {data.get('social_media', 'Не указано')}
- Дополнительно: {data.get('additional_info', 'Не указано')}"""

def generate_strategy_openai(system_prompt: str, user_prompt: str, preview_only: bool) -> dict:
    response = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=4000 if preview_only else 8000,
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    return json.loads(content)

def generate_strategy_gemini(system_prompt: str, user_prompt: str) -> dict:
    model = genai.GenerativeModel('gemini-1.5-flash', 
                                  generation_config={"response_mime_type": "application/json"})
    
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    response = model.generate_content(full_prompt)
    return json.loads(response.text)

def generate_strategy(data: dict, preview_only: bool = True) -> dict:
    system_prompt = PREVIEW_SYSTEM_PROMPT if preview_only else FULL_SYSTEM_PROMPT
    user_prompt = build_user_prompt(data)

    # Prefer Gemini if GOOGLE_API_KEY is set
    if os.environ.get("GOOGLE_API_KEY"):
        try:
            return generate_strategy_gemini(system_prompt, user_prompt)
        except Exception as e:
            print(f"Gemini error: {e}. Falling back to OpenAI.")
            return generate_strategy_openai(system_prompt, user_prompt, preview_only)
    else:
        return generate_strategy_openai(system_prompt, user_prompt, preview_only)
