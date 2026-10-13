# Resultados: whisper.cpp vs GPT Transcribe (OpenAI)

Insumo pra decisão D2 da ata E06 (07/10/2026): "a escolha do transcritor
fica para depois de um teste comparativo entre o whisper.cpp e a API da
OpenAI, avaliando qualidade e custo".

Gerado com [`comparar_transcritores.py`](comparar_transcritores.py), usando
os mesmos dois áudios de teste já salvos no Drive (ciclo de testes,
"Bot IACP Teste").

## Teste 1 — áudio curto (8,4s)

| | whisper.cpp | GPT Transcribe |
|---|---|---|
| Texto | "Você vai salvar meu áudio agora usando o Open Whisper." | "Você vai salvar meu áudio agora usando o Open Whisper." |
| Tempo | 7,42s | 2,18s |
| Custo | $0 | $0,000843 |

Idêntico nos dois — nenhum acertou "OpenWhispr" sozinho.

## Teste 2 — áudio mais longo (16s), com termos técnicos

| | whisper.cpp | GPT Transcribe |
|---|---|---|
| Texto | "Bom dia, esse é um áudio que será transcrito usando o interface do **Weasper.CPP** que é também utilizado pelo **Open Weasper**, mas sempre se traduzido para texto, essa transcrição de áudio." | "Bom dia! Esse é um áudio que será transcrito usando a interface do **whisper.cpp**, que é também utilizado pelo **OpenWhisper**. Assim, será traduzido para texto a transcrição de áudio." |
| Tempo | 6,81s | 1,8s |
| Custo | $0 | $0,001599 |

GPT Transcribe acertou "whisper.cpp" e quase acertou "OpenWhisper" (só
faltou o "r" final) — exatamente os termos que o whisper.cpp erra
sistematicamente. Também ficou ~3,8x mais rápido nos dois testes.

## O que isso significa pra decisão

**Qualidade:** GPT Transcribe claramente melhor em termos técnicos/nomes
próprios — reduziria (não elimina) a dependência da correção por
glossário. Mas também parece "limpar" a fala mais do que o whisper.cpp
(frases um pouco mais lineares) — não dá pra saber com só 2 amostras se
isso é ganho de legibilidade ou perda de fidelidade ao que foi dito de
verdade. Vale testar com mais áudios antes de considerar isso decidido
(o João tinha tarefa de compartilhar transcrições antigas do MacWhisper
pra esse fim — e06j2 da ata).

**Velocidade:** GPT Transcribe ganha nos dois testes por boa margem.

**Custo:** Irrelevante por mensagem (frações de centavo), mas escala com
volume — vale a equipe estimar quantos minutos de áudio por mês esperam
receber antes de decidir se isso importa de verdade.

**O ponto que pesa mais, e não é só número:** usar a API da OpenAI manda
o áudio pra fora da infraestrutura do time — é exatamente o que a decisão
original D8 (ata 30/09) queria evitar ("a transcrição continua local, por
causa do dado de voz"). O Eliseu já tinha levantado isso na reunião E06.
Essa troca (qualidade/velocidade vs manter o dado local) é uma decisão de
política do time, não community técnica — não é algo que este teste
resolve sozinho.

## Como rodar mais testes

```bash
export OPENAI_API_KEY="sk-..."
./venv/bin/python comparar_transcritores.py <audio.ogg> --language pt
```

Opcional: `--openai-model gpt-4o-mini-transcribe` pra comparar com a
versão mais barata (~$0,003/min vs ~$0,006/min do `gpt-4o-transcribe`).
