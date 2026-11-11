"""CABECALHO DO ARQUIVO: consulta, remoção e limpeza das filas de produção."""

import re
from pathlib import Path
from zipfile import BadZipFile

import openpyxl

from .. import state
from ..bases.service import carregar_bases
from ..config import PASTA_SAIDA
from ..types import (
    CategoriaArquivada,
    ListaArquivosArquivados,
    RemocaoTask,
    RestauracaoArquivo,
    ResumoFilas,
    ResumoMaquinaFila,
    TaskFila,
    TaskFilaNumerada,
    TaskRemovida,
    TasksMaquina,
)

LIMITE_ARQUIVOS_ARQUIVADOS = 10
CATEGORIAS_ARQUIVADAS: dict[str, tuple[str, tuple[str, ...]]] = {
    "concluido": ("Concluído", ("Concluido", "Concluído")),
    "falhou": ("Falhou", ("Falhou",)),
    "reavaliacao": ("Reavaliação", ("Reavaliacao", "Reavaliação")),
    "excluido": ("Excluído", ()),
}


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


def listar_arquivos_arquivados() -> ListaArquivosArquivados:
    """Lista até dez arquivos mais recentes por categoria, sem apagar os antigos."""
    categorias: list[CategoriaArquivada] = []
    for categoria, (nome_categoria, pastas) in CATEGORIAS_ARQUIVADAS.items():
        if categoria == "excluido":
            candidatos = [
                caminho
                for caminho in PASTA_SAIDA.glob("*.xlsx")
                if caminho.is_file() and _eh_arquivo_personalizado_arquivado(caminho)
            ]
        else:
            candidatos = [
                caminho
                for pasta in pastas
                for caminho in (PASTA_SAIDA / pasta).glob("*.xlsx")
                if caminho.is_file()
            ]

        candidatos.sort(
            key=lambda caminho: (caminho.stat().st_mtime_ns, caminho.name),
            reverse=True,
        )
        categorias.append(
            {
                "categoria": categoria,
                "nome_categoria": nome_categoria,
                "arquivos": [
                    {"nome_arquivo": caminho.name}
                    for caminho in candidatos[:LIMITE_ARQUIVOS_ARQUIVADOS]
                ],
            }
        )
    return {"categorias": categorias}


def _eh_arquivo_personalizado_arquivado(caminho: Path) -> bool:
    return "_" in caminho.stem and not caminho.stem.endswith("_restaurado")


def _criar_task_a_partir_da_planilha(caminho: Path) -> TaskFila:
    """Reconstrói os dados da fila a partir do layout de uma ficha PO gerada."""
    workbook = None
    try:
        workbook = openpyxl.load_workbook(caminho, data_only=True, read_only=True)
        planilha = workbook["PO"]
        codigo_maquina = int(planilha["A6"].value)
        titulo_po = planilha["A1"].value
        operacao = str(planilha["B2"].value or "")
        produto = f"{planilha['A4'].value or ''} ({planilha['B4'].value or ''})"
        tempo_fixo = float(planilha["E8"].value)
        tempo_mtm = round(
            sum(
                float(planilha.cell(row=linha, column=5).value or 0)
                for linha in range(9, planilha.max_row + 1)
            ),
            4,
        )
    except (
        KeyError,
        TypeError,
        ValueError,
        OSError,
        BadZipFile,
        openpyxl.utils.exceptions.InvalidFileException,
    ) as erro:
        raise ValueError(
            f"Não foi possível reconstruir a task a partir da planilha {caminho.name}."
        ) from erro
    finally:
        if workbook is not None:
            workbook.close()

    return {
        "codigo_de_maquina": codigo_maquina,
        "titulo_po": str(titulo_po) if titulo_po is not None else None,
        "operacao": operacao,
        "produto": produto,
        "tempo_fixo_min": tempo_fixo,
        "tempo_mtm_min": tempo_mtm,
        "tempo_total_min": round(tempo_fixo + tempo_mtm, 4),
        "arquivo_gerado": caminho.name,
    }


def restaurar_arquivo_arquivado(
    categoria: str,
    nome_arquivo: str,
    recolocar_na_fila: bool,
) -> RestauracaoArquivo:
    """Move um arquivo arquivado de volta à saída e, se pedido, recupera sua task."""
    if categoria not in CATEGORIAS_ARQUIVADAS:
        raise ValueError(f"Categoria de arquivo inválida: {categoria}.")
    if Path(nome_arquivo).name != nome_arquivo or "/" in nome_arquivo or "\\" in nome_arquivo:
        raise ValueError("Informe somente o nome do arquivo, sem diretórios.")
    if Path(nome_arquivo).suffix.casefold() != ".xlsx":
        raise ValueError("Somente arquivos XLSX podem ser restaurados.")

    _, pastas = CATEGORIAS_ARQUIVADAS[categoria]
    if categoria == "excluido":
        caminho_raiz = PASTA_SAIDA / nome_arquivo
        candidatos = (
            [caminho_raiz]
            if _eh_arquivo_personalizado_arquivado(caminho_raiz)
            else []
        )
    else:
        candidatos = [PASTA_SAIDA / pasta / nome_arquivo for pasta in pastas]
    caminho_origem = next((caminho for caminho in candidatos if caminho.is_file()), None)
    if caminho_origem is None:
        raise FileNotFoundError(f"Arquivo arquivado não encontrado: {nome_arquivo}.")

    caminho_destino = PASTA_SAIDA / (
        f"{caminho_origem.stem}_restaurado{caminho_origem.suffix}"
    )
    if caminho_destino.exists():
        raise FileExistsError(
            f"Já existe um arquivo restaurado com o nome {caminho_destino.name}."
        )

    task: TaskFila | None = None
    if recolocar_na_fila:
        task = _criar_task_a_partir_da_planilha(caminho_origem)
        carregar_bases()
        if task["codigo_de_maquina"] not in state.codigo_de_maquina:
            raise ValueError(
                f"Máquina com código {task['codigo_de_maquina']} não encontrada na base."
            )
        task["arquivo_gerado"] = caminho_destino.name

    caminho_origem.rename(caminho_destino)
    if task is not None:
        state.filas_maquinas.setdefault(task["codigo_de_maquina"], []).append(task)

    return {
        "mensagem": (
            f"Arquivo restaurado como {caminho_destino.name}."
            + (" Task recolocada na fila." if task is not None else "")
        ),
        "categoria": categoria,
        "arquivo_original": nome_arquivo,
        "arquivo_restaurado": caminho_destino.name,
        "recolocado_na_fila": task is not None,
        "task_na_fila": task,
    }


def limpar_filas_maquinas() -> dict[str, str]:
    """Esvazia as filas de todas as máquinas sem excluir arquivos Excel.

    Returns:
        Mensagem confirmando que as filas em memória foram limpas.
    """
    for codigo_maquina in state.filas_maquinas:
        state.filas_maquinas[codigo_maquina] = []
    return {"mensagem": "Filas de todas as máquinas zeradas com sucesso!"}
