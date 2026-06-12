from __future__ import annotations

from typing import Any

from evigraph.methods import MethodRunner


class EviGraphPipeline:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.runner = MethodRunner(config)

    def run(self, query: str, corpus_path: str | None = None, top_k: int = 8) -> dict[str, Any]:
        return self.runner.run(query, "full_evigraph", corpus_path, top_k)
