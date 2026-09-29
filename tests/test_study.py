from datetime import datetime, timedelta, timezone
from pathlib import Path

from fsrs import Rating

from senser.parser import parse_text
from senser.scheduler import Scheduler
from senser.stats import activity, summarize
from senser.store import Store
from senser.study import Session

NOW = datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc)
TEXT = "## Q: One? ^a-1\n1\n## Q: Two? ^a-2\n2\n## Term: Drei = three ^a-3\n"


def make_session(store: Store, new_limit: int = 10, now: datetime = NOW) -> Session:
    cards, _ = parse_text(TEXT, Path("x.md"), "deck")
    return Session(cards, store, Scheduler(), new_limit, now)


def answer(session: Session, rating: Rating, now: datetime = NOW) -> None:
    session.answer(session.outcomes(now)[rating], duration_ms=1000)


def test_new_cards_respect_limit_and_bury_siblings():
    with Store(":memory:") as store:
        assert len(make_session(store, new_limit=2)) == 2
        session = make_session(store)
        assert [c.id for c in session._queue] == ["a-1", "a-2", "a-3"]


def test_again_requeues_easy_does_not():
    with Store(":memory:") as store:
        session = make_session(store)
        answer(session, Rating.Again)
        assert session._queue[-1].id == "a-1"
        answer(session, Rating.Easy)  # a-2
        assert "a-2" not in [c.id for c in session._queue]


def test_state_persists_between_sessions(tmp_path):
    db = tmp_path / "state.db"
    with Store(db) as store:
        session = make_session(store)
        answer(session, Rating.Easy)
    with Store(db) as store:
        assert set(store.states()) == {"a-1"}
        assert store.first_reviews_since(NOW - timedelta(hours=1)) == 1
        # a-1 is not due yet, so only the remaining new cards are queued
        assert [c.id for c in make_session(store)._queue] == ["a-2", "a-3"]


def test_mastery_and_activity():
    cards, _ = parse_text(TEXT, Path("x.md"), "deck")
    scheduler = Scheduler()
    with Store(":memory:") as store:
        assert summarize("all", cards, store.states(), scheduler, NOW).mastery == 0
        session = make_session(store)
        answer(session, Rating.Easy)
        answer(session, Rating.Again)
        stats = summarize("all", cards, store.states(), scheduler, NOW)
        # 4 faces: a-1 graduated (Easy, recall 1), a-2 still learning, 2 new
        assert stats.new == 2 and stats.mastery == 0.25

        act = activity(store.reviews(), NOW)
        assert act.pass_rate_30d == 0.5
        assert act.streak_days == 1


def test_hint_is_recorded_and_old_databases_migrate(tmp_path):
    import sqlite3

    db = tmp_path / "old.db"
    legacy = sqlite3.connect(db)
    legacy.execute(
        "CREATE TABLE reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, card_id TEXT NOT NULL, "
        "rating INTEGER NOT NULL, reviewed_at TEXT NOT NULL, duration_ms INTEGER)"
    )
    legacy.execute("INSERT INTO reviews (card_id, rating, reviewed_at) VALUES ('a-9', 3, ?)", (NOW.isoformat(),))
    legacy.commit()
    legacy.close()

    with Store(db) as store:
        session = make_session(store)
        session.answer(session.outcomes(NOW)[Rating.Good], duration_ms=500, hint=True)
        assert [review.hint for review in store.reviews()] == [False, True]
        assert activity(store.reviews(), NOW).hint_rate_30d == 0.5
