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

## Em aberto

- Quem revisa os `-corrigido.txt` e decide se substituem o original — não
  definido ainda (nem na reunião, nem aqui).
- Se este job roda no mesmo container do `whisper-server` ou em separado —
  o Eliseu mencionou "no mesmo contêiner", mas isso depende de como ele
  estruturar o deploy no CIn.
