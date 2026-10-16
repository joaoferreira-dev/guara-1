"""Medição local da seção 2; usa apenas a biblioteca padrão do Python."""

import ctypes
import json
import platform
import sys
import threading
import time
import urllib.request
from datetime import datetime
from pathlib import Path


class MemoryStatus(ctypes.Structure):
    _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
        (name, ctypes.c_ulonglong)
        for name in ("total", "available", "page_total", "page_available", "virtual_total", "virtual_available", "extended")
    ]


def memory():
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise ctypes.WinError()
    return {"total_bytes": status.total, "available_bytes": status.available,
            "used_bytes": status.total - status.available}


def api(route, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request("http://localhost:11434/api/" + route, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as response:
        return json.load(response)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    output_dir = Path(__file__).resolve().parents[1] / "resultados" / "benchmarks"
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")
    output = output_dir / f"validacao-qwen-{timestamp}.json"
    print(f"Registro desta execução: {output}", flush=True)
    report = {"started_at": datetime.now().astimezone().isoformat(),
              "python": platform.python_version(), "ollama": api("version"),
              "models": api("tags"), "initial_running_models": api("ps"),
              "settings": {"think": False, "num_ctx": 2048, "num_predict": 256,
                           "temperature": 0, "seed": 42}, "tests": []}
    prompts = [
        ("conversa", "Responda em português brasileiro, em até duas frases: estou começando a aprender Python. Por onde começo?"),
        ("continuidade", "Qual foi a linguagem que eu disse que estou começando a aprender? Responda apenas com o nome."),
        ("problema", "Uma loja vende 3 cadernos por R$ 18 cada. Aplica 10% de desconto no total e depois cobra R$ 8 de frete. Qual é o valor final? Mostre a conta em até três linhas."),
        ("codigo", "Escreva apenas um bloco de código Python com uma função chamada soma_pares(numeros) que retorna a soma dos números pares de uma lista de inteiros. Deve funcionar com lista vazia e números negativos. Não use bibliotecas, entrada de usuário ou acesso a arquivos."),
    ]
    history = []
    for name, prompt in prompts:
        messages = history + [{"role": "user", "content": prompt}] if name == "continuidade" else [{"role": "user", "content": prompt}]
        baseline = memory()
        samples = [baseline]
        stop = threading.Event()

        def sample():
            while not stop.wait(0.25):
                samples.append(memory())

        worker = threading.Thread(target=sample, daemon=True)
        worker.start()
        started = time.perf_counter()
        try:
            result = api("chat", {"model": "qwen3:1.7b", "messages": messages,
                                  "stream": False, "think": False, "keep_alive": "10m",
                                  "options": {k: v for k, v in report["settings"].items() if k != "think"}})
        finally:
            elapsed = time.perf_counter() - started
            stop.set()
            worker.join()
        samples.append(memory())
        record = {"name": name, "messages": messages, "wall_seconds": elapsed,
                  "memory_before": baseline, "memory_after": samples[-1],
                  "system_used_peak_bytes": max(s["used_bytes"] for s in samples),
                  "memory_samples": len(samples), "running_models_after": api("ps"),
                  "response": result}
        report["tests"].append(record)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"test": name, "wall_seconds": round(elapsed, 3),
                          "response": result["message"]["content"],
                          "done_reason": result.get("done_reason")}, ensure_ascii=False), flush=True)
        if name == "conversa":
            history = messages + [result["message"]]
    report["finished_at"] = datetime.now().astimezone().isoformat()
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
