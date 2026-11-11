"""CABECALHO DO ARQUIVO: leitura e consulta das bases de máquinas e elementos MTM."""

import logging

import pandas as pd

from .. import state
from ..config import CAMINHO_ENTRADAS

logger = logging.getLogger(__name__)


def carregar_bases() -> None:
    """Carrega em memória as abas de elementos MTM e máquinas de Entradas.xlsx.

    Relê a planilha quando o caminho ou a data de modificação mudar e inicializa
    uma fila vazia para cada máquina identificada.
    """
    caminho_bases = CAMINHO_ENTRADAS.resolve()
    versao_arquivo = (str(caminho_bases), caminho_bases.stat().st_mtime_ns)
    if (
        state.descricao_do_elemento
        and state.codigo_de_maquina
        and state.versao_arquivo_bases == versao_arquivo
    ):
        return

    df_mtm: pd.DataFrame = pd.read_excel(
        caminho_bases,
        sheet_name="MATRIZ_DE_ELEMENTOS",
    )
    df_maquinas: pd.DataFrame = pd.read_excel(
        caminho_bases,
        sheet_name="TEMPO-CM",
        header=1,
    )
    colunas_maquina = [
        "Código de máquina",
        "Tipo Máquina",
        "Descrição",
        "RPM",
        "Tempo (tempo/metro",
    ]
    registros_incompletos = df_maquinas[colunas_maquina].isna().any(axis=1)
    for coluna in ("Tipo Máquina", "Descrição"):
        registros_incompletos |= (
            df_maquinas[coluna].astype("string").str.strip().eq("").fillna(True)
        )
    if registros_incompletos.any():
        linhas_ignoradas = (df_maquinas.index[registros_incompletos] + 3).tolist()
        codigos_ignorados = (
            df_maquinas.loc[registros_incompletos, "Código de máquina"].tolist()
        )
        logger.warning(
            "Ignorando registros incompletos de máquinas em %s "
            "(linhas do Excel: %s; códigos: %s).",
            CAMINHO_ENTRADAS.name,
            linhas_ignoradas,
            codigos_ignorados,
        )
        df_maquinas = df_maquinas.loc[~registros_incompletos]

    colunas_mtm_validas = [
        "Descrição do elemento",
        "Código do agrupador",
        "Código do elemento",
        "elemento + agrupador",
        "Tempo",
    ]
    df_mtm = df_mtm[colunas_mtm_validas]
    if df_maquinas.empty:
        raise ValueError(
            f"Nenhuma máquina com os campos obrigatórios foi encontrada em "
            f"{caminho_bases.name}."
        )

    state.descricao_do_elemento[:] = df_mtm["Descrição do elemento"].astype(str).tolist()
    state.codigo_do_agrupador[:] = df_mtm["Código do agrupador"].astype(int).tolist()
    state.codigo_do_elemento[:] = df_mtm["Código do elemento"].astype(int).tolist()
    state.tempo[:] = df_mtm["Tempo"].astype(float).tolist()
    codigos_formatados: list[str] = [
        f"{agrup}.{elem}"
        for agrup, elem in zip(
            state.codigo_do_agrupador,
            state.codigo_do_elemento,
        )
    ]
    state.codigo_de_maquina[:] = df_maquinas["Código de máquina"].astype(int).tolist()
    state.tipo_maquina[:] = df_maquinas["Tipo Máquina"].astype(str).tolist()
    state.descricao[:] = df_maquinas["Descrição"].astype(str).tolist()
    state.rpm[:] = df_maquinas["RPM"].astype(int).tolist()
    state.tempo_tempo_metro[:] = df_maquinas["Tempo (tempo/metro"].astype(float).tolist()
    state.elemento_mais_agrupador[:] = codigos_formatados
    state.codigo_mtm_formatado[:] = codigos_formatados

    for codigo_maquina in state.codigo_de_maquina:
        state.filas_maquinas.setdefault(codigo_maquina, [])

    state.versao_arquivo_bases = versao_arquivo
    print("Variáveis da planilha Entradas.xlsx carregadas com sucesso!")


def obter_todas_as_bases() -> dict[str, object]:
    """Prepara todas as bases em formato de dicionário para consulta da API.

    Returns:
        Dicionário com as variáveis brutas, a matriz MTM e as máquinas.
    """
    carregar_bases()

    matriz_mtm_lista: list[dict[str, object]] = [
        {
            "Descricao_do_elemento": state.descricao_do_elemento[i],
            "Codigo_do_agrupador": state.codigo_do_agrupador[i],
            "Codigo_do_elemento": state.codigo_do_elemento[i],
            "elemento_mais_agrupador": state.elemento_mais_agrupador[i],
            "codigo_formatado": state.codigo_mtm_formatado[i],
            "Tempo": state.tempo[i],
        }
        for i in range(len(state.descricao_do_elemento))
    ]
    maquinas_lista: list[dict[str, object]] = [
        {
            "Codigo_de_maquina": state.codigo_de_maquina[i],
            "Tipo_Maquina": state.tipo_maquina[i],
            "Descricao": state.descricao[i],
            "RPM": state.rpm[i],
            "Tempo_tempo_metro": state.tempo_tempo_metro[i],
        }
        for i in range(len(state.codigo_de_maquina))
    ]

    nomes_variaveis: tuple[str, ...] = (
        "descricao_do_elemento",
        "codigo_do_agrupador",
        "codigo_do_elemento",
        "elemento_mais_agrupador",
        "tempo",
        "codigo_de_maquina",
        "tipo_maquina",
        "descricao",
        "rpm",
        "tempo_tempo_metro",
    )
    variaveis: dict[str, object] = {
        nome: getattr(state, nome)
        for nome in nomes_variaveis
    }
    return {
        "variaveis": variaveis,
        "matriz_mtm": matriz_mtm_lista,
        "maquinas": maquinas_lista,
    }
