"""CABECALHO DO ARQUIVO: tipos estruturados usados pelos serviços do backend."""

from typing import TypedDict


class ProdutoDados(TypedDict):
    """Campos do produto lidos da demanda."""

    agrupamento_familia: str
    tamanho: str
    medidas_peca_m: str
    pontos_cm: float
    perimetro_costura_m: float


class DadosDemanda(TypedDict):
    """Dados da demanda prontos para o cálculo da ficha PO."""

    titulo_po: str | None
    rev: str
    operacao: str
    produto: ProdutoDados
    cod_eqp: int
    elementos: list[str]


class ItemPO(TypedDict):
    """Elemento ou tempo fixo apresentado na ficha PO."""

    codigo_do_elemento: str
    elementos: str
    frequencia: int
    tempos_em_minutos: float


class CabecalhoPO(TypedDict):
    """Campos do cabeçalho da ficha de produção."""

    titulo_po: str | None
    rev: str
    operacao: str
    agrupamento_familia: str
    tamanho: str
    medidas_peca_m: str
    pontos_cm: float
    perimetro_costura_m: float
    cod_eqp: int
    equipamento: str
    modelo_maquina: str
    rpm_limite_inferior: int
    rpm_padrao: int
    rpm_limite_superior: int


class FichaPOBase(TypedDict):
    """Estrutura principal da ficha PO antes de incluir metadados opcionais."""

    cabecalho: CabecalhoPO
    tabela_elementos: list[ItemPO]


class FichaPO(FichaPOBase, total=False):
    """Ficha PO com o caminho do Excel incluído após a exportação."""

    arquivo_gerado: str


class TaskFila(TypedDict):
    """Dados de uma tarefa armazenada na fila da máquina."""

    codigo_de_maquina: int
    titulo_po: str | None
    operacao: str
    produto: str
    tempo_fixo_min: float
    tempo_mtm_min: float
    tempo_total_min: float
    arquivo_gerado: str | None


class TaskFilaNumerada(TaskFila):
    """Task de fila acrescida do índice usado para selecionar a remoção."""

    indice: int


class TaskRemovida(TaskFilaNumerada):
    """Task removida, identificada também pelo motivo da exclusão."""

    motivo_exclusao: str


class TasksMaquina(TypedDict):
    """Fila numerada de uma máquina específica."""

    codigo_de_maquina: int
    tasks: list[TaskFilaNumerada]


class ResumoMaquinaFila(TypedDict):
    """Resumo da quantidade e do tempo de tasks de uma máquina."""

    codigo_de_maquina: int
    tipo_maquina: str
    descricao: str
    quantidade_tasks: int
    tempo_total_fila_min: float
    tasks: list[TaskFilaNumerada]


class ResumoFilas(TypedDict):
    """Resumo consolidado das filas de todas as máquinas."""

    maquinas_fila: list[ResumoMaquinaFila]


class RemocaoTask(TypedDict):
    """Resposta da remoção de uma task e atualização da fila."""

    mensagem: str
    motivo: str
    arquivo_renomeado: str | None
    caminho_arquivo_renomeado: str | None
    task_removida: TaskRemovida
    codigo_de_maquina: int
    tasks: list[TaskFilaNumerada]


class CalculoDemandaResponse(TypedDict):
    """Resposta da API com os dados extraídos e a ficha calculada."""

    dados_extraidos_da_demanda: DadosDemanda
    ficha_po_calculada: FichaPO
