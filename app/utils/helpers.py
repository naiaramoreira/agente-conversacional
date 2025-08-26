import os
import unicodedata


def normalize_text(s: str) -> str:
    if s is None:
        return ""
    s_nf = unicodedata.normalize("NFD", s)
    s_nf = "".join(ch for ch in s_nf if unicodedata.category(ch) != "Mn")
    s_nf = s_nf.replace("’", "'").replace("‘", "'")
    s_nf = s_nf.replace("'", "").strip().lower()
    s_nf = " ".join(s_nf.split())
    return s_nf


def dataset_path() -> str:
    candidates = [
        os.path.join(os.path.dirname(__file__), "restaurantes.txt"),
        os.path.join(os.getcwd(), "restaurantes.txt"),
        "data/restaurantes.txt",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        "Arquivo restaurantes.txt não encontrado. "
    )
