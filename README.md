# create_google_calendar_events

Ferramenta de linha de comando para automatizar a criação de múltiplos eventos
de dia inteiro em uma determinada agenda do Google Calendar, utilizando a API
disponibilizada pelo Google.

## Instalação

A instalação desse projeto foi testada em uma instância do Ubuntu 22.04 LTS via
WSL no Windows 11, com Python 3.12. Para começar, inicialize e ative um ambiente
virtual:

```bash
python -m venv .venv && source .venv/bin/activate
```

Para o fluxo de autenticação é necessário instalar um browser de sua preferência:

```bash
sudo apt update && sudo apt install -y firefox
```

Finalmente, instale as dependências com

```bash
pip install -r requirements.txt
```

## Criando e Configurando Projeto no Google Cloud

Para que a aplicação funcione, é necessário criar credenciais para a API do
Google Calendar. Para isso, siga os passos abaixo:

### Crie um projeto no Google Cloud Console e Habilitando a Google Calendar API

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Faça login com sua conta do Google.
3. Crie um novo projeto ou selecione um projeto existente.
4. No menu lateral, vá para `APIs e serviços` > `Painel`. Clique em `+ ATIVAR APIS E SERVIÇOS`.
5. Pesquise por `Google Calendar API` e habilite-a.

### Crie as Credenciais para o Aplicativo

1. No menu lateral, vá para `APIs e serviços` > `Credenciais`.
2. Clique em `+ CRIAR CREDENCIAIS` > `ID do cliente OAuth`.
3. Selecione `Aplicativo de Computador` como o tipo de aplicativo.
4. Dê um nome ao seu aplicativo (por exemplo, "Create Google Calendar Events").
5. Clique em `CRIAR` e na tela seguinte, clique em `BAIXAR JSON` para baixar o arquivo com as credenciais criadas.
6. Mova ou copie o arquivo para o diretório da aplicação, renomeando-o para `credentials.json`.

### Configure Usuários de Teste

1. Novamente no menu lateral, vá para `APIs e serviços` > `Credenciais`.
2. Clique no cliente OAuth criado e no menu lateral vá para `Público-alvo`.
3. Na seção `Usuários de Teste`, clique em `+ ADD USERS` e adicione sua conta
   como um usuário de teste. Isso é necessário para aplicações não verificadas.

## Como Utilizar a Ferramenta

No diretório do projeto, com o ambiente virtual ativado:

```bash
$ python create_google_calendar_events.py --help
usage: create_google_calendar_events.py [-h] -d DAYS [DAYS ...] -m MONTH -y YEAR -n NAME -c CALENDAR

Cria eventos de dia inteiro no Google Calendar em uma agenda específica nos dias do mês e ano informados.

options:
  -h, --help            show this help message and exit
  -d DAYS [DAYS ...], --days DAYS [DAYS ...]
                        Dias do mês separados por espaços
  -m MONTH, --month MONTH
                        Número do mês (1-12)
  -y YEAR, --year YEAR  Ano (1990-2999)
  -n NAME, --name NAME  Nome dos eventos
  -c CALENDAR, --calendar CALENDAR
                        Nome da agenda do Google Calendar na qual os eventos serão criados

$ python create_google_calendar_events.py \
         --year 2025 \
         --month 04 \
         --days 01 02 03 10 11 12 \
         --name "Evento de Dia Inteiro" \
         --calendar Trabalho
```
