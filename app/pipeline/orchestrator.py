import json
from typing import Dict, Any
from app.agents.autogen_factory import AutogenAgentFactory
from app.pipeline.name_resolver import choose_best_name
from app.pipeline.steps import (
    autogen_fetch_reviews,
    autogen_analyze_reviews,
    autogen_score
)
from app.utils.helpers import normalize_text
from app.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger("orchestrator")


class Orchestrator:
    """
    Coordena o pipeline fetch → análise → score com Autogen (initiate_chats).
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.factory = AutogenAgentFactory(model=model)
        self.entry = self.factory.make_entrypoint_agent()

    def run(self, user_query: str) -> Dict[str, Any]:
        restaurant_name = choose_best_name(user_query)
        if not restaurant_name:
            raise RuntimeError("Não foi possível identificar o nome do restaurante na consulta.")

        reviews_dict = autogen_fetch_reviews(self.factory, self.entry, user_query, restaurant_name)
        if not reviews_dict:
            raise RuntimeError("Não foi possível acessar o agente de busca de avaliações.")

        name_from_agent, reviews = next(iter(reviews_dict.items()))
        if normalize_text(name_from_agent) != normalize_text(restaurant_name):
            restaurant_name = name_from_agent

        if not isinstance(reviews, list) or len(reviews) == 0:
            raise RuntimeError("Não foi possível acessar o agente de busca de avaliações (retorno vazio).")

        analysis_out = autogen_analyze_reviews(self.factory, self.entry, restaurant_name, reviews)
        if not analysis_out:
            raise RuntimeError("Não foi possível acessar o agente de análise de avaliações.")

        payload = {
            "restaurant_name": analysis_out["restaurant_name"],
            "food_scores": analysis_out["food_scores"],
            "customer_service_scores": analysis_out["customer_service_scores"],
        }
        score_json = autogen_score(self.factory, self.entry, payload)
        if not score_json:
            raise RuntimeError("Não foi possível acessar o agente de cálculo de pontuação.")

        logger.info(f"Resultado final: {json.dumps(score_json, ensure_ascii=False)}")
        val = list(score_json.values())[0]
        if isinstance(val, (int, float)):
            n = len(reviews)
            logger.info(
                f"A avaliação média do {payload['restaurant_name']} é {float(val):.3f} "
                f"(Base: {n} avaliação{'s' if n != 1 else ''})."
            )
        else:
            logger.info(f"Comentário: {val}")

        return {
            "restaurant_name": restaurant_name,
            "reviews": reviews,
            "analysis": analysis_out,
            "score_json": score_json,
        }
