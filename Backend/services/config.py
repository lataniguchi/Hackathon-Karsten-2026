"""CABECALHO DO ARQUIVO: caminhos compartilhados de entrada e saída do projeto."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
CAMINHO_ENTRADAS = BASE_DIR / "dados" / "Entradas.xlsx"
if not CAMINHO_ENTRADAS.exists():
    CAMINHO_ENTRADAS = BASE_DIR / "Entradas.xlsx"

PASTA_SAIDA = BASE_DIR / "saida_po"
PASTA_SAIDA.mkdir(exist_ok=True)
