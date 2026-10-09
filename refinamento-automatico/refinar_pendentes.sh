#!/bin/sh
# Job de lote, pensado pra rodar via cron: acha transcricoes novas na pasta
# do ciclo atual (Drive), gera uma versao corrigida pelo glossario como
# ARQUIVO SEPARADO (<nome>-corrigido.txt) — nunca sobrescreve nem apaga o
# original, pra alguem poder revisar a correcao depois com calma.
#
# Nao reprocessa: pula qualquer arquivo que ja termine em "-corrigido.txt"
# (evita corrigir a propria correcao), e pula transcricoes que ja tem um
# "-corrigido.txt" irmao na mesma listagem (evita refazer trabalho).
#
# Uso: ./refinar_pendentes.sh
# Cron (a cada 15 min): */15 * * * * /caminho/refinar_pendentes.sh >> /var/log/refinar-transcricao.log 2>&1
set -e

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
DRIVE_SCRIPT="$REPO_ROOT/.claude/skills/corrigir-transcricao/scripts/drive_transcricoes.py"
PY="$REPO_ROOT/venv/bin/python"
REFINAR="$REPO_ROOT/refinamento-automatico/refinar_transcricao.sh"

TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

LISTAGEM_FILE="$TMP_DIR/listagem.tsv"
"$PY" "$DRIVE_SCRIPT" listar > "$LISTAGEM_FILE"

while IFS="$(printf '\t')" read -r file_id nome modificado; do
    [ -z "$file_id" ] && continue

    case "$nome" in
        *-corrigido.txt|_chat.txt)
            continue
            ;;
    esac

    base=$(basename "$nome" .txt)
    corrigido_nome="${base}-corrigido.txt"

    if cut -f2 "$LISTAGEM_FILE" | grep -qx "$corrigido_nome"; then
        continue
    fi

    echo "Processando: $nome"
    bruto_path="$TMP_DIR/$nome"
    "$PY" "$DRIVE_SCRIPT" baixar "$file_id" "$bruto_path"

    corrigido_path="$TMP_DIR/$corrigido_nome"
    if ! "$REFINAR" "$bruto_path" > "$corrigido_path"; then
        echo "ERRO ao refinar '$nome' — pulando, tenta de novo no proximo job." >&2
        continue
    fi

    "$PY" "$DRIVE_SCRIPT" criar "$corrigido_nome" "$corrigido_path"
    echo "Criado: $corrigido_nome"
done < "$LISTAGEM_FILE"
