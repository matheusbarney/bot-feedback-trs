---
name: corrigir-transcricao
description: Revisa e corrige as transcrições de áudio (.txt, geradas pelo whisper.cpp local) do ciclo atual do bot de feedback TRS, usando o glossário de termos do projeto (glossario.md) como referência. Use esta skill sempre que o usuário pedir para revisar, corrigir, limpar ou conferir transcrições do bot do Telegram, mencionar erros de transcrição (ex: termos técnicos ou nomes saindo errados), pedir para "rodar a correção do glossário", ou perguntar o que falta corrigir no ciclo atual — mesmo que não diga explicitamente "use a skill corrigir-transcricao".
---

# Corrigir transcrição

## Por que esta skill existe

O bot do Telegram ([bot.py](../../../bot.py)) transcreve áudios com um modelo
local de whisper.cpp. É rápido e mantém o dado de voz local (decisão D8 da
ata da equipe), mas erra sistematicamente termos técnicos e nomes próprios do
domínio do projeto — porque o modelo não tem contexto nenhum sobre o
vocabulário específico do IACP. A decisão da equipe foi resolver isso com
Claude Code, já que ele já está no fluxo de trabalho do time: em vez de um
find-and-replace cego, alguém roda esta skill de vez em quando pra revisar as
transcrições recentes usando bom senso + o glossário do projeto.

Isso significa que seu trabalho aqui não é só substituir strings
mecanicamente — é ler cada transcrição com atenção, usar [glossario.md](../../../glossario.md)
como referência de termos conhecidos, e também aplicar seu próprio
julgamento para pegar variações que não estão listadas literalmente (ex: se
o glossário tem "Weasper.CPP → Whisper.cpp" mas a transcrição saiu
"Wyspr cpp", você deve reconhecer que é o mesmo erro).

## Passo a passo

1. **Leia o glossário.** Abra [glossario.md](../../../glossario.md) na raiz
   do repo antes de corrigir qualquer coisa — ele tem os termos corretos do
   domínio (ferramentas, siglas de sistemas do governo/CIn, nomes de
   pessoas do projeto) e os erros de transcrição já conhecidos de cada um.

2. **Liste as transcrições do ciclo atual.** Rode, a partir da raiz do repo:
   ```bash
   ./venv/bin/python .claude/skills/corrigir-transcricao/scripts/drive_transcricoes.py listar
   ```
   Isso imprime `file_id`, nome e data de modificação de cada `.txt` dentro
   da pasta `Ciclo-XX-Telegram` do ciclo atual (lido de `ciclo_atual.json`),
   reaproveitando a mesma autenticação e navegação de pastas que o bot já
   usa — não invente outro jeito de acessar o Drive.

   Se o usuário já apontou um arquivo ou uma transcrição específica (ex:
   colou o texto direto no chat), pule a listagem e trabalhe só com isso.

3. **Baixe o conteúdo de cada transcrição a revisar:**
   ```bash
   ./venv/bin/python .claude/skills/corrigir-transcricao/scripts/drive_transcricoes.py baixar <file_id> /tmp/<nome>.txt
   ```
   Não assuma que precisa revisar todas de uma vez — se o usuário pediu só
   a mais recente, ou só uma pessoa específica, filtre pelo nome do arquivo
   (`{timestamp}_{remetente}.txt`) antes de baixar tudo.

4. **Corrija usando o glossário + seu julgamento.** Para cada transcrição:
   - Troque os termos errados pelos corretos, usando o glossário como base.
   - Preserve tudo o que não for claramente um erro de transcrição — não
     reescreva o estilo de fala da pessoa, não "melhore" a redação, não
     remova hesitações ou repetições que pareçam genuínas. O objetivo é
     corrigir vocabulário errado, não editar a fala de ninguém.
   - Se encontrar um erro que se repete mas não está no glossário, anote —
     vai virar uma entrada nova no passo 6.

5. **Mostre um resumo do que mudou antes de escrever em qualquer lugar.**
   Para cada arquivo revisado, mostre ao usuário as mudanças especificas (um
   diff simples ou uma lista "trocou X por Y") — nunca decida sozinho
   sobrescrever o Drive sem o usuário ver o que foi alterado. Transcrição de
   áudio tem espaço real para falso positivo (a pessoa pode ter dito mesmo
   algo parecido com um termo do glossário sem ser aquele termo).

6. **Pergunte o que fazer com o resultado**, pra cada arquivo ou para o lote
   todo (o que fizer mais sentido pelo volume):
   - **Sobrescrever o `.txt` original no Drive** — `atualizar <file_id> <arquivo_local>`.
   - **Salvar como arquivo separado** (ex: `{nome-original}-corrigido.txt`,
     mesma pasta) — `criar <nome> <arquivo_local>`.
   - **Só mostrar, não escrever nada** — útil quando o usuário só queria
     conferir a qualidade da transcrição.

   Só rode `atualizar` ou `criar` depois de confirmação explícita do
   usuário — nunca como ação automática default.

7. **Proponha atualizar o glossário** se, no passo 4, você encontrou erros
   recorrentes que não estavam documentados. Mostre a entrada nova proposta
   (termo correto + variações erradas observadas) e só adicione a
   [glossario.md](../../../glossario.md) depois que o usuário confirmar — é
   assim que o glossário cresce com o uso real, em vez de ficar parado.

## O que esta skill não faz

- Não transcreve áudio do zero (isso é o `transcribe_audio()` em `bot.py`,
  rodando contra o `whisper-server` local/do servidor).
- Não decide sozinha o ciclo a revisar — sempre usa o que está em
  `ciclo_atual.json`, a menos que o usuário peça outro ciclo explicitamente
  (nesse caso, edite temporariamente o arquivo ou adapte o script).
- Não apaga nem sobrescreve nada no Drive sem confirmação explícita do
  usuário no passo 6.
