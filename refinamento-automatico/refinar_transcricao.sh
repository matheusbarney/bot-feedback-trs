#!/bin/sh
# Corrige uma transcricao via Claude Code em modo nao-interativo (`claude -p`),
# usando o glossario do projeto como referencia. Le o texto bruto de um
# arquivo e imprime o texto corrigido no stdout — nao mexe em Drive nem em
# nenhum outro arquivo, so faz a transformacao de texto. Quem decide o que
# fazer com a saida (criar arquivo separado, etc) e o chamador.
#
# Uso: ./refinar_transcricao.sh <arquivo_bruto.txt>
#
# Pre-requisito: `claude login` ja feito nesta maquina (sessao de conta,
# nao API key — ver README.md deste diretorio). Sem isso, falha com
# "Failed to authenticate: OAuth session expired ou nao configurada".
set -e

if [ -z "$1" ]; then
    echo "Uso: $0 <arquivo_bruto.txt>" >&2
    exit 1
fi

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
GLOSSARIO=$(cat "$REPO_ROOT/glossario.md")
BRUTO=$(cat "$1")

# --allowedTools "" e --system-prompt (substitui a persona padrao de
# assistente de codigo) sao obrigatorios aqui: sem eles, o `claude -p`
# roda como agente completo, com acesso a ferramentas — ja vimos isso
# alucinar "metadados" que nao existiam no texto e fazer perguntas de
# esclarecimento, o que e inutil (e silenciosamente quebrado) num job
# sem ninguem pra responder. Nao usar --bare: essa flag força
# autenticacao por API key e ignora OAuth/login, o que quebra o
# requisito de usar conta em vez de API (custo).
claude -p "Corrija os termos técnicos e nomes próprios nesta transcrição de áudio, usando este glossário do projeto como referência. Preserve tudo que não for erro de vocabulário — não reescreva o estilo de fala, não remova hesitações genuínas, não resuma nem explique nada. Responda só com o texto corrigido, sem comentário nenhum antes ou depois.

Glossário:
$GLOSSARIO

Transcrição:
$BRUTO" \
    --output-format text \
    --allowedTools "" \
    --system-prompt "Você é uma ferramenta de correção de texto, não um assistente de programação. Sua única tarefa é corrigir termos de vocabulário num texto, usando o glossário fornecido. Responda SOMENTE com o texto corrigido. Nunca faça perguntas, nunca peça esclarecimento, nunca comente sobre o que recebeu — se algo parecer estranho ou ambíguo, apenas devolva o trecho o mais parecido possível com o original, sem markdown, sem aspas, sem prefixo."
