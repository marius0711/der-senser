"""Review session logic, independent of any user interface."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta

import fsrs
from fsrs import Rating

from senser.model import Card
from senser.scheduler import Outcome, Scheduler
from senser.store import Store

# Cards scheduled again within this window (learning steps) stay in the session.
REQUEUE_WINDOW = timedelta(minutes=20)


def local_midnight(now: datetime) -> datetime:
    return now.astimezone().replace(hour=0, minute=0, second=0, microsecond=0)


def remaining_new(store: Store, per_day: int, now: datetime) -> int:
    """How many new cards may still be introduced today."""
    return max(0, per_day - store.first_reviews_since(local_midnight(now)))


def build_queue(cards: list[Card], states: dict[str, fsrs.Card], now: datetime, new_limit: int) -> list[Card]:
    """Due cards (most overdue first), then up to `new_limit` new cards.

    Only one face per card is shown per session, so a term is never
    asked in both directions back to back.
    """
    due = sorted(
        (card for card in cards if card.id in states and states[card.id].due <= now),
        key=lambda card: states[card.id].due,
    )
    queued = {card.base_id for card in due}
    new: list[Card] = []
    for card in cards:
        if len(new) >= new_limit:
            break
        if card.id not in states and card.base_id not in queued:
            new.append(card)
            queued.add(card.base_id)
    return due + new


class Session:
    def __init__(self, cards: list[Card], store: Store, scheduler: Scheduler, new_limit: int, now: datetime) -> None:
        self._store = store
        self._scheduler = scheduler
        self._states = store.states()
        self._queue = deque(build_queue(cards, self._states, now, new_limit))

    def __len__(self) -> int:
        return len(self._queue)

    @property
    def current(self) -> Card | None:
        return self._queue[0] if self._queue else None

    def outcomes(self, now: datetime) -> dict[Rating, Outcome]:
        """Possible outcomes for the current card, one per rating."""
        if self.current is None:
            raise IndexError("session is finished")
        return self._scheduler.outcomes(self._states.get(self.current.id), now)

    def answer(self, outcome: Outcome, duration_ms: int | None = None, hint: bool = False) -> None:
        """Store the chosen outcome for the current card and advance.

        `hint` records whether the German prompt was shown.
        """
        card = self._queue.popleft()
        state, log = outcome
        self._store.record(card.id, state, log, duration_ms, hint)
        self._states[card.id] = state
        if state.due - log.review_datetime <= REQUEUE_WINDOW:
            self._queue.append(card)
