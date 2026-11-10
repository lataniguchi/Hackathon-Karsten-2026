"""Carregador central dos dados de referencia a partir de casos_de_teste.json."""

import json
from pathlib import Path

CAMINHO_JSON = Path(__file__).resolve().parent / "casos_de_teste.json"


def carregar_casos_de_teste() -> list[dict]:
    """Carrega os casos de teste externos em formato de dicionario."""
    with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


CASOS_DE_TESTE = carregar_casos_de_teste()
MAPA_CASOS = {caso["id"]: caso for caso in CASOS_DE_TESTE}
