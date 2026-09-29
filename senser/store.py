"""SQLite persistence for review state and history.

Card content lives in Markdown; this database only knows card ids.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import fsrs

SCHEMA = """
CREATE TABLE IF NOT EXISTS states (
    card_id TEXT PRIMARY KEY,
    fsrs    TEXT NOT NULL,
    due     TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reviews (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id     TEXT NOT NULL,
    rating      INTEGER NOT NULL,
    reviewed_at TEXT NOT NULL,
    duration_ms INTEGER
);
CREATE INDEX IF NOT EXISTS reviews_card ON reviews(card_id);
CREATE INDEX IF NOT EXISTS reviews_time ON reviews(reviewed_at);
"""


@dataclass(frozen=True)
class Review:
    card_id: str
    rating: int
    reviewed_at: datetime
    duration_ms: int | None


def _timestamp(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat()


class Store:
    def __init__(self, path: Path | str) -> None:
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        # The web app opens one store and uses it from the server's event-loop
        # thread; requests are handled one at a time, so sharing is safe.
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.executescript(SCHEMA)

    def __enter__(self) -> Store:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._db.close()

    def states(self) -> dict[str, fsrs.Card]:
        rows = self._db.execute("SELECT card_id, fsrs FROM states")
        return {card_id: fsrs.Card.from_json(data) for card_id, data in rows}

    def record(self, card_id: str, state: fsrs.Card, log: fsrs.ReviewLog, duration_ms: int | None = None) -> None:
        with self._db:
            self._db.execute(
                "INSERT INTO states (card_id, fsrs, due) VALUES (?, ?, ?) "
                "ON CONFLICT (card_id) DO UPDATE SET fsrs = excluded.fsrs, due = excluded.due",
                (card_id, state.to_json(), _timestamp(state.due)),
            )
            self._db.execute(
                "INSERT INTO reviews (card_id, rating, reviewed_at, duration_ms) VALUES (?, ?, ?, ?)",
                (card_id, int(log.rating), _timestamp(log.review_datetime), duration_ms),
            )

    def reviews(self, since: datetime | None = None) -> list[Review]:
        query = "SELECT card_id, rating, reviewed_at, duration_ms FROM reviews"
        params: tuple[str, ...] = ()
        if since is not None:
            query += " WHERE reviewed_at >= ?"
            params = (_timestamp(since),)
        rows = self._db.execute(query + " ORDER BY reviewed_at", params)
        return [Review(cid, rating, datetime.fromisoformat(at), ms) for cid, rating, at, ms in rows]

    def first_reviews_since(self, since: datetime) -> int:
        """Number of cards whose very first review happened at or after `since`."""
        (count,) = self._db.execute(
            "SELECT COUNT(*) FROM (SELECT MIN(reviewed_at) AS first FROM reviews GROUP BY card_id) "
            "WHERE first >= ?",
            (_timestamp(since),),
        ).fetchone()
        return count
