"""Reconhecimento conservador de referências e continuações de arquivos."""

import re
import unicodedata


FILE_NOTICE = (
    "Nenhum arquivo foi lido. A ferramenta não forneceu conteúdo nesta interação; "
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
