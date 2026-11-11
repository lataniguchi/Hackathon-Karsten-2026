"""CABECALHO DO ARQUIVO: extração e normalização dos dados de demanda."""

import io
import json
from typing import Any

import docx

from ..config import BASE_DIR
from ..types import DadosDemanda


def _decodificar_conteudo_json(texto: str) -> tuple[str, dict[str, Any] | None]:
    """Desempacota JSON com texto ou devolve os campos de um JSON estruturado."""
    for _ in range(3):
        try:
            conteudo: Any = json.loads(texto)
        except json.JSONDecodeError:
            return texto, None

        if isinstance(conteudo, str):
            texto = conteudo
            continue
        if not isinstance(conteudo, dict):
            raise ValueError("O JSON da demanda deve ser um objeto ou conter texto.")

        for chave in ("texto", "texto_demanda"):
            texto_interno = conteudo.get(chave)
            if isinstance(texto_interno, str):
                texto = texto_interno
                break
        else:
            for chave in ("dados_extraidos_da_demanda", "demanda"):
                dados_internos = conteudo.get(chave)
                if isinstance(dados_internos, dict):
                    conteudo = dados_internos
                    break
            return texto, conteudo
    return texto, None


def _obter_valor(campos: dict[str, Any], *chaves: str, padrao: Any = "") -> Any:
    """Busca um campo JSON ou textual por qualquer um dos nomes conhecidos."""
    for chave in chaves:
        valor = campos.get(chave)
        if valor is not None:
            return valor
    return padrao


def _converter_float(valor: Any, nome_campo: str) -> float:
    """Converte valores numéricos de JSON ou texto, incluindo vírgula decimal."""
    try:
        return float(str(valor).replace(",", ".").strip())
    except (TypeError, ValueError) as erro:
        raise ValueError(f"O valor do campo {nome_campo} não é numérico: {valor!r}.") from erro


def _montar_dados_demanda(campos: dict[str, Any]) -> DadosDemanda:
    """Monta o formato interno a partir de chaves JSON ou rótulos da demanda."""
    produto = campos.get("produto")
    campos_produto = dict(produto) if isinstance(produto, dict) else {}
    campos_produto.update(campos)

    cod_eqp_valor = _obter_valor(campos_produto, "cód. eqp", "cod. eqp", "cod_eqp", padrao=1)
    try:
        cod_eqp = int(cod_eqp_valor)
    except (TypeError, ValueError) as erro:
        raise ValueError(f"O código do equipamento não é um número inteiro: {cod_eqp_valor!r}.") from erro

    elementos_raw = _obter_valor(campos_produto, "elementos", padrao=[])
    if isinstance(elementos_raw, str):
        elementos = [item.strip() for item in elementos_raw.split(",") if item.strip()]
    elif isinstance(elementos_raw, list):
        elementos = [str(item).strip() for item in elementos_raw if str(item).strip()]
    else:
        raise ValueError("O campo elementos deve ser uma lista ou texto separado por vírgulas.")

    titulo_po = _obter_valor(campos_produto, "título", "titulo", "titulo_po", "título_po", padrao=None)
    return {
        "titulo_po": str(titulo_po) if titulo_po is not None else None,
        "rev": str(_obter_valor(campos_produto, "rev", padrao="00")),
        "operacao": str(_obter_valor(campos_produto, "operação", "operacao")),
        "produto": {
            "agrupamento_familia": str(
                _obter_valor(
                    campos_produto,
                    "agrupamento família",
                    "agrupamento familia",
                    "agrupamento_familia",
                )
            ),
            "tamanho": str(_obter_valor(campos_produto, "tamanho")),
            "medidas_peca_m": str(
                _obter_valor(
                    campos_produto,
                    "medidas da peça (em m)",
                    "medidas da peca (em m)",
                    "medidas_peca_m",
                )
            ),
            "pontos_cm": _converter_float(
                _obter_valor(campos_produto, "pontos/cm", "pontos_cm", padrao=0.0),
                "pontos/cm",
            ),
            "perimetro_costura_m": _converter_float(
                _obter_valor(
                    campos_produto,
                    "perímetro costura (em m)",
                    "perimetro costura (em m)",
                    "perimetro_costura_m",
                    padrao=0.0,
                ),
                "perímetro costura",
            ),
        },
        "cod_eqp": cod_eqp,
        "elementos": elementos,
    }


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
        texto = conteudo_bytes.decode("utf-8-sig", errors="ignore").strip()
        texto, campos_json = _decodificar_conteudo_json(texto)
        if campos_json is not None:
            campos_json_normalizados = {
                str(chave).strip().strip('"').lower(): valor
                for chave, valor in campos_json.items()
            }
            return _montar_dados_demanda(campos_json_normalizados)
        linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]

    campos: dict[str, str] = {}
    for linha in linhas:
        if ":" in linha:
            chave, valor = linha.split(":", 1)
            chave_limpa = chave.strip().lower()
            valor_limpo = valor.strip().strip('"').strip("“").strip("”").strip("'")
            campos[chave_limpa] = valor_limpo

    return _montar_dados_demanda(campos)
