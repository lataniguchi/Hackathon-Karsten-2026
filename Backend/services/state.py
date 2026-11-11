"""CABECALHO DO ARQUIVO: estado em memória das bases e filas de produção."""

from .types import TaskFila

descricao_do_elemento: list[str] = []
codigo_do_agrupador: list[int] = []
codigo_do_elemento: list[int] = []
elemento_mais_agrupador: list[str] = []
tempo: list[float] = []
codigo_mtm_formatado: list[str] = []

codigo_de_maquina: list[int] = []
tipo_maquina: list[str] = []
descricao: list[str] = []
rpm: list[int] = []
tempo_tempo_metro: list[float] = []
versao_arquivo_bases: tuple[str, int] | None = None

filas_maquinas: dict[int, list[TaskFila]] = {}
