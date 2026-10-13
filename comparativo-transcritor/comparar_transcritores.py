#!/usr/bin/env python3
"""
Compara o whisper.cpp (local/servidor, o que ja esta em producao) com a
API "GPT Transcribe" da OpenAI, para o mesmo arquivo de audio -- insumo
pra decisao D2 da ata E06 (07/10/2026): "a escolha do transcritor fica
para depois de um teste comparativo entre o whisper.cpp e a API da
OpenAI, avaliando qualidade e custo".

Nao decide nada sozinho: so coleta os dois resultados lado a lado (texto,
tempo, custo estimado) para alguem comparar a qualidade com os proprios
ouvidos/julgamento. Nao fica permanentemente no pipeline do bot -- e uma
ferramenta de teste, nao uma integracao de producao (essa decisao ainda
nao foi tomada).

Uso:
    export OPENAI_API_KEY="sk-..."
    ./venv/bin/python comparativo-transcritor/comparar_transcritores.py <audio.ogg> [--language pt] [--openai-model gpt-4o-transcribe]

Modelos da OpenAI suportados (--openai-model):
    gpt-4o-transcribe       (~$0.006/min) -- o "GPT Transcribe" mencionado na reuniao
    gpt-4o-mini-transcribe  (~$0.003/min) -- mais barato, pra comparar custo

Precos conferidos em 10/2026 (developers.openai.com/api/docs/pricing) --
confirme o valor atual antes de decidir com base em custo, preco de API muda.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

WHISPER_SERVER_URL = os.environ.get("WHISPER_SERVER_URL", "http://127.0.0.1:8080/inference")

PRECO_POR_MINUTO_USD = {
    "gpt-4o-transcribe": 0.006,
    "gpt-4o-mini-transcribe": 0.003,
}


def duracao_segundos(audio_path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def converter_para_wav(ogg_path: str) -> str:
    wav_path = f"{ogg_path}.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", ogg_path, "-ar", "16000", "-ac", "1", wav_path],
        capture_output=True, check=True,
    )
    return wav_path


def transcrever_whisper_cpp(wav_path: str, language: str) -> dict:
    t0 = time.monotonic()
    try:
        with open(wav_path, "rb") as f:
            resp = requests.post(
                WHISPER_SERVER_URL,
                files={"file": f},
                data={"response_format": "json", "language": language},
                timeout=120,
            )
        resp.raise_for_status()
        texto = resp.json().get("text", "").strip()
        erro = None
    except requests.RequestException as e:
        texto, erro = "", str(e)
    return {"motor": "whisper.cpp (local/servidor)", "texto": texto, "tempo_s": round(time.monotonic() - t0, 2),
            "custo_usd": 0.0, "custo_obs": "infra propria, sem cobranca por uso", "erro": erro}


def transcrever_openai(audio_path: str, model: str, language: str, api_key: str, duracao_min: float) -> dict:
    t0 = time.monotonic()
    try:
        with open(audio_path, "rb") as f:
            resp = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                data={"model": model, "language": language},
                files={"file": f},
                timeout=120,
            )
        resp.raise_for_status()
        texto = resp.json().get("text", "").strip()
        erro = None
    except requests.RequestException as e:
        texto = ""
        erro = f"{e}"
        if getattr(e, "response", None) is not None:
            erro += f" | corpo: {e.response.text[:300]}"
    custo = round(duracao_min * PRECO_POR_MINUTO_USD.get(model, 0), 6)
    return {"motor": f"OpenAI {model}", "texto": texto, "tempo_s": round(time.monotonic() - t0, 2),
            "custo_usd": custo, "custo_obs": f"~${PRECO_POR_MINUTO_USD.get(model, 0)}/min (conferir preco atual)", "erro": erro}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("audio", help="Caminho do arquivo de audio (.ogg, .wav, .mp3...)")
    parser.add_argument("--language", default="pt")
    parser.add_argument("--openai-model", default="gpt-4o-transcribe", choices=list(PRECO_POR_MINUTO_USD))
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Falta OPENAI_API_KEY no ambiente.", file=sys.stderr)
        sys.exit(1)

    duracao = duracao_segundos(args.audio)
    wav_path = converter_para_wav(args.audio)
    try:
        resultado_whisper = transcrever_whisper_cpp(wav_path, args.language)
    finally:
        os.unlink(wav_path)

    resultado_openai = transcrever_openai(args.audio, args.openai_model, args.language, api_key, duracao / 60)

    saida = {
        "arquivo": args.audio,
        "duracao_s": round(duracao, 2),
        "resultados": [resultado_whisper, resultado_openai],
    }
    print(json.dumps(saida, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
