# Deploy no Railway (validação antes de ir pro servidor do CIn)

Conforme o Eliseu pediu: valida tudo aqui, numa infra que você controla
direto, antes de mandar pra infra do CIn — lá qualquer ajuste pequeno
depende de pedir permissão de novo, o que trava a iteração.

Os dois Dockerfiles deste repo ([Dockerfile](Dockerfile) para o bot,
[whisper-server/Dockerfile](whisper-server/Dockerfile) para a transcrição)
já foram buildados e testados localmente com Docker, rodando como dois
containers conversando entre si — é esse mesmo arranjo que vira dois
serviços no Railway.

## 1. Criar o projeto no Railway

No [railway.app](https://railway.app), crie um projeto novo e conecte este
repositório do GitHub (`matheusbarney/bot-feedback-trs`). Dentro dele, crie
**dois serviços separados**, ambos apontando pro mesmo repositório:

### Serviço `whisper-server`

- Em **Settings → Build**, defina o **Root Directory** (ou "Dockerfile
  Path") como `whisper-server/Dockerfile`.
- Em **Settings → Networking**, **não** exponha domínio público — esse
  serviço só precisa ser alcançado pelo bot, via rede privada do Railway.
- Variável opcional: `WHISPER_LANG` (default `pt`, já no Dockerfile).
- **Fixe a porta**: defina a variável `PORT=8080` nesse serviço (em vez de
  deixar o Railway escolher uma porta dinâmica) — é o valor que o serviço
  do bot vai usar pra montar a URL interna.

### Serviço `bot`

- **Root Directory**/Dockerfile: `Dockerfile` (raiz do repo).
- Variáveis de ambiente necessárias:
  - `TELEGRAM_BOT_TOKEN` — o token do bot.
  - `DRIVE_ROOT_FOLDER` — pasta raiz no Drive (produção real ou de teste).
  - `WHISPER_SERVER_URL` — `http://whisper-server.railway.internal:8080/inference`
    (troque `whisper-server` pelo nome exato que você deu ao serviço acima;
    é esse nome que vira o hostname interno).
  - `GOOGLE_CREDENTIALS_JSON_B64` e `GOOGLE_TOKEN_JSON_B64` — ver seção
    abaixo.

## 2. Credenciais do Drive (sem usar Volume)

O Railway não tem um jeito simples de montar um arquivo pequeno direto —
em vez de configurar um Volume só pra dois arquivos de poucos KB, o
[docker-entrypoint.sh](docker-entrypoint.sh) materializa `credentials.json`
e `token.json` a partir de variáveis de ambiente em base64, na primeira vez
que o container sobe.

Gere os valores localmente (a partir dos arquivos que você já tem, nunca
commitados):

```bash
base64 -w0 credentials.json
base64 -w0 token.json
```

Cole cada resultado nas variáveis `GOOGLE_CREDENTIALS_JSON_B64` e
`GOOGLE_TOKEN_JSON_B64` do serviço `bot` no Railway.

**Atenção, ponto real de risco:** se a tela de consentimento OAuth do
projeto Google Cloud ainda estiver em modo **Testing** (não publicada/
verificada), o `refresh_token` expira sozinho depois de **7 dias**, e o
bot vai parar de conseguir renovar o acesso ao Drive — vai ser preciso
rodar `auth_drive.py` de novo e atualizar a variável. Pra evitar isso:
mude a tela de consentimento OAuth pra "In production" no Google Cloud
Console (não precisa de verificação do Google pra uso interno com poucos
usuários, só tira o limite de 7 dias). Vale resolver isso antes de contar
com o bot rodando sem intervenção por mais de uma semana.

## 3. Validar

Depois do deploy dos dois serviços, confira nos logs do serviço `bot`:

```text
Iniciando Bot de Feedback TRS...
HTTP Request: POST .../getMe "HTTP/1.1 200 OK"
HTTP Request: POST .../getUpdates "HTTP/1.1 200 OK"
```

E manda uma mensagem de teste (texto e áudio) pro bot — se a transcrição
funcionar, o log do serviço `bot` mostra o upload do `.ogg` seguido do
`.txt` na mesma pasta, igual na validação local.

## 4. Dimensionamento (RAM/CPU)

Medido de verdade com `docker stats` local (dois containers, rede
compartilhada), não é estimativa — relevante pro Eliseu confirmar a
configuração do servidor do CIn, já que isso ficou em aberto na ata
("confirmar a configuração real do servidor, quantos núcleos e quanta
memória, porque a informação disponível é contraditória").

| | Parado (idle) | Durante transcrição (pico) |
|---|---|---|
| **whisper-server** | ~520–546 MB | ~670 MB, CPU batendo ~390% (usa 4 threads simultâneos) |
| **bot** | ~10–45 MB | sem variação relevante, sempre abaixo de 50 MB |

Teste feito com áudios curtos (0.5s e 2.4s) — arquivo mais longo deve
consumir mais RAM/CPU transitoriamente durante o processamento.

**Recomendação pra passar pro Eliseu:**
- **RAM**: 2 GB de margem de segurança pros dois serviços juntos (pico
  real somado ficou em ~720 MB nos testes com áudio curto).
- **CPU**: pelo menos **4 núcleos** disponíveis, pra transcrição não
  filar com outras cargas do servidor — hoje o `whisper-server` está
  configurado com `-t 4` (4 threads); dá pra reduzir se o servidor
  tiver menos núcleo, só fica proporcionalmente mais lento.

## 5. Depois de validado

Só depois disso faz sentido levar pro Eliseu/infra do CIn — ele vai usar
os mesmos dois Dockerfiles (ou a mesma lógica, se a infra do CIn não for
baseada em container) como referência, já sabendo que o arranjo funciona.
