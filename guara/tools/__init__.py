"""Registro explícito da única ferramenta disponível."""

from guara.tools.files import FileError

TOOL_NAME = "ler_arquivo"
TOOLS = [{"type": "function", "function": {
    "name": TOOL_NAME,
    "description": "Ler texto UTF-8, até 4096 bytes e 2400 caracteres. Caminhos relativos partem da pasta da sessão. A aplicação pede autorização para arquivos externos.",
    "parameters": {"type": "object", "properties": {
        "caminho": {"type": "string", "description": "Caminho do arquivo solicitado pelo usuário"}
    }, "required": ["caminho"], "additionalProperties": False}
}}]


def validate_call(calls, files):
    if not isinstance(calls, list) or len(calls) != 1:
        raise FileError("É permitida somente uma chamada de ferramenta por interação.")
    call = calls[0]
    function = call.get("function") if isinstance(call, dict) else None
    if not isinstance(function, dict) or function.get("name") != TOOL_NAME:
        raise FileError("Ferramenta não cadastrada.")
    return files.resolve(function.get("arguments"))
