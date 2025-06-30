from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
from curses_calendar import curses_main as curses_calendar_main
from curses_prompt import curses_main as curses_prompt_main
import curses
import pickle
import argparse
import pathlib

# Se modificarmos as SCOPES, deletar o arquivo token.pickle.
SCOPES = ["https://www.googleapis.com/auth/calendar"]
SCRIPT_DIR = pathlib.Path.home().joinpath(".create_google_calendar_events")
SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
TOKEN_FILE = SCRIPT_DIR.joinpath("token.pickle")
CREDENTIALS_FILE = SCRIPT_DIR.joinpath("credentials.json")


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


def length_limited(limit, argname):
    def checker(value):
        if len(value) > limit:
            raise argparse.ArgumentTypeError(
                f"O argumento `{argname}` deve ter no máximo {limit} caracteres."
            )
        return value

    return checker


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
        help="Número do mês (1-12). Por padrão, o mês atual é usado. Corresponde ao mês inicial do widget de calendário, caso usado.",
    )

    parser.add_argument(
        "-y",
        "--year",
        type=valid_year,
        default=datetime.now().year,
        metavar="YYYY",
        help="Ano (1990-2999), Por padrão, o ano atual é usado. Corresponde ao ano inicial do widget de calendário, caso usado.",
    )

    parser.add_argument(
        "-n",
        "--name",
        type=length_limited(37, "name"),
        default="",
        help="Nome dos eventos. Caso não seja informado, um prompt em curses será exibido para digitar o nome desejado.",
    )

    parser.add_argument(
        "-c",
        "--calendar",
        type=length_limited(37, "calendar"),
        default="",
        help="Nome da agenda do Google Calendar na qual os eventos serão criados. Caso não seja informado, um prompt em curses será exibido para digitar o calendário desejado.",
    )

    return parser.parse_args()


def get_credentials_from_browser_login():
    """Abre um navegador para autenticação do usuário e obtém as credenciais."""
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(TOKEN_FILE, "wb") as token:
        pickle.dump(creds, token)

    return creds


def get_credentials():
    """Obtém credenciais do usuário."""
    creds = None

    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print("Erro no refresh do token de acesso.")
            print("Excluíndo token.pickle para nova autenticação.")
            TOKEN_FILE.unlink(missing_ok=True)

    return get_credentials_from_browser_login()


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

    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    if "" in (event_name, calendar_name):
        event_name, calendar_name = curses.wrapper(
            curses_prompt_main, event_name, calendar_name
        )

    if "" in (event_name, calendar_name):
        print("Nome do evento e nome da agenda são obrigatórios.")
        print("Tente novamente.")
        return

    days = args.days
    dates = sorted(f"{args.year}-{args.month:02d}-{day:02d}" for day in days)

    if len(dates) == 0:
        dates = curses.wrapper(
            curses_calendar_main,
            init_year=args.year,
            init_month=args.month,
        )

    if len(dates) == 0:
        print("Nenhum dia foi selecionado.")
        print("Tente novamente.")
        return

    calendar_id = get_calendar_id(service, calendar_name)

    if not calendar_id:
        print(f"Agenda `{calendar_name}` não encontrada.")
        print("Cheque as agendas existentes no Google Calendar e tente novamente.")
        return

    for date in dates:
        event = {
            "summary": event_name,
            "start": {"date": date},
            "end": {"date": date},
        }

        event = service.events().insert(calendarId=calendar_id, body=event).execute()

        print("Evento criado:")
        print(f"  Nome: {event.get('summary')}")
        print(f"  Data: {event.get('start').get('date')}")
        print(f"  Link: {event.get('htmlLink')}")
        print()


if __name__ == "__main__":
    main()
