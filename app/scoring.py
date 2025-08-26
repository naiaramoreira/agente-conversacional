import math
from typing import Dict, List


def calculate_overall_score(
    restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]
) -> Dict[str, float]:
    if not food_scores or not customer_service_scores:
        raise ValueError("As listas de notas não podem estar vazias.")
    if len(food_scores) != len(customer_service_scores):
        raise ValueError("As listas de notas devem ter o mesmo tamanho.")
    n = len(food_scores)
    for v in food_scores + customer_service_scores:
        if not (1 <= int(v) <= 5):
            raise ValueError("As notas devem estar no intervalo de 1 a 5.")
    total = 0.0
    for f, s in zip(food_scores, customer_service_scores):
        total += math.sqrt((f ** 2) * s)
    denom = n * math.sqrt(125.0)
    score = (total / denom) * 10.0
    score = round(score + 1e-12, 3)
    return {restaurant_name: score}
