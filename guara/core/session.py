"""Fatos limitados da sessão, independentes do contexto enviado ao modelo."""

import json
import re

from guara.core.capabilities import normalize


class SessionFacts:
    def __init__(self):
        self.file_reads = 0
        self.first_message = None
        self.counts = {kind: 0 for kind in ("model", "file_unavailable", "session_fact", "error", "access_request")}

    def record(self, prompt, kind):
        if kind not in self.counts:
            raise ValueError("Origem de resposta inválida.")
        if self.first_message is None:
            self.first_message = prompt
        self.counts[kind] += 1

    def answer(self, prompt):
        """Responder apenas consultas reconhecidas, usando registros do Python."""
        text = normalize(prompt)
        if (
            re.search(r"\b(?:primeir[ao]|inicio)\b", text)
            and re.search(r"\b(?:pergunt\w*|mensagem|pedido|pedi|solicitei|falei|disse)\b", text)
            and re.search(r"\b(?:perguntei|pedi|solicitei|falei|disse|minha|meu|eu)\b", text)
        ):
            if self.first_message is None:
                return "Ainda não havia mensagem sua nesta sessão antes desta pergunta."
            return "Sua primeira mensagem nesta sessão foi: {}".format(
                json.dumps(self.first_message, ensure_ascii=False)
            )
        if re.fullmatch(
            r"(?:o que voce (?:ja )?fez (?:nessa|nesta|na|durante (?:essa|esta)) conversa|"
            r"o que (?:ja )?aconteceu (?:nessa|nesta|na) conversa|resuma (?:nossa|a nossa|esta|essa) conversa)[?!. ]*",
            text,
        ):
            return (
                "Até sua mensagem anterior, o registro desta sessão contém: "
                "{} resposta(s) do modelo, {} pedido(s) de arquivo recusado(s), "
                "{} resposta(s) local(is) sobre a sessão e {} falha(s) de integração. "
                "Leituras de arquivo concluídas pela ferramenta: {}. Pedidos de autorização externa: {}."
            ).format(self.counts["model"], self.counts["file_unavailable"],
                     self.counts["session_fact"], self.counts["error"], self.file_reads, self.counts["access_request"])
        return None
