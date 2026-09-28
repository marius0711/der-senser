"""Parse Markdown card files into Card objects.

A card is a level-2 heading of the form `## <Type>: <title> ^<id>`,
followed by its body up to the next heading. Other headings are
ignored, so card files can mix cards with regular notes.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import yaml

from senser.model import Card, Issue, Kind

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
CARD_HEADING = re.compile(
    r"^(?P<kind>[A-Za-z]+)\s*(?::\s*(?P<title>.*?))?\s*(?:\^(?P<id>\S+))?$"
)
TRAILING_ID = re.compile(r"\^[a-z0-9-]+$")
VALID_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
CLOZE = re.compile(r"\{\{(.+?)\}\}")
LIST_ITEM = re.compile(r"^(?:\d+[.)]|[-*])\s+", re.MULTILINE)

KINDS = {
    "q": Kind.QA,
    "cloze": Kind.CLOZE,
    "term": Kind.TERM,
    "sequence": Kind.SEQUENCE,
    "seq": Kind.SEQUENCE,
}


@dataclass
class Collection:
    """All cards found under a cards directory, plus parse problems."""

    cards: list[Card]
    issues: list[Issue]

    @property
    def decks(self) -> list[str]:
        return sorted({card.deck for card in self.cards})


def load_cards(root: Path) -> Collection:
    """Parse every `*.md` file below `root`.

    The deck defaults to the file's folder path relative to `root`
    (or the file name for top-level files) and can be overridden with
    `deck:` in the frontmatter.
    """
    if not root.is_dir():
        raise FileNotFoundError(f"cards directory not found: {root}")

    cards: list[Card] = []
    issues: list[Issue] = []
    seen: dict[str, Card] = {}
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        default_deck = "/".join(relative.parent.parts) or relative.stem
        file_cards, file_issues = parse_text(path.read_text(encoding="utf-8"), path, default_deck)
        issues.extend(file_issues)
        for card in file_cards:
            if card.id in seen:
                first = seen[card.id]
                issue = Issue(path, card.line, f"duplicate id '{card.base_id}' (first used in {first.source}:{first.line})")
                if issue not in issues:  # term cards have two faces, report once
                    issues.append(issue)
                continue
            seen[card.id] = card
            cards.append(card)
    return Collection(cards, issues)


def parse_text(text: str, source: Path, default_deck: str) -> tuple[list[Card], list[Issue]]:
    """Parse one card file. Malformed cards are reported and skipped."""
    try:
        meta, lines, offset = _split_frontmatter(text)
    except yaml.YAMLError as exc:
        return [], [Issue(source, 1, f"invalid frontmatter: {exc}")]
    if not isinstance(meta, dict):
        return [], [Issue(source, 1, "frontmatter must be a mapping")]

    deck = str(meta.get("deck") or default_deck)
    raw_tags = meta.get("tags") or ()
    tags = (str(raw_tags),) if isinstance(raw_tags, str) else tuple(str(t) for t in raw_tags)

    cards: list[Card] = []
    issues: list[Issue] = []
    for number, level, heading, body in _sections(lines, offset):
        match = CARD_HEADING.match(heading) if level == 2 else None
        kind = KINDS.get(match["kind"].lower()) if match else None
        if kind is None:
            if TRAILING_ID.search(heading):
                issues.append(Issue(source, number, "heading has an id but no card type (Q, Cloze, Term, Sequence)"))
            continue

        card_id = match["id"]
        if not card_id:
            issues.append(Issue(source, number, "card has no id, append ' ^your-id' to the heading"))
            continue
        if not VALID_ID.match(card_id):
            issues.append(Issue(source, number, f"invalid id '{card_id}', use lowercase letters, digits and '-'"))
            continue

        try:
            faces = _faces(kind, match["title"] or "", body)
        except ValueError as exc:
            issues.append(Issue(source, number, str(exc)))
            continue
        for suffix, prompt, answer in faces:
            cards.append(Card(card_id + suffix, deck, kind, prompt, answer, tags, source, number))
    return cards, issues


def _faces(kind: Kind, title: str, body: str) -> list[tuple[str, str, str]]:
    """Return (id suffix, prompt, answer) per face. Raises ValueError if malformed."""
    if kind is Kind.QA:
        if not title:
            raise ValueError("Q card needs a question after 'Q:'")
        if not body:
            raise ValueError("Q card has no answer")
        return [("", title, body)]

    if kind is Kind.CLOZE:
        if not CLOZE.search(body):
            raise ValueError("Cloze card has no {{blanks}}")
        context = f"**{title}**\n\n" if title else ""
        return [("", context + CLOZE.sub("**[…]**", body), context + CLOZE.sub(r"**\1**", body))]

    if kind is Kind.TERM:
        left, separator, right = (part.strip() for part in title.partition("="))
        if not (separator and left and right):
            raise ValueError("Term card needs 'Term: <term> = <translation>'")
        note = f"\n\n{body}" if body else ""
        return [("", left, right + note), (".r", right, left + note)]

    if not title:
        raise ValueError("Sequence card needs a title after 'Sequence:'")
    steps = len(LIST_ITEM.findall(body))
    if steps < 2:
        raise ValueError("Sequence card needs at least two list items")
    return [("", f"{title}\n\n*Recall the {steps} steps in order.*", body)]


def _split_frontmatter(text: str) -> tuple[object, list[str], int]:
    """Return (frontmatter, remaining lines, number of lines consumed)."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for end in range(1, len(lines)):
            if lines[end].strip() == "---":
                meta = yaml.safe_load("\n".join(lines[1:end])) or {}
                return meta, lines[end + 1:], end + 1
    return {}, lines, 0


def _sections(lines: list[str], offset: int) -> Iterator[tuple[int, int, str, str]]:
    """Yield (line number, heading level, heading text, body) per heading.

    Lines inside fenced code blocks never count as headings.
    """
    current: tuple[int, int, str] | None = None
    body: list[str] = []
    in_fence = False
    for number, line in enumerate(lines, start=offset + 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        heading = None if in_fence else HEADING.match(line)
        if heading:
            if current:
                yield *current, "\n".join(body).strip()
            current, body = (number, len(heading[1]), heading[2]), []
        elif current:
            body.append(line)
    if current:
        yield *current, "\n".join(body).strip()
