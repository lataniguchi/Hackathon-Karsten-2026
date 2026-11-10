# 🚀 Hackathon Auto-T&M Karsten - Contrato de Desenvolvimento da Equipe

Este documento define a arquitetura do projeto e as responsabilidades de cada um dos 3 integrantes. Nosso foco principal é a **simplicidade**, a **entrega de resultados** funcionais até o prazo final (11/11/2026 às 14:00) e a **inovação** para garantir pontuação máxima.

## 🏗️ Arquitetura (Frontend Desacoplado do Backend)

Para evitar gargalos, adotamos uma arquitetura onde a tela não depende da lógica de cálculo para ser construída:

* **Backend:** FastAPI (Python) - Rápido de fazer, excelente para receber/enviar dados e fácil de plugar um banco de dados simples (SQLite) para o dashboard.
* **Frontend:** [Definir: Streamlit ou React] - Focado em capturar os dados do usuário, exibir resultados e gerar gráficos.
* **Comunicação:** O Frontend envia um `JSON` para a API, e a API devolve os cálculos prontos.

---

## 🛣️ O Plano de Batalha (Fase 1 e Fase 2)

**REGRA DE OURO:** Ninguém começa a Fase 2 antes da Fase 1 estar 100% testada e entregando o arquivo PO exigido pela banca!

### 🎯 Fase 1: O MVP (Garante os 35 pontos básicos)
O fluxo básico obrigatório: Receber os dados -> Calcular Tempos -> Gerar a Ficha PO na tela e para exportação.

### 🌟 Fase 2: O Diferencial (Garante os 20 pontos de Criatividade)
Implementação de um sistema de "Fila de Produção" para balanceamento de carga. O sistema registrará quantas tarefas (tasks) cada máquina tem na fila e mostrará em um dashboard gráfico para evitar que uma máquina fique sobrecarregada enquanto outra fica ociosa.

---

## 👥 Divisão de Tarefas e Contrato de Entregas

### 🧑‍💻 Integrante 1: Motor de Cálculo e API (O "Cérebro")
**Responsável por:** [Nome do Integrante 1]

* **Fase 1 (MVP):**
  1. `carregar_base()`: Ler as abas da planilha (MTM e Máquinas) usando `pandas`.
  2. `calcular_tempo_fixo(perimetro, tempo_metro)`: $Tempo FIXO = Perímetro \times Tempo/Metro$.
  3. `calcular_tempos_mtm(sequencia)`: Somar os tempos referentes à sequência MTM.
  4. Criar a rota `POST /api/calcular`.

* **Fase 2 (Fila e Dashboard):**
  1. Criar um mini-banco (SQLite) ou estrutura em memória para salvar as ordens calculadas associadas ao código da máquina.
  2. Criar a rota `GET /api/dashboard` que devolve uma lista das máquinas e o tempo total acumulado (soma do TP das tasks) na fila de cada uma.

### 🧑‍💻 Integrante 2: Interface e Ingestão de Dados (A "Cara" do Projeto)
**Responsável por:** [Nome do Integrante 2]

* **Fase 1 (MVP):**
  1. Criar os campos de entrada (Nome da Peça, Perímetro, Densidade, Máquina e Roteiro).
  2. Criar a função que envia (POST) esses dados para a rota do Integrante 1.
  3. Exibir a tabela visual (Ficha PO) com os resultados (Use dados *mockados* até a API ficar pronta).

* **Fase 2 (Fila e Dashboard):**
  1. Criar uma nova aba ou seção na tela chamada "Dashboard de Produção".
  2. Consumir a rota `GET /api/dashboard` e gerar um Gráfico de Barras (Eixo X: Máquinas / Eixo Y: Tempo Total na Fila) para visualizar o balanceamento de carga.

### 🧑‍💻 Integrante 3: Exportação e "Closing" (O "Empacotador")
**Responsável por:** [Nome do Integrante 3]

* **Fase 1 (MVP):**
  1. `gerar_ficha_po(dados_calculados)`: Script para exportar o resultado final no formato do gabarito (Excel/PDF).
  2. Integrar essa função com um botão "Exportar" no Frontend.
  3. Atualizar o `README.md` com o passo a passo exato de execução do projeto.

* **Fase 2 (Pitch e Argumentação):**
  1. Preparar o roteiro do Pitch (5 minutos).
  2. Estruturar a apresentação para mostrar primeiro a geração da Ficha PO (Precisão) e terminar com o "Fator Uau": mostrar o Dashboard de Fila funcionando e explicar como isso resolve gargalos reais na indústria têxtil.

---

## 🤝 O Contrato de Dados (JSON)

**1. Fluxo de Cálculo (POST /api/calcular)**
*Enviado pelo Frontend:*
```json
{
  "produto": {
    "nome": "Sobre-lençol Solteiro",
    "perimetro_m": 4.5,
    "densidade_pontos": 40
  },
  "maquina_codigo": "M-001",
  "roteiro_mtm": ["2.1", "1.1", "3.1"]
}
```
*Devolvido pela API:*
```json
{
  "tempo_fixo_min": 1.25,
  "elementos_mtm": [
    {"codigo": "2.1", "descricao": "Pegar peça", "tempo_min": 0.10}
  ],
  "tempo_total_tp": 1.40
}
```

**2. Fluxo do Dashboard - Fase 2 (GET /api/dashboard)**
*Devolvido pela API para montar o gráfico:*
```json
{
  "fila_maquinas": [
    {"maquina_codigo": "M-001", "qtd_tasks": 15, "tempo_total_acumulado_min": 45.5},
    {"maquina_codigo": "M-002", "qtd_tasks": 3, "tempo_total_acumulado_min": 12.0}
  ]
}
```