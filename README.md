# 🚀 Hackathon Auto-T&M Karsten - Contrato de Desenvolvimento da Equipe

Este documento define a arquitetura do projeto e as responsabilidades de cada integrante para a reta final do hackathon. O Backend já está estruturado, modularizado e com as regras de negócio finalizadas. 

**Foco agora: Integração do Frontend e Preparação para o Pitch da Banca (11/11/2026).**

## 🏗️ Arquitetura do Sistema (Desacoplada)
- **Backend (Finalizado):** FastAPI (Python) estruturado em Domain-Driven Design (pacote `services/`). Validação de dados via Pydantic e geração nativa de planilhas `.xlsx` via `openpyxl`.
- **Frontend (Em andamento):** [Streamlit / React / HTML+JS] - Responsável pela interface visual, painel de filas e consumo dinâmico da API.
- **Flexibilidade de Ingestão:** O sistema aceita dados via Formulário estruturado, Upload de `.docx`/`.txt` ou Texto Livre (Copy/Paste).

---

## 👥 Divisão de Tarefas (Atualizada)

### 🧑‍💻 Integrante 1: Backend, Arquitetura e Engenharia de Dados
**Responsável por:** [Seu Nome - Dimitri]
**Status:** ✅ Concluído / Em Manutenção
**O que foi entregue:**
1. **Motor MTM & PO:** Cálculo automatizado do Tempo FIXO e Elementos MTM.
2. **Exportação Automática:** Geração da Ficha PO (`.xlsx`) formatada idêntica ao gabarito (`PO-SL-000`).
3. **Múltiplas Ingestões:** Leitura e extração de dados diretos de arquivos de texto e `.docx` (Ordem de Produção).
4. **Sistema de Balanceamento:** Rotas completas para gerenciar filas de produção (K tasks), incluindo arquivamento de tarefas concluídas/falhas com recálculo de tempos.
5. **Automação de Setup:** Script `iniciar.bat` pronto para a banca testar com 1 clique.

### 🧑‍💻 Integrante 2: Frontend e Painel de Produção (UI/UX)
**Responsável por:** [Nome do Integrante 2]
**Status:** 🚧 Em Andamento
**Objetivo:** Consumir a API robusta que já está no ar e criar uma interface amigável.
**Tarefas urgentes:**
1. Criar a tela de ingestão permitindo ao usuário escolher como enviar a demanda (Ex: Botão de Upload de Arquivo consumindo `/api/calcular-demanda` OU Caixa de Texto consumindo `/api/calcular-demanda-texto`).
2. Adicionar o botão de **"Download Ficha PO"** que chama a rota `/api/download-po/{titulo_po}` para baixar o `.xlsx` gerado.
3. Criar a aba **Dashboard / Filas**, consumindo `/api/filas` para gerar gráficos visuais de qual máquina está mais sobrecarregada (Balanceamento).

### 🧑‍💻 Integrante 3: Qualidade (QA), Documentação e Pitch (O "Closer")
**Responsável por:** [Nome do Integrante 3]
**Status:** 🚧 Em Andamento
**Objetivo:** Como o Backend absorveu a exportação, este integrante foca 100% em garantir os 25 pontos do Pitch e o polimento da entrega.
**Tarefas urgentes:**
1. **Roteiro do Pitch (5 min):** Criar a narrativa da apresentação. Focar no diferencial da equipe (múltiplas formas de inserir dados + balanceamento visual de fila de máquinas).
2. **Testes de Ponta a Ponta:** Testar exaustivamente o software com os dados de exemplo (`demanda_000.docx` e `Entradas.xlsx`), garantindo que não há quebras ao tentar deletar/adicionar itens da fila.
3. **Repositório:** Refinar este README (adicionar prints da tela do frontend assim que prontas) e checar se o repositório público está impecável para a banca (conforme item 5.3 do regulamento).

---

## 📡 Contrato de API (Endpoints Disponíveis para o Frontend)

O Frontend deve se conectar nestas rotas (rode o `iniciar.bat` e acesse `http://127.0.0.1:8000/docs` para testar):

| Rota HTTP | Método | Função |
| :--- | :---: | :--- |
| `/api/bases` | `GET` | Retorna as opções de máquinas e elementos (Ideal para preencher *Selects/Dropdowns* no Front). |
| `/api/calcular-demanda` | `POST` | Envio de arquivo físico (`.docx` ou `.txt`) via `multipart/form-data`. Calcula a PO e salva Excel. |
| `/api/calcular-demanda-texto` | `POST` | Envio do texto da demanda colado direto em `text/plain`. Calcula a PO e salva Excel. |
| `/api/download-po/{titulo_po}` | `GET` | Baixa o arquivo `.xlsx` gerado. |
| `/api/filas` | `GET` | Retorna o resumo de tasks de cada máquina para montar os gráficos de produtividade. |
| `/api/filas/{codigo}/tasks/{indice}` | `DELETE` | Remove uma tarefa da fila informando um motivo (ex: "Concluido", "Falhou") no JSON. |
| `/api/filas` | `DELETE` | Zera a fila de todas as máquinas (botão de "Reset/Fim de Expediente"). |
