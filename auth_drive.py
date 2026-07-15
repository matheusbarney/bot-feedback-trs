"""
auth_drive.py — Gera o token.json para autenticação OAuth do Google Drive.
Execute UMA vez na sua máquina local, depois copie o token.json para o VPS.

Uso:
    python3 auth_drive.py

Pré-requisito:
    Coloque credentials.json na mesma pasta (baixado do Google Cloud Console).
    Em Google Cloud: APIs & Services → Credentials → Create → OAuth 2.0 Client ID → Desktop app
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os

SCOPES = ["https://www.googleapis.com/auth/drive"]

def main():
    if not os.path.exists("credentials.json"):
        print("ERRO: credentials.json não encontrado.")
        print("Baixe em: console.cloud.google.com → APIs & Services → Credentials → OAuth 2.0 Client ID → Desktop app")
        return

    print("Abrindo navegador para autorização...")
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)

    with open("token.json", "w") as f:
        f.write(creds.to_json())

    print("\n✓ token.json gerado com sucesso!")
    print("\nAgora copie para o VPS:")
    print("  scp token.json root@104.131.127.99:/root/bot-telegram/")

if __name__ == "__main__":
    main()
