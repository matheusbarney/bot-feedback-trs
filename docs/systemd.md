# Systemd do Bot Feedback TRS — explicação simples

## O que é systemd?

`systemd` é o gerenciador de serviços do Linux.

No nosso caso, ele serve para deixar o bot rodando como um serviço do servidor, sem precisar manter um terminal aberto.

Em vez de iniciar o bot manualmente assim:

```bash
cd /root/bot-feedback-trs
./venv/bin/python bot.py
```

criamos um serviço chamado:

```text
bot-feedback.service
```

Aí o Linux fica responsável por:

- iniciar o bot quando o servidor liga;
- reiniciar o bot se ele cair;
- guardar logs;
- permitir parar, iniciar e reiniciar com comandos simples.

## Por que isso é importante?

Sem systemd, o bot só roda enquanto o terminal usado para iniciar o Python continuar aberto.

Com systemd, o bot roda em segundo plano de forma estável.

## Arquivo do serviço

O arquivo do serviço fica aqui:

```text
/etc/systemd/system/bot-feedback.service
```

Conteúdo recomendado:

```ini
[Unit]
Description=Bot Feedback TRS
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/bot-feedback-trs
ExecStart=/root/bot-feedback-trs/venv/bin/python bot.py
EnvironmentFile=/root/bot-feedback-trs/.env
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## O que significa cada linha?

| Linha | Explicação |
|---|---|
| `Description=Bot Feedback TRS` | Nome legível do serviço |
| `After=network-online.target` | Só inicia depois que a internet estiver disponível |
| `WorkingDirectory=/root/bot-feedback-trs` | Pasta onde está o código do bot |
| `ExecStart=.../python bot.py` | Comando que inicia o bot |
| `EnvironmentFile=/root/bot-feedback-trs/.env` | Arquivo onde fica o token do Telegram |
| `Restart=always` | Se o bot cair, o Linux tenta subir de novo |
| `RestartSec=5` | Espera 5 segundos antes de reiniciar |
| `WantedBy=multi-user.target` | Permite iniciar o serviço junto com o servidor |

## Arquivo `.env`

O token do Telegram não deve ficar no GitHub.

Ele fica em um arquivo local:

```text
/root/bot-feedback-trs/.env
```

Formato:

```bash
TELEGRAM_BOT_TOKEN=COLE_O_TOKEN_AQUI
```

Depois proteja o arquivo:

```bash
chmod 600 /root/bot-feedback-trs/.env
```

## Como instalar o serviço

Depois de clonar o repo, instalar dependências e carregar as credenciais:

```bash
systemctl daemon-reload
systemctl enable bot-feedback.service
systemctl start bot-feedback.service
```

## Comandos do dia a dia

### Ver se o bot está rodando

```bash
systemctl status bot-feedback.service --no-pager
```

### Reiniciar o bot

```bash
systemctl restart bot-feedback.service
```

### Parar o bot

```bash
systemctl stop bot-feedback.service
```

### Ligar o bot

```bash
systemctl start bot-feedback.service
```

### Ver logs recentes

```bash
journalctl -u bot-feedback.service -n 80 --no-pager
```

### Acompanhar logs ao vivo

```bash
journalctl -u bot-feedback.service -f
```

## Logs esperados quando está funcionando

```text
Iniciando Bot de Feedback TRS...
Bot rodando. Ctrl+C para parar.
getMe 200 OK
setMyCommands 200 OK
Application started
getUpdates 200 OK
```

## Erro comum: duas instâncias do bot

Se aparecer algo assim:

```text
telegram.error.Conflict: terminated by other getUpdates request
```

significa que existem duas cópias do mesmo bot rodando.

Solução:

1. deixe apenas o systemd rodando;
2. pare qualquer `python bot.py` iniciado manualmente;
3. reinicie o serviço.

Comandos úteis:

```bash
ps aux | grep '[p]ython.*bot.py'
systemctl restart bot-feedback.service
systemctl status bot-feedback.service --no-pager
```

## Melhor prática neste projeto

- O repositório GitHub guarda o código e a documentação.
- O Drive guarda o pacote de credenciais sensíveis.
- O systemd mantém o bot rodando no servidor.
- O arquivo `.env` fica só no servidor e nunca deve ir para o GitHub.
