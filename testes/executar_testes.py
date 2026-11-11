"""Executor central dos testes automatizados e testes de carga."""

import datetime
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from testes.test_carga import (
    test_carga_estagio_20,
    test_carga_estagio_50,
    test_carga_estagio_100,
)
from testes.test_motor_calculo import (
    test_cenarios_de_calculo,
    test_deteccao_divergencias_teste_do_teste,
    test_geracao_planilha_excel,
    test_leitura_bases_dados,
    test_robustez_casos_adversariais,
    test_tratamento_excecao_maquina_invalida,
)
from testes.test_rotas_api import (
    test_rota_adicao_e_balanceamento_fila,
    test_rota_consulta_bases,
    test_rota_ingestao_e_calculo_texto,
    test_rota_remocao_tarefa_fila,
    test_listagem_limitada_e_restauracao_de_arquivado,
)

CAMINHO_HISTORICO = ROOT_DIR / "testes" / "historico.txt"


def executar():
    testes = [
        ("Leitura das bases de dados", test_leitura_bases_dados),
        ("Cenarios de calculo (13 produtos e 3 maquinas)", test_cenarios_de_calculo),
        ("Robustez e casos de borda (emojis, dizimas, espacos)", test_robustez_casos_adversariais),
        ("Verificacao do validador (deteccao de dados adulterados)", test_deteccao_divergencias_teste_do_teste),
        ("Tratamento de excecao para maquina inexistente", test_tratamento_excecao_maquina_invalida),
        ("Geracao fisica das planilhas Excel", test_geracao_planilha_excel),
        ("Rota de consulta de bases (/api/bases)", test_rota_consulta_bases),
        ("Rota de ingestao e calculo (/api/calcular...)", test_rota_ingestao_e_calculo_texto),
        ("Inclusao e balanceamento em fila", test_rota_adicao_e_balanceamento_fila),
        ("Remocao de tarefa da fila com motivo", test_rota_remocao_tarefa_fila),
        ("Listagem limitada e restauracao de arquivo", test_listagem_limitada_e_restauracao_de_arquivado),
        ("Teste de Carga - Estagio 1: 20 requisicoes", test_carga_estagio_20),
        ("Teste de Carga - Estagio 2: 50 requisicoes", test_carga_estagio_50),
        ("Teste de Carga - Estagio 3: 100 requisicoes", test_carga_estagio_100),
    ]

    print("======================= Testes Automatizados =======================", flush=True)
    inicio_geral = time.perf_counter()
    todos_passaram = True
    metricas_execucao = []

    for nome, funcao in testes:
        t0 = time.perf_counter()
        try:
            funcao()
            duracao = time.perf_counter() - t0
            metricas_execucao.append((nome, True, duracao, None))
            pontos = "." * max(2, 58 - len(nome))
            print(f"[PASSOU] {nome} {pontos} ({duracao:.2f}s)", flush=True)
        except Exception as e:
            duracao = time.perf_counter() - t0
            todos_passaram = False
            metricas_execucao.append((nome, False, duracao, str(e)))
            pontos = "." * max(2, 58 - len(nome))
            print(f"[FALHOU] {nome} {pontos} ({duracao:.2f}s)", flush=True)
            print(f"         Detalhe: {e}", flush=True)

    tempo_total = time.perf_counter() - inicio_geral
    status_final = "Aprovado" if todos_passaram else "Falha"

    print("--------------------------------------------------------------------", flush=True)
    print(f"Tempo total: {tempo_total:.2f}s", flush=True)
    print(f"STATUS: {status_final}", flush=True)
    print(f"Historico atualizado em: {CAMINHO_HISTORICO.name}", flush=True)
    print("====================================================================", flush=True)

    # Gravacao do registro no historico
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linhas_historico = [
        f"--- Execucao: {timestamp} ---",
        f"Status: {status_final} | Duracao: {tempo_total:.2f}s",
    ]
    for nome, sucesso, duracao, erro in metricas_execucao:
        ind = "OK" if sucesso else "FALHA"
        linhas_historico.append(f"  [{ind}] {nome}: {duracao:.2f}s")
        if erro:
            linhas_historico.append(f"        Motivo: {erro}")
    linhas_historico.append("\n")

    with open(CAMINHO_HISTORICO, "a", encoding="utf-8") as f:
        f.write("\n".join(linhas_historico))

    return 0 if todos_passaram else 1


if __name__ == "__main__":
    codigo_saida = executar()
    sys.exit(codigo_saida)
