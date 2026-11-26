"""Load synthetic cases and illustrative policies."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def load_policies(data_dir: Path = DATA_DIR) -> dict[str, dict]:
    policies = {}
    for path in sorted((data_dir / "policies").glob("*.json")):
        policy = json.loads(path.read_text())
        policies[policy["policy_id"]] = policy
    return policies


def load_cases(data_dir: Path = DATA_DIR) -> list[dict]:
    return json.loads((data_dir / "cases.json").read_text())


def split_sentences(text: str) -> list[str]:
    """Split on sentence-ending punctuation followed by whitespace (keeps decimals like 43.2 intact)."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
