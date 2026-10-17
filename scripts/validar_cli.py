"""Capturar o renderizador da CLI e, opcionalmente, conversar com Ollama real."""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from prompt_toolkit.data_structures import Size
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from guara.core.conversation import Conversation
from guara.terminal.interface import TerminalUI


class SizedOutput(DummyOutput):
    def __init__(self, rows, columns):
        self.rows, self.columns = rows, columns

    def get_size(self):
        return Size(rows=self.rows, columns=self.columns)


async def wait_until(predicate, timeout=40):
    async def poll():
        while not predicate():
            await asyncio.sleep(0.02)
    await asyncio.wait_for(poll(), timeout)


async def capture(rows, columns, real, sample=False):
    with create_pipe_input() as pipe:
        output = SizedOutput(rows, columns)
        ui = TerminalUI(Conversation(), input=pipe, output=output)
        validation_errors = []
        task = asyncio.create_task(ui.application.run_async())
        try:
            await wait_until(lambda: ui.application.renderer.last_rendered_screen is not None)
            if sample:
                ui.append("Você", "Quero uma conversa sem rótulos.\nEsta é a segunda linha da mensagem.")
                ui.append("Guará 1", "As respostas aparecem diretamente no corpo do terminal.")
                ui.editor.text = "Mensagem em edição\nSegunda linha\nTerceira linha"
            if real:
                pipe.send_text("Quanto é 2 + 2? Responda apenas o número.\r")
                await wait_until(lambda: ui.conversation.facts.counts["model"] == 1 and not ui.busy)
                pipe.send_text("Qual foi minha primeira mensagem?\r")
                await wait_until(lambda: ui.conversation.facts.counts["session_fact"] == 1 and not ui.busy)
                if "\n4\n" not in ui.transcript.text:
                    validation_errors.append("A resposta real a 2 + 2 não foi exatamente 4.")
            ui.application.invalidate()
            await asyncio.sleep(0.15)
            screen = ui.application.renderer.last_rendered_screen
            lines = ["".join(screen.data_buffer[y][x].char for x in range(columns)).rstrip()
                     for y in range(rows)]
            assert lines[-1].startswith("  Guará-1")
            backgrounds = []
            for row in range(rows):
                start, previous = 0, None
                for column in range(columns + 1):
                    color = (ui.application.style.get_attrs_for_style_str(
                        screen.data_buffer[row][column].style
                    ).bgcolor if column < columns else None)
                    if color != previous:
                        if previous not in (None, "", "default"):
                            backgrounds.append({"row": row, "start": start, "end": column, "color": previous})
                        start, previous = column, color
            return {"rows": rows, "columns": columns, "screen": lines,
                    "transcript": ui.transcript.text, "real_ollama": real,
                    "synthetic_sample": sample, "background_regions": backgrounds,
                    "validation_errors": validation_errors,
                    "input_height": ui.editor.window.render_info.window_height}
        finally:
            ui.application.exit()
            await task


async def main(real, sample=False):
    report = {"executed_at": datetime.now().astimezone().isoformat(), "captures": []}
    for rows, columns in ((24, 80), (36, 120), (12, 40)):
        report["captures"].append(await capture(rows, columns, real and columns == 80, sample))
    target = Path(__file__).resolve().parents[1] / "resultados" / (
        "validacao-cli-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".json"
    )
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(target)
    for item in report["captures"]:
        print("\n{} × {}".format(item["columns"], item["rows"]))
        print("\n".join("{:02d} {}".format(i, line) for i, line in enumerate(item["screen"])))

    return 1 if any(item["validation_errors"] for item in report["captures"]) else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--real", action="store_true", help="Fazer uma chamada real ao Ollama na captura 80×24.")
    parser.add_argument("--amostra", action="store_true", help="Mostrar mensagens sintéticas e entrada com três linhas.")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(main(args.real, args.amostra)))
