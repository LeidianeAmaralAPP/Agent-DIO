# Agente organizador de tarefas no Trello

Agente conversacional feito com Google ADK e Gemini para registrar e organizar
as tarefas do dia em um quadro do Trello.

## O que faz

- Começa perguntando quais são as tarefas de hoje e informa a data local.
- Cria um card por tarefa na lista **A fazer**, com descrição e vencimento.
- Lista todos os cards ou filtra por status.
- Move um card para **A fazer**, **Em andamento** ou **Concluído**.

As ferramentas do agente ficam em `agenttaskmanager/agent.py`:

- `get_temporal_context`: fornece a data atual.
- `adicionar_tarefa`: cria cards no Trello.
- `listar_tarefas`: lista e filtra cards.
- `mudar_status_tarefa`: move um card entre listas.

## Pré-requisitos

- Python 3.10 ou superior.
- Uma chave de API do [Google AI Studio](https://aistudio.google.com/apikey).
- Um quadro do Trello e credenciais da API.

## Configuração do Trello

1. Crie um quadro com as listas **A fazer**, **Em andamento** e **Concluído**.
   O agente também reconhece `To Do`/`Todo`, `Doing`/`In Progress` e
   `Done`/`Completed`.
2. Registre um Power-Up em <https://trello.com/power-ups/admin/> e copie a
   API Key e o Secret.
3. Gere um token com permissões de leitura e escrita. O guia de referência
   está em [readme.md do projeto-base](https://github.com/digitalinnovationone/agent-carbon-footprint/blob/main/agents/agent04/readme.md).

## Instalação e execução

No PowerShell, na raiz deste repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.exemplo .env
```

Edite `.env` e preencha `GOOGLE_API_KEY`, `TRELLO_API_KEY`,
`TRELLO_API_SECRET` e `TRELLO_TOKEN`. `TRELLO_BOARD_NAME` deve ser o nome
exato do quadro; o valor padrão é `DIO`.

Com o ambiente virtual ativado, inicie a interface de desenvolvimento:

```powershell
adk web
```

Abra o endereço indicado pelo comando e selecione o agente `agenttaskmanager`.

## Melhoria implementada

A melhoria escolhida foi aceitar variações de status com e sem acento,
maiúsculas/minúsculas e sinônimos em português e inglês. Assim, por exemplo,
`concluído`, `concluido`, `done` e `completed` levam à lista de conclusão.
O agente também aponta status inválidos em vez de mostrar silenciosamente
todas as tarefas.

Para evitar mudança de dia ao enviar vencimentos, a data `AAAA-MM-DD` é
convertida para meio-dia UTC antes de ser enviada ao Trello. O mesmo dia
informado permanece visível no fuso horário local usado normalmente no Brasil.

## Verificação

Para verificar a sintaxe do agente:

```powershell
python -m compileall -q agenttaskmanager
```

Para validar a integração, configure as credenciais e teste no `adk web`:

1. Informe uma tarefa e confira se o card aparece em **A fazer** com descrição
   e vencimento de hoje.
2. Peça a lista de tarefas e depois filtre por `concluído` (com acento).
3. Relate que concluiu a tarefa; confirme que o card foi movido para
   **Concluído**.
4. Repita o filtro usando `concluido` sem acento e confirme que ele retorna a
   mesma lista.

## Segurança e limitações

- As credenciais ficam em `.env`, que está listado no `.gitignore`. Não
  publique esse arquivo nem compartilhe suas chaves e tokens.
- Configure o nome do quadro em `TRELLO_BOARD_NAME` caso não se chame `DIO`.
- O agente usa nomes de cards para movê-los. Se houver cards com nomes iguais,
  ele pede que sejam diferenciados, evitando mover o card errado.
