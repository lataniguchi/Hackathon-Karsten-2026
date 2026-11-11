"""CABECALHO DO ARQUIVO: schemas Pydantic para validar entradas e saídas HTTP."""

from pydantic import BaseModel, ConfigDict, Field


class DemandaTextoSchema(BaseModel):
    """Corpo JSON que transporta o texto de uma demanda."""

    texto: str = Field(..., min_length=1)


class RemoverTaskSchema(BaseModel):
    """Corpo JSON com o motivo obrigatório para remover uma task."""

    model_config = ConfigDict(str_strip_whitespace=True)

    motivo: str = Field(
        ...,
        min_length=1,
        description="Concluido, Falhou, Reavaliacao ou uma descrição personalizada.",
    )


class TaskFilaDadosSchema(BaseModel):
    """Campos comuns de uma task de fila."""

    codigo_de_maquina: int
    titulo_po: str | None = None
    operacao: str
    produto: str
    tempo_fixo_min: float
    tempo_mtm_min: float
    tempo_total_min: float
    arquivo_gerado: str | None = None


class TaskFilaSchema(TaskFilaDadosSchema):
    """Representação validada de uma task numerada na fila."""

    indice: int


class TasksMaquinaSchema(BaseModel):
    """Resposta com tasks de uma máquina específica."""

    codigo_de_maquina: int
    tasks: list[TaskFilaSchema]


class ResumoMaquinaFilaSchema(BaseModel):
    """Resumo da fila, quantidade e tempo acumulado de uma máquina."""

    codigo_de_maquina: int
    tipo_maquina: str
    descricao: str
    quantidade_tasks: int
    tempo_total_fila_min: float
    tasks: list[TaskFilaSchema]


class ResumoFilasSchema(BaseModel):
    """Resposta consolidada da consulta de todas as filas."""

    maquinas_fila: list[ResumoMaquinaFilaSchema]


class TaskRemovidaSchema(TaskFilaSchema):
    """Task removida, incluindo o motivo registrado."""

    motivo_exclusao: str


class RemoverTaskResponseSchema(TasksMaquinaSchema):
    """Resposta da remoção com a task arquivada e a fila atualizada."""

    mensagem: str
    motivo: str
    arquivo_renomeado: str | None = None
    caminho_arquivo_renomeado: str | None = None
    task_removida: TaskRemovidaSchema


class ArquivoArquivadoSchema(BaseModel):
    """Arquivo disponível para restauração."""

    nome_arquivo: str


class CategoriaArquivadaSchema(BaseModel):
    """Arquivos mais recentes disponíveis em uma categoria."""

    categoria: str
    nome_categoria: str
    arquivos: list[ArquivoArquivadoSchema]


class ListaArquivosArquivadosSchema(BaseModel):
    """Categorias de arquivos arquivados."""

    categorias: list[CategoriaArquivadaSchema]


class RestaurarArquivoSchema(BaseModel):
    """Escolha explícita sobre recuperar também a task na fila."""

    recolocar_na_fila: bool


class RestauracaoArquivoResponseSchema(BaseModel):
    """Resultado da restauração do arquivo e, se solicitado, da task."""

    mensagem: str
    categoria: str
    arquivo_original: str
    arquivo_restaurado: str
    recolocado_na_fila: bool
    task_na_fila: TaskFilaDadosSchema | None = None
