"""CABECALHO DO ARQUIVO: extração e normalização dos dados de demanda."""

import io

import docx

from ..config import BASE_DIR
from ..types import DadosDemanda


def extrair_dados_demanda(
    conteudo_bytes: bytes | None = None,
    nome_arquivo: str = "demanda_000.docx",
) -> DadosDemanda:
    """Extrai os campos da demanda de um arquivo DOCX ou TXT.

    Args:
        conteudo_bytes: Conteúdo do arquivo; se omitido, o arquivo é lido de
            ``dados/`` ou da raiz do projeto.
        nome_arquivo: Nome usado para localizar o arquivo e identificar o formato.

    Returns:
        Dados normalizados da ordem de produção.
    """
    if conteudo_bytes is None:
        caminho_local = BASE_DIR / "dados" / nome_arquivo
        if not caminho_local.exists():
            caminho_local = BASE_DIR / nome_arquivo
        conteudo_bytes = caminho_local.read_bytes()

    if nome_arquivo.lower().endswith(".docx"):
        documento = docx.Document(io.BytesIO(conteudo_bytes))
        linhas = [paragrafo.text.strip() for paragrafo in documento.paragraphs if paragrafo.text.strip()]
    else:
        texto = conteudo_bytes.decode("utf-8", errors="ignore")
        linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]

    campos: dict[str, str] = {}
    for linha in linhas:
        if ":" in linha:
            chave, valor = linha.split(":", 1)
            chave_limpa = chave.strip().lower()
            valor_limpo = valor.strip().strip('"').strip("“").strip("”").strip("'")
            campos[chave_limpa] = valor_limpo

    def para_float(valor: str | float) -> float:
        """Converte números com vírgula ou ponto decimal para ``float``."""
        return float(str(valor).replace(",", ".").strip())

    cod_eqp = int(campos.get("cód. eqp", campos.get("cod. eqp", 1)))
    pontos_cm = para_float(campos.get("pontos/cm", 0.0))
    perimetro_m = para_float(
        campos.get("perímetro costura (em m)", campos.get("perimetro costura (em m)", 0.0))
    )
    elementos_raw = campos.get("elementos", "")

    return {
        "titulo_po": campos.get("título"),
        "rev": campos.get("rev", "00"),
        "operacao": campos.get("operação", campos.get("operacao", "")),
        "produto": {
            "agrupamento_familia": campos.get(
                "agrupamento família", campos.get("agrupamento familia", "")
            ),
            "tamanho": campos.get("tamanho", ""),
            "medidas_peca_m": campos.get(
                "medidas da peça (em m)", campos.get("medidas da peca (em m)", "")
            ),
            "pontos_cm": pontos_cm,
            "perimetro_costura_m": perimetro_m,
        },
        "cod_eqp": cod_eqp,
        "elementos": [elemento.strip() for elemento in elementos_raw.split(",") if elemento.strip()],
    }
