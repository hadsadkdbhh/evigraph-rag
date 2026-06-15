from __future__ import annotations

import os
import sys


REQUIRED = ["LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL"]


def main() -> int:
    provider = os.getenv("LLM_PROVIDER", "openai_compatible")
    missing = [name for name in REQUIRED if not os.getenv(name)]
    if provider != "openai_compatible":
        print(f"Unsupported LLM_PROVIDER for planner smoke: {provider}")
        return 1
    if missing:
        print("LLM numeric planner is not ready.")
        print("Missing environment variables: " + ", ".join(missing))
        print("Set LLM_PROVIDER=openai_compatible plus LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL.")
        return 1
    print("LLM numeric planner environment looks ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
