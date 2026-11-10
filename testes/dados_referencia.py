"""Carregador central dos dados de referencia a partir de casos_de_teste.json e casos_adversariais.json."""

import json
from pathlib import Path

DIR_ATUAL = Path(__file__).resolve().parent
CAMINHO_JSON_OFICIAL = DIR_ATUAL / "casos_de_teste.json"
CAMINHO_JSON_ADVERSARIAL = DIR_ATUAL / "casos_adversariais.json"


def carregar_json(caminho: Path) -> list[dict]:
    """Carrega arquivo JSON externo em lista de dicionarios."""
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


CASOS_DE_TESTE = carregar_json(CAMINHO_JSON_OFICIAL)
CASOS_ADVERSARIAIS = carregar_json(CAMINHO_JSON_ADVERSARIAL)

MAPA_CASOS = {caso["id"]: caso for caso in CASOS_DE_TESTE}
MAPA_CASOS_ADVERSARIAIS = {caso["id"]: caso for caso in CASOS_ADVERSARIAIS}
