from pathlib import Path

from senser.parser import load_cards

EXAMPLES = Path(__file__).parent.parent / "examples" / "cards"


def test_example_cards_are_valid():
    collection = load_cards(EXAMPLES)
    assert collection.issues == []
    assert len(collection.decks) >= 10
