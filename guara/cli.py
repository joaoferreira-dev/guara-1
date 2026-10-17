"""Seleção de interface e conversa em texto simples."""

import argparse
import sys

from guara.core.conversation import Conversation


def main():
    """Modo de texto simples, também usado com entrada redirecionada."""
    print("Guará 1 — OrbeIA")
    print("Conversa local em português. Comandos: /limpar, /conversar, /arquivo, /permitir, /negar e /sair.")
    print("Histórico apenas nesta sessão. Leitura na pasta de início; acesso externo exige autorização.")
    conversation = Conversation()
    try:
        while True:
            reply = conversation.submit(input("\nVocê: "))
            if reply.exit:
                break
            if reply.text:
                prefix = "\nGuará 1: " if reply.kind not in ("system", "error") else ""
                print(prefix + reply.text)
            if reply.limited:
                print("Aviso: a resposta atingiu o limite de geração e pode estar incompleta.")
    except (EOFError, KeyboardInterrupt):
        pass
    print("\nAté mais!")


def launch(argv=None):
    parser = argparse.ArgumentParser(prog="guara", description="Guará 1 — assistente local do projeto OrbeIA.", add_help=False)
    options = parser.add_argument_group("opções")
    options.add_argument("-h", "--help", action="help", help="Mostrar ajuda e encerrar.")
    options.add_argument("--texto", action="store_true", help="Usar conversa em texto simples, sem tela interativa.")
    args = parser.parse_args(argv)
    if args.texto or not (sys.stdin.isatty() and sys.stdout.isatty()):
        main()
        return
    try:
        from guara.terminal.interface import TerminalUI
    except ModuleNotFoundError as error:
        if error.name not in ("prompt_toolkit", "wcwidth"):
            raise
        print("Instale a interface com: .venv/Scripts/python.exe -m pip install -r requirements.txt",
              file=sys.stderr)
        raise SystemExit(1)
    TerminalUI(Conversation()).run()
