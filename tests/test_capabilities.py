"""Reconhecedores de referências usados para evitar respostas sem leitura."""
import unittest
from guara.core.capabilities import mentions_file, is_file_followup

class CapabilityTests(unittest.TestCase):
    def test_references(self):
        for prompt in ("Leia README.md", "abra o arquivo", "liste o diretório", r"abra C:\dados\notas", "veja ../privado"):
            self.assertTrue(mentions_file(prompt))
        for prompt in ("Olá", "Explique listas", "Quanto é 2 + 2?"):
            self.assertFalse(mentions_file(prompt))

    def test_followups(self):
        for prompt in ("Me traga a última frase", "E como termina?", "Resuma", "Qual o conteúdo?"):
            self.assertTrue(is_file_followup(prompt))
        self.assertFalse(is_file_followup("Olá"))
