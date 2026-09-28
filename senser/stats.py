"""Knowledge state and activity metrics."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

import fsrs

from senser.model import Card
from senser.scheduler import Scheduler
from senser.store import Review


@dataclass(frozen=True)
class DeckStats:
    deck: str
    total: int
    new: int
    due: int
    mastery: float  # mean recall probability; new and still-learning cards count as 0


@dataclass(frozen=True)
class Activity:
    reviews_today: int
    pass_rate_30d: float | None  # share of reviews not rated "Again"
    streak_days: int


def summarize(label: str, cards: list[Card], states: dict[str, fsrs.Card], scheduler: Scheduler, now: datetime) -> DeckStats:
    known = [states[card.id] for card in cards if card.id in states]
    # Recall is ~1 right after any review, so only graduated cards count as known.
    recall = sum(scheduler.retrievability(state, now) for state in known if state.state == fsrs.State.Review)
    return DeckStats(
        deck=label,
        total=len(cards),
        new=len(cards) - len(known),
        due=sum(1 for state in known if state.due <= now),
        mastery=recall / len(cards) if cards else 0.0,
    )


def deck_stats(cards: list[Card], states: dict[str, fsrs.Card], scheduler: Scheduler, now: datetime) -> list[DeckStats]:
    groups: dict[str, list[Card]] = defaultdict(list)
    for card in cards:
        groups[card.deck].append(card)
    return [summarize(deck, group, states, scheduler, now) for deck, group in sorted(groups.items())]


def activity(reviews: list[Review], now: datetime) -> Activity:
    """Metrics from review history. Days are counted in local time."""
    today = now.astimezone().date()
    days = {review.reviewed_at.astimezone().date() for review in reviews}

    recent = [review for review in reviews if review.reviewed_at >= now - timedelta(days=30)]
    passed = sum(1 for review in recent if review.rating != fsrs.Rating.Again)

    streak = 0
    day = today if today in days else today - timedelta(days=1)
    while day in days:
        streak += 1
        day -= timedelta(days=1)

    return Activity(
        reviews_today=sum(1 for review in reviews if review.reviewed_at.astimezone().date() == today),
        pass_rate_30d=passed / len(recent) if recent else None,
        streak_days=streak,
    )
