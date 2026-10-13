# Refinamento automático da transcrição (Claude Code não-interativo)

Job de servidor, separado do bot — ideia do Eliseu na reunião E06 (07/10):
em vez de a correção pelo glossário depender de alguém abrir o Claude Code e
rodar a skill `/corrigir-transcricao` manualmente, isso roda sozinho via
cron, logado com **conta** (não API key), pra não cair em cobrança por
token.

Cria sempre um **arquivo separado** (`{nome}-corrigido.txt`) ao lado do
original — nunca sobrescreve, nunca apaga. Alguém revisa a correção depois,
com calma, antes de decidir o que fazer com ela.

## 1. Login (uma vez, por máquina)

```bash
claude login
```

Fluxo OAuth — num servidor sem navegador, abre a URL impressa no seu
navegador local (via túnel SSH ou só copiando o link). Depois disso a
sessão fica salva em `~/.claude/` **daquela máquina**, e os scripts abaixo
funcionam sem pedir login de novo.

**Atenção:** essa sessão pode expirar — vimos exatamente esse erro
(`Failed to authenticate: OAuth session expired and could not be
refreshed`) ao testar o comando `claude -p` num ambiente sandbox separado,
não neste servidor nem numa conta que o time controla. Não dá pra afirmar
prazo nenhum (não sabemos a janela real de validade/renovação dessa sessão
— só que a falha existe e é possível). O ponto prático, independente do
prazo: é o tipo de falha que um cron job **não avisa sozinho** — se a
sessão expirar de verdade um dia, `refinar_pendentes.sh` passa a falhar
calado a cada execução, a menos que alguém monitore
`/var/log/refinar-transcricao.log` ou configure um alerta. Mesma categoria
de cuidado que o token OAuth do Google Drive em modo Testing (ver
`RAILWAY.md`) — risco possível de autenticação expirar sem aviso, não um
prazo conhecido de quando isso acontece.

## 2. Os dois scripts

- **`refinar_transcricao.sh <arquivo.txt>`** — corrige um arquivo só,
  imprime o resultado no stdout. Não mexe em Drive, não decide nada sobre
  onde salvar — só transforma texto.

  **Importante:** o `claude -p` sem restrição roda como agente completo,
  com acesso a ferramentas — testamos com dado real e ele alucinou
  "metadados" que não existiam no texto e devolveu uma pergunta de
  esclarecimento em vez da correção. O script já usa `--allowedTools ""`
  e um `--system-prompt` customizado pra forçar um comportamento de
  "ferramenta de texto", não de assistente de código — não tira essas
  flags achando que é redundante.
- **`refinar_pendentes.sh`** — o job de lote de verdade. Lista as
  transcrições do ciclo atual (reaproveita
  `.claude/skills/corrigir-transcricao/scripts/drive_transcricoes.py`),
  pula o que já tem correção ou já é uma correção, roda
  `refinar_transcricao.sh` em cada pendente, e sobe o resultado como
  `{nome}-corrigido.txt` no Drive.

## 3. Cron

```cron
*/15 * * * * /caminho/para/refinamento-automatico/refinar_pendentes.sh >> /var/log/refinar-transcricao.log 2>&1
```

15 minutos é um ponto de partida — não há urgência real aqui (ninguém
revisa a correção na hora), então pode espaçar mais se quiser economizar
chamadas.

## 4. Deploy real (CIn) — checklist pro Eliseu

Tudo que foi validado até aqui usou uma pasta de teste no Drive ("Bot IACP
Teste") e uma conta pessoal. Pra apontar pro SIMIMAPEAR de verdade
(`FeedbackTRS`), falta:

1. **Repositório e ambiente** — clonar o repo, criar venv, instalar
   `requirements.txt`, igual ao setup local.

2. **Credenciais do Drive — conta certa, não a de teste.** Precisa de um
   `token.json`/`credentials.json` válidos pra uma conta com acesso real à
   `FeedbackTRS` — idealmente a conta do GERAIA (como a D7 original já
   previa), não a conta pessoal usada na validação. Mesmo fluxo de sempre:
   OAuth client no Google Cloud, `auth_drive.py` uma vez.

3. **`DRIVE_ROOT_FOLDER=FeedbackTRS`** no `.env` daquele servidor — **sem
   aspas** (já pegamos esse bug aqui: aspas literais na variável fazem o
   Drive procurar uma pasta chamada `"FeedbackTRS"` com aspas no nome, que
   não existe). É essa variável, sozinha, que decide se tudo aponta pro
   SIMIMAPEAR real ou pra qualquer pasta de teste.

4. **`ciclo_atual.json` precisa refletir o ciclo real no momento do
   deploy** — não necessariamente o valor que está commitado agora;
   confirmar com o time qual é o ciclo vigente nessa hora.

5. **Claude Code instalado e logado no servidor**:
   ```bash
   npm install -g @anthropic-ai/claude-code   # ou instalador equivalente
   claude login
   ```
   Decidir de qual conta (Pro/Max/Team — idealmente do GERAIA, já que o
   ponto todo é custo por assinatura, não por token da API).

6. **Cron instalado** (se o CIn rodar algo tipo Debian/Ubuntu, geralmente
   já vem; no Arch/CachyOS usado na validação local precisou instalar
   `cronie` à parte) e o crontab configurado (seção 3 acima).

7. **Cuidado com o `PATH`:** o fix em `refinar_transcricao.sh` assume
   `claude` instalado em `~/.local/bin` (onde o instalador padrão coloca).
   Se o Eliseu instalar diferente (outro usuário, outro gerenciador de
   pacote), **o caminho no script precisa bater** com onde o binário
   realmente ficou — conferir com `which claude` depois de instalar.

8. **Monitoramento.** O Eliseu já está montando observabilidade pro
   MAPEAR (aviso por Telegram quando cai) — vale plugar o log desse cron
   (`/var/log/refinar-transcricao.log`) no mesmo mecanismo, já que tanto a
   sessão do Claude quanto o token OAuth do Drive podem expirar
   silenciosamente (ver seção 1 acima e `RAILWAY.md`).

## Em aberto

- Quem revisa os `-corrigido.txt` e decide se substituem o original — não
  definido ainda (nem na reunião, nem aqui).
- Se este job roda no mesmo container do `whisper-server` ou em separado —
  o Eliseu mencionou "no mesmo contêiner", mas isso depende de como ele
  estruturar o deploy no CIn.
