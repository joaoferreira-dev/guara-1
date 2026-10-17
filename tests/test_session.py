"""Fatos da sessão não dependem da geração de texto ou do contexto curto."""

import unittest

from guara.core import conversation as app
from guara.core.session import SessionFacts


class SessionTests(unittest.TestCase):
    def test_first_message_survives_rolling_history(self):
        facts = SessionFacts()
        history = app.remember([], facts, "Leia README.md", app.FILE_NOTICE, "file_unavailable")
        for index in range(10):
            history = app.remember(history, facts, "Pergunta {}".format(index), "Resposta", "model")
        self.assertEqual(len(history), 6)
        self.assertNotIn("README", str(history))
        self.assertEqual(facts.first_message, "Leia README.md")
        self.assertIn('"Leia README.md"', facts.answer("O que perguntei primeiro?"))

    def test_no_previous_message_is_not_invented(self):
        facts = SessionFacts()
        self.assertIn("Ainda não havia mensagem", facts.answer("Qual minha primeira pergunta?"))
        self.assertIsNone(facts.first_message)

    def test_record_sources_and_errors(self):
        facts = SessionFacts()
        for kind in facts.counts:
            facts.record("Mensagem", kind)
        self.assertEqual(facts.counts, {kind: 1 for kind in facts.counts})
        self.assertIn("1 falha(s) de integração", facts.answer("O que você já fez nessa conversa?"))
        with self.assertRaises(ValueError):
            facts.record("Mensagem", "origem inventada")

    def test_other_questions_are_not_answered_as_session_facts(self):
        facts = SessionFacts()
        for prompt in ("Qual foi a primeira linguagem de programação?", "Quem é você?", "Olá"):
            self.assertIsNone(facts.answer(prompt))


if __name__ == "__main__":
    unittest.main()
