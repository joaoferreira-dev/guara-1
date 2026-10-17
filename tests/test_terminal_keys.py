"""Distinguir Shift+Enter de Enter no parser VT e nos eventos Windows."""

import sys
import unittest
from unittest.mock import Mock, patch

from prompt_toolkit.input.vt100_parser import Vt100Parser
from prompt_toolkit.keys import Keys

from guara.terminal.keys import configure_shift_enter


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
        from guara.terminal.keys import ShiftEnterConsoleReader

        # Traduzir eventos sintéticos sem abrir ou alterar o console.
        reader = ShiftEnterConsoleReader.__new__(ShiftEnterConsoleReader)
        event = KEY_EVENT_RECORD()
        event.KeyDown = True
        event.VirtualKeyCode = 13
        event.uChar.UnicodeChar = "\r"
        for modifiers, expected in ((0, Keys.ControlM), (reader.SHIFT_PRESSED, Keys.ControlJ)):
            event.ControlKeyState = modifiers
            self.assertEqual([key.key for key in reader._event_to_key_presses(event)], [expected])

    @unittest.skipUnless(sys.platform == "win32", "Backend exclusivo do Windows")
    def test_vt_backend_is_replaced_and_raw_mode_preserves_native_modifiers(self):
        from prompt_toolkit.input.win32 import Win32Input
        from guara.terminal.keys import create_terminal_input

        terminal_input = Win32Input.__new__(Win32Input)
        previous_reader = Mock()
        terminal_input.console_input_reader = previous_reader
        terminal_input._use_virtual_terminal_input = True
        native_reader = Mock()
        with patch("guara.terminal.keys.create_input", return_value=terminal_input), patch(
            "guara.terminal.keys.ShiftEnterConsoleReader", return_value=native_reader
        ), patch("prompt_toolkit.input.win32.raw_mode") as raw_mode:
            result = create_terminal_input()
            self.assertIs(result.console_input_reader, native_reader)
            self.assertFalse(result._use_virtual_terminal_input)
            previous_reader.close.assert_called_once()
            result.raw_mode()
            raw_mode.assert_called_once_with(use_win10_virtual_terminal_input=False)


if __name__ == "__main__":
    unittest.main()
