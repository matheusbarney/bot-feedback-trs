#!/usr/bin/env python3
"""
Lista, baixa, atualiza e cria transcricoes (.txt) na pasta do ciclo atual no
Drive. Reaproveita as funcoes de autenticacao e navegacao de pastas que ja
existem em bot.py, em vez de duplicar logica de API do Drive aqui.

Uso (rodar com o python do venv do projeto, a partir da raiz do repo):
    ./venv/bin/python .claude/skills/corrigir-transcricao/scripts/drive_transcricoes.py listar
    ./venv/bin/python .claude/skills/corrigir-transcricao/scripts/drive_transcricoes.py baixar <file_id> <destino_local>
    ./venv/bin/python .claude/skills/corrigir-transcricao/scripts/drive_transcricoes.py atualizar <file_id> <arquivo_local>
    ./venv/bin/python .claude/skills/corrigir-transcricao/scripts/drive_transcricoes.py criar <nome> <arquivo_local>

"listar" imprime uma linha por arquivo .txt encontrado na pasta
Ciclo-XX-Telegram do ciclo atual (ciclo_atual.json): file_id, nome e data de
modificacao, separados por tab.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from bot import (  # noqa: E402
    build_drive_service,
    get_root_folder_id,
    get_telegram_folder_id,
    load_cycle,
    LIST_KWARGS,
    FILE_KWARGS,
)


def _telegram_folder_id(service):
    root_id = get_root_folder_id(service)
    cycle = load_cycle()
    return get_telegram_folder_id(service, root_id, cycle)


def cmd_listar():
    service = build_drive_service()
    folder_id = _telegram_folder_id(service)
    query = (
        f"'{folder_id}' in parents and trashed=false "
        f"and name contains '.txt' and name != '_chat.txt'"
    )
    results = service.files().list(
        q=query, fields="files(id,name,modifiedTime)", **LIST_KWARGS
    ).execute()
    for f in results.get("files", []):
        print(f"{f['id']}\t{f['name']}\t{f.get('modifiedTime', '')}")


def cmd_baixar(file_id: str, destino: str):
    service = build_drive_service()
    content = service.files().get_media(fileId=file_id).execute()
    data = content if isinstance(content, bytes) else content.encode("utf-8")
    Path(destino).write_bytes(data)
    print(f"Salvo em {destino}")


def cmd_atualizar(file_id: str, arquivo_local: str):
    from googleapiclient.http import MediaFileUpload

    service = build_drive_service()
    service.files().update(
        fileId=file_id,
        media_body=MediaFileUpload(arquivo_local, mimetype="text/plain"),
        **FILE_KWARGS,
    ).execute()
    print(f"Atualizado: {file_id}")


def cmd_criar(nome: str, arquivo_local: str):
    from googleapiclient.http import MediaFileUpload

    service = build_drive_service()
    folder_id = _telegram_folder_id(service)
    meta = {"name": nome, "parents": [folder_id]}
    media = MediaFileUpload(arquivo_local, mimetype="text/plain")
    result = service.files().create(
        body=meta, media_body=media, fields="id,webViewLink", **FILE_KWARGS
    ).execute()
    print(f"Criado: {result.get('id')}\t{result.get('webViewLink', '')}")


COMMANDS = {
    "listar": cmd_listar,
    "baixar": cmd_baixar,
    "atualizar": cmd_atualizar,
    "criar": cmd_criar,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(1)
    COMMANDS[sys.argv[1]](*sys.argv[2:])


if __name__ == "__main__":
    main()
