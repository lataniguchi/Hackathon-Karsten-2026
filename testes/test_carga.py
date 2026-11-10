"""Testes de carga progressivos (20, 50 e 100) com correlacao por identificador unico."""

import inspect
import sys
from pathlib import Path

# Ajuste do path para importar os modulos do Backend
ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "Backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import main
from schemas import DemandaTextoSchema
from services.config import PASTA_SAIDA
from services.fila import limpar_filas_maquinas
from testes.dados_referencia import CASOS_DE_TESTE, MAPA_CASOS


def _executar(retorno_ou_coro):
    """Executa a rota de forma direta e compativel."""
    if inspect.iscoroutine(retorno_ou_coro):
        try:
            retorno_ou_coro.send(None)
        except StopIteration as e:
            return e.value
    return retorno_ou_coro


def _limpar_arquivos_excedentes():
    """Remove planilhas temporarias excedentes geradas durante os lotes de carga."""
    for arq in PASTA_SAIDA.glob("PO-SL-*.xlsx"):
        if arq.name != "PO-SL-001.xlsx":
            try:
                arq.unlink()
            except OSError:
                pass


def _executar_lote_carga(quantidade: int):
    """Executa um lote de requisicoes validando entrada vs saida por ID e fila por maquina."""
    limpar_filas_maquinas()
    sucessos = 0
    contagem_esperada: dict[int, int] = {}
    tempo_esperado: dict[int, float] = {}

    for i in range(quantidade):
        caso_esperado = CASOS_DE_TESTE[i % len(CASOS_DE_TESTE)]
        payload = DemandaTextoSchema(texto=caso_esperado["texto_demanda"])

        resposta = _executar(main.calcular_via_json_texto(payload, adicionar_na_fila=True))
        assert "dados_extraidos_da_demanda" in resposta, "Dados extraidos ausentes na resposta."
        assert "ficha_po_calculada" in resposta, "Ficha PO ausente na resposta."

        # Correlacao estrita por ID para evitar falso negativo
        id_recebido = resposta["dados_extraidos_da_demanda"]["titulo_po"]
        assert id_recebido == caso_esperado["id"], (
            f"Falso negativo detectado: esperado {caso_esperado['id']}, recebido {id_recebido}."
        )

        caso_gabarito = MAPA_CASOS[id_recebido]
        itens = resposta["ficha_po_calculada"]["tabela_elementos"]
        total_calculado = round(sum(item["tempos_em_minutos"] for item in itens), 4)
        total_esperado = caso_gabarito["saida_esperada"]["tempo_total_tp"]
        assert abs(total_calculado - total_esperado) < 0.0001, (
            f"Divergencia de calculo no ID {id_recebido}: "
            f"calculado {total_calculado}, esperado {total_esperado}."
        )

        cod_maq = caso_gabarito["saida_esperada"]["cod_eqp"]
        contagem_esperada[cod_maq] = contagem_esperada.get(cod_maq, 0) + 1
        tempo_esperado[cod_maq] = round(tempo_esperado.get(cod_maq, 0.0) + total_esperado, 4)
        sucessos += 1

    assert sucessos == quantidade, f"Sucesso em apenas {sucessos}/{quantidade} requisicoes."

    # Validacao do consolidado e do balanceamento individual por maquina
    resumo = main.consultar_filas_maquinas()
    total_tasks_fila = sum(m["quantidade_tasks"] for m in resumo["maquinas_fila"])
    assert total_tasks_fila == quantidade, (
        f"Contagem incorreta na fila: esperado {quantidade}, encontrado {total_tasks_fila}."
    )

    for maq in resumo["maquinas_fila"]:
        c_maq = maq["codigo_de_maquina"]
        qtd_esp = contagem_esperada.get(c_maq, 0)
        tmp_esp = tempo_esperado.get(c_maq, 0.0)
        assert maq["quantidade_tasks"] == qtd_esp, (
            f"Balanceamento incorreto na maquina {c_maq}: esperado {qtd_esp}, encontrado {maq['quantidade_tasks']}."
        )
        assert abs(maq["tempo_total_fila_min"] - tmp_esp) < 0.001, (
            f"Tempo acumulado incorreto na maquina {c_maq}: esperado {tmp_esp}, encontrado {maq['tempo_total_fila_min']}."
        )

    # Limpeza apos o lote
    limpar_filas_maquinas()
    _limpar_arquivos_excedentes()


def test_carga_estagio_20():
    """Valida o estagio 1 de carga com 20 requisicoes."""
    _executar_lote_carga(20)


def test_carga_estagio_50():
    """Valida o estagio 2 de carga com 50 requisicoes."""
    _executar_lote_carga(50)


def test_carga_estagio_100():
    """Valida o estagio 3 de carga com 100 requisicoes."""
    _executar_lote_carga(100)
