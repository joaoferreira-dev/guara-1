"""Compatibilidade de Shift+Enter com prompt_toolkit 3.0.52."""

import sys

from prompt_toolkit.input import create_input
from prompt_toolkit.input.ansi_escape_sequences import ANSI_SEQUENCES
from prompt_toolkit.input.vt100_parser import _IS_PREFIX_OF_LONGER_MATCH_CACHE
from prompt_toolkit.keys import Keys


def configure_shift_enter():
    # CSI-u e modifyOtherKeys preservam o modificador em terminais VT.
    sequences = ("\x1b[13;2u", "\x1b[27;2;13~")
    if any(ANSI_SEQUENCES.get(sequence) != Keys.ControlJ for sequence in sequences):
        for sequence in sequences:
            ANSI_SEQUENCES[sequence] = Keys.ControlJ
        _IS_PREFIX_OF_LONGER_MATCH_CACHE.clear()


if sys.platform == "win32":
    from prompt_toolkit.input.win32 import ConsoleInputReader, Win32Input
    from prompt_toolkit.key_binding.key_processor import KeyPress

    class ShiftEnterConsoleReader(ConsoleInputReader):
        def _event_to_key_presses(self, event):
            modifiers = event.ControlKeyState
            if (event.VirtualKeyCode == 13 and modifiers & self.SHIFT_PRESSED
                    and not modifiers & (self.LEFT_CTRL_PRESSED | self.RIGHT_CTRL_PRESSED
                                         | self.LEFT_ALT_PRESSED | self.RIGHT_ALT_PRESSED)):
                return [KeyPress(Keys.ControlJ, "\n")]
            return super()._event_to_key_presses(event)


def create_terminal_input():
    configure_shift_enter()
    terminal_input = create_input()
    if sys.platform == "win32" and isinstance(terminal_input, Win32Input):
        # Win32Input prefere o leitor VT quando o console o permite. Nesse
        # caminho, Enter pode chegar sem modificadores. Ler os eventos nativos
        # preserva SHIFT_PRESSED e mantém o atalho distinto de Enter.
        terminal_input.console_input_reader.close()
        terminal_input._use_virtual_terminal_input = False
        terminal_input.console_input_reader = ShiftEnterConsoleReader()
    return terminal_input
