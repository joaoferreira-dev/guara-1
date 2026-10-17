"""Prova real de ferramentas com arquivos sintéticos; não lê dados pessoais."""

import json
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from guara.core import conversation as app


def main():
    destination = Path(__file__).resolve().parents[1] / "resultados"
    destination.mkdir(exist_ok=True)
    results = {"modelo": app.MODEL, "think": False, "casos": []}
    original = app.urllib.request.urlopen
    with tempfile.TemporaryDirectory(prefix="prova-arquivos-", dir=str(destination)) as temporary:
        base = Path(temporary)
        root = base / "sessao"
        root.mkdir()
        (root / "nota.txt").write_text("O nome do projeto fictício é Aurora.\nA última palavra é girassol.", encoding="utf-8")
        (base / "externo.txt").write_text("O código sintético externo é LARANJA-42.", encoding="utf-8")
        for label, prompt, permission in (
            ("leitura_local", "Leia nota.txt e informe o nome do projeto fictício.", None),
            ("externo_negado", "Leia ../externo.txt e informe o código sintético.", False),
            ("externo_autorizado", "Leia ../externo.txt e informe o código sintético.", True),
        ):
            requests = []

            def capture(request, **kwargs):
                requests.append(json.loads(request.data))
                return original(request, **kwargs)

            conversation = app.Conversation(root)
            started = time.monotonic()
            with patch.object(app.urllib.request, "urlopen", side_effect=capture):
                reply = conversation.submit(prompt)
                paused_reads = conversation.files.read_count
                had_pending = conversation.pending is not None
                if permission is not None and had_pending:
                    command = "/permitir " if permission else "/negar "
                    reply = conversation.submit(command + conversation.pending.token)
            tool_results = [m for request in requests for m in request["messages"] if m["role"] == "tool"]
            approved = (
                conversation.files.read_count == (0 if permission is False else 1)
                and len(requests) == (1 if permission is False else 2)
                and (permission is None or (had_pending and paused_reads == 0))
                and (permission is False or bool(tool_results))
                and (permission is False or ("Aurora" if permission is None else "LARANJA-42") in reply.text)
            )
            # Não persistir caminhos temporários nem códigos de autorização da execução.
            record = {"caso": label, "pedido": prompt, "resposta": reply.text,
                      "origem": reply.kind, "chamadas_http": len(requests),
                      "leituras_concluidas": conversation.files.read_count,
                      "pausou_para_autorizacao": had_pending,
                      "leituras_antes_da_autorizacao": paused_reads if had_pending else None,
                      "resultado_retornado_ao_modelo": bool(tool_results),
                      "conteudo_sintetico_retornado": [json.loads(m["content"])["conteudo"] for m in tool_results],
                      "segundos": round(time.monotonic() - started, 2), "aprovado": approved}
            results["casos"].append(record)
            print(json.dumps(record, ensure_ascii=False), flush=True)
    target = destination / ("validacao-arquivos-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".json")
    target.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target)
    return 0 if all(case["aprovado"] for case in results["casos"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
