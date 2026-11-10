"""CABECALHO DO ARQUIVO: leitura e consulta das bases de máquinas e elementos MTM."""

import pandas as pd

from .. import state
from ..config import CAMINHO_ENTRADAS


def carregar_bases() -> None:
    """Carrega em memória as abas de elementos MTM e máquinas de Entradas.xlsx.

    Evita reler a planilha quando as bases já foram carregadas e inicializa
    uma fila vazia para cada máquina identificada.
    """
    if state.descricao_do_elemento and state.codigo_de_maquina:
        return

    df_mtm: pd.DataFrame = pd.read_excel(
        CAMINHO_ENTRADAS,
        sheet_name="MATRIZ_DE_ELEMENTOS",
    )
    df_maquinas: pd.DataFrame = pd.read_excel(
        CAMINHO_ENTRADAS,
        sheet_name="TEMPO-CM",
        header=1,
    )
    colunas_mtm_validas = [
        "Descrição do elemento",
        "Código do agrupador",
        "Código do elemento",
        "elemento + agrupador",
        "Tempo",
    ]
    df_mtm = df_mtm[colunas_mtm_validas]

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
