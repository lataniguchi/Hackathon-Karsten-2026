## REGULAMENTO OFICIAL DO HACKATHON: AUTO-T&M KARSTEN

Desafio de Automação de Tempos e Métodos na Indústria Têxtil

## 1. DO OBJETIVO E DO DESAFIO

- 1.1. O Hackathon Auto-T&M Karsten é uma competição de inovação e desenvolvimento de software promovida pela [Nome da Instituição de Ensino] em parceria com a Karsten S.A.

- 1.2. O desafio consiste em criar uma solução computacional (sistema web, desktop ou aplicação em nuvem) capaz de automatizar o processo de formação de tempos operacionais da Engenharia de Tempos e Métodos (T&M). O software deve consumir cadastros de apoio (Elementos MTM e Máquinas), processar os parâmetros do produto e a sequência de operações, e gerar automaticamente a ficha padronizada de Processo Operacional (PO).

## 2. DA ELEGIBILIDADE E DAS EQUIPES E INSCRIÇÕES

- 2.1. Poderão participar estudantes regularmente matriculados nos cursos de Engenharia de Computação, Ciência da Computação, Engenharia de Software, Sistemas de Informação e áreas correlatas.

- 2.2. As equipes deverão ser compostas por no mínimo 2 (dois) e no máximo 5 (cinco) integrantes.

## 3. ESTRUTURA DE DADOS E KITS DE ENTRADA E SAÍDA

Para fins de desenvolvimento e validação durante o evento, a organização fornecerá um Kit

de Apoio do Desafio composto por:

- 3.1. Cadastros de Apoio (Base Estática do Sistema)

Uma planilha de referência contendo duas abas principais:

- Aba MATRIZ DE ELEMENTOS (MTM): Catálogo contendo 6 procedimentos operacionais padrão (Código MTM, Descrição do Elemento e Tempo Unitário em minutos).


- Aba TEMPO-CM (Máquinas): Cadastro técnico contendo 3 máquinas de costura (Código da Máquina, Descrição/Modelo, RPM Padrão e Fator de Tempo por Metro em min/m).

## 3.2. Dados de Entrada da Operação

Parâmetros de teste representando o produto a ser roteirizado:

- Dados do Produto: Nome da Peça (ex: Sobre-lençol Solteiro), Perímetro/Comprimento de Costura (em metros) e Densidade de Pontos (Pontos/cm).

- Equipamento: Código da máquina selecionada para a operação.

- Roteiro de Operações: Sequência ordenada dos códigos MTM a serem executados (ex: 2.1, 1.1, 3.1).

Nota sobre o meio de entrada: A forma de envio ou captura dos dados de

entrada fica a critério da equipe (pode ser realizada via interface gráfica interativa, formulário web, upload de arquivo Excel, CSV, JSON ou texto).

## 3.3. Exemplo de Saída Esperada (Planilha PO)

Um modelo gabarito da ficha de Processo Operacional (PO) consolidada, contendo:

- Cabeçalho de identificação do produto e equipamento.

- fórmula:Tempo FIXO (min) = Perímetro de Costura (m) * Tempo/Metro da Máquina Elemento FIXO (Costura de Máquina): Tempo calculado automaticamente via

- Elementos Manuais: Descrições e tempos consultados automaticamente no banco MTM para cada código informado.

- Tempo Total da Operação ( 𝑇𝑃): Somatório automático de todos os elementos (FIXO + MTM).

## 4. REQUISITOS DA SOLUÇÃO (ESCOPO DO DESAFIO)

- 1. Modelagem/Carga de Dados: Módulo para cadastrar ou ler as tabelas de apoio (Catálogo MTM e Máquinas).

- 2. Motor de Cálculo T&M: Lógica automática para calcular o tempo do elemento FIXO e somar os tempos dos procedimentos MTM selecionados.

- 3. Geração e Exportação da Ficha PO: Capacidade de exibir em tela e exportar a ficha final formatada do Processo Operacional (PO) nos moldes do exemplo fornecido.


## 5. DA DINÂMICA DO EVENTO E ENTREGÁVEIS

- 5.1. O Hackathon terá início em 03/11/2026 às 13:00 e fim em 11/11/2026 às 14:00.

- 5.2. Dados de exemplo podem ser encontrados no link: dados_hackat [URL 🔗](https://drive.google.com/drive/folders/1Cufkkll0jnr135UQmd7J9kRjrHPdgVRw?usp=sharing)

- 5.3. Ao final da competição, cada equipe deverá entregar:

- Link do repositório público do código-fonte (GitHub/GitLab) contendo arquivo README.md com instruções claras de instalação e execução.

- Demonstração prática do software rodando o cenário de teste oficial do evento perante a banca examinadora (Pitch de 5 minutos + 3 minutos de arguição).

## 6. CRITÉRIOS DE AVALIAÇÃO

A banca examinadora avaliará as entregas com base na seguinte pontuação (Total: 100

pontos):

| Critério | Descrição | Pontuação |
| --- | --- | --- |
| Aderência Funcional e | Execução correta dos cálculos | 35 pts |
| Precisão | (Tempo FIXO e Total), |   |
|   | integridade na geração da ficha |   |
|   | PO com base no gabarito oficial. |   |
| Arquitetura e Qualidade do | Organização do código, | 20 pts |
| Código | estrutura dos dados, |   |
|   | usabilidade/interface do |   |
|   | software e facilidade de |   |
|   | operação. |   |
| Flexibilidade de Ingestão de | Robustez do método escolhido | 20 pts |
| Dados e Criatividade da | para receber os parâmetros do |   |
| solução. | produto e a sequência de |   |
|   | operações. |   |
| Pitch e Apresentação | Clareza na demonstração ao | 25 pts |
|   | vivo e respostas às dúvidas |   |
|   | técnicas da banca. |   |


## 7. PREMIAÇÃO:

Haverá premiação para os 3 (três) primeiros colocados.

## 8. DISPOSIÇÕES GERAIS E PROPRIEDADE INTELECTUAL

7.1. Os direitos autorais e de propriedade intelectual do código-fonte gerado pertencem aos alunos participantes. 7.2. A empresa parceira Karsten S.A. reserva-se o direito de utilizar as ideias e protótipos para fins de avaliação interna, podendo convidar as equipes de destaque para negociação ou

projetos de teste-piloto pós-evento.
