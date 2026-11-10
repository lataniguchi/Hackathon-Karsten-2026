"""Testes de integracao das rotas e contratos da API FastAPI baseados em dados externos."""

import inspect
import sys
from pathlib import Path

# Ajuste do path para importar os modulos do Backend
ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "Backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import main
from schemas import DemandaTextoSchema, RemoverTaskSchema
from testes.dados_referencia import CASOS_DE_TESTE


def _executar(retorno_ou_coro):
    """Executa a rota de forma direta e compativel."""
    if inspect.iscoroutine(retorno_ou_coro):
        try:
            retorno_ou_coro.send(None)
        except StopIteration as e:
            return e.value
    return retorno_ou_coro


def test_rota_consulta_bases():
    """Valida a rota /api/bases retornando catalogo de maquinas e elementos."""
    resposta = main.listar_bases()
    assert "matriz_mtm" in resposta, "Catalogo MTM ausente na rota de bases."
    assert "maquinas" in resposta, "Lista de maquinas ausente na rota de bases."
    assert len(resposta["maquinas"]) > 0, "Nenhuma maquina retornada."


def test_rota_ingestao_e_calculo_texto():
    """Valida a rota /api/calcular-demanda-json-texto com entrada de texto puro do cenario 1."""
    caso = CASOS_DE_TESTE[0]
    payload = DemandaTextoSchema(texto=caso["texto_demanda"])
    resposta = _executar(main.calcular_via_json_texto(payload, adicionar_na_fila=True))

    assert "dados_extraidos_da_demanda" in resposta, "Dados extraidos ausentes na resposta."
    assert "ficha_po_calculada" in resposta, "Ficha PO calculada ausente na resposta."

    ficha = resposta["ficha_po_calculada"]
    itens = ficha["tabela_elementos"]
    item_fixo = next((i for i in itens if i["codigo_do_elemento"] == "FIXO"), None)
    assert item_fixo is not None, "Elemento FIXO ausente na PO calculada."
    assert abs(item_fixo["tempos_em_minutos"] - caso["saida_esperada"]["tempo_fixo_min"]) < 0.0001


def test_rota_adicao_e_balanceamento_fila():
    """Valida a inclusao de tarefas na fila de producao da maquina."""
    caso = CASOS_DE_TESTE[0]
    resumo = main.consultar_filas_maquinas()
    maquinas = resumo.get("maquinas_fila", [])
    maq1 = next((m for m in maquinas if m["codigo_de_maquina"] == caso["saida_esperada"]["cod_eqp"]), None)
    assert maq1 is not None, "Maquina 1 nao localizada no resumo de filas."
    assert maq1["quantidade_tasks"] >= 1, "Tarefa calculada nao foi enfileirada na maquina 1."
    assert maq1["tempo_total_fila_min"] > 0, "Tempo acumulado da fila deve ser maior que zero."


def test_rota_remocao_tarefa_fila():
    """Valida a remocao de tarefa da fila com motivo e recalculo."""
    resumo_antes = main.consultar_filas_maquinas()
    maq1_antes = next((m for m in resumo_antes["maquinas_fila"] if m["codigo_de_maquina"] == 1), None)
    qtd_antes = maq1_antes["quantidade_tasks"] if maq1_antes else 0

    if qtd_antes > 0:
        payload = RemoverTaskSchema(motivo="Concluido")
        res_remocao = main.remover_task_maquina(codigo_maquina=1, indice=1, payload=payload)
        assert res_remocao["motivo"] == "Concluido", "Motivo de remocao invalido."
        assert "mensagem" in res_remocao, "Mensagem de confirmacao ausente."

        resumo_depois = main.consultar_filas_maquinas()
        maq1_depois = next((m for m in resumo_depois["maquinas_fila"] if m["codigo_de_maquina"] == 1), None)
        qtd_depois = maq1_depois["quantidade_tasks"] if maq1_depois else 0
        assert qtd_depois == qtd_antes - 1, "Quantidade de tarefas nao foi decrementada."
