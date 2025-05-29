from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
from curses_calendar import curses_main as curses_calendar_main
from curses_prompt import curses_main as curses_prompt_main
import curses
import pickle
import os.path
import argparse
import calendar

# Se modificarmos as SCOPES, deletar o arquivo token.pickle.
SCOPES = ["https://www.googleapis.com/auth/calendar"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.pickle")
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, "credentials.json")


def valid_month(value):
    """Valida o valor do mês."""
    month_int = int(value)

    if month_int < 1 or month_int > 12:
        raise argparse.ArgumentTypeError(
            f"{value} não é um mês válido. Deve estar entre 1 e 12."
        )

    return month_int


def valid_year(value):
    """Valida o valor do ano."""
    year_int = int(value)

    if year_int < 1990 or year_int > 2999:
        raise argparse.ArgumentTypeError(
            f"{value} não é um ano válido. Deve estar entre 1990 e 2999."
        )

    return year_int


def parse_args():
    """Analisa os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Cria eventos de dia inteiro no Google Calendar em uma agenda específica nos dias do mês e ano informados."
    )

    parser.add_argument(
        "-d",
        "--days",
        nargs="+",
        type=int,
        default=[],
        metavar="DD",
        help="Dias do mês separados por espaços. Caso não sejam informados, um widget de calendário em curses será exibido para selecionar os dias.",
    )

    parser.add_argument(
        "-m",
        "--month",
        type=valid_month,
        default=datetime.now().month,
        metavar="MM",
        help="Número do mês (1-12)",
    )

    parser.add_argument(
        "-y",
        "--year",
        type=valid_year,
        default=datetime.now().year,
        metavar="YYYY",
        help="Ano (1990-2999)",
    )

    parser.add_argument("-n", "--name", type=str, default="", help="Nome dos eventos")

    parser.add_argument(
        "-c",
        "--calendar",
        type=str,
        default="",
        help="Nome da agenda do Google Calendar na qual os eventos serão criados",
    )

    return parser.parse_args()


def get_credentials():
    """Obtém credenciais do usuário."""
    creds = None

    # O arquivo token.pickle armazena os tokens de acesso e atualização do usuário,
    # e é criado automaticamente quando o fluxo de autorização é concluído pela primeira vez.
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    # Se não houver credenciais (disponíveis), deixe o usuário logar.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Salve as credenciais para a próxima execução
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return creds


def get_calendar_id(service, calendar_name):
    """Obtém o id de uma agenda pelo nome."""
    page_token = None

    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()

        for calendar_list_entry in calendar_list["items"]:
            if calendar_list_entry["summary"] == calendar_name:
                return calendar_list_entry["id"]

        page_token = calendar_list.get("nextPageToken")

        if not page_token:
            break

    return None


def main():
    """Cria eventos de dia inteiro no Google Calendar em uma agenda específica."""
    args = parse_args()

    event_name = args.name
    calendar_name = args.calendar
    days = args.days

    if "" in (event_name, calendar_name):
        event_name, calendar_name = curses.wrapper(
            curses_prompt_main, event_name, calendar_name
        )

    if "" in (event_name, calendar_name):
        print("Nome do evento e nome da agenda são obrigatórios.")
        return

    if len(days) == 0:
        year, month, days = curses.wrapper(
            curses_calendar_main,
            init_year=args.year,
            init_month=args.month,
        )

        days.sort()

    if len(days) == 0:
        print("Nenhum dia selecionado")
        return

    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    calendar_id = get_calendar_id(service, calendar_name)

    if not calendar_id:
        print(f"Agenda `{calendar_name}` não encontrada.")
        return

    for day in days:
        event = {
            "summary": event_name,
            "start": {
                "date": f"{args.year:04d}-{args.month:02d}-{day:02d}",
            },
            "end": {
                "date": f"{args.year:04d}-{args.month:02d}-{day:02d}",
            },
        }

        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f'Evento criado: {event.get("htmlLink")}')


if __name__ == "__main__":
    main()
