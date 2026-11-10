"""CABECALHO DO ARQUIVO: cálculo da ficha PO e geração do arquivo Excel."""

import re
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from .. import state
from ..bases.service import carregar_bases
from ..config import PASTA_SAIDA
from ..types import DadosDemanda, FichaPO, ItemPO, TaskFila


def processar_calculo_po(
    dados_entrada: DadosDemanda,
    adicionar_na_fila: bool = True,
    salvar_excel: bool = True,
) -> FichaPO:
    """Calcula os tempos da PO, exporta a planilha e opcionalmente enfileira.

    Args:
        dados_entrada: Campos normalizados extraídos da demanda.
        adicionar_na_fila: Indica se a task calculada será adicionada à fila.
        salvar_excel: Indica se a ficha será exportada para XLSX.

    Returns:
        Ficha calculada, incluindo o caminho do XLSX quando salvo.
    """
    carregar_bases()

    cod_eqp_int = int(dados_entrada["cod_eqp"])
    produto_info = dados_entrada["produto"]
    perimetro = float(produto_info["perimetro_costura_m"])
    roteiro = dados_entrada["elementos"]

    if cod_eqp_int not in state.codigo_de_maquina:
        raise ValueError(f"Máquina com código {cod_eqp_int} não encontrada na base TEMPO-CM.")

    idx_maq = state.codigo_de_maquina.index(cod_eqp_int)
    equipamento_nome = state.tipo_maquina[idx_maq]
    modelo_maquina = state.descricao[idx_maq]
    rpm_padrao_maq = state.rpm[idx_maq]
    fator_tempo_metro = state.tempo_tempo_metro[idx_maq]

    tempo_fixo = round(perimetro * fator_tempo_metro, 4)
    rpm_inf = int(rpm_padrao_maq * 0.90)
    rpm_sup = int(rpm_padrao_maq * 1.10)

    elementos_calculados: list[ItemPO] = []
    soma_mtm = 0.0
    for codigo in roteiro:
        cod_str = str(codigo).strip()
        idx_elem = -1
        if cod_str in state.codigo_mtm_formatado:
            idx_elem = state.codigo_mtm_formatado.index(cod_str)
        elif cod_str.isdigit():
            idx_elem = next(
                (
                    i
                    for i, codigo_formatado in enumerate(state.elemento_mais_agrupador)
                    if codigo_formatado.replace(".", "") == cod_str
                ),
                -1,
            )
            if idx_elem != -1:
                cod_str = state.elemento_mais_agrupador[idx_elem]

        if idx_elem != -1:
            desc_elem = state.descricao_do_elemento[idx_elem]
            tempo_elem = round(float(state.tempo[idx_elem]), 4)
        else:
            desc_elem = "Elemento não encontrado"
            tempo_elem = 0.0

        elementos_calculados.append(
            {
                "codigo_do_elemento": cod_str,
                "elementos": desc_elem,
                "frequencia": 1,
                "tempos_em_minutos": tempo_elem,
            }
        )
        soma_mtm += tempo_elem

    tempo_total_tp = round(tempo_fixo + soma_mtm, 4)
    titulo_po = dados_entrada.get("titulo_po")
    operacao = dados_entrada["operacao"]
    itens_po: list[ItemPO] = [
        {
            "codigo_do_elemento": "FIXO",
            "elementos": "Tempo de costura",
            "frequencia": 1,
            "tempos_em_minutos": tempo_fixo,
        },
        *elementos_calculados,
    ]
    ficha_po: FichaPO = {
        "cabecalho": {
            "titulo_po": titulo_po,
            "rev": dados_entrada["rev"],
            "operacao": operacao,
            "agrupamento_familia": produto_info["agrupamento_familia"],
            "tamanho": produto_info["tamanho"],
            "medidas_peca_m": produto_info["medidas_peca_m"],
            "pontos_cm": float(produto_info["pontos_cm"]),
            "perimetro_costura_m": perimetro,
            "cod_eqp": cod_eqp_int,
            "equipamento": equipamento_nome,
            "modelo_maquina": modelo_maquina,
            "rpm_limite_inferior": rpm_inf,
            "rpm_padrao": rpm_padrao_maq,
            "rpm_limite_superior": rpm_sup,
        },
        "tabela_elementos": itens_po,
    }

    caminho_excel = None
    if salvar_excel:
        caminho_excel = gerar_planilha_po_xlsx(ficha_po)
        ficha_po["arquivo_gerado"] = str(caminho_excel)

    if adicionar_na_fila:
        tarefa: TaskFila = {
            "codigo_de_maquina": cod_eqp_int,
            "titulo_po": titulo_po,
            "operacao": operacao,
            "produto": f"{produto_info['agrupamento_familia']} ({produto_info['tamanho']})",
            "tempo_fixo_min": tempo_fixo,
            "tempo_mtm_min": round(soma_mtm, 4),
            "tempo_total_min": tempo_total_tp,
            "arquivo_gerado": caminho_excel.name if caminho_excel else None,
        }
        state.filas_maquinas.setdefault(cod_eqp_int, []).append(tarefa)

    return ficha_po


def obter_proximo_indice_po() -> int:
    """Retorna o próximo índice livre, considerando arquivos arquivados."""
    indices: list[int] = []
    for caminho in PASTA_SAIDA.rglob("PO-SL-*.xlsx"):
        match = re.fullmatch(r"PO-SL-(\d+)(?:_.*)?", caminho.stem)
        if match:
            indices.append(int(match.group(1)))
    return max(indices, default=0) + 1


def gerar_planilha_po_xlsx(ficha_po: FichaPO) -> Path:
    """Cria e formata a ficha PO em Excel conforme o layout estabelecido.

    Args:
        ficha_po: Cabeçalho e itens calculados que serão escritos na planilha.

    Returns:
        Caminho do arquivo XLSX criado.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    assert ws is not None
    ws.title = "PO"

    cab = ficha_po["cabecalho"]
    itens: list[ItemPO] = ficha_po["tabela_elementos"]
    fonte_titulo = Font(name="Arial", size=14, bold=True)
    fonte_header = Font(name="Arial", size=10, bold=True)
    fonte_normal = Font(name="Arial", size=10, bold=False)
    fill_cinza = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
    fill_amarelo = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    borda_fina = Side(border_style="thin", color="000000")
    borda_completa = Border(
        left=borda_fina,
        right=borda_fina,
        top=borda_fina,
        bottom=borda_fina,
    )
    alinhamento_centro = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws.merge_cells("A1:D1")
    ws["A1"] = cab["titulo_po"]
    ws["A1"].font = fonte_titulo
    ws["E1"] = f"Rev. {cab['rev']}"
    ws["E1"].font = fonte_titulo

    ws["A2"] = "Operação"
    ws["A2"].font = fonte_header
    ws["A2"].fill = fill_cinza
    ws.merge_cells("B2:E2")
    ws["B2"] = cab["operacao"]
    ws["B2"].font = fonte_normal

    headers_prod = [
        "Agrupamento família",
        "Tamanho",
        "Medidas da peça (em m)",
        "Pontos/cm",
        "Perímetro costura\n(em m)",
    ]
    valores_prod: list[str | float] = [
        cab["agrupamento_familia"],
        cab["tamanho"],
        cab["medidas_peca_m"],
        cab["pontos_cm"],
        cab["perimetro_costura_m"],
    ]
    for col_idx, (header, valor) in enumerate(zip(headers_prod, valores_prod), start=1):
        celula_cabecalho = ws.cell(row=3, column=col_idx, value=header)
        celula_cabecalho.font = fonte_header
        celula_cabecalho.fill = fill_cinza
        celula_valor = ws.cell(row=4, column=col_idx, value=valor)
        celula_valor.font = fonte_normal
        if col_idx in (4, 5):
            celula_valor.number_format = "0.00"

    headers_eqp = [
        "Cód. Eqp.",
        "Equipamento",
        "RPM - limite inferior",
        "RPM - padrão",
        "RPM - limite superior",
    ]
    valores_eqp: list[str | int] = [
        cab["cod_eqp"],
        cab["equipamento"],
        "=D6*0.9",
        cab["rpm_padrao"],
        "=D6*1.1",
    ]
    for col_idx, (header, valor) in enumerate(zip(headers_eqp, valores_eqp), start=1):
        celula_cabecalho = ws.cell(row=5, column=col_idx, value=header)
        celula_cabecalho.font = fonte_header
        celula_cabecalho.fill = fill_cinza
        celula_valor = ws.cell(row=6, column=col_idx, value=valor)
        celula_valor.font = fonte_normal

    ws["A7"] = "Código do elemento"
    ws.merge_cells("B7:C7")
    ws["B7"] = "Elementos"
    ws["D7"] = "Frequência"
    ws["E7"] = "Tempos (em minutos)"
    for col_idx in range(1, 6):
        cell = ws.cell(row=7, column=col_idx)
        cell.font = fonte_header
        cell.fill = fill_cinza

    for idx, item in enumerate(itens, start=8):
        ws.merge_cells(start_row=idx, start_column=2, end_row=idx, end_column=3)
        ws.cell(row=idx, column=1, value=item["codigo_do_elemento"])
        ws.cell(row=idx, column=2, value=item["elementos"])
        ws.cell(row=idx, column=4, value=item["frequencia"])
        celula_tempo = ws.cell(row=idx, column=5, value=item["tempos_em_minutos"])
        celula_tempo.number_format = "0.0000"

        eh_fixo = item["codigo_do_elemento"] == "FIXO"
        for col_idx in range(1, 6):
            celula = ws.cell(row=idx, column=col_idx)
            celula.font = fonte_header if eh_fixo else fonte_normal
            if eh_fixo:
                celula.fill = fill_amarelo

    linha_total = 8 + len(itens)
    for row in ws.iter_rows(min_row=1, max_row=linha_total, min_col=1, max_col=5):
        for cell in row:
            cell.border = borda_completa
            cell.alignment = alinhamento_centro

    for coluna, largura in {"A": 22, "B": 22, "C": 24, "D": 20, "E": 24}.items():
        ws.column_dimensions[coluna].width = largura

    caminho_arquivo = PASTA_SAIDA / f"PO-SL-{obter_proximo_indice_po():03d}.xlsx"
    wb.save(caminho_arquivo)
    return caminho_arquivo
