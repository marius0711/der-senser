"""Core data types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class Kind(StrEnum):
    QA = "qa"
    CLOZE = "cloze"
    TERM = "term"
    SEQUENCE = "sequence"


@dataclass(frozen=True)
class Card:
    """One reviewable face of a card.

    Most cards have a single face. Term cards have two: `id` asks
    left -> right, `id.r` asks right -> left.
    """

    id: str
    deck: str
    kind: Kind
    prompt: str
    answer: str
    tags: tuple[str, ...]
    source: Path
    line: int
    prompt_de: str = ""  # optional German version of the prompt, shown on request

    @property
    def base_id(self) -> str:
        """The id written in the Markdown file, shared by sibling faces."""
        return self.id.split(".", 1)[0]

    def in_deck(self, deck: str | None) -> bool:
        """True if the card belongs to `deck` or one of its sub-decks."""
        return deck is None or self.deck == deck or self.deck.startswith(deck + "/")


@dataclass(frozen=True)
class Issue:
    """A problem found while parsing card files."""

    source: Path
    line: int
    message: str
