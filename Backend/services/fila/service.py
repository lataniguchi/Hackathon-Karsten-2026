"""CABECALHO DO ARQUIVO: consulta, remoção e limpeza das filas de produção."""

import re
from pathlib import Path

from .. import state
from ..bases.service import carregar_bases
from ..config import PASTA_SAIDA
from ..types import (
    RemocaoTask,
    ResumoFilas,
    ResumoMaquinaFila,
    TaskFilaNumerada,
    TaskRemovida,
    TasksMaquina,
)


def obter_resumo_filas() -> ResumoFilas:
    """Retorna as filas de todas as máquinas, com tasks numeradas e tempos."""
    carregar_bases()
    resumo: list[ResumoMaquinaFila] = []
    for i, codigo_maquina in enumerate(state.codigo_de_maquina):
        tarefas = state.filas_maquinas.get(codigo_maquina, [])
        tarefas_numeradas: list[TaskFilaNumerada] = []
        for indice, tarefa in enumerate(tarefas, start=1):
            tarefas_numeradas.append({"indice": indice, **tarefa})
        resumo.append(
            {
                "codigo_de_maquina": codigo_maquina,
                "tipo_maquina": state.tipo_maquina[i],
                "descricao": state.descricao[i],
                "quantidade_tasks": len(tarefas),
                "tempo_total_fila_min": round(
                    sum(tarefa["tempo_total_min"] for tarefa in tarefas),
                    4,
                ),
                "tasks": tarefas_numeradas,
            }
        )
    return {"maquinas_fila": resumo}


def listar_tasks_maquina(codigo_maquina: int) -> TasksMaquina:
    """Lista as tasks de uma máquina com índices começando em 1.

    Args:
        codigo_maquina: Código da máquina cuja fila será consultada.

    Returns:
        Código da máquina e lista numerada de tasks.

    Raises:
        ValueError: Quando o código não corresponde a uma máquina cadastrada.
    """
    carregar_bases()
    if codigo_maquina not in state.filas_maquinas:
        raise ValueError(f"Máquina com código {codigo_maquina} não encontrada.")

    tarefas_numeradas: list[TaskFilaNumerada] = []
    for indice, tarefa in enumerate(state.filas_maquinas[codigo_maquina], start=1):
        tarefas_numeradas.append({"indice": indice, **tarefa})
    return {"codigo_de_maquina": codigo_maquina, "tasks": tarefas_numeradas}


def deletar_task_maquina(codigo_maquina: int, indice: int, motivo: str) -> RemocaoTask:
    """Arquiva a planilha da task e depois a remove da fila da máquina.

    Motivos predefinidos movem o XLSX para sua pasta de status. Outros motivos
    personalizados apenas renomeiam o arquivo na pasta principal de saída.

    Args:
        codigo_maquina: Código da máquina que contém a task.
        indice: Índice da task na fila, começando em 1.
        motivo: Status predefinido ou descrição personalizada da remoção.

    Returns:
        Dados da task removida e a fila atualizada.

    Raises:
        ValueError: Se a máquina, o índice ou o motivo forem inválidos.
        FileNotFoundError: Se o XLSX associado à task não existir.
        FileExistsError: Se o nome do arquivo de destino já estiver ocupado.
    """
    tarefas_numeradas = listar_tasks_maquina(codigo_maquina)["tasks"]
    if indice < 1 or indice > len(tarefas_numeradas):
        raise ValueError(
            f"Índice {indice} inválido para a máquina {codigo_maquina}; "
            f"selecione um índice entre 1 e {len(tarefas_numeradas)}."
        )

    motivo_limpo = motivo.strip()
    if not motivo_limpo:
        raise ValueError("Informe o motivo da remoção da task.")
    sufixo_personalizado = re.sub(
        r"[^\w-]+",
        "_",
        motivo_limpo,
        flags=re.UNICODE,
    ).strip("_")
    if not sufixo_personalizado:
        raise ValueError("O motivo informado não pode ser usado no nome do arquivo.")

    motivos_predefinidos: dict[str, str] = {
        "concluido": "Concluido",
        "falhou": "Falhou",
        "reavaliacao": "Reavaliacao",
    }
    motivo_predefinido = motivos_predefinidos.get(motivo_limpo.casefold())
    sufixo = motivo_predefinido or sufixo_personalizado
    tarefa = state.filas_maquinas[codigo_maquina][indice - 1]
    arquivo_renomeado: str | None = None
    caminho_arquivo_renomeado: str | None = None

    nome_arquivo = tarefa.get("arquivo_gerado")
    if nome_arquivo:
        caminho_origem = PASTA_SAIDA / Path(nome_arquivo).name
        if not caminho_origem.is_file():
            raise FileNotFoundError(
                f"Planilha gerada para a task não foi encontrada: {caminho_origem.name}"
            )
        pasta_destino = (
            PASTA_SAIDA / motivo_predefinido
            if motivo_predefinido
            else PASTA_SAIDA
        )
        caminho_destino = pasta_destino / (
            f"{caminho_origem.stem}_{sufixo}{caminho_origem.suffix}"
        )
        if caminho_destino.exists():
            raise FileExistsError(
                f"Já existe uma planilha com o nome {caminho_destino.name}."
            )
        if motivo_predefinido:
            pasta_destino.mkdir(exist_ok=True)
        caminho_origem.rename(caminho_destino)
        arquivo_renomeado = caminho_destino.name
        caminho_arquivo_renomeado = str(caminho_destino)

    task_removida = state.filas_maquinas[codigo_maquina].pop(indice - 1)
    task_removida_com_motivo: TaskRemovida = {
        "indice": indice,
        **task_removida,
        "motivo_exclusao": motivo_limpo,
    }
    return {
        "mensagem": f"Task de índice {indice} removida da máquina {codigo_maquina}.",
        "motivo": motivo_limpo,
        "arquivo_renomeado": arquivo_renomeado,
        "caminho_arquivo_renomeado": caminho_arquivo_renomeado,
        "task_removida": task_removida_com_motivo,
        **listar_tasks_maquina(codigo_maquina),
    }


def limpar_filas_maquinas() -> dict[str, str]:
    """Esvazia as filas de todas as máquinas sem excluir arquivos Excel.

    Returns:
        Mensagem confirmando que as filas em memória foram limpas.
    """
    for codigo_maquina in state.filas_maquinas:
        state.filas_maquinas[codigo_maquina] = []
    return {"mensagem": "Filas de todas as máquinas zeradas com sucesso!"}
