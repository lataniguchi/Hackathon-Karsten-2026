"""CABECALHO DO ARQUIVO: rotas HTTP da API FastAPI para cálculo, bases e filas."""

from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from schemas import (
    DemandaTextoSchema,
    ListaArquivosArquivadosSchema,
    RemoverTaskResponseSchema,
    RemoverTaskSchema,
    RestauracaoArquivoResponseSchema,
    RestaurarArquivoSchema,
    ResumoFilasSchema,
    TasksMaquinaSchema,
)
from services.bases import obter_todas_as_bases
from services.config import PASTA_SAIDA
from services.demanda import extrair_dados_demanda
from services.fila import (
    deletar_task_maquina,
    listar_arquivos_arquivados,
    listar_tasks_maquina,
    limpar_filas_maquinas,
    obter_resumo_filas,
    restaurar_arquivo_arquivado,
)
from services.po import processar_calculo_po
from services.types import (
    CalculoDemandaResponse,
    RemocaoTask,
    ListaArquivosArquivados,
    RestauracaoArquivo,
    ResumoFilas,
    TasksMaquina,
)

app = FastAPI(
    title="API Auto-T&M Karsten",
    description="Backend para leitura de Demanda (.docx), cálculo de Ficha PO (.xlsx) e balanceamento de máquinas",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home() -> dict[str, str]:
    """Retorna o estado da API e o endereço da documentação interativa."""
    return {"status": "API Auto-T&M Karsten ativa!", "docs": "/docs"}


@app.get("/api/bases")
def listar_bases() -> dict[str, object]:
    """Retorna as bases de máquinas e elementos disponíveis."""
    return obter_todas_as_bases()


@app.post("/api/calcular-demanda")
async def calcular_via_arquivo_demanda(
    arquivo: UploadFile = File(description="Envie o arquivo demanda_000.docx ou .txt"),
    adicionar_na_fila: bool = True,
) -> CalculoDemandaResponse:
    """Recebe um arquivo de demanda, calcula a PO e gera a planilha Excel.

    Args:
        arquivo: Arquivo DOCX ou TXT enviado em multipart/form-data.
        adicionar_na_fila: Se verdadeiro, adiciona a PO à fila da máquina.

    Returns:
        Dados extraídos da demanda e ficha PO calculada.
    """
    try:
        conteudo = await arquivo.read()
        dados_extraidos = extrair_dados_demanda(
            conteudo_bytes=conteudo,
            nome_arquivo=arquivo.filename or "demanda.txt",
        )
        resultado = processar_calculo_po(
            dados_extraidos,
            adicionar_na_fila=adicionar_na_fila,
            salvar_excel=True,
        )
        return {
            "dados_extraidos_da_demanda": dados_extraidos,
            "ficha_po_calculada": resultado,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao processar arquivo de demanda: {e}",
        ) from e


@app.post("/api/calcular-demanda-texto")
async def calcular_via_texto_demanda(
    texto_demanda: str = Body(
        ...,
        media_type="text/plain",
        description="Digite ou cole o texto da demanda diretamente aqui",
        examples=[
            'Título: PO-SL-001\nREV: 00\nOperação: "Bainhar no corpo do SL - 1 lado"\nAgrupamento família: Sobre-lençol\nTamanho: Solteiro\nMedidas da peça (em m): 1,80 x 2,50\nPontos/cm: 2,50\nPerímetro costura (em m): 6,96\nCód. Eqp: 1\nElementos: 2.1, 1.1, 3.1'
        ],
    ),
    adicionar_na_fila: bool = True,
) -> CalculoDemandaResponse:
    """Calcula e exporta uma PO a partir de texto simples enviado na requisição.

    Args:
        texto_demanda: Conteúdo textual com os campos da demanda.
        adicionar_na_fila: Se verdadeiro, adiciona a PO à fila da máquina.

    Returns:
        Dados extraídos da demanda e ficha PO calculada.
    """
    try:
        dados_extraidos = extrair_dados_demanda(
            conteudo_bytes=texto_demanda.encode("utf-8"),
            nome_arquivo="demanda_digitada.txt",
        )
        resultado = processar_calculo_po(
            dados_extraidos,
            adicionar_na_fila=adicionar_na_fila,
            salvar_excel=True,
        )
        return {
            "dados_extraidos_da_demanda": dados_extraidos,
            "ficha_po_calculada": resultado,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao processar texto da demanda: {e}",
        ) from e


@app.post("/api/calcular-demanda-json-texto")
async def calcular_via_json_texto(
    payload: DemandaTextoSchema,
    adicionar_na_fila: bool = True,
) -> CalculoDemandaResponse:
    """Calcula e exporta uma PO a partir do campo ``texto`` de um JSON.

    Args:
        payload: Corpo validado pelo schema DemandaTextoSchema.
        adicionar_na_fila: Se verdadeiro, adiciona a PO à fila da máquina.

    Returns:
        Dados extraídos da demanda e ficha PO calculada.
    """
    try:
        dados_extraidos = extrair_dados_demanda(
            conteudo_bytes=payload.texto.encode("utf-8"),
            nome_arquivo="demanda_digitada.txt",
        )
        resultado = processar_calculo_po(
            dados_extraidos,
            adicionar_na_fila=adicionar_na_fila,
            salvar_excel=True,
        )
        return {
            "dados_extraidos_da_demanda": dados_extraidos,
            "ficha_po_calculada": resultado,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao processar texto da demanda: {e}",
        ) from e


@app.get("/api/download-po/{titulo_po}")
def baixar_planilha_po(titulo_po: str):
    """Envia ao cliente um XLSX gerado que ainda está na pasta principal.

    Args:
        titulo_po: Nome do arquivo sem extensão ou com extensão XLSX.

    Raises:
        HTTPException: Retorna 404 quando o arquivo não existe.
    """
    nome_limpo = titulo_po.replace(".xlsx", "")
    caminho = PASTA_SAIDA / f"{nome_limpo}.xlsx"
    if not caminho.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Planilha {nome_limpo}.xlsx ainda não foi gerada.",
        )
    return FileResponse(
        path=caminho,
        filename=f"{nome_limpo}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.get("/api/filas", response_model=ResumoFilasSchema)
def consultar_filas_maquinas() -> ResumoFilas:
    """Fornece um resumo das tasks e do tempo acumulado de cada máquina."""
    return obter_resumo_filas()


@app.get(
    "/api/arquivos-arquivados",
    response_model=ListaArquivosArquivadosSchema,
)
def consultar_arquivos_arquivados() -> ListaArquivosArquivados:
    """Lista até dez arquivos mais recentes de cada categoria arquivada."""
    return listar_arquivos_arquivados()


@app.post(
    "/api/arquivos-arquivados/{categoria}/{nome_arquivo}/restaurar",
    response_model=RestauracaoArquivoResponseSchema,
)
def restaurar_arquivo(
    categoria: str,
    nome_arquivo: str,
    payload: RestaurarArquivoSchema,
) -> RestauracaoArquivo:
    """Restaura um XLSX e permite escolher se a task volta para a fila."""
    try:
        return restaurar_arquivo_arquivado(
            categoria,
            nome_arquivo,
            payload.recolocar_na_fila,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@app.get(
    "/api/filas/{codigo_maquina}/tasks",
    response_model=TasksMaquinaSchema,
)
def consultar_tasks_maquina(codigo_maquina: int) -> TasksMaquina:
    """Lista as tasks de uma máquina antes que o usuário escolha um índice.

    Args:
        codigo_maquina: Código numérico da máquina consultada.

    Raises:
        HTTPException: Retorna 404 se a máquina não estiver cadastrada.
    """
    try:
        return listar_tasks_maquina(codigo_maquina)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.delete(
    "/api/filas/{codigo_maquina}/tasks/{indice}",
    response_model=RemoverTaskResponseSchema,
)
def remover_task_maquina(
    codigo_maquina: int,
    indice: int,
    payload: RemoverTaskSchema,
) -> RemocaoTask:
    """Remove uma task e arquiva seu Excel de acordo com o motivo informado.

    Args:
        codigo_maquina: Código da máquina que contém a task.
        indice: Índice numerado da task, começando em 1.
        payload: Motivo predefinido ou personalizado validado pelo schema.

    Raises:
        HTTPException: Retorna 400 para entrada inválida e 409 para falhas
            relacionadas ao arquivo que deve ser arquivado.
    """
    try:
        return deletar_task_maquina(codigo_maquina, indice, payload.motivo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (FileNotFoundError, FileExistsError) as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@app.delete("/api/filas")
def resetar_filas() -> dict[str, str]:
    """Limpa as tasks em memória de todas as máquinas."""
    return limpar_filas_maquinas()
