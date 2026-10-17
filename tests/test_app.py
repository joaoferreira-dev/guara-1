"""Verificações da integração sem chamar o modelo."""

import io
import json
import socket
import unittest
import urllib.error
from unittest.mock import patch, ANY

from guara.core import conversation as app
from guara import cli


def pair(prompt, answer, origin=None):
    messages = [{"role": "user", "content": prompt}, {"role": "assistant", "content": answer}]
    if origin:
        messages[-1]["origin"] = origin
    return messages


def response(content="Olá!", reason="stop"):
    return json.dumps({"done": True, "done_reason": reason,
                       "message": {"role": "assistant", "content": content}}).encode("utf-8")


class ChatTests(unittest.TestCase):
    def test_request_disables_thinking_and_keeps_history(self):
        history = pair("Estou aprendendo Python.", "Vamos praticar.")
        with patch("guara.core.conversation.urllib.request.urlopen") as open_url:
            open_url.return_value.__enter__.return_value.read.return_value = response("Python")
            self.assertEqual(app.chat(history, "Qual linguagem?"), ("Python", False))
            request = open_url.call_args.args[0]
            payload = json.loads(request.data)
            self.assertIs(payload["think"], False)
            self.assertEqual(payload["model"], "guara1")
            self.assertEqual(payload["messages"][0], {"role": "system", "content": app.SYSTEM_MESSAGE})
            self.assertEqual(payload["messages"][1:], history + [{"role": "user", "content": "Qual linguagem?"}])
            self.assertEqual(open_url.call_args.kwargs["timeout"], 30)

    def test_trim_discards_complete_old_turns_without_mutation(self):
        history = sum((pair(str(i), str(i)) for i in range(5)), [])
        self.assertEqual(app.trim_history(history), history[4:])
        self.assertEqual(len(history), 10)
        self.assertEqual(app.trim_history(pair("x" * 1000, "y" * 1000), 1000), [])

    def test_input_limits_prevent_network_calls(self):
        with patch("guara.core.conversation.urllib.request.urlopen") as open_url:
            for prompt in ("", " ", "x" * 1001):
                with self.subTest(prompt_length=len(prompt)), self.assertRaises(app.ChatError):
                    app.chat([], prompt)
            open_url.assert_not_called()

    def test_invalid_responses_are_rejected(self):
        invalid = [b"not JSON", b"[]", b"{}", response(""), response(None),
                   response("x" * 4001), b"x" * 65537,
                   b'{"done":true,"message":{"role":"user","content":"oi"}}']
        with patch("guara.core.conversation.urllib.request.urlopen") as open_url:
            for raw in invalid:
                with self.subTest(raw_length=len(raw)), self.assertRaises(app.ChatError):
                    open_url.return_value.__enter__.return_value.read.return_value = raw
                    app.chat([], "Oi")

    def test_network_errors_have_useful_messages(self):
        errors = [
            (socket.timeout(), "30 segundos"),
            (urllib.error.URLError(socket.timeout()), "30 segundos"),
            (urllib.error.URLError("conexão recusada"), "ativo"),
            (urllib.error.HTTPError(app.API_URL, 404, "ausente", {}, None), "ollama create"),
            (urllib.error.HTTPError(app.API_URL, 500, "erro", {}, None), "HTTP 500"),
        ]
        for error, expected in errors:
            with self.subTest(error=type(error).__name__), patch(
                "guara.core.conversation.urllib.request.urlopen", side_effect=error
            ), self.assertRaisesRegex(app.ChatError, expected):
                app.chat([], "Oi")

    def test_generation_limit_is_reported(self):
        with patch("guara.core.conversation.urllib.request.urlopen") as open_url:
            open_url.return_value.__enter__.return_value.read.return_value = response("Parcial", "length")
            self.assertEqual(app.chat([], "Oi"), ("Parcial", True))

    def test_clear_and_unknown_command_do_not_call_model(self):
        with patch("builtins.input", side_effect=["Oi", "/limpar", "/outro", "Novo", "/sair"]), patch(
            "guara.core.conversation.chat", return_value=("Olá", False)
        ) as chat, patch("sys.stdout", new_callable=io.StringIO) as output:
            cli.main()
            self.assertEqual(chat.call_count, 2)
            self.assertEqual(chat.call_args_list[1].args[0], [])
            self.assertIn("Comando desconhecido", output.getvalue())

    def test_failed_turn_is_recorded_as_application_error(self):
        with patch("builtins.input", side_effect=["Primeiro", "Falha", "Depois", "/sair"]), patch(
            "guara.core.conversation.chat", side_effect=[("Resposta", False), app.ChatError("erro"), ("OK", False)]
        ) as chat, patch("sys.stdout", new_callable=io.StringIO):
            cli.main()
            self.assertEqual(chat.call_args_list[2].args[0],
                             pair("Primeiro", "Resposta") + pair("Falha", "Aviso: erro", "error"))

    def test_eof_and_interrupt_exit_cleanly(self):
        for error in (EOFError, KeyboardInterrupt):
            with self.subTest(error=error), patch("builtins.input", side_effect=error), patch(
                "sys.stdout", new_callable=io.StringIO
            ) as output:
                cli.main()
                self.assertIn("Até mais", output.getvalue())

    def test_oversized_file_request_does_not_change_session(self):
        with patch("builtins.input", side_effect=["arquivo " + "x" * 1000, "Olá", "/sair"]), patch(
            "guara.core.conversation.chat", return_value=("Olá", False)
        ) as chat, patch("sys.stdout", new_callable=io.StringIO) as output:
            cli.main()
            chat.assert_called_once_with([], "Olá", files=ANY)
            self.assertIn("no máximo 1.000", output.getvalue())

    def test_legitimate_file_mentions_and_application_refusals_are_preserved(self):
        history = pair("O que você fez?", "Não li arquivos.") + pair(
            "Leia README.md", app.FILE_NOTICE, "file_unavailable"
        )
        with patch("guara.core.conversation.urllib.request.urlopen") as open_url:
            open_url.return_value.__enter__.return_value.read.return_value = response("4")
            self.assertEqual(app.chat(history, "Quanto é 2 + 2?"), ("4", False))
            messages = json.loads(open_url.call_args.args[0].data)["messages"]
            self.assertEqual(messages[1:3], history[:2])
            self.assertEqual(messages[3], history[2])
            self.assertIn("[Resposta da aplicação: file_unavailable]", messages[4]["content"])
            self.assertNotIn("origin", messages[4])
            self.assertEqual(len(history), 4)

    def test_session_facts_reset_with_clear_commands(self):
        for command in ("/limpar", "/conversar"):
            with self.subTest(command=command), patch(
                "builtins.input", side_effect=["Leia README.md", command, "Olá",
                                               "Qual foi minha primeira mensagem?", "/sair"]
            ), patch("guara.core.conversation.chat", return_value=("Oi", False)), patch(
                "sys.stdout", new_callable=io.StringIO
            ) as output:
                cli.main()
                self.assertIn('Sua primeira mensagem nesta sessão foi: "Olá"', output.getvalue())


if __name__ == "__main__":
    unittest.main()
