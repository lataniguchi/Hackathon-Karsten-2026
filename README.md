# 🚀 Hackathon Auto-T&M Karsten - Contrato de Desenvolvimento da Equipe

Este documento define a arquitetura do projeto e as responsabilidades de cada integrante para a reta final do hackathon. O Backend já está estruturado, modularizado e com as regras de negócio finalizadas. 

**Status:** integração do Frontend concluída; pronto para demonstração e validação.

## 🏗️ Arquitetura do Sistema (Desacoplada)
- **Backend (Finalizado):** FastAPI (Python) estruturado em Domain-Driven Design (pacote `services/`). Validação de dados via Pydantic e geração nativa de planilhas `.xlsx` via `openpyxl`.
- **Frontend (Concluído):** painel HTML/JavaScript em `Frontend/index.html`, responsável pela ingestão de demandas, acompanhamento das filas e consumo da API.
- **Flexibilidade de Ingestão:** aceita arquivos `.docx`, `.txt` e `.json`, além de preenchimento manual dos campos da demanda. O JSON usa o formato `{"texto": "..."}`.

---

## 👥 Divisão de Tarefas (Atualizada)

### 🧑‍💻 Integrante 1: Backend, Arquitetura e Engenharia de Dados
**Responsável por:** Dimitri Maia
**Status:** ✅ Concluído / Em Manutenção
**O que foi entregue:**
1. **Motor MTM & PO:** Cálculo automatizado do Tempo FIXO e Elementos MTM.
2. **Exportação Automática:** Geração da Ficha PO (`.xlsx`) formatada idêntica ao gabarito (`PO-SL-000`).
3. **Múltiplas Ingestões:** Leitura e extração de dados diretos de arquivos de texto e `.docx` (Ordem de Produção).
4. **Sistema de Balanceamento:** Rotas completas para gerenciar filas de produção (K tasks), incluindo arquivamento de tarefas concluídas/falhas com recálculo de tempos.
5. **Automação de Setup:** Script `iniciar.bat` pronto para a banca testar com 1 clique.

### 🧑‍💻 Integrante 2: Frontend e Painel de Produção (UI/UX)
**Responsável por:** Laís Aya
**Status:** ✅ Concluído
**O que foi entregue:**
1. **Ingestão de demandas:** upload de `.docx` e `.txt`, envio de `.json` para a rota JSON da API e formulário manual com campos específicos.
2. **Ficha PO:** exibição do resultado do cálculo e download da planilha `.xlsx` gerada.
3. **Dashboard de produção:** KPIs, gráfico de carga por máquina em minutos e listagem das tasks ativas com ações para concluir ou excluir.
4. **Gestão de filas:** exclusão com seleção de motivo, confirmação antes de concluir ou resetar todas as filas.
5. **Histórico:** listagem de arquivos concluídos, falhos, em reavaliação e excluídos, com opção de restauração e escolha sobre recolocar a task na fila.

### Integrante 3: Qualidade (QA), Testes e Validação
**Responsável por:** Silas Torres
**Status:** ✅ Concluído / Em Manutenção
**O que foi entregue:**
1. **Suíte de Testes Automatizados:** Bateria de testes cobrindo leitura de bases, cálculo do Tempo FIXO, elementos MTM, tempo total TP e exportação física de planilhas.
2. **Validação das Rotas da API:** Testes de integração cobrindo consulta de bases, ingestão de texto/arquivo, balanceamento de fila e deleção de tarefas com motivo.
3. **Automação de Execução:** Script `testes/rodar_testes.bat` para execução local em 1 clique com métricas de tempo e registro persistente em `testes/historico.txt`.
4. **Compatibilidade Multiplataforma:** Validação e correção de tipagens para garantir funcionamento estável em versões do Python a partir da 3.10.

---

### Como Rodar os Testes Automatizados

Para validar todo o sistema localmente em menos de 1 segundo:

1. Dê um duplo clique no arquivo **`testes/rodar_testes.bat`** (ou execute `python testes/executar_testes.py`).
2. O script validará o motor de cálculo e as rotas da API, gravando as métricas em `testes/historico.txt`.

---

## 📡 Contrato de API (Endpoints Disponíveis para o Frontend)

O Frontend deve se conectar nestas rotas (rode o `iniciar.bat` e acesse `http://127.0.0.1:8000/docs` para testar):

| Rota HTTP | Método | Função |
| :--- | :---: | :--- |
| `/api/bases` | `GET` | Retorna as opções de máquinas e elementos (Ideal para preencher *Selects/Dropdowns* no Front). |
| `/api/calcular-demanda` | `POST` | Envio de arquivo físico (`.docx` ou `.txt`) via `multipart/form-data`. Calcula a PO e salva Excel. |
| `/api/calcular-demanda-texto` | `POST` | Envio do texto da demanda colado direto em `text/plain`. Calcula a PO e salva Excel. |
| `/api/calcular-demanda-json-texto` | `POST` | Envio de JSON no formato `{"texto": "..."}`. Calcula a PO e salva Excel. |
| `/api/download-po/{titulo_po}` | `GET` | Baixa o arquivo `.xlsx` gerado. |
| `/api/filas` | `GET` | Retorna o resumo de tasks de cada máquina para montar os gráficos de produtividade. |
| `/api/filas/{codigo_maquina}/tasks` | `GET` | Lista as tasks atuais de uma máquina. |
| `/api/filas/{codigo}/tasks/{indice}` | `DELETE` | Remove uma tarefa da fila informando um motivo (ex: "Concluido", "Falhou") no JSON. |
| `/api/filas` | `DELETE` | Zera a fila de todas as máquinas (botão de "Reset/Fim de Expediente"). |
| `/api/arquivos-arquivados` | `GET` | Lista arquivos de demandas concluídas, falhas, reavaliações e exclusões. |
| `/api/arquivos-arquivados/{categoria}/{nome_arquivo}/restaurar` | `POST` | Restaura um arquivo e aceita `{"recolocar_na_fila": true/false}`. |
