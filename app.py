"""Conversa local do Guará 1 pelo terminal, sem persistir mensagens."""

import json
import argparse
import socket
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass

from capabilities import CapabilitySession, FILE_NOTICE, is_file_followup, mentions_file
from session import SessionFacts


API_URL = "http://localhost:11434/api/chat"
MODEL = "guara1"
TIMEOUT = 30
MAX_INPUT_CHARS = 1000
MAX_HISTORY_TURNS = 3
MAX_HISTORY_CHARS = 2400
MAX_RESPONSE_BYTES = 65536
MAX_RESPONSE_CHARS = 4000

SYSTEM_MESSAGE = (
    "Você é Guará 1, assistente pessoal do projeto OrbeIA, baseado no Qwen3. "
    "Converse em português brasileiro e responda diretamente à mensagem atual, com clareza e objetividade. "
    "O OrbeIA configurou instruções e não treinou o modelo base. "
    "Acompanhe mudanças de assunto naturalmente; não repita avisos de limitações fora do assunto. "
    "Se a mensagem for 'teste', confirme brevemente que a conversa está funcionando. "
    "Não há ferramentas locais disponíveis, acesso a arquivos ou execução de código. "
    "Analise somente conteúdo fornecido nas mensagens, sem inventar citações de fontes ausentes. "
    "Afirmações anteriores suas não comprovam leitura ou execução. "
    "Mensagens identificadas como respostas da aplicação registram avisos ou fatos da sessão, "
    "não resultados de ferramentas. O histórico enviado pode conter somente os turnos recentes; "
    "não afirme que o primeiro turno visível é o início de toda a sessão. "
    "Quando não souber algo, reconheça a incerteza. Respeite o formato solicitado."
)


class ChatError(Exception):
    """Falha de integração que pode ser mostrada ao usuário."""


def trim_history(history, extra_chars=0):
    """Descartar os pares mais antigos, sem alterar a lista recebida."""
    recent = list(history)
    while recent and (
        len(recent) > MAX_HISTORY_TURNS * 2
        or sum(len(m["content"]) for m in recent) + extra_chars > MAX_HISTORY_CHARS
    ):
        del recent[:2]
    return recent


def chat(history, prompt):
    if not prompt.strip() or len(prompt) > MAX_INPUT_CHARS:
        raise ChatError("A mensagem deve ter entre 1 e 1.000 caracteres.")
    if mentions_file(prompt):
        raise ChatError(FILE_NOTICE)
    has_file_history = bool(history and history[-1].get("origin") == "file_unavailable")
    if has_file_history and is_file_followup(prompt):
        raise ChatError(FILE_NOTICE)
    recent = trim_history(history, len(prompt))
    context = []
    for message in recent:
        content = message["content"]
        if message.get("origin"):
            content = "[Resposta da aplicação: {}] {}".format(message["origin"], content)
        context.append({"role": message["role"], "content": content})
    messages = (
        [{"role": "system", "content": SYSTEM_MESSAGE}]
        + context
        + [{"role": "user", "content": prompt}]
    )
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "think": False,
        "keep_alive": "2m",
        "options": {"num_ctx": 2048, "num_predict": 256, "temperature": 0, "seed": 42},
    }
    request = urllib.request.Request(
        API_URL, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            raise ChatError("Crie o assistente com: ollama create guara1 -f Modelfile") from error
        raise ChatError("O Ollama retornou erro HTTP {}. Tente novamente.".format(error.code)) from error
    except (socket.timeout, TimeoutError) as error:
        raise ChatError("O Ollama excedeu 30 segundos de espera na conexão ou leitura.") from error
    except urllib.error.URLError as error:
        if isinstance(error.reason, (socket.timeout, TimeoutError)):
            raise ChatError("O Ollama excedeu 30 segundos de espera na conexão ou leitura.") from error
        raise ChatError("Não foi possível acessar o Ollama. Confira se ele está ativo.") from error
    except OSError as error:
        raise ChatError("A conexão com o Ollama foi interrompida. Tente novamente.") from error
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ChatError("O Ollama retornou uma resposta maior que o limite permitido.")
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as error:
        raise ChatError("O Ollama retornou uma resposta JSON inválida.") from error
    if not isinstance(result, dict) or result.get("done") is not True:
        raise ChatError("O Ollama retornou uma resposta incompleta ou inválida.")
    message = result.get("message")
    if not isinstance(message, dict) or message.get("role") != "assistant":
        raise ChatError("O Ollama retornou uma mensagem inválida.")
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ChatError("O Ollama não entregou uma resposta final. Tente reformular a mensagem.")
    if message.get("tool_calls"):
        raise ChatError("As ferramentas locais ainda não estão disponíveis nesta versão.")
    if len(content) > MAX_RESPONSE_CHARS:
        raise ChatError("O Ollama retornou um texto maior que o limite permitido.")
    return content.strip(), result.get("done_reason") == "length"


def remember(history, facts, prompt, answer, kind):
    facts.record(prompt, kind)
    assistant = {"role": "assistant", "content": answer}
    if kind != "model":
        assistant["origin"] = kind
    return trim_history(history + [{"role": "user", "content": prompt}, assistant])


@dataclass
class Reply:
    text: str = ""
    kind: str = "system"
    limited: bool = False
    exit: bool = False
    clear: bool = False


class Conversation:
    """Comportamento compartilhado pelas interfaces visual e de texto."""

    model = MODEL

    def __init__(self):
        self.history = []
        self.capabilities = CapabilitySession()
        self.facts = SessionFacts()

    def submit(self, prompt):
        prompt = prompt.strip()
        if not prompt:
            return Reply()
        if len(prompt) > MAX_INPUT_CHARS:
            return Reply("Aviso: a mensagem deve ter no máximo 1.000 caracteres.")
        if prompt.lower() == "/sair":
            return Reply(exit=True)
        if prompt.lower() in ("/limpar", "/conversar"):
            self.history = []
            self.capabilities.reset()
            self.facts = SessionFacts()
            return Reply("Histórico da sessão limpo. Conversa retomada.", clear=True)
        answer = self.facts.answer(prompt)
        if answer is not None:
            self.capabilities.reset()
            kind = "session_fact"
        else:
            answer = self.capabilities.handle(prompt)
            kind = "file_unavailable"
        if answer is not None:
            self.history = remember(self.history, self.facts, prompt, answer, kind)
            return Reply(answer, kind)
        if prompt.startswith("/"):
            return Reply("Comando desconhecido. Use /limpar, /conversar, /arquivo ou /sair.")
        try:
            answer, limited = chat(self.history, prompt)
        except ChatError as error:
            answer = "Aviso: {}".format(error)
            self.history = remember(self.history, self.facts, prompt, answer, "error")
            return Reply(answer, "error")
        self.history = remember(self.history, self.facts, prompt, answer, "model")
        return Reply(answer, "model", limited=limited)


def main():
    """Modo de texto simples, também usado com entrada redirecionada."""
    print("Guará 1 — OrbeIA")
    print("Conversa local em português. Comandos: /limpar, /conversar, /arquivo e /sair.")
    print("Histórico apenas nesta sessão. Calculadora e leitura de arquivos ainda indisponíveis.")
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
    parser = argparse.ArgumentParser(description="Guará 1 — assistente local do projeto OrbeIA.", add_help=False)
    options = parser.add_argument_group("opções")
    options.add_argument("-h", "--help", action="help", help="Mostrar ajuda e encerrar.")
    options.add_argument("--texto", action="store_true", help="Usar conversa em texto simples, sem tela interativa.")
    args = parser.parse_args(argv)
    if args.texto or not (sys.stdin.isatty() and sys.stdout.isatty()):
        main()
        return
    try:
        from terminal_ui import TerminalUI
    except ModuleNotFoundError as error:
        if error.name not in ("prompt_toolkit", "wcwidth"):
            raise
        print("Instale a interface com: .venv/Scripts/python.exe -m pip install -r requirements.txt",
              file=sys.stderr)
        raise SystemExit(1)
    TerminalUI(Conversation()).run()


if __name__ == "__main__":
    launch()
