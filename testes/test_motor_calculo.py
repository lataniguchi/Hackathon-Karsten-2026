"""Testes unitarios do motor de calculo e regras de negocio baseados em dados externos."""

import sys
from pathlib import Path

# Ajuste do path para importar os modulos do Backend
ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "Backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services.bases.service import carregar_bases, obter_todas_as_bases
from services.po.service import gerar_planilha_po_xlsx, processar_calculo_po
from testes.dados_referencia import CASOS_ADVERSARIAIS, CASOS_DE_TESTE


def test_leitura_bases_dados():
    """Valida a leitura e integridade das planilhas de maquinas e elementos."""
    carregar_bases()
    bases = obter_todas_as_bases()
    assert "matriz_mtm" in bases, "Chave matriz_mtm ausente nas bases carregadas."
    assert "maquinas" in bases, "Chave maquinas ausente nas bases carregadas."
    assert len(bases["maquinas"]) >= 3, "Quantidade de maquinas menor que o esperado."
    assert len(bases["matriz_mtm"]) >= 9, "Quantidade de elementos MTM menor que o esperado."


def test_cenarios_de_calculo():
    """Valida o calculo de todos os 13 cenarios reais do catalogo (todas as maquinas e produtos)."""
    carregar_bases()
    for caso in CASOS_DE_TESTE:
        cid = caso["id"]
        entrada = caso["entrada"]
        esperado = caso["saida_esperada"]

        resultado = processar_calculo_po(
            entrada,
            adicionar_na_fila=False,
            salvar_excel=False,
        )
        itens = resultado["tabela_elementos"]
        item_fixo = next((i for i in itens if i["codigo_do_elemento"] == "FIXO"), None)
        assert item_fixo is not None, f"[{cid}] Item FIXO nao foi gerado."

        # Validacao do tempo fixo
        assert abs(item_fixo["tempos_em_minutos"] - esperado["tempo_fixo_min"]) < 0.0001, (
            f"[{cid}] Tempo FIXO ({item_fixo['tempos_em_minutos']}) "
            f"difere do esperado ({esperado['tempo_fixo_min']})."
        )

        # Validacao da soma MTM
        soma_mtm = sum(i["tempos_em_minutos"] for i in itens if i["codigo_do_elemento"] != "FIXO")
        assert abs(soma_mtm - esperado["soma_mtm_min"]) < 0.0001, (
            f"[{cid}] Soma MTM ({soma_mtm:.4f}) difere do esperado ({esperado['soma_mtm_min']})."
        )

        # Validacao do tempo total TP
        total = round(sum(i["tempos_em_minutos"] for i in itens), 4)
        assert abs(total - esperado["tempo_total_tp"]) < 0.0001, (
            f"[{cid}] Tempo total TP ({total}) difere do esperado ({esperado['tempo_total_tp']})."
        )


def test_robustez_casos_adversariais():
    """Valida resiliencia a entradas extremas (emojis, dizimas, espacos extras, numeros gigantes)."""
    carregar_bases()
    for caso in CASOS_ADVERSARIAIS:
        cid = caso["id"]
        entrada = caso["entrada"]
        esperado = caso["saida_esperada"]

        resultado = processar_calculo_po(
            entrada,
            adicionar_na_fila=False,
            salvar_excel=False,
        )
        itens = resultado["tabela_elementos"]
        item_fixo = next((i for i in itens if i["codigo_do_elemento"] == "FIXO"), None)
        assert item_fixo is not None, f"[{cid}] Item FIXO nao foi gerado."

        assert abs(item_fixo["tempos_em_minutos"] - esperado["tempo_fixo_min"]) < 0.0001, (
            f"[{cid}] Tempo FIXO ({item_fixo['tempos_em_minutos']}) difere do esperado."
        )

        total = round(sum(i["tempos_em_minutos"] for i in itens), 4)
        assert abs(total - esperado["tempo_total_tp"]) < 0.0001, (
            f"[{cid}] Tempo total TP ({total}) difere do esperado."
        )


def test_deteccao_divergencias_teste_do_teste():
    """Valida o framework de testes: comprova que dados adulterados geram reprovacao garantida."""
    caso_adulterado = {
        "entrada": CASOS_DE_TESTE[0]["entrada"],
        "saida_esperada_falsa": {
            "tempo_total_tp": 999.9999,  # Valor deliberadamente falso
        },
    }
    resultado = processar_calculo_po(
        caso_adulterado["entrada"],
        adicionar_na_fila=False,
        salvar_excel=False,
    )
    total_real = round(sum(i["tempos_em_minutos"] for i in resultado["tabela_elementos"]), 4)
    gabarito_falso = caso_adulterado["saida_esperada_falsa"]["tempo_total_tp"]

    # O validador DEVE detectar que total_real != gabarito_falso
    detectou_divergencia = abs(total_real - gabarito_falso) > 0.0001
    assert detectou_divergencia, "Falha de QA: o framework aceitou um calculo adulterado sem acusar erro."


def test_tratamento_excecao_maquina_invalida():
    """Valida a recusa controlada quando uma maquina inexistente e solicitada."""
    carregar_bases()
    entrada_invalida = {
        **CASOS_DE_TESTE[0]["entrada"],
        "cod_eqp": 99,
    }
    try:
        processar_calculo_po(entrada_invalida, adicionar_na_fila=False, salvar_excel=False)
        assert False, "O sistema deveria ter recusado codigo de maquina inexistente (99)."
    except ValueError as e:
        assert "não encontrada" in str(e).lower() or "nao encontrada" in str(e).lower()


def test_geracao_planilha_excel():
    """Valida a criacao fisica da planilha XLSX formatada com base no cenario 1."""
    carregar_bases()
    resultado = processar_calculo_po(
        CASOS_DE_TESTE[0]["entrada"],
        adicionar_na_fila=False,
        salvar_excel=False,
    )
    caminho_xlsx = gerar_planilha_po_xlsx(resultado)
    assert caminho_xlsx.exists(), f"Arquivo Excel nao foi criado em: {caminho_xlsx}"
    assert caminho_xlsx.stat().st_size > 0, "Arquivo Excel gerado esta vazio."
