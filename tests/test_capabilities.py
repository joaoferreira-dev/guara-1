"""Regressões do fluxo controlado de arquivos indisponíveis."""

import unittest

from guara.core.capabilities import CapabilitySession, FILE_NOTICE, mentions_file


class CapabilityTests(unittest.TestCase):
    def test_common_references_and_command_activate_file_mode(self):
        for prompt in ("Leia README.md", "ABRA O DOCUMENTO", "liste o diretório",
                       "acesse a PASTA", "consulte notas.TXT", r"abra C:\dados\notas",
                       "veja ../privado", "/arquivo", "/arquivo segredo"):
            with self.subTest(prompt=prompt):
                session = CapabilitySession()
                self.assertEqual(session.handle(prompt), FILE_NOTICE)
                self.assertEqual(session.handle("Como termina?"), FILE_NOTICE)

    def test_reset_releases_file_mode(self):
        session = CapabilitySession()
        session.handle("README.md")
        session.reset()
        self.assertIsNone(session.handle("Olá"))

    def test_ordinary_conversation_remains_available(self):
        session = CapabilitySession()
        for prompt in ("Olá", "Estou aprendendo Python", "Quanto é 3 vezes 4?", "Explique listas"):
            self.assertFalse(mentions_file(prompt))
            self.assertIsNone(session.handle(prompt))

    def test_new_topic_resumes_automatically(self):
        for prompt in ("teste", "Olá", "Quanto é 2 + 2?", "Explique listas em Python"):
            with self.subTest(prompt=prompt):
                session = CapabilitySession()
                session.handle("Leia README.md")
                self.assertIsNone(session.handle(prompt))
                self.assertFalse(session.file_mode)

    def test_related_followups_remain_blocked(self):
        session = CapabilitySession()
        session.handle("README.md")
        for prompt in ("Me traga a última frase", "E como termina?", "Resuma", "Qual o conteúdo?"):
            self.assertEqual(session.handle(prompt), FILE_NOTICE)


if __name__ == "__main__":
    unittest.main()
