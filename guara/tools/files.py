"""Leitura limitada de texto; permissões pertencem ao Python."""

import os
import re
import stat
from pathlib import Path

MAX_FILE_BYTES = 4096
MAX_FILE_CHARS = 2400
EXTENSIONS = {".txt", ".md", ".csv", ".json", ".log", ".py", ".yaml", ".yml", ".toml", ".ini"}


class FileError(Exception):
    """Pedido inválido ou leitura não realizada."""


class AccessRequired(Exception):
    def __init__(self, path):
        self.path = path
        super().__init__(str(path))


def opened_path(stream):
    """Verificar o destino já aberto para detectar troca de links."""
    if os.name == "nt":
        import ctypes
        import msvcrt
        from ctypes import wintypes
        function = ctypes.WinDLL("kernel32", use_last_error=True).GetFinalPathNameByHandleW
        function.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
        function.restype = wintypes.DWORD
        buffer = ctypes.create_unicode_buffer(32768)
        size = function(msvcrt.get_osfhandle(stream.fileno()), buffer, len(buffer), 0)
        if not size or size >= len(buffer):
            raise FileError("Não foi possível verificar o destino do arquivo aberto.")
        name = buffer.value
        if name.startswith("\\\\?\\UNC\\"):
            raise FileError("Caminhos de rede não são aceitos.")
        return Path(name.removeprefix("\\\\?\\")).resolve()
    return Path(os.readlink("/proc/self/fd/{}".format(stream.fileno()))).resolve()


class FileAccess:
    def __init__(self, root=None):
        self.root = Path.cwd().resolve() if root is None else Path(root).resolve()
        self.read_count = 0
        self.last_path = None

    def resolve(self, arguments):
        if not isinstance(arguments, dict) or set(arguments) != {"caminho"}:
            raise FileError("Informe somente o argumento caminho.")
        name = arguments["caminho"]
        if not isinstance(name, str) or not name.strip() or len(name) > 1000:
            raise FileError("Caminho inválido: use de 1 a 1.000 caracteres.")
        if any(ord(c) < 32 for c in name) or name.startswith(("\\\\", "//")):
            raise FileError("Dispositivos e caminhos de rede não são aceitos.")
        rest = name
        if re.match(r"^[A-Za-z]:", name):
            if len(name) < 3 or name[2] not in "\\/":
                raise FileError("Use um caminho absoluto ou relativo à pasta da sessão.")
            rest = name[2:]
        if ":" in rest:
            raise FileError("Fluxos alternativos e dispositivos não são aceitos.")
        try:
            path = (self.root / name).resolve()
        except (OSError, ValueError, RuntimeError) as error:
            raise FileError("Não foi possível resolver o caminho.") from error
        if str(path).startswith(("\\\\", "//")):
            raise FileError("Caminhos de rede não são aceitos.")
        if path.suffix.lower() not in EXTENSIONS:
            raise FileError("Formato não aceito. Use texto: {}.".format(", ".join(sorted(EXTENSIONS))))
        devices = {"CON", "PRN", "AUX", "NUL"}
        devices.update("{}{}".format(prefix, i) for prefix in ("COM", "LPT") for i in range(10))
        if path.name.upper().split(".")[0] in devices:
            raise FileError("Dispositivos não são aceitos.")
        return path

    def is_local(self, path):
        try:
            path.relative_to(self.root)
            return True
        except ValueError:
            return False

    def read(self, path, approved=None):
        """Autorização externa vale para este destino exato e esta chamada."""
        try:
            target = path.resolve()
            if target != path:
                raise FileError("O destino mudou; solicite a leitura novamente.")
            if not self.is_local(target) and approved != target:
                raise AccessRequired(target)
            if not target.is_file():
                raise FileError("Arquivo não encontrado ou caminho não é um arquivo regular.")
            with target.open("rb") as stream:
                info = os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise FileError("Somente arquivos regulares sem hard links são aceitos.")
                if opened_path(stream) != target:
                    raise FileError("O destino mudou durante a abertura; leitura cancelada.")
                if info.st_size > MAX_FILE_BYTES:
                    raise FileError("O arquivo excede o limite de 4.096 bytes.")
                raw = stream.read(MAX_FILE_BYTES + 1)
            if len(raw) > MAX_FILE_BYTES:
                raise FileError("O arquivo excede o limite de 4.096 bytes.")
            text = raw.decode("utf-8-sig")
            if "\x00" in text or any(ord(c) < 32 and c not in "\n\r\t" for c in text):
                raise FileError("O arquivo contém dados binários ou controles não aceitos.")
            if len(text) > MAX_FILE_CHARS:
                raise FileError("O texto excede o limite de 2.400 caracteres.")
        except UnicodeDecodeError as error:
            raise FileError("Use um arquivo de texto codificado em UTF-8.") from error
        except (OSError, ValueError, RuntimeError) as error:
            raise FileError("Não foi possível abrir ou ler o arquivo.") from error
        self.read_count += 1
        self.last_path = target
        return {"caminho": str(target), "conteudo": text, "bytes": len(raw)}
