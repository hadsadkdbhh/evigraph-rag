from __future__ import annotations

import importlib.util
import os


REQUIRED_PACKAGES = [
    "sentence_transformers",
    "torch",
    "transformers",
    "sklearn",
]


def main() -> int:
    missing = [package for package in REQUIRED_PACKAGES if importlib.util.find_spec(package) is None]
    model_name = os.environ.get("EVIGRAPH_NEURAL_DENSE_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    print(f"EVIGRAPH_NEURAL_DENSE_MODEL={model_name}")
    if missing:
        print("missing=" + ",".join(missing))
        print("install: python -m pip install -r requirements-neural-retrieval.txt")
        return 1
    print("neural_retrieval_dependencies=available")
    print("next: python .\\scripts\\run_manifest.py --manifest .\\configs\\experiments.finqa_600.neural_retrieval_full_evigraph_v43.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
