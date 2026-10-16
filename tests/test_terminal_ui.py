"""Exercitar entrada e renderização reais do prompt_toolkit, sem Ollama."""

import asyncio
import threading
import unittest
from unittest.mock import patch

from prompt_toolkit.data_structures import Size
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from app import Conversation, Reply
from terminal_ui import MAX_TRANSCRIPT_CHARS, TerminalUI, CommandCompleter
from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document
import app


class SizedOutput(DummyOutput):
    def __init__(self, rows=24, columns=80):
        self.rows, self.columns = rows, columns

    def get_size(self):
        return Size(rows=self.rows, columns=self.columns)


def screen_lines(ui, output):
    screen = ui.application.renderer.last_rendered_screen
    return ["".join(screen.data_buffer[y][x].char for x in range(output.columns))
            for y in range(output.rows)]


async def until(predicate, timeout=3):
    async def poll():
        while not predicate():
            await asyncio.sleep(0.01)
    await asyncio.wait_for(poll(), timeout)


class LaunchTests(unittest.TestCase):
    def test_command_completer_filters_only_commands(self):
        completer = CommandCompleter()
        def options(text):
            return [item.text for item in completer.get_completions(Document(text, len(text)), CompleteEvent())]
        self.assertEqual(options("/"), ["/limpar", "/conversar", "/arquivo", "/sair"])
        self.assertEqual(options("/li"), ["/limpar"])
        self.assertEqual(options("/inexistente"), [])
        self.assertEqual(options("texto /li"), [])
        self.assertEqual(options("/arquivo README.md"), [])

    def test_interactive_terminal_uses_visual_interface_by_default(self):
        with patch("sys.stdin.isatty", return_value=True), patch("sys.stdout.isatty", return_value=True), patch(
            "terminal_ui.TerminalUI"
        ) as terminal:
            app.launch([])
            terminal.return_value.run.assert_called_once()

    def test_redirected_input_uses_plain_interface(self):
        with patch("sys.stdin.isatty", return_value=False), patch("app.main") as plain:
            app.launch([])
            plain.assert_called_once()

    def test_text_flag_overrides_interactive_terminal(self):
        with patch("sys.stdin.isatty", return_value=True), patch("sys.stdout.isatty", return_value=True), patch(
            "app.main"
        ) as plain:
            app.launch(["--texto"])
            plain.assert_called_once()


class TerminalTests(unittest.IsolatedAsyncioTestCase):
    async def test_slash_menu_filters_and_tab_fills_without_submitting(self):
        with create_pipe_input() as pipe, patch("app.chat") as chat:
            output = SizedOutput()
            ui = TerminalUI(Conversation(), input=pipe, output=output)
            task = asyncio.create_task(ui.application.run_async())
            try:
                await until(lambda: ui.application.is_running)
                pipe.send_text("/")
                await until(lambda: ui.editor.buffer.complete_state is not None)
                await until(lambda: "Reiniciar sessão" in "\n".join(screen_lines(ui, output)))
                self.assertEqual(len(ui.editor.buffer.complete_state.completions), 4)
                self.assertTrue(screen_lines(ui, output)[-1].startswith("  Guará-1"))
                pipe.send_text("li")
                await until(lambda: ui.editor.buffer.complete_state is not None
                            and len(ui.editor.buffer.complete_state.completions) == 1)
                pipe.send_text("\t")
                await until(lambda: ui.editor.text == "/limpar")
                chat.assert_not_called()
                self.assertIsNone(ui.conversation.facts.first_message)
                pipe.send_text("\r")
                await until(lambda: "Histórico da sessão limpo" in ui.transcript.text and not ui.busy)
            finally:
                ui.application.exit()
                await task

    async def test_menu_arrow_selection_and_escape(self):
        with create_pipe_input() as pipe:
            ui = TerminalUI(Conversation(), input=pipe, output=SizedOutput(rows=12, columns=40))
            task = asyncio.create_task(ui.application.run_async())
            try:
                await until(lambda: ui.application.is_running)
                pipe.send_text("/")
                await until(lambda: ui.editor.buffer.complete_state is not None)
                pipe.send_text("\x1b[B")
                await until(lambda: ui.editor.buffer.complete_state.current_completion is not None)
                selected = ui.editor.buffer.complete_state.current_completion.text
                pipe.send_text("\t")
                await until(lambda: ui.editor.text == selected and ui.editor.buffer.complete_state is None)
                ui.editor.text = "/"
                ui.editor.buffer.cursor_position = 1
                ui.editor.buffer.start_completion(select_first=False)
                await until(lambda: ui.editor.buffer.complete_state is not None)
                pipe.send_text("\x1b")
                await until(lambda: ui.editor.buffer.complete_state is None)
                self.assertEqual(ui.editor.text, "/")
            finally:
                ui.application.exit()
                await task

    async def test_footer_and_input_stay_at_bottom_across_sizes(self):
        for rows, columns in ((24, 80), (36, 120), (12, 40)):
            with self.subTest(size=(rows, columns)), create_pipe_input() as pipe:
                output = SizedOutput(rows, columns)
                ui = TerminalUI(Conversation(), input=pipe, output=output)
                task = asyncio.create_task(ui.application.run_async())
                try:
                    await until(lambda: ui.application.renderer.last_rendered_screen is not None)
                    lines = screen_lines(ui, output)
                    self.assertTrue(lines[-1].startswith("  Guará-1"), lines[-1])
                    self.assertIn("Qwen3-1.7B", lines[-1])
                    self.assertTrue(any(">" in line for line in lines[-5:-1]))
                    self.assertIn("Guará 1", lines[0])
                finally:
                    ui.application.exit()
                    await task

    async def test_submit_refusal_recovery_and_clear_use_shared_engine(self):
        with create_pipe_input() as pipe, patch("app.chat", return_value=("Olá!", False)):
            ui = TerminalUI(Conversation(), input=pipe, output=SizedOutput())
            task = asyncio.create_task(ui.application.run_async())
            try:
                await until(lambda: ui.application.is_running)
                pipe.send_text("Leia README.md\r")
                await until(lambda: "Nenhum arquivo foi lido" in ui.transcript.text and not ui.busy)
                pipe.send_text("Olá\r")
                await until(lambda: "Olá!" in ui.transcript.text and not ui.busy)
                self.assertEqual(ui.conversation.facts.first_message, "Leia README.md")
                pipe.send_text("/limpar\r")
                await until(lambda: "Histórico da sessão limpo" in ui.transcript.text and not ui.busy)
                self.assertNotIn("Leia README.md", ui.transcript.text)
                self.assertIsNone(ui.conversation.facts.first_message)
                pipe.send_text("/sair\r")
                await asyncio.wait_for(task, 2)
            finally:
                if not task.done():
                    ui.application.exit()
                    await task

    async def test_busy_prevents_concurrent_submits_and_ctrl_c_exits(self):
        entered, release = threading.Event(), threading.Event()
        calls = []

        class SlowConversation:
            model = "guara1"

            def submit(self, prompt):
                calls.append(prompt)
                entered.set()
                release.wait(5)
                return Reply("Concluído", "model")

        with create_pipe_input() as pipe:
            ui = TerminalUI(SlowConversation(), input=pipe, output=SizedOutput())
            task = asyncio.create_task(ui.application.run_async())
            try:
                await until(lambda: ui.application.is_running)
                pipe.send_text("Primeiro\r")
                await until(entered.is_set)
                self.assertIn("Trabalhando", ui.status_label())
                await until(lambda: any("Trabalhando" in line for line in screen_lines(ui, ui.application.output)))
                old_activity = ui.activity_label()
                await until(lambda: ui.activity_label() != old_activity)
                self.assertIn("Trabalhando", "\n".join(screen_lines(ui, ui.application.output)))
                pipe.send_text("Rascunho\r")
                await until(lambda: ui.editor.text == "Rascunho")
                self.assertEqual(calls, ["Primeiro"])
                pipe.send_text("\x03")
                await asyncio.wait_for(task, 1)
            finally:
                release.set()
                if not task.done():
                    ui.application.exit()
                    await task

    async def test_multiline_input_and_literal_response(self):
        with create_pipe_input() as pipe, patch("app.chat", return_value=("<b>Texto</b>\x1b[31m", False)):
            ui = TerminalUI(Conversation(), input=pipe, output=SizedOutput())
            task = asyncio.create_task(ui.application.run_async())
            try:
                await until(lambda: ui.application.is_running)
                pipe.send_text("Linha 1\x1b[13;2uLinha 2\r")
                await until(lambda: "<b>Texto</b>" in ui.transcript.text and not ui.busy)
                self.assertEqual(ui.conversation.facts.first_message, "Linha 1\nLinha 2")
                self.assertNotIn("\x1b", ui.transcript.text)
            finally:
                ui.application.exit()
                await task

    async def test_scrolling_long_conversation_keeps_footer(self):
        with create_pipe_input() as pipe:
            output = SizedOutput()
            ui = TerminalUI(Conversation(), input=pipe, output=output)
            ui.append("Guará 1", "\n".join("Linha {}".format(i) for i in range(100)))
            task = asyncio.create_task(ui.application.run_async())
            try:
                await until(lambda: ui.application.renderer.last_rendered_screen is not None)
                before = ui.transcript.buffer.cursor_position
                pipe.send_text("\x1b[5~")
                await until(lambda: ui.transcript.buffer.cursor_position < before)
                self.assertTrue(screen_lines(ui, output)[-1].startswith("  Guará-1"))
                ui.append("Guará 1", "x" * MAX_TRANSCRIPT_CHARS)
                self.assertLessEqual(len(ui.transcript.text), MAX_TRANSCRIPT_CHARS)
            finally:
                ui.application.exit()
                await task

    async def test_user_background_without_speaker_labels_or_terminal_background(self):
        with create_pipe_input() as pipe:
            output = SizedOutput()
            ui = TerminalUI(Conversation(), input=pipe, output=output)
            ui.append("Você", "Minha mensagem")
            ui.append("Guará 1", "Resposta do assistente")
            task = asyncio.create_task(ui.application.run_async())
            try:
                await until(lambda: ui.application.renderer.last_rendered_screen is not None)
                lines = screen_lines(ui, output)
                self.assertNotIn("\nVocê\n", ui.transcript.text)
                self.assertNotIn("\nGuará 1\n", ui.transcript.text)
                self.assertIn(" > Minha mensagem", ui.transcript.text)
                user_row = next(i for i, line in enumerate(lines) if "Minha mensagem" in line)
                answer_row = next(i for i, line in enumerate(lines) if "Resposta do assistente" in line)
                screen = ui.application.renderer.last_rendered_screen

                def background(row, col):
                    return ui.application.style.get_attrs_for_style_str(screen.data_buffer[row][col].style).bgcolor

                self.assertEqual(background(user_row, 2), "1b1f29")
                self.assertEqual(background(user_row, output.columns - 5), "1b1f29")
                self.assertIn(background(answer_row, 2), ("", "default"))
                self.assertIn(background(2, 0), ("", "default"))
            finally:
                ui.application.exit()
                await task

    async def test_input_grows_with_newlines_and_wrap_and_marker_is_centered(self):
        with create_pipe_input() as pipe:
            output = SizedOutput()
            ui = TerminalUI(Conversation(), input=pipe, output=output)
            task = asyncio.create_task(ui.application.run_async())
            try:
                await until(lambda: ui.editor.window.render_info is not None)
                self.assertEqual(ui.editor.window.render_info.window_height, 1)
                pipe.send_text("Linha 1\x1b[13;2uLinha 2\x1b[13;2uLinha 3")
                await until(lambda: ui.editor.window.render_info.window_height == 3)
                screen = ui.application.renderer.last_rendered_screen
                lines = screen_lines(ui, output)
                marker_row = next(i for i, line in enumerate(lines) if line.startswith(" > "))
                input_rows = [i for i in range(output.rows) if "class:input" in screen.data_buffer[i][0].style]
                self.assertLessEqual(abs(marker_row - (min(input_rows) + max(input_rows)) / 2), 0.5)
                self.assertTrue(lines[-1].startswith("  Guará-1"))
                ui.editor.text = "x" * 160
                ui.application.invalidate()
                await until(lambda: ui.editor.window.render_info.window_height == 3)
                self.assertEqual(ui.editor_height(), 3)
                ui.editor.text = ""
                ui.application.invalidate()
                await until(lambda: ui.editor.window.render_info.window_height == 1)
            finally:
                ui.application.exit()
                await task

    async def test_activity_disappears_after_reply_or_error(self):
        for kind in ("model", "error"):
            entered, release = threading.Event(), threading.Event()

            class WaitingConversation:
                model = "guara1"

                def submit(self, prompt):
                    entered.set()
                    release.wait(3)
                    return Reply("Resultado concluído", kind)

            with self.subTest(kind=kind), create_pipe_input() as pipe:
                output = SizedOutput(rows=12, columns=40)
                ui = TerminalUI(WaitingConversation(), input=pipe, output=output)
                task = asyncio.create_task(ui.application.run_async())
                try:
                    await until(lambda: ui.application.is_running)
                    pipe.send_text("Mensagem\r")
                    await until(entered.is_set)
                    await until(lambda: any("Trabalhando" in line for line in screen_lines(ui, output)))
                    pipe.send_text("Rascunho\x1b[13;2uSegunda linha\x1b[13;2uTerceira linha")
                    await until(lambda: ui.editor.buffer.document.line_count == 3)
                    self.assertTrue(screen_lines(ui, output)[-1].startswith("  Guará-1"))
                    release.set()
                    await until(lambda: "Resultado concluído" in ui.transcript.text and not ui.busy)
                    await until(lambda: not any("Trabalhando" in line for line in screen_lines(ui, output)))
                    self.assertIsNone(ui.activity_started)
                    self.assertIn("Pronto", ui.status_label())
                finally:
                    release.set()
                    ui.application.exit()
                    await task


if __name__ == "__main__":
    unittest.main()
