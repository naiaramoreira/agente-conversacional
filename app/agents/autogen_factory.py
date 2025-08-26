import os
import re
import json
from typing import Optional, Dict, List
from autogen import ConversableAgent
from app.fetch import fetch_restaurant_data
from app.scoring import calculate_overall_score
from app.utils.logger import setup_logging, get_logger
from dotenv import load_dotenv

load_dotenv()
setup_logging()
logger = get_logger("agents_autogen")


class AutogenAgentFactory:
    """
    Fábrica de agentes usando autogen.ConversableAgent.
    Exposto:
      - make_entrypoint_agent()
      - make_data_fetch_agent()
      - make_review_analysis_agent()
      - make_score_agent()
      - extract_json(text)
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY não encontrada no ambiente.")

        self.llm_config = {
            "config_list": [
                {
                    "model": model,
                    "api_key": api_key,
                }
            ]
        }

    @staticmethod
    def extract_json(text: str) -> Optional[dict]:
        if not isinstance(text, str) or not text:
            return None
        try:
            m = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if not m:
                return None
            return json.loads(m.group(0))
        except Exception:
            return None

    def make_entrypoint_agent(self) -> ConversableAgent:
        """
        Supervisor que dispara initiate_chats E EXECUTA as tools.
        """
        agent = ConversableAgent(
            "entrypoint_agent",
            system_message=(
                "Você é o agente orquestrador. Encaminhe a tarefa ao agente apropriado, "
                "aguarde a resposta e retorne somente o resultado final ao solicitante."
            ),
            llm_config=self.llm_config,
            code_execution_config=False,
            default_auto_reply=None,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1
        )

        agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)

        def _calc(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
            return calculate_overall_score(restaurant_name, food_scores, customer_service_scores)

        agent.register_for_execution(name="calculate_overall_score")(_calc)
        return agent

    def make_data_fetch_agent(self) -> ConversableAgent:
        """
        Agente que SUGERE o uso de fetch_restaurant_data (execução ocorrerá no entrypoint_agent).
        """
        agent = ConversableAgent(
            "data_fetch_agent",
            system_message=(
                "Você é o data_fetch_agent. "
                "Use SEMPRE a ferramenta fetch_restaurant_data para obter avaliações e "
                "responda EXATAMENTE com o JSON retornado pela ferramenta, sem comentários."
            ),
            llm_config=self.llm_config,
            code_execution_config=False,
            default_auto_reply=None,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
        )
        agent.register_for_llm(
            name="fetch_restaurant_data",
            description="Obtém as avaliações de um restaurante específico."
        )(fetch_restaurant_data)
        return agent

    def make_review_analysis_agent(self) -> ConversableAgent:
        """
        Agente que transforma avaliações em escores, sem usar ferramentas.
        """
        mapping = (
            "1/5: horrível, nojento, terrível\n"
            "2/5: ruim, desagradável, ofensivo\n"
            "3/5: mediano, sem graça, irrelevante\n"
            "4/5: bom, agradável, satisfatório\n"
            "5/5: incrível, impressionante, surpreendente"
        )
        return ConversableAgent(
            "review_analysis_agent",
            system_message=(
                "Você é o review_analysis_agent. Converta avaliações em escores 1..5 para COMIDA e ATENDIMENTO.\n"
                "Mapeamento OBRIGATÓRIO (use SOMENTE estes adjetivos; não infira nada além deles):\n" + mapping + "\n\n"
                "REGRAS ESTRITAS:\n"
                "• Procure SOMENTE os adjetivos exatamente como escritos acima (case-insensitive, acentuação conta).\n"
                "• Para cada avaliação:\n"
                "    – COMIDA = o score do adjetivo encontrado sobre comida; se nenhum desses adjetivos aparecer, use 3/5.\n"
                "    – ATENDIMENTO = o score do adjetivo encontrado sobre atendimento; se nenhum desses adjetivos aparecer, use 3/5.\n"
                "• Se aparecerem múltiplos adjetivos para a MESMA dimensão, escolha o MAIS NEGATIVO (menor score).\n"
                "• Palavras fora do léxico (ex.: rápido, demorado, preço, porções, ambiente etc.) DEVEM SER IGNORADAS (não influenciam o score).\n"
                "• O tamanho de food_scores e customer_service_scores deve ser igual ao número de avaliações.\n"
                "• Retorne SOMENTE JSON válido com as chaves: restaurant_name, food_scores, customer_service_scores.\n"
                "• NÃO chame nenhuma ferramenta.\n"
            ),
            llm_config=self.llm_config,
            code_execution_config=False,
            default_auto_reply=None,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
        )

    def make_score_agent(self) -> ConversableAgent:
        """
        Agente que SUGERE o uso de calculate_overall_score (execução ocorrerá no entrypoint_agent).
        """
        agent = ConversableAgent(
            "score_agent",
            system_message=(
                "Você é o score_agent. "
                "Dadas as listas de escores e o nome do restaurante, "
                "use SEMPRE a ferramenta calculate_overall_score e responda "
                "EXATAMENTE com o JSON retornado."
            ),
            llm_config=self.llm_config,
            code_execution_config=False,
            default_auto_reply=None,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
        )

        def _calc(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
            return calculate_overall_score(restaurant_name, food_scores, customer_service_scores)

        agent.register_for_llm(
            name="calculate_overall_score",
            description="Calcula a pontuação final (0..10) com 3 casas a partir das listas de escores."
        )(_calc)
        return agent
