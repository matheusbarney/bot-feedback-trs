# Servico headless de transcricao (whisper.cpp), para rodar como servico
# separado do bot no Railway (e depois no servidor do CIn). Compila o
# whisper-server a partir do codigo fonte oficial do projeto, em vez de
# depender de um binario extraido de terceiros (ex: o AppImage do OpenWhispr
# usado so para validacao local) — mais facil de manter e atualizar.

FROM debian:bookworm-slim AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential cmake git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN git clone --depth 1 https://github.com/ggml-org/whisper.cpp.git .
RUN cmake -B build -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build -j --config Release --target whisper-server

FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# whisper-server e dinamicamente ligado a libwhisper/libggml, que ficam no
# mesmo diretorio do binario no build — copia tudo, nao so o executavel.
COPY --from=build /src/build/bin/ /app/

# Modelo GGML multilingue (~466MB) — o mesmo testado localmente. Baixado no
# build para o start do container nao depender de rede nem de volume.
ARG WHISPER_MODEL_URL=https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin
RUN curl -L --fail -o /app/model.bin "$WHISPER_MODEL_URL"

ENV WHISPER_LANG=pt
EXPOSE 8080

# Railway injeta PORT em runtime; --host 0.0.0.0 e obrigatorio para o bot
# (outro servico) conseguir alcancar isso pela rede privada do Railway.
CMD ["/bin/sh", "-c", "/app/whisper-server -m /app/model.bin -l ${WHISPER_LANG:-pt} --host 0.0.0.0 --port ${PORT:-8080}"]
