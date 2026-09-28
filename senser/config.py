"""Load `senser.toml`.

Lookup order: `--config`, `$SENSER_CONFIG`, `./senser.toml`,
`~/.config/senser/senser.toml`. Relative paths in the file are
resolved against the file's directory.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

CONFIG_NAME = "senser.toml"


@dataclass(frozen=True)
class Config:
    cards_dir: Path
    db_path: Path
    new_per_day: int = 15
    desired_retention: float = 0.9


def find_config(explicit: Path | None = None) -> Path | None:
    if explicit is not None:
        path = explicit.expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"config file not found: {path}")
        return path
    candidates = [
        os.environ.get("SENSER_CONFIG"),
        Path.cwd() / CONFIG_NAME,
        Path.home() / ".config" / "senser" / CONFIG_NAME,
    ]
    for candidate in candidates:
        if candidate and Path(candidate).expanduser().is_file():
            return Path(candidate).expanduser()
    return None


def load_config(explicit: Path | None = None) -> Config:
    path = find_config(explicit)
    data = tomllib.loads(path.read_text(encoding="utf-8")) if path else {}
    base = path.parent if path else Path.cwd()

    def resolve(value: str) -> Path:
        resolved = Path(value).expanduser()
        return resolved if resolved.is_absolute() else (base / resolved).resolve()

    return Config(
        cards_dir=resolve(data.get("cards_dir", "cards")),
        db_path=resolve(data.get("db_path", "~/.senser/state.db")),
        new_per_day=int(data.get("new_per_day", 15)),
        desired_retention=float(data.get("desired_retention", 0.9)),
    )
