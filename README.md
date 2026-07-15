# Bot Feedback TRS

Bot de Telegram para coletar feedbacks do projeto TRS e organizar os registros no Google Drive por ciclos.

Bot em produção identificado como **@robotrs_bot** / **Robô dos TRs**.

## O que ele faz

O bot recebe mensagens pelo Telegram e salva o conteúdo em uma estrutura de ciclos no Google Drive:

```text
FeedbackTRS/
└── Ciclo-XX/
    └── Ciclo-XX-Telegram/
        ├── _chat.txt
        ├── imagens/
        ├── audios/
        └── documentos/
```

Tipos de entrada suportados:

- texto;
- mensagens de voz;
- arquivos de áudio;
- fotos;
- documentos.

## Comandos do Telegram

```text
/cicloatual   Ver o ciclo atual de feedback
/novociclo    Iniciar um novo ciclo
/resumo       Ver as entradas recentes do ciclo atual
```

## Arquivos principais

```text
bot.py              Script principal do bot
requirements.txt    Dependências Python
ciclo_atual.json    Estado simples com o número do ciclo atual
auth_drive.py       Auxiliar para autenticação Google Drive
```

Arquivos sensíveis e/ou grandes ficam fora do Git via `.gitignore`:

```text
token.json
credentials.json
service_account.json
.env
bot.log
venv/
```

## Instalação local

```bash
cd /root/bot-feedback-trs
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## Configuração necessária

Defina o token do Telegram no ambiente:

```bash
export TELEGRAM_BOT_TOKEN="SEU_TOKEN_AQUI"
```

Também é necessário ter autenticação do Google Drive disponível no diretório do projeto, normalmente via `token.json` gerado pelo fluxo OAuth do `auth_drive.py`.

> **Importante:** não commitar `token.json`, `credentials.json`, `.env` ou qualquer token do Telegram.

## Rodar manualmente

```bash
cd /root/bot-feedback-trs
./venv/bin/python bot.py
```

## Serviço systemd em produção

Neste servidor, o serviço encontrado é:

```text
/etc/systemd/system/bot-feedback.service
```

Comandos úteis:

```bash
systemctl status bot-feedback.service --no-pager
systemctl restart bot-feedback.service
journalctl -u bot-feedback.service -f
```

## Observação operacional

Se aparecer erro como:

```text
telegram.error.Conflict: terminated by other getUpdates request
```

significa que há mais de uma instância do mesmo bot rodando. Deixe apenas o serviço systemd ativo e mate processos manuais antigos de `python bot.py`.
