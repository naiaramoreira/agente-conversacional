from typing import List, Tuple
from app.utils.helpers import dataset_path
from app.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger("dataset")


def parse_dataset() -> List[Tuple[str, str]]:
    pairs = []
    path = dataset_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.lower() == "none":
                    continue
                dot_idx = line.find(".")
                if dot_idx <= 0:
                    continue
                name = line[:dot_idx].strip()
                review = line[dot_idx + 1 :].strip()
                if name and review:
                    pairs.append((name, review))
    except FileNotFoundError:
        logger.error("Arquivo não encontrado")
        raise
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {e}")
        raise
    return pairs
