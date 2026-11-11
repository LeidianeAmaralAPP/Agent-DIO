import os
import unicodedata
from datetime import date, datetime, time, timezone

from dotenv import load_dotenv
from google.adk.agents import Agent
from trello import TrelloClient

load_dotenv()

_STATUS_ALIASES = {
    "a fazer": {"a fazer", "to do", "todo"},
    "em andamento": {"em andamento", "doing", "in progress"},
    "concluido": {"concluido", "done", "completed"},
}
_STATUS_LABELS = {
    "a fazer": "A fazer",
    "em andamento": "Em andamento",
    "concluido": "Concluído",
}


def _normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character for character in decomposed
        if not unicodedata.combining(character)
    )
    return " ".join(without_accents.casefold().split())


def _resolve_status(value: str) -> str | None:
    normalized = _normalize_text(value)
    return next(
        (
            status
            for status, aliases in _STATUS_ALIASES.items()
            if normalized in {_normalize_text(alias) for alias in aliases}
        ),
        None,
    )


def _trello_due_date(value: str) -> str:
    try:
        task_date = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise ValueError("Informe a data no formato AAAA-MM-DD.") from error

    due_at_noon_utc = datetime.combine(
        task_date,
        time(hour=12),
        tzinfo=timezone.utc,
    )
    return due_at_noon_utc.isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def _get_trello_client() -> TrelloClient:
    api_key = os.getenv("TRELLO_API_KEY")
    api_secret = os.getenv("TRELLO_API_SECRET")
    token = os.getenv("TRELLO_TOKEN")
    if not api_key or not api_secret or not token:
        raise ValueError(
            "Preencha TRELLO_API_KEY, TRELLO_API_SECRET e TRELLO_TOKEN no .env."
        )

    return TrelloClient(
        api_key=api_key,
        api_secret=api_secret,
        token=token,
    )


def _get_board_and_lists():
    client = _get_trello_client()
    board_name = os.getenv("TRELLO_BOARD_NAME", "DIO").strip()
    matching_boards = [
        board
        for board in client.list_boards()
        if _normalize_text(board.name) == _normalize_text(board_name)
    ]

    if not matching_boards:
        raise ValueError(
            f"Quadro '{board_name}' não encontrado. "
            "Confira TRELLO_BOARD_NAME no arquivo .env."
        )
    if len(matching_boards) > 1:
        raise ValueError(
            f"Mais de um quadro tem o nome '{board_name}'. "
            "Defina um nome único para o quadro."
        )

    board = matching_boards[0]
    return board, board.list_lists()


def _list_for_status(lists, status: str):
    return next(
        (
            trello_list
            for trello_list in lists
            if _resolve_status(trello_list.name) == status
        ),
        None,
    )


def get_temporal_context() -> str:
    """Retorna a data local de hoje no formato AAAA-MM-DD."""
    return date.today().isoformat()


def adicionar_tarefa(
    nome_da_task: str,
    descricao_da_task: str,
    due_date: str | None = None,
) -> dict[str, str]:
    """Cria um card com nome e descrição não vazios; sem due_date, usa hoje."""
    if not nome_da_task.strip():
        return {"erro": "O nome da tarefa não pode ficar vazio."}
    if not descricao_da_task.strip():
        return {
            "erro": (
                "A descrição da tarefa não pode ficar vazia. "
                "Pergunte uma descrição antes de criar o card."
            )
        }

    task_date = (
        due_date.strip()
        if due_date and due_date.strip()
        else get_temporal_context()
    )
    try:
        trello_due = _trello_due_date(task_date)
    except ValueError as error:
        return {"erro": str(error)}

    board, lists = _get_board_and_lists()
    todo_list = _list_for_status(lists, "a fazer")
    if todo_list is None:
        return {
            "erro": "Não encontrei a lista 'A fazer' (ou 'To Do') no quadro."
        }

    card = todo_list.add_card(
        name=nome_da_task.strip(),
        desc=descricao_da_task.strip(),
        due=trello_due,
    )
    return {
        "resultado": "sucesso",
        "nome": card.name,
        "lista": todo_list.name,
        "vencimento": task_date,
        "quadro": board.name,
    }


def listar_tarefas(status: str = "todas") -> dict[str, object]:
    """Lista todos os cards ou filtra por A fazer, Em andamento ou Concluído."""
    normalized_status = _normalize_text(status)
    all_statuses = {"todas", "todos", "all"}
    resolved_status = _resolve_status(status)

    if normalized_status not in all_statuses and resolved_status is None:
        return {
            "erro": (
                "Status inválido. Use 'todas', 'A fazer', "
                "'Em andamento' ou 'Concluído'."
            )
        }

    board, lists = _get_board_and_lists()
    selected_lists = (
        lists
        if normalized_status in all_statuses
        else [
            trello_list
            for trello_list in lists
            if _resolve_status(trello_list.name) == resolved_status
        ]
    )

    tasks = []
    for trello_list in selected_lists:
        for card in trello_list.list_cards():
            tasks.append(
                {
                    "nome": card.name,
                    "descricao": card.desc or "",
                    "vencimento": card.due or None,
                    "status": trello_list.name,
                    "url": card.url,
                }
            )
    return {"quadro": board.name, "tarefas": tasks}


def mudar_status_tarefa(nome_da_task: str, novo_status: str) -> dict[str, str]:
    """Move um card para A fazer, Em andamento ou Concluído."""
    if not nome_da_task.strip():
        return {"erro": "Informe o nome do card que deseja mover."}

    target_status = _resolve_status(novo_status)
    if target_status is None:
        return {
            "erro": (
                "Status inválido. Use 'A fazer', 'Em andamento' "
                "ou 'Concluído'."
            )
        }

    board, lists = _get_board_and_lists()
    destination = _list_for_status(lists, target_status)
    if destination is None:
        return {
            "erro": (
                f"Não encontrei a lista '{_STATUS_LABELS[target_status]}' "
                f"no quadro '{board.name}'."
            )
        }

    normalized_name = _normalize_text(nome_da_task)
    matching_cards = [
        (trello_list, card)
        for trello_list in lists
        for card in trello_list.list_cards()
        if _normalize_text(card.name) == normalized_name
    ]
    if not matching_cards:
        return {"erro": f"Não encontrei o card '{nome_da_task}'."}
    if len(matching_cards) > 1:
        return {
            "erro": (
                f"Há mais de um card chamado '{nome_da_task}'. "
                "Renomeie os cards para diferenciá-los."
            )
        }

    source, card = matching_cards[0]
    card.change_list(destination.id)
    return {
        "resultado": "sucesso",
        "nome": card.name,
        "origem": source.name,
        "destino": destination.name,
        "quadro": board.name,
    }


root_agent = Agent(
    model="gemini-2.5-flash",
    name="agente_organizador_de_tarefas",
    description="Organiza as tarefas do dia em um quadro do Trello.",
    instruction="""
Você organiza tarefas do dia no quadro do Trello configurado.

No início da conversa, use get_temporal_context e pergunte quais são as
tarefas de hoje, informando a data retornada. Para cada tarefa informada,
identifique um nome e uma descrição não vazia. O nome pode ser o resumo curto
da tarefa; não invente detalhes para preencher a descrição. Se o nome ou a
descrição estiverem ausentes ou pouco claros, pergunte apenas o dado que falta
e espere a resposta antes de criar o card. Use o vencimento de hoje, retornado
por get_temporal_context, salvo quando a pessoa indicar outra data. Depois de
criar as tarefas recebidas, pergunte se há mais alguma; pare quando a pessoa
disser que não.

Use listar_tarefas quando pedirem para ver tarefas, aplicando o status
solicitado quando houver. Use mudar_status_tarefa para mover cards conforme
a pessoa relatar o progresso. Aceite variações de status com ou sem acentos.
Informe resultados e erros exatamente como retornados pelas ferramentas;
nunca diga que uma alteração ocorreu se a ferramenta não confirmou.
""",
    tools=[
        get_temporal_context,
        adicionar_tarefa,
        listar_tarefas,
        mudar_status_tarefa,
    ],
)
