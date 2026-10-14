"""FastAPI app: dashboard, review and card list.

Single-user and local: one review session lives in memory, and card
files are re-read whenever a page needs them, so edits show up without
a restart.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fsrs import Rating, State
from markdown_it import MarkdownIt

from senser.config import Config
from senser.parser import Collection, load_cards
from senser.scheduler import Outcome, Scheduler, interval_label, utcnow
from senser.stats import activity, deck_stats, summarize
from senser.store import Store
from senser.study import EXTRA_NEW, Session, build_queue, remaining_new

HERE = Path(__file__).parent
MARKDOWN = MarkdownIt("commonmark", {"html": False}).enable("table")


class WebState:
    """Everything the app keeps between requests."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.scheduler = Scheduler(config.desired_retention)
        self.store = Store(config.db_path)
        self.session: Session | None = None
        self.deck: str | None = None
        self.reviewed = 0
        self.pending: tuple[str, dict[Rating, Outcome]] | None = None  # (card id, outcomes shown)

    def collection(self) -> Collection:
        return load_cards(self.config.cards_dir)

    def start(self, deck: str | None, extra: int = 0) -> None:
        """Start a session. `extra` allows new cards beyond the daily limit."""
        cards = [card for card in self.collection().cards if card.in_deck(deck)]
        now = utcnow()
        new_limit = remaining_new(self.store, self.config.new_per_day, now) + extra
        self.session = Session(cards, self.store, self.scheduler, new_limit, now)
        self.deck, self.reviewed, self.pending = deck, 0, None


def create_app(config: Config) -> FastAPI:
    web = WebState(config)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        web.store.close()

    app = FastAPI(title="Der Senser", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
    templates = Jinja2Templates(directory=HERE / "templates")
    templates.env.filters["markdown"] = MARKDOWN.render

    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        collection = web.collection()
        now = utcnow()
        states = web.store.states()
        new_limit = remaining_new(web.store, config.new_per_day, now)
        return templates.TemplateResponse(request, "dashboard.html", {
            "decks": deck_stats(collection.cards, states, web.scheduler, now),
            "total": summarize("Total", collection.cards, states, web.scheduler, now),
            "activity": activity(web.store.reviews(since=now - timedelta(days=400)), now),
            "queue_size": len(build_queue(collection.cards, states, now, new_limit)),
            "new_limit": new_limit,
            "new_per_day": config.new_per_day,
            "extra_new": EXTRA_NEW,
            "issues": collection.issues,
            "cards_dir": config.cards_dir,
        })

    @app.get("/review/start")
    async def review_start(deck: str | None = None, extra: bool = False):
        web.start(deck or None, EXTRA_NEW if extra else 0)
        return RedirectResponse("/review", status_code=303)

    @app.get("/review", response_class=HTMLResponse)
    async def review(request: Request):
        if web.session is None:
            web.start(None)
        card = web.session.current
        context = {"card": card, "deck": web.deck, "reviewed": web.reviewed, "remaining": len(web.session)}
        if card is None:
            # Explain an empty session: is the daily limit holding back new cards?
            states = web.store.states()
            context["new_waiting"] = sum(
                1 for c in web.collection().cards if c.in_deck(web.deck) and c.id not in states
            )
            context["new_left"] = remaining_new(web.store, config.new_per_day, utcnow())
            context["new_per_day"] = config.new_per_day
            context["extra_new"] = EXTRA_NEW
        else:
            outcomes = web.session.outcomes(utcnow())
            web.pending = (card.id, outcomes)
            context["ratings"] = [
                {"value": rating.value, "name": rating.name, "interval": interval_label(state.due - log.review_datetime)}
                for rating, (state, log) in outcomes.items()
            ]
        return templates.TemplateResponse(request, "review.html", context)

    @app.post("/review/answer")
    async def review_answer(
        card_id: str = Form(), rating: int = Form(), duration_ms: int | None = Form(None), hint: bool = Form(False)
    ):
        # Ignore stale or repeated submissions (back button, double click).
        if web.session and web.session.current and web.pending and web.pending[0] == card_id == web.session.current.id:
            web.session.answer(web.pending[1][Rating(rating)], duration_ms, hint)
            web.reviewed += 1
            web.pending = None
        return RedirectResponse("/review", status_code=303)

    @app.get("/cards", response_class=HTMLResponse)
    async def cards(request: Request, deck: str | None = None):
        collection = web.collection()
        now = utcnow()
        states = web.store.states()
        rows = []
        for card in collection.cards:
            if not card.in_deck(deck or None):
                continue
            state = states.get(card.id)
            rows.append({
                "card": card,
                "title": card.prompt.splitlines()[0].replace("**", ""),
                "learning": bool(state and state.state != State.Review),
                "recall": web.scheduler.retrievability(state, now) if state else None,
                "due": state.due.astimezone().strftime("%Y-%m-%d %H:%M") if state else None,
                "overdue": bool(state and state.due <= now),
            })
        return templates.TemplateResponse(request, "cards.html", {
            "rows": rows, "decks": collection.decks, "deck": deck or None,
        })

    return app
