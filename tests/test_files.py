"""Contratos, isolamento e ciclo HTTP com dados sintéticos."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from guara.core import conversation as app
from guara.tools import validate_call
from guara.tools.files import FileAccess, FileError, AccessRequired


def call(path="nota.txt", name="ler_arquivo", arguments=None):
    return {"function": {"name": name, "arguments": {"caminho": path} if arguments is None else arguments}}


def wire(content="", calls=None):
    message = {"role": "assistant", "content": content}
    if calls is not None:
        message["tool_calls"] = calls
    return json.dumps({"done": True, "message": message}).encode("utf-8")


class FileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "sessao"
        self.root.mkdir()
        self.note = self.root / "nota.txt"
        self.note.write_text("O projeto sintético chama-se Aurora.\nFim do exemplo.", encoding="utf-8")
        self.external = self.base / "externo.txt"
        self.external.write_text("Texto externo sintético.", encoding="utf-8")
        self.files = FileAccess(self.root)

    def http(self, responses):
        mock = patch("guara.core.conversation.urllib.request.urlopen").start()
        self.addCleanup(patch.stopall)
        mock.return_value.__enter__.return_value.read.side_effect = responses
        return mock

    def test_root_is_cwd_at_start_and_does_not_follow_later_chdir(self):
        with patch("guara.tools.files.Path.cwd", return_value=self.root):
            files = FileAccess()
        self.assertEqual(files.root, self.root)
        self.assertIn("Aurora", files.read(files.resolve({"caminho": "nota.txt"}))["conteudo"])

    def test_relative_absolute_and_nested_local_paths(self):
        for path in ("nota.txt", str(self.note), "sub/../nota.txt"):
            self.assertIn("Aurora", self.files.read(self.files.resolve({"caminho": path}))["conteudo"])
        self.assertEqual(self.files.read_count, 3)

    def test_external_requires_exact_approval_on_each_read(self):
        for path in ("../externo.txt", str(self.external)):
            resolved = self.files.resolve({"caminho": path})
            with self.assertRaises(AccessRequired):
                self.files.read(resolved)
            with self.assertRaises(AccessRequired):
                self.files.read(resolved, approved=self.note)
            self.assertIn("externo", self.files.read(resolved, approved=resolved)["conteudo"])
            with self.assertRaises(AccessRequired):
                self.files.read(resolved)

    def test_sibling_prefix_is_external(self):
        sibling = self.base / "sessao-outra"
        sibling.mkdir()
        path = sibling / "nota.txt"
        path.write_text("exemplo", encoding="utf-8")
        with self.assertRaises(AccessRequired):
            self.files.read(path)

    def test_formats_encoding_binary_and_size(self):
        for name, content in (("a.pdf", b"pdf"), ("a.txt", b"\xff"), ("b.txt", b"a\x00b"),
                              ("c.txt", b"a" * 4097), ("d.txt", b"a" * 2401)):
            (self.root / name).write_bytes(content)
            with self.subTest(name=name), self.assertRaises(FileError):
                self.files.read(self.files.resolve({"caminho": name}))
        self.assertEqual(self.files.read_count, 0)
        self.note.write_text("\ufeffOlá", encoding="utf-8")
        self.assertEqual(self.files.read(self.note)["conteudo"], "Olá")

    def test_missing_directory_and_invalid_paths(self):
        for path in ("ausente.txt", "pasta.txt"):
            if path.startswith("pasta"):
                (self.root / path).mkdir()
            with self.assertRaises(FileError):
                self.files.read(self.files.resolve({"caminho": path}))
        for path in ("", "a\x00.txt", "a.txt:segredo", r"\\servidor\a.txt", r"C:a.txt", "NUL.txt"):
            with self.subTest(path=path), self.assertRaises(FileError):
                self.files.resolve({"caminho": path})

    def test_strict_registry_and_arguments(self):
        for calls in ([call(name="calculadora")], [call(arguments={"caminho": 1})],
                      [call(arguments={"caminho": "nota.txt", "permitir": True})],
                      [call(arguments={})], [None], [call(), call()], "invalido", []):
            with self.subTest(calls=calls), self.assertRaises(FileError):
                validate_call(calls, self.files)

    def test_symlink_escape_requires_permission(self):
        link = self.root / "link.txt"
        try:
            link.symlink_to(self.external)
        except OSError as error:
            self.skipTest("Sistema não permitiu criar link simbólico: {}".format(error))
        path = self.files.resolve({"caminho": "link.txt"})
        self.assertEqual(path, self.external)
        with self.assertRaises(AccessRequired):
            self.files.read(path)

    def test_hardlinks_and_open_target_changes_are_rejected(self):
        link = self.root / "hard.txt"
        os.link(str(self.external), str(link))
        with self.assertRaises(FileError):
            self.files.read(link)
        with patch("guara.tools.files.opened_path", return_value=self.external), self.assertRaises(FileError):
            self.files.read(self.note)
        self.assertEqual(self.files.read_count, 0)

    def test_directory_link_and_changed_approved_target(self):
        directory = self.root / "atalho"
        try:
            directory.symlink_to(self.base, target_is_directory=True)
        except OSError as error:
            self.skipTest("Sistema não permitiu criar link simbólico: {}".format(error))
        path = self.files.resolve({"caminho": "atalho/externo.txt"})
        with self.assertRaises(AccessRequired):
            self.files.read(path)
        # Trocar o destino entre solicitação e aprovação não pode herdar permissão.
        another = self.base / "outro.txt"
        another.write_text("Outro texto sintético.", encoding="utf-8")
        self.external.unlink()
        self.external.symlink_to(another)
        with self.assertRaises(FileError):
            self.files.read(path, approved=path)
        self.assertEqual(self.files.read_count, 0)

    def test_http_cycle_contains_real_result_and_no_third_call(self):
        http = self.http([wire(calls=[call()]), wire("Aurora.")])
        self.assertEqual(app.chat([], "Leia nota.txt", self.files), ("Aurora.", False))
        self.assertEqual(http.call_count, 2)
        first, second = [json.loads(c.args[0].data) for c in http.call_args_list]
        self.assertEqual(first["tools"][0]["function"]["name"], "ler_arquivo")
        self.assertNotIn("tools", second)
        self.assertEqual(second["messages"][-1]["role"], "tool")
        self.assertIn("Aurora", second["messages"][-1]["content"])
        self.assertFalse(first["think"])
        self.assertEqual(self.files.read_count, 1)

    def test_model_receives_initial_directory_and_relative_readme_instruction(self):
        (self.root / "README.md").write_text("Projeto sintético Aurora.", encoding="utf-8")
        http = self.http([wire(calls=[call("README.md")]), wire("Aurora.")])
        conversation = app.Conversation(self.root)
        self.assertEqual(conversation.submit("Leia README.md").text, "Aurora.")
        requests = [json.loads(c.args[0].data) for c in http.call_args_list]
        for request in requests:
            context = request["messages"][0]["content"]
            self.assertIn(json.dumps(str(self.root), ensure_ascii=False), context)
            self.assertIn('{"caminho": "README.md"}', context)
            self.assertIn("Não invente pastas", context)
        self.assertEqual(requests[0]["messages"][-1]["content"], "Leia README.md")
        self.assertIsNone(conversation.pending)
        self.assertEqual(conversation.files.last_path, self.root / "README.md")

    def test_no_tool_means_no_invented_file_answer_and_topic_resumes(self):
        self.http([wire("Inventei um resumo"), wire("Inventei o final"), wire("Olá!")])
        conversation = app.Conversation(self.root)
        self.assertEqual(conversation.submit("Leia nota.txt").kind, "file_unavailable")
        self.assertEqual(conversation.submit("E como termina?").kind, "file_unavailable")
        self.assertEqual(conversation.submit("Olá").text, "Olá!")
        self.assertEqual(conversation.facts.first_message, "Leia nota.txt")
        self.assertEqual(conversation.files.read_count, 0)

    def test_new_topic_does_not_reuse_previous_file_for_continue(self):
        http = self.http([wire(calls=[call()]), wire("Aurora."),
                          wire("Listas guardam elementos."), wire("Exemplo: [1, 2].")])
        conversation = app.Conversation(self.root)
        conversation.submit("Leia nota.txt")
        conversation.submit("Explique listas em Python")
        reply = conversation.submit("Continue")
        self.assertEqual(reply.text, "Exemplo: [1, 2].")
        self.assertIsNone(conversation.files.last_path)
        self.assertEqual(conversation.files.read_count, 1)
        self.assertEqual(http.call_count, 4)

    def test_permission_pauses_and_resumes_only_exact_pending_call(self):
        http = self.http([wire(calls=[call("../externo.txt")]), wire("Texto externo sintético.")])
        conversation = app.Conversation(self.root)
        reply = conversation.submit("Leia ../externo.txt")
        self.assertIn(str(self.external), reply.text)
        self.assertEqual(http.call_count, 1)
        self.assertEqual(conversation.files.read_count, 0)
        token = conversation.pending.token
        conversation.submit("/permitir errado")
        self.assertIsNotNone(conversation.pending)
        self.assertEqual(conversation.submit("/permitir " + token).text, "Texto externo sintético.")
        self.assertEqual(conversation.files.read_count, 1)
        self.assertEqual(conversation.facts.file_reads, 1)
        conversation.submit("/permitir " + token)
        self.assertEqual(http.call_count, 2)
        self.assertIn("1", conversation.submit("O que você já fez nessa conversa?").text)

    def test_permission_request_preserves_first_message_after_cancellation(self):
        self.http([wire(calls=[call("../externo.txt")])])
        conversation = app.Conversation(self.root)
        conversation.submit("/arquivo ../externo.txt")
        self.assertEqual(conversation.facts.first_message, "/arquivo ../externo.txt")
        reply = conversation.submit("Qual foi minha primeira mensagem?")
        self.assertIn("/arquivo ../externo.txt", reply.text)
        self.assertIsNone(conversation.pending)
        self.assertEqual(conversation.files.read_count, 0)

    def test_final_network_failure_keeps_read_facts(self):
        self.http([wire(calls=[call()]), OSError("interrupção sintética")])
        conversation = app.Conversation(self.root)
        reply = conversation.submit("Leia nota.txt")
        self.assertEqual(reply.kind, "error")
        self.assertIn("O arquivo foi lido", reply.text)
        self.assertEqual(conversation.facts.file_reads, 1)

    def test_denial_new_topic_and_clear_cancel_pending(self):
        for action in ("deny", "Olá", "/limpar", "/conversar"):
            with self.subTest(action=action):
                http = self.http([wire(calls=[call("../externo.txt")]), wire("Olá")])
                conversation = app.Conversation(self.root)
                conversation.submit("Leia ../externo.txt")
                token = conversation.pending.token
                conversation.submit("/negar " + token if action == "deny" else action)
                self.assertIsNone(conversation.pending)
                conversation.submit("/permitir " + token)
                self.assertEqual(conversation.files.read_count, 0)
                self.assertEqual(http.call_count, 2 if action == "Olá" else 1)

    def test_second_call_cannot_execute_more_tools_and_facts_keep_actual_read(self):
        http = self.http([wire(calls=[call()]), wire(calls=[call("../externo.txt")])])
        conversation = app.Conversation(self.root)
        reply = conversation.submit("Leia nota.txt")
        self.assertEqual(reply.kind, "error")
        self.assertIsNone(conversation.pending)
        self.assertEqual(conversation.facts.file_reads, 1)
        self.assertEqual(http.call_count, 2)

    def test_global_launcher_keeps_cwd(self):
        import subprocess
        import sys
        launcher = Path(__file__).resolve().parents[1] / "scripts" / "iniciar_guara.py"
        result = subprocess.run([sys.executable, str(launcher), "--texto"], cwd=str(self.root),
                                input="/arquivo\n/sair\n", text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(self.root), result.stdout)
