import pytest
from fastapi.testclient import TestClient

from senser.config import Config
from senser.store import Store
from senser.web.app import create_app

CARDS = """\
## Q: What is a strain gauge? ^s-1
A resistor that changes with strain.

## Cloze ^s-2
The gauge factor of metal foil is about {{2}}.
"""


@pytest.fixture
def client(tmp_path):
    deck = tmp_path / "cards" / "sensors"
    deck.mkdir(parents=True)
    (deck / "gauges.md").write_text(CARDS)
    config = Config(cards_dir=tmp_path / "cards", db_path=tmp_path / "state.db")
    with TestClient(create_app(config)) as client:
        yield client


def answer(client, card_id, rating=4):
    return client.post("/review/answer", data={"card_id": card_id, "rating": rating, "duration_ms": 1500})


def test_dashboard_lists_decks(client):
    page = client.get("/")
    assert page.status_code == 200
    assert "sensors" in page.text
    assert "Start review" in page.text


def test_review_flow(client):
    page = client.get("/review/start?deck=sensors")
    assert "What is a strain gauge?" in page.text
    assert "Easy" in page.text

    page = answer(client, "s-1")
    assert "[…]" in page.text  # the cloze prompt is next

    page = answer(client, "s-2")
    assert "Session done" in page.text

    cards = client.get("/cards").text
    assert "new</span>" not in cards
    assert "Reviews today" in client.get("/").text


def test_stale_answer_is_ignored(client):
    client.get("/review/start")
    page = answer(client, "s-2")  # not the current card
    assert "What is a strain gauge?" in page.text


def test_cards_filter(client):
    page = client.get("/cards?deck=sensors")
    assert "s-1" in page.text and "s-2" in page.text


def test_german_help_is_recorded(tmp_path):
    deck = tmp_path / "cards" / "sensors"
    deck.mkdir(parents=True)
    (deck / "gauges.md").write_text("## Q: What is a strain gauge? ^s-1\nDE: Was ist ein DMS?\nA resistor.\n")
    config = Config(cards_dir=tmp_path / "cards", db_path=tmp_path / "state.db")
    with TestClient(create_app(config)) as client:
        page = client.get("/review/start")
        assert "Was ist ein DMS?" in page.text
        client.post("/review/answer", data={"card_id": "s-1", "rating": 3, "hint": 1})
    with Store(config.db_path) as store:
        assert [review.hint for review in store.reviews()] == [True]


def test_daily_limit_offers_extra_cards(tmp_path):
    deck = tmp_path / "cards" / "sensors"
    deck.mkdir(parents=True)
    (deck / "gauges.md").write_text(CARDS)
    config = Config(cards_dir=tmp_path / "cards", db_path=tmp_path / "state.db", new_per_day=1)
    with TestClient(create_app(config)) as client:
        client.get("/review/start")
        answer(client, "s-1")  # Easy: graduates, uses up the daily limit
        dashboard = client.get("/").text
        assert "Learn 10 more new cards" in dashboard
        assert "+10 new" in dashboard
        assert "daily limit of 1 new cards is reached" in client.get("/review/start?deck=sensors").text
        page = client.get("/review/start?deck=sensors&extra=1")
        assert "[…]" in page.text  # the cloze card is offered after all
