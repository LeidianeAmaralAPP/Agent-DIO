# 🤖 Trello Task Agent — DIO & Google ADK

Projeto desenvolvido como parte do desafio da **Digital Innovation One
(DIO)**: um agente de produtividade em Python que usa o **Google Agent
Development Kit (ADK)** e a API do **Gemini** para organizar tarefas diárias
no **Trello** por meio de uma conversa.

## 🚀 Funcionalidades

- **Boas-vindas inteligentes:** inicia a conversa perguntando as tarefas do
  dia e informa a data atual.
- **Criar cards:** adiciona tarefas com nome, descrição e data de entrega.
- **Listar tarefas:** exibe todos os cards ou filtra por status — *A fazer*,
  *Em andamento* ou *Concluído*.
- **Mover tarefas:** atualiza a lista do card conforme o progresso informado
  na conversa.

### 🧰 Ferramentas do agente

As ferramentas estão implementadas em [`agenttaskmanager/agent.py`](./agenttaskmanager/agent.py):

| Ferramenta | O que faz |
| --- | --- |
| `get_temporal_context` | Informa a data atual. |
| `adicionar_tarefa` | Cria um card na lista **A fazer**. |
| `listar_tarefas` | Lista os cards ou filtra por status. |
| `mudar_status_tarefa` | Move um card para outra lista. |

## 🛠️ Tecnologias

- **Python 3.10+**
- **Google ADK** e **Gemini API**
- **py-trello** para integração com o Trello
- **python-dotenv** para carregar variáveis de ambiente

## 📋 Pré-requisitos

- Python 3.10 ou superior.
- Uma chave de API do [Google AI Studio](https://aistudio.google.com/apikey).
- Um quadro do Trello e credenciais da API.

## 🔐 Configurar o Trello

1. Crie um quadro com as listas **A fazer**, **Em andamento** e
   **Concluído**. O agente também reconhece `To Do`/`Todo`,
   `Doing`/`In Progress` e `Done`/`Completed`.
2. Registre um Power-Up em <https://trello.com/power-ups/admin/> e obtenha a
   API Key e o Secret.
3. Gere um token com permissões de leitura e escrita. Consulte o
   [guia de configuração do Trello](https://github.com/digitalinnovationone/agent-carbon-footprint/blob/main/agents/agent04/readme.md).

## ⚙️ Instalação e execução

No PowerShell, na pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.exemplo .env
```

Edite o arquivo `.env` e preencha as credenciais:

```env
GOOGLE_API_KEY=sua-chave-do-google-ai-studio
TRELLO_API_KEY=sua-chave-do-trello
TRELLO_API_SECRET=seu-segredo-do-trello
TRELLO_TOKEN=seu-token-do-trello
TRELLO_BOARD_NAME=DIO
```

`TRELLO_BOARD_NAME` deve corresponder ao nome do seu quadro. O valor padrão é
`DIO`.

Inicie a interface de desenvolvimento:

```powershell
adk web
```

Abra o endereço exibido no terminal e selecione o agente `agenttaskmanager`.

## ✨ Melhorias implementadas

- **Status mais flexíveis:** reconhece variações com ou sem acento,
  diferenças entre maiúsculas e minúsculas e sinônimos em português e inglês.
  Por exemplo, `concluído`, `concluido`, `done` e `completed` correspondem ao
  status de conclusão. Status inválidos são informados em vez de retornar
  todas as tarefas sem aviso.
- **Data de entrega:** envia o vencimento ao Trello como meio-dia UTC para
  reduzir o risco de o fuso horário exibir o card com um dia de diferença.
- **Conexão centralizada:** valida as credenciais e reutiliza uma função
  comum para conectar ao Trello e localizar o quadro configurado.
- **Criação com dados completos:** exige nome e descrição não vazios. Se faltar
  um deles ou não estiver claro, o agente pergunta antes de tentar criar o
  card. Quando a pessoa não indica outra data, usa a data de hoje.

## ✅ Como testar

Primeiro, verifique a sintaxe do agente:

```powershell
python -m compileall -q agenttaskmanager
```

Depois, configure as credenciais e teste pelo `adk web`:

1. Informe uma tarefa sem descrição e confira se o agente pergunta o que deve
   registrar antes de criar o card. Responda com a descrição e confirme que o
   card aparece em **A fazer** com vencimento.
2. Peça para listar as tarefas e filtre por `concluído`.
3. Relate que concluiu uma tarefa e confirme se o card foi movido para
   **Concluído**.
4. Repita o filtro com `concluido` sem acento e compare o resultado.

## 🔒 Segurança

- O arquivo `.env` está no `.gitignore`; mantenha nele suas credenciais reais.
- Não publique nem compartilhe sua chave do Google, API Key, Secret ou token
  do Trello.
- Se seu quadro tiver cards com nomes iguais, o agente informa a ambiguidade
  em vez de mover um card sem confirmação.
