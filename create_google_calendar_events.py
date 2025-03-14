import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path

# Se modificarmos as SCOPES, deletar o arquivo token.pickle.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
    """Cria eventos de dia inteiro no Google Calendar em uma agenda específica."""
    creds = None

    # O arquivo token.pickle armazena os tokens de acesso e atualização do usuário,
    # e é criado automaticamente quando o fluxo de autorização é concluído pela primeira vez.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # Se não houver credenciais (disponíveis), deixe o usuário logar.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Salve as credenciais para a próxima execução
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)

    # Obtenha o id da agenda "Trabalho"
    calendar_id = get_calendar_id(service, "Trabalho")

    if not calendar_id:
        print('Agenda "Trabalho" não encontrada.')
        return

    # Obtenha argumentos de linha de comando
    dias = [int(dia) for dia in sys.argv[1].split(",")]
    mes = int(sys.argv[2])
    ano = int(sys.argv[3])
    descricao = sys.argv[4]

    for dia in dias:
        # Cria o evento
        event = {
            "summary": descricao,
            "start": {
                "date": f"{ano:04d}-{mes:02d}-{dia:02d}",
            },
            "end": {
                "date": f"{ano:04d}-{mes:02d}-{dia:02d}",
            },
        }

        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f'Evento criado: {event.get("htmlLink")}')


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


if __name__ == "__main__":
    main()
