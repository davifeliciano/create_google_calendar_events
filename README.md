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

```bash
$ python create_google_calendar_events.py --help
usage: create_google_calendar_events.py [-h] [-d DD [DD ...]] [-m MM] [-y YYYY] [-n NAME]
                                        [-c CALENDAR]

Cria eventos de dia inteiro no Google Calendar em uma agenda específica nos dias do mês e ano
informados.

options:
  -h, --help            show this help message and exit
  -d DD [DD ...], --days DD [DD ...]
                        Dias do mês separados por espaços. Caso não sejam informados, um widget de
                        calendário em curses será exibido para selecionar os dias.
  -m MM, --month MM     Número do mês (1-12). Por padrão, o mês atual é usado. Corresponde ao mês
                        inicial do widget de calendário, caso usado.
  -y YYYY, --year YYYY  Ano (1990-2999), Por padrão, o ano atual é usado. Corresponde ao ano inicial
                        do widget de calendário, caso usado.
  -n NAME, --name NAME  Nome dos eventos. Caso não seja informado, um prompt em curses será exibido
                        para digitar o nome desejado.
  -c CALENDAR, --calendar CALENDAR
                        Nome da agenda do Google Calendar na qual os eventos serão criados. Caso não
                        seja informado, um prompt em curses será exibido para digitar o calendário
                        desejado.
```

Para gerar um executável em `./dist/` com nome customizado:

```bash
pyinstaller --onefile create_google_calendar_events.py -n batch_create_gc_events
```
