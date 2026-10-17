"""Fluxo explícito para capacidades indisponíveis nesta versão."""

import re
import unicodedata


FILE_NOTICE = (
    "Nenhum arquivo foi lido. A leitura de arquivos ainda não está disponível nesta versão; "
    "não posso informar seu conteúdo, resumo ou última frase. "
    "Podemos continuar conversando sobre outro assunto."
)


def normalize(text):
    return "".join(
        c for c in unicodedata.normalize("NFKD", text.lower())
        if not unicodedata.combining(c)
    ).strip()


def mentions_file(text):
    """Reconhecer referências comuns; não interpretar intenções arbitrárias."""
    normalized = normalize(text)
    return bool(
        re.search(r"\b(?:arquivos?|documentos?|pastas?|diretorios?)\b", normalized)
        or re.search(
            r"\b[\w.-]+\.(?:md|txt|csv|json|log|pdf|docx?|xlsx?|py|ya?ml|toml|ini|env)\b",
            normalized,
        )
        or re.search(r"(?:[a-z]:[\\/]|(?:\.\.?|~)[\\/])\S+", normalized)
    )


def is_file_followup(text):
    """Reconhecer continuações comuns somente após referência a arquivo."""
    normalized = normalize(text)
    return bool(
        re.search(r"\b(?:ultima|primeira|segunda)\s+(?:frase|linha|pagina|palavra)\b", normalized)
        or re.fullmatch(
            r"(?:e\s+)?(?:como\s+(?:ele\s+)?(?:termina|comeca)|"
            r"(?:o\s+)?que\s+(?:ele\s+)?(?:diz|contem)|"
            r"qual\s+(?:e\s+)?(?:o\s+)?(?:conteudo|final)|"
            r"resuma(?:-o| isso)?|mostre\s+(?:o\s+)?(?:conteudo|final|trecho)|continue)[?!. ]*",
            normalized,
        )
    )


class CapabilitySession:
    """Manter o estado de arquivo fora do histórico limitado do modelo."""

    def __init__(self):
        self.file_mode = False

    def reset(self):
        self.file_mode = False

    def handle(self, prompt):
        command = prompt.split(maxsplit=1)[0].lower() if prompt.strip() else ""
        if command == "/arquivo" or mentions_file(prompt):
            self.file_mode = True
            return FILE_NOTICE
        if self.file_mode and is_file_followup(prompt):
            return FILE_NOTICE
        self.reset()
        return None
