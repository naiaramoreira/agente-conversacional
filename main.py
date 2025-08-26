import sys
from app.pipeline.orchestrator import Orchestrator


def main(user_query: str):
    orch = Orchestrator(model="gpt-4o-mini")
    orch.run(user_query)


# NÃO modifique abaixo
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Certifique-se de incluir uma consulta para algum restaurante ao executar a função main."
    main(sys.argv[1])
