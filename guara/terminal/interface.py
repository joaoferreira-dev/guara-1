"""Interface em tela cheia com entrada e identificação do modelo fixas."""

import asyncio
import threading
import time

from prompt_toolkit.application import Application
from prompt_toolkit.completion import Completer, Completion, CompleteEvent
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, VSplit, Window, Float, FloatContainer
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout.containers import VerticalAlign
from prompt_toolkit.layout.containers import ConditionalContainer
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.utils import get_cwidth
from guara.terminal.keys import configure_shift_enter, create_terminal_input


WELCOME = (
    "GUARÁ 1\n"
    "Seu assistente local do projeto OrbeIA.\n\n"
    "Escreva uma mensagem para começar.\n"
    "/limpar  nova conversa    /arquivo  leitura    /sair  encerrar\n\n"
    "Leitura na pasta de início. Acesso externo exige /permitir CODIGO; /negar CODIGO recusa.\n"
)
MAX_TRANSCRIPT_CHARS = 40000
INPUT_STYLE = "bg:#1b1f29 #f1f3f5"
PROMPT_MARKER = " > "
ACTIVITY_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
COMMANDS = (
    ("/limpar", "Nova conversa"),
    ("/conversar", "Reiniciar sessão"),
    ("/arquivo", "Ler texto ou mostrar pasta da sessão"),
    ("/permitir", "Autorizar leitura externa pelo código"),
    ("/negar", "Recusar leitura externa pelo código"),
    ("/sair", "Encerrar"),
)


class CommandCompleter(Completer):
    def get_completions(self, document, complete_event):
        prefix = document.text_before_cursor
        if (not prefix.startswith("/") or any(c.isspace() for c in prefix)
                or document.cursor_position != len(document.text)):
            return
        for command, description in COMMANDS:
            if command.startswith(prefix.lower()):
                yield Completion(command, start_position=-len(prefix), display_meta=description)


class ConversationLexer(Lexer):
    def __init__(self, line_style, width):
        self.line_style, self.width = line_style, width

    def lex_document(self, document):
        def line_style(index):
            text = document.lines[index]
            style = self.line_style(index)
            if style == "class:user-message":
                width = self.width()
                # Preencher também as linhas quebradas automaticamente pelo terminal.
                # BufferControl acrescenta uma célula para o cursor; reservá-la
                # evita criar uma linha vazia a cada linha da mensagem.
                padding = (-(get_cwidth(text) + 1)) % width
                text += " " * padding
            return [(style, text)]
        return line_style


async def submit_in_thread(conversation, prompt):
    """Manter a tela responsiva; sair não aguarda uma chamada HTTP pendente."""
    loop = asyncio.get_running_loop()
    result = loop.create_future()

    def deliver(value, error):
        if result.done():
            return
        if error is None:
            result.set_result(value)
        else:
            result.set_exception(error)

    def worker():
        try:
            value, error = conversation.submit(prompt), None
        except Exception as exception:
            value, error = None, exception
        try:
            loop.call_soon_threadsafe(deliver, value, error)
        except RuntimeError:
            pass  # A interface já encerrou; não há sessão a atualizar.

    threading.Thread(target=worker, daemon=True, name="guara-ollama").start()
    return await result


class TerminalUI:
    def __init__(self, conversation, input=None, output=None):
        configure_shift_enter()
        if input is None:
            input = create_terminal_input()
        self.conversation = conversation
        self.busy = False
        self.activity_started = None
        self._messages = [("welcome", WELCOME.rstrip())]
        self._line_styles = []
        self.transcript = TextArea(
            read_only=True, focusable=False, scrollbar=True,
            wrap_lines=True, lexer=ConversationLexer(self._line_style, self._transcript_width),
            style="class:body",
        )
        self._render_transcript()
        self.editor = TextArea(
            multiline=True, wrap_lines=True, height=self.editor_height,
            style="class:input", completer=CommandCompleter(), complete_while_typing=True,
        )
        self.application = Application(
            layout=Layout(self._layout(), focused_element=self.editor),
            key_bindings=self._bindings(), full_screen=True, mouse_support=True,
            style=Style.from_dict({
                "": "bg:default",
                "title": "#f4ad73 bold",
                "subtitle": "#8e96a8",
                "body": "",
                "user-message": INPUT_STYLE,
                "warning": "#e5bd6e bold",
                "input": INPUT_STYLE,
                "border": "#525d70",
                "model": "#9ac9ed",
                "status": "#8e96a8",
                "activity": "#f4ad73",
                "completion-menu.completion": INPUT_STYLE,
                "completion-menu.completion.current": "bg:#334155 #f1f3f5 bold",
                "completion-menu.meta.completion": INPUT_STYLE,
                "completion-menu.meta.completion.current": "bg:#334155 #f4ad73",
                "scrollbar.background": "bg:default",
                "scrollbar.button": "bg:default #525d70",
            }),
            input=input, output=output, refresh_interval=0.12,
        )

    def _size(self):
        application = getattr(self, "application", None)
        if application is None:
            return 24, 80
        size = application.output.get_size()
        return size.rows, size.columns

    def _transcript_width(self):
        return max(1, self._size()[1] - 5)

    def editor_height(self):
        rows, columns = self._size()
        width = max(1, columns - 5)
        lines = sum(max(1, (get_cwidth(line.expandtabs(4)) + width - 1) // width)
                    for line in self.editor.text.split("\n"))
        return min(lines, 8, max(1, rows - 10 - int(self.busy)))

    def _line_style(self, index):
        return self._line_styles[index] if index < len(self._line_styles) else "class:body"

    def _render_transcript(self):
        lines, styles = [], []
        for speaker, text in self._messages:
            if lines:
                lines.append("")
                styles.append("class:body")
            block = text.split("\n")
            if speaker == "Você":
                block = [""] + [PROMPT_MARKER + block[0]] + ["   " + line for line in block[1:]] + [""]
                style = "class:user-message"
            elif speaker == "Aviso":
                style = "class:warning"
            else:
                style = "class:body"
            lines.extend(block)
            styles.extend([style] * len(block))
        self._line_styles = styles
        content = "\n".join(lines)
        self.transcript.buffer.set_document(Document(content, cursor_position=len(content)), bypass_readonly=True)

    def model_label(self):
        name = "Guará-1" if self.conversation.model == "guara1" else self.conversation.model
        return "  {} · Qwen3-1.7B".format(name)

    def status_label(self):
        if self.busy:
            return "Trabalhando… · Ctrl+C sair "
        return "Pronto · Enter enviar · Ctrl+C sair "

    def activity_label(self):
        elapsed = max(0, time.monotonic() - self.activity_started) if self.activity_started is not None else 0
        frame = ACTIVITY_FRAMES[int(elapsed / 0.12) % len(ACTIVITY_FRAMES)]
        return "  {} Trabalhando… {} s".format(frame, int(elapsed))

    def _layout(self):
        content = HSplit([
            Window(FormattedTextControl("  Guará 1  /  OrbeIA"), height=1, style="class:title"),
            Window(FormattedTextControl("  Assistente pessoal local · conversa em português"),
                   height=1, style="class:subtitle"),
            Window(height=1),
            VSplit([Window(width=2), self.transcript, Window(width=2)]),
            ConditionalContainer(
                Window(FormattedTextControl(self.activity_label), height=1, style="class:activity"),
                filter=Condition(lambda: self.busy),
            ),
            Window(FormattedTextControl("  Shift+Enter nova linha · PgUp/PgDn rolar"),
                   height=1, style="class:subtitle"),
            Window(height=1, char="─", style="class:border"),
            HSplit([
                Window(height=1, style="class:input"),
                VSplit([
                    HSplit([Window(FormattedTextControl(PROMPT_MARKER), height=1, style="class:input")],
                           align=VerticalAlign.TOP, width=3, style="class:input"),
                    self.editor,
                    Window(width=2, style="class:input"),
                ], height=self.editor_height),
                Window(height=1, style="class:input"),
            ], style="class:input"),
            Window(height=1, char="─", style="class:border"),
            VSplit([
                Window(FormattedTextControl(self.model_label),
                       width=Dimension(min=22, preferred=26), height=1, style="class:model"),
                Window(FormattedTextControl(self.status_label), height=1, style="class:status"),
            ], height=1),
        ])
        return FloatContainer(content=content, floats=[
            Float(xcursor=True, ycursor=True, content=CompletionsMenu(max_height=4, scroll_offset=0)),
        ])

    def complete_command(self):
        buffer = self.editor.buffer
        state = buffer.complete_state
        if state is not None:
            completion = state.current_completion or state.completions[0]
        else:
            matches = list(buffer.completer.get_completions(buffer.document, CompleteEvent(completion_requested=True)))
            if not matches:
                return False
            completion = matches[0]
        buffer.apply_completion(completion)
        return True

    def _bindings(self):
        keys = KeyBindings()

        @keys.add("enter")
        def send(event):
            prompt = self.editor.text.strip()
            state = self.editor.buffer.complete_state
            if state is not None and state.current_completion is not None:
                self.complete_command()
                return
            if prompt.startswith("/") and prompt.lower() not in dict(COMMANDS):
                if self.complete_command():
                    return
            if prompt.lower() == "/sair":
                event.app.exit()
                return
            if self.busy or not prompt:
                return
            self.busy = True
            self.activity_started = time.monotonic()
            self.editor.text = ""
            event.app.create_background_task(self._send(prompt))

        @keys.add("tab")
        def complete(event):
            if not self.complete_command() and not self.editor.text.startswith("/"):
                self.editor.buffer.insert_text("    ")

        @keys.add("escape", filter=Condition(lambda: self.editor.buffer.complete_state is not None))
        def close_menu(event):
            self.editor.buffer.cancel_completion()

        @keys.add("c-j")
        # Windows Terminal pode enviar ESC + CR ao pressionar Shift+Enter.
        @keys.add("escape", "enter")
        def newline(event):
            self.editor.buffer.insert_text("\n")

        @keys.add("c-c")
        def exit_app(event):
            event.app.exit()

        @keys.add("c-d")
        def eof(event):
            if not self.editor.text:
                event.app.exit()
            else:
                self.editor.buffer.delete()

        @keys.add("pageup")
        def scroll_up(event):
            self.transcript.buffer.cursor_up(count=8)

        @keys.add("pagedown")
        def scroll_down(event):
            self.transcript.buffer.cursor_down(count=8)

        @keys.add("c-end")
        def bottom(event):
            self.transcript.buffer.cursor_position = len(self.transcript.text)

        return keys

    def append(self, speaker, text):
        # TextArea mostra texto literal: saídas não são interpretadas como HTML ou ANSI.
        text = "".join(c for c in text if c in "\n\t" or (ord(c) >= 32 and not 127 <= ord(c) < 160))
        self._messages.append((speaker, text.expandtabs(4)))
        while len(self._messages) > 1 and sum(len(t) + 4 for _, t in self._messages) > MAX_TRANSCRIPT_CHARS:
            self._messages.pop(0)
        if len(self._messages[-1][1]) > MAX_TRANSCRIPT_CHARS - 4:
            self._messages[-1] = (speaker, self._messages[-1][1][-(MAX_TRANSCRIPT_CHARS - 4):])
        self._render_transcript()
        self.application.invalidate()

    async def _send(self, prompt):
        self.append("Você", prompt)
        try:
            reply = await submit_in_thread(self.conversation, prompt)
            if reply.exit:
                self.application.exit()
                return
            if reply.clear:
                self._messages = [("welcome", WELCOME.rstrip())]
                self._render_transcript()
            if reply.text:
                self.append("Aviso" if reply.kind in ("error", "system") else "Guará 1", reply.text)
            if reply.limited:
                self.append("Aviso", "A resposta atingiu o limite de geração e pode estar incompleta.")
        except asyncio.CancelledError:
            raise
        except Exception:
            self.append("Aviso", "Não foi possível concluir a resposta. Tente novamente.")
        finally:
            self.busy = False
            self.activity_started = None
            self.application.invalidate()

    def run(self):
        self.application.run()
