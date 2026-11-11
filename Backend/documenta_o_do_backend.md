# ⚙️ Backend API - Auto-T&M Karsten

Este é o repositório do **Backend** para o projeto Auto-T&M do Hackathon Karsten. A API foi construída com **FastAPI** e adota uma arquitetura modular para garantir escalabilidade, leitura rápida de dados estáticos e geração precisa da Ficha PO.

## 🚀 Como Iniciar o Servidor (Para testes locais)

Esqueça comandos complexos no terminal. Para rodar a API, basta seguir 2 passos:

1. Dê um duplo clique no arquivo **`iniciar.bat`**.

2. Ele instalará todas as dependências necessárias automaticamente e subirá o servidor.

3. Acesse o painel interativo (Swagger) no seu navegador:
   👉 **http://127.0.0.1:8000/docs**

> **Aviso para o Integrante 2 (Frontend):** O CORS já está configurado para aceitar requisições de qualquer origem (`allow_origins=["*"]`). Você pode conectar seu React/Streamlit/HTML sem problemas de bloqueio!

## 📂 Estrutura de Pastas e Arquivos

O projeto utiliza uma arquitetura baseada em serviços (DDD - Domain-Driven Design) para separar as responsabilidades:

```
📦 raiz
 ┣ 📂 dados/                # Coloque aqui o Entradas.xlsx e os .docx de teste
 ┣ 📂 saida_po/             # Onde as planilhas PO (.xlsx) geradas serão salvas
 ┣ 📂 services/             # Regras de negócio divididas por domínio
 ┃ ┣ 📜 bases/              # Leitura e cache da planilha Entradas.xlsx
 ┃ ┣ 📜 demanda/            # Extração de dados do .docx / .txt
 ┃ ┣ 📜 fila/               # Lógica de enfileiramento e deleção de tasks
 ┃ ┣ 📜 po/                 # Motor de cálculo e exportação do Excel
 ┃ ┣ 📜 config.py           # Caminhos absolutos do projeto
 ┃ ┣ 📜 state.py            # Variáveis globais (Cache em RAM)
 ┃ ┗ 📜 types.py            # Tipagens do Python (para evitar bugs)
 ┣ 📜 core.py               # (Legado) Exporta as funções para compatibilidade
 ┣ 📜 iniciar.bat           # Script de automação de inicialização
 ┣ 📜 main.py               # 🔀 ROTAS DA API FASTAPI (Onde a mágica da web acontece)
 ┣ 📜 requirements.txt      # Dependências do Python
 ┗ 📜 schemas.py            # Validação de dados de entrada e saída (Pydantic)

```

## 📡 Rotas da API (Guia para o Frontend)

Todas as requisições devem ser feitas para `http://127.0.0.1:8000`.

### 1. Ingestão de Demanda e Cálculo

A API aceita 3 formas diferentes de processar a demanda, garantindo flexibilidade total. Todas elas calculam o MTM, geram o Excel e colocam a task na fila.

* **`POST /api/calcular-demanda`**

  * **Uso:** Upload direto de arquivo.

  * **Body:** `multipart/form-data` contendo o arquivo (campo `arquivo`).

  * **Ideal para:** Um botão `<input type="file">` no Front.

  * **Arquivos TXT:** Aceita texto de demanda simples, JSON no formato `{"texto": "Título: ..."}` ou JSON com os campos da demanda (`titulo_po`, `produto`, `cod_eqp`, `elementos`, etc.).

* **`POST /api/calcular-demanda-texto`**

  * **Uso:** Envio de texto puro colado.

  * **Body:** `text/plain` (string crua).

  * **Ideal para:** Testes rápidos direto no Swagger (`/docs`).

* **`POST /api/calcular-demanda-json-texto`**

  * **Uso:** Envio de texto em formato JSON estruturado.

  * **Body:** `{"texto": "Título: PO-SL-001\nREV: 00..."}`

  * **Ideal para:** Uma caixa de texto (`<textarea>`) no Frontend enviando via `fetch` ou `axios`.

  * **Compatibilidade:** Também aceita o conteúdo como string JSON ou no campo `texto_demanda`. Para evitar `422`, envie `Content-Type: application/json` e um dos formatos aceitos.

### 2. Download do Resultado

* **`GET /api/download-po/{titulo_po}`**

  * **Uso:** Baixar a Ficha PO gerada.

  * **Parâmetro URL:** O nome do arquivo salvo (Ex: `PO-SL-001`). O ".xlsx" é opcional.

  * **Retorno:** Retorna o arquivo binário (Download forçado no navegador).

### 3. Painel e Filas (Balanceamento)

* **`GET /api/bases`**

  * **Uso:** Puxar os dados de `Entradas.xlsx` para preencher tabelas ou menus suspensos (Dropdowns) de máquinas e roteiros no Frontend.

* **`GET /api/filas`**

  * **Uso:** Retorna o status atual das filas (Tasks e Tempos Acumulados) de todas as máquinas.

  * **Ideal para:** Gerar os gráficos visuais de produtividade/gargalo.

* **`DELETE /api/filas/{codigo_maquina}/tasks/{indice}`**

  * **Uso:** Remove uma task específica da fila e arquiva o Excel dela.

  * **Parâmetros URL:** `codigo_maquina` (ex: 1) e `indice` da task (começa em 1).

  * **Body (JSON):** `{"motivo": "Concluido"}` (Pode ser Concluido, Falhou, Reavaliacao, etc).

* **`GET /api/arquivos-arquivados`**

  * **Uso:** Lista os arquivos arquivados nas categorias Concluído, Falhou, Reavaliação e Excluído.

  * **Limite:** Retorna os 10 arquivos mais recentes por categoria. Arquivos mais antigos permanecem no disco.

* **`POST /api/arquivos-arquivados/{categoria}/{nome_arquivo}/restaurar`**

  * **Uso:** Move o XLSX arquivado para a pasta principal de saída e acrescenta `_restaurado` ao nome.

  * **Categorias:** `concluido`, `falhou`, `reavaliacao` e `excluido`.

  * **Body (JSON):** `{"recolocar_na_fila": true}` ou `{"recolocar_na_fila": false}`. O cliente deve perguntar ao usuário antes de enviar essa escolha. Quando verdadeiro, a task é reconstruída a partir da planilha e recolocada na fila da máquina.

  * **Observação:** A restauração remove o arquivo da categoria arquivada. Se o nome restaurado já existir, a API retorna conflito sem sobrescrever arquivos.

* **`DELETE /api/filas`**

  * **Uso:** Esvazia as filas de todas as máquinas de uma vez. O "botão vermelho" de fim de turno.

## 🧪 Como testar os Cálculos

Você não precisa digitar tudo manualmente para testar. Você pode enviar a demanda de duas formas:

### Opção A: Formato de Texto Puro (Para arquivos .txt ou rota text/plain)
Use o formato abaixo nas rotas de texto puro ou salve como `.txt`/`.docx` para testar o upload:

```text
Título: PO-SL-001
REV: 00
Operação: "Bainhar no corpo do SL - 1 lado"
Agrupamento família: Sobre-lençol
Tamanho: Solteiro
Medidas da peça (em m): 1,80 x 2,50
Pontos/cm: 2,50
Perímetro costura (em m): 6,96
Cód. Eqp: 1
Elementos: 2.1, 1.1, 3.1
```

### Opção B: Formato JSON (Para a rota /api/calcular-demanda-json-texto)
Se o Frontend for enviar a requisição via `fetch`/`axios` capturando o conteúdo de um campo `<textarea>`, o JSON enviado deve ficar assim (note as quebras de linha `\n`):

```json
{
  "texto": "Título: PO-SL-001\nREV: 00\nOperação: \"Bainhar no corpo do SL - 1 lado\"\nAgrupamento família: Sobre-lençol\nTamanho: Solteiro\nMedidas da peça (em m): 1,80 x 2,50\nPontos/cm: 2,50\nPerímetro costura (em m): 6,96\nCód. Eqp: 1\nElementos: 2.1, 1.1, 3.1"
}
```

O sistema cruzará a string `"2.1"` com os dados do Excel e encontrará a descrição "Apanhar peça e posicionar na mesa" e seu respectivo tempo.