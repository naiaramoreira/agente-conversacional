import json
from typing import Optional, Dict, Any, List
from app.utils.logger import get_logger

logger = get_logger("pipeline.steps")


def autogen_fetch_reviews(
        factory, entry, user_query: str, guessed: Optional[str]
) -> Dict[str, List[str]]:
    """
    Usa o data_fetch_agent via entrypoint e espera {nome: [reviews...]}.
    """
    data_fetch = factory.make_data_fetch_agent()
    fetch_input = user_query if guessed is None else f'Quero as avaliações de "{guessed}".'

    chat = entry.initiate_chats([{
        "recipient": data_fetch,
        "message": fetch_input,
        "max_turns": 2,
        "summary_method": "last_msg",
        "clear_history": True,
    }])

    text = (chat[0].summary or "").strip()
    out = factory.extract_json(text) or {}
    logger.debug(f"autogen_fetch_reviews -> {out}")
    return out


def autogen_analyze_reviews(
        factory, entry, restaurant_name: str, reviews: List[str]
) -> Optional[Dict[str, Any]]:
    """
    Usa o review_analysis_agent para converter avaliações → escores (JSON).
    """
    review_agent = factory.make_review_analysis_agent()
    joined = "\n".join(f"- {r}" for r in (reviews or []))
    schema = {
        "type": "object",
        "properties": {
            "restaurant_name": {"type": "string"},
            "food_scores": {"type": "array", "items": {"type": "integer"}},
            "customer_service_scores": {
                "type": "array", "items": {"type": "integer"}
            },
        },
        "required": ["restaurant_name", "food_scores", "customer_service_scores"],
        "additionalProperties": False,
    }
    message = (
        f"Restaurante: {restaurant_name}\n"
        f"Avaliações (uma por linha):\n{joined}\n\n"
        "Responda SOMENTE com JSON válido no schema a seguir (não inclua comentários):\n"
        f"{json.dumps(schema, ensure_ascii=False)}"
    )

    chat = entry.initiate_chats([{
        "recipient": review_agent,
        "message": message,
        "max_turns": 2,
        "summary_method": "last_msg",
        "clear_history": True,
    }])

    out = factory.extract_json(chat[0].summary or "")
    logger.debug(f"autogen_analyze_reviews -> {out}")
    return out


def autogen_score(
        factory, entry, payload: Dict[str, Any]
) -> Optional[Dict[str, float]]:
    """
    Usa o score_agent para chamar a tool calculate_overall_score e
    retornar {nome: nota}.
    """
    score_agent = factory.make_score_agent()
    msg = (
        "Calcule a pontuação chamando a ferramenta calculate_overall_score com os argumentos abaixo, "
        "e responda EXATAMENTE com o JSON da ferramenta:\n"
        f"restaurant_name: {payload['restaurant_name']}\n"
        f"food_scores: {payload['food_scores']}\n"
        f"customer_service_scores: {payload['customer_service_scores']}"
    )

    chat = entry.initiate_chats([{
        "recipient": score_agent,
        "message": msg,
        "max_turns": 2,
        "summary_method": "last_msg",
        "clear_history": True,
    }])

    out = factory.extract_json(chat[0].summary or "")
    logger.debug(f"autogen_score -> {out}")
    return out
