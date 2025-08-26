
import re
from typing import Optional, List
from app.dataset import parse_dataset
from app.utils.helpers import normalize_text


def extract_restaurant_name_freeform(user_query: str) -> Optional[str]:
    """
    Extrai nome entre aspas ou após 'é o/a ... ?' em perguntas livres.
    """
    m = re.search(r"['\"]([^'\"]+)['\"]", user_query or "")
    if m:
        return m.group(1).strip()
    m = re.search(r"[Éé] (o|a)?\s*([^?]+)\??$", user_query or "")
    if m:
        return m.group(2).strip()
    return None


def guess_restaurant_from_query(user_query: str) -> Optional[str]:
    """
    Tenta deduzir o nome comparando a query normalizada com nomes
    do dataset normalizados.
    """
    uq = normalize_text(user_query or "")
    if not uq:
        return None
    names: List[str] = []
    seen = set()
    for name, _ in parse_dataset():
        key = normalize_text(name)
        if key not in seen:
            names.append(name)
            seen.add(key)
    for name in names:
        if normalize_text(name) in uq:
            return name
    return None


def choose_best_name(user_query: str) -> Optional[str]:
    """
    Combina heurística do dataset + regex para escolher o melhor nome.
    """
    ds = guess_restaurant_from_query(user_query)
    if ds:
        return ds
    return extract_restaurant_name_freeform(user_query)
