from typing import Dict, List
from app.dataset import parse_dataset
from app.utils.helpers import normalize_text


def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    target_key = restaurant_name.strip()
    target_norm = normalize_text(target_key)
    reviews: List[str] = []
    for name, review in parse_dataset():
        if normalize_text(name) == target_norm:
            reviews.append(review)
    return {target_key: reviews}
