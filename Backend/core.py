"""CABECALHO DO ARQUIVO: reexporta a API antiga do core para compatibilidade.

As implementações estão organizadas por responsabilidade no pacote services.
"""

from services.bases import carregar_bases, obter_todas_as_bases
from services.config import BASE_DIR, CAMINHO_ENTRADAS, PASTA_SAIDA
from services.demanda import extrair_dados_demanda
from services.po import (
    gerar_planilha_po_xlsx,
    obter_proximo_indice_po,
    processar_calculo_po,
)
from services.fila import (
    deletar_task_maquina,
    limpar_filas_maquinas,
    listar_tasks_maquina,
    obter_resumo_filas,
)
from services.state import (
    codigo_de_maquina,
    codigo_do_agrupador,
    codigo_do_elemento,
    codigo_mtm_formatado,
    descricao,
    descricao_do_elemento,
    elemento_mais_agrupador,
    filas_maquinas,
    rpm,
    tempo,
    tempo_tempo_metro,
    tipo_maquina,
)

__all__ = [
    "BASE_DIR",
    "CAMINHO_ENTRADAS",
    "PASTA_SAIDA",
    "carregar_bases",
    "codigo_de_maquina",
    "codigo_do_agrupador",
    "codigo_do_elemento",
    "codigo_mtm_formatado",
    "deletar_task_maquina",
    "descricao",
    "descricao_do_elemento",
    "elemento_mais_agrupador",
    "extrair_dados_demanda",
    "filas_maquinas",
    "gerar_planilha_po_xlsx",
    "limpar_filas_maquinas",
    "listar_tasks_maquina",
    "obter_proximo_indice_po",
    "obter_resumo_filas",
    "obter_todas_as_bases",
    "processar_calculo_po",
    "rpm",
    "tempo",
    "tempo_tempo_metro",
    "tipo_maquina",
]
