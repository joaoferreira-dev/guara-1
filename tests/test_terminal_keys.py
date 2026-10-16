"""Distinguir Shift+Enter de Enter no parser VT e nos eventos Windows."""

import sys
import unittest

from prompt_toolkit.input.vt100_parser import Vt100Parser
from prompt_toolkit.keys import Keys

from terminal_keys import configure_shift_enter


class TerminalKeyTests(unittest.TestCase):
    def test_shift_enter_sequences_and_plain_enter_are_distinct(self):
        configure_shift_enter()
        for sequence, expected in (("\x1b[13;2u", Keys.ControlJ),
                                   ("\x1b[27;2;13~", Keys.ControlJ), ("\r", Keys.ControlM)):
            with self.subTest(sequence=sequence):
                keys = []
                parser = Vt100Parser(keys.append)
                parser.feed(sequence)
                parser.flush()
                self.assertEqual([key.key for key in keys], [expected])

    @unittest.skipUnless(sys.platform == "win32", "Eventos nativos exclusivos do Windows")
    def test_native_windows_shift_enter_does_not_submit(self):
        from prompt_toolkit.win32_types import KEY_EVENT_RECORD
        from terminal_keys import ShiftEnterConsoleReader

        # Traduzir eventos sintéticos sem abrir ou alterar o console.
        reader = ShiftEnterConsoleReader.__new__(ShiftEnterConsoleReader)
        event = KEY_EVENT_RECORD()
        event.KeyDown = True
        event.VirtualKeyCode = 13
        event.uChar.UnicodeChar = "\r"
        for modifiers, expected in ((0, Keys.ControlM), (reader.SHIFT_PRESSED, Keys.ControlJ)):
            event.ControlKeyState = modifiers
            self.assertEqual([key.key for key in reader._event_to_key_presses(event)], [expected])


if __name__ == "__main__":
    unittest.main()
