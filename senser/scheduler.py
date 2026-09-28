"""Thin wrapper around the FSRS scheduler."""

from __future__ import annotations

import copy
from datetime import datetime, timezone

import fsrs
from fsrs import Rating

Outcome = tuple[fsrs.Card, fsrs.ReviewLog]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Scheduler:
    def __init__(self, desired_retention: float = 0.9) -> None:
        self._fsrs = fsrs.Scheduler(desired_retention=desired_retention)

    def review(self, state: fsrs.Card | None, rating: Rating, now: datetime) -> Outcome:
        """Schedule a review without mutating `state`. `None` means a new card."""
        card = copy.deepcopy(state) if state is not None else fsrs.Card()
        return self._fsrs.review_card(card, rating, review_datetime=now)

    def outcomes(self, state: fsrs.Card | None, now: datetime) -> dict[Rating, Outcome]:
        """Result of each possible rating, computed once so previews match what gets stored."""
        return {rating: self.review(state, rating, now) for rating in Rating}

    def retrievability(self, state: fsrs.Card | None, now: datetime) -> float:
        """Probability of recalling the card right now (0 for new cards)."""
        if state is None:
            return 0.0
        return self._fsrs.get_card_retrievability(state, current_datetime=now)
