#!/bin/sh
# Materializa credentials.json/token.json a partir de variaveis de ambiente
# em base64, se ainda nao existirem no container. No Railway nao tem um
# jeito simples de montar um arquivo pequeno sem usar Volume — isso evita
# precisar de um Volume so para dois arquivos de poucos KB.
#
# Gerar os valores localmente com:
#   base64 -w0 credentials.json
#   base64 -w0 token.json
# E colar o resultado nas variaveis GOOGLE_CREDENTIALS_JSON_B64 /
# GOOGLE_TOKEN_JSON_B64 no Railway.
set -e

if [ -n "$GOOGLE_CREDENTIALS_JSON_B64" ] && [ ! -f /app/credentials.json ]; then
    echo "$GOOGLE_CREDENTIALS_JSON_B64" | base64 -d > /app/credentials.json
fi

if [ -n "$GOOGLE_TOKEN_JSON_B64" ] && [ ! -f /app/token.json ]; then
    echo "$GOOGLE_TOKEN_JSON_B64" | base64 -d > /app/token.json
fi

exec "$@"
