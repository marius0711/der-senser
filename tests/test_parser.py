from pathlib import Path

from senser.model import Kind
from senser.parser import load_cards, parse_text

SOURCE = Path("deck.md")


def parse(text: str, deck: str = "default"):
    return parse_text(text, SOURCE, deck)


def test_qa_card():
    cards, issues = parse("## Q: What is OEE? ^le-1\nAvailability x performance x quality.\n")
    assert issues == []
    [card] = cards
    assert (card.id, card.kind, card.prompt) == ("le-1", Kind.QA, "What is OEE?")
    assert card.answer == "Availability x performance x quality."
    assert card.line == 1


def test_cloze_masks_prompt_and_fills_answer():
    [card], _ = parse("## Cloze ^c-1\nThe ratio is {{100:1}}.\n")
    assert card.prompt == "The ratio is **[…]**."
    assert card.answer == "The ratio is **100:1**."


def test_term_yields_two_faces():
    cards, _ = parse("## Term: Traglast = payload ^t-1\nMax. load at the flange.\n")
    assert [(c.id, c.prompt) for c in cards] == [("t-1", "Traglast"), ("t-1.r", "payload")]
    assert cards[0].answer.startswith("payload")
    assert {c.base_id for c in cards} == {"t-1"}


def test_sequence_counts_top_level_steps():
    [card], _ = parse("## Sequence: 8D ^s-1\n1. Team\n2. Problem\n   - detail\n3. Containment\n")
    assert "3 steps" in card.prompt


def test_frontmatter_sets_deck_and_tags():
    [card], _ = parse("---\ndeck: sensors/force\ntags: [dms]\n---\n\n## Q: Gauge factor? ^s-1\nk = 2\n")
    assert card.deck == "sensors/force"
    assert card.tags == ("dms",)
    assert card.line == 6


def test_regular_headings_and_code_are_ignored():
    text = "# Title\n## Background\nnotes\n## Q: A? ^a-1\n```\n## not a heading\n```\n"
    cards, issues = parse(text)
    assert issues == []
    assert "## not a heading" in cards[0].answer


def test_problems_are_reported():
    text = (
        "## Q: No id\nanswer\n"
        "## Q: Bad id ^Bad_ID\nanswer\n"
        "## Q: Empty ^e-1\n"
        "## Cloze ^c-1\nno blanks\n"
        "## Term: missing separator ^t-1\n"
        "## Notes ^n-1\n"
    )
    cards, issues = parse(text)
    assert cards == []
    assert [issue.line for issue in issues] == [1, 3, 5, 6, 8, 9]


def test_load_cards_derives_deck_and_detects_duplicates(tmp_path):
    (tmp_path / "sensors").mkdir()
    (tmp_path / "sensors" / "force.md").write_text("## Term: DMS = strain gauge ^x-1\n")
    (tmp_path / "top.md").write_text("## Q: Dup? ^x-1\nyes\n")
    collection = load_cards(tmp_path)
    assert [c.deck for c in collection.cards] == ["sensors", "sensors"]
    assert len(collection.issues) == 1
    assert "duplicate id 'x-1'" in collection.issues[0].message
