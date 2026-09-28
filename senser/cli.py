"""Command-line interface."""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Annotated, Optional

import typer
from fsrs import Rating
from rich.console import Console
from rich.markdown import Markdown
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from senser.config import Config, load_config
from senser.parser import Collection, load_cards
from senser.scheduler import Outcome, Scheduler, utcnow
from senser.stats import activity, deck_stats, summarize
from senser.store import Store
from senser.study import Session

app = typer.Typer(
    name="senser",
    help="Der Senser: spaced-repetition flashcards in Markdown.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()

ConfigOption = Annotated[Optional[Path], typer.Option("--config", "-c", help="Path to senser.toml.")]
DeckOption = Annotated[Optional[str], typer.Option("--deck", "-d", help="Limit to a deck and its sub-decks.")]

RATING_STYLES = {
    Rating.Again: "red",
    Rating.Hard: "yellow",
    Rating.Good: "green",
    Rating.Easy: "cyan",
}


def _load(config_path: Path | None) -> tuple[Config, Collection]:
    try:
        config = load_config(config_path)
        return config, load_cards(config.cards_dir)
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[red]error:[/] {escape(str(exc))}")
        raise typer.Exit(1) from exc


def _select(collection: Collection, deck: str | None) -> list:
    if collection.issues:
        console.print(
            f"[yellow]{len(collection.issues)} problem(s) in card files, affected cards are skipped. "
            "Run `senser lint`.[/]"
        )
    cards = [card for card in collection.cards if card.in_deck(deck)]
    if deck and not cards:
        console.print(f"[red]error:[/] no cards in deck '{escape(deck)}'. Known decks: {', '.join(collection.decks)}")
        raise typer.Exit(1)
    return cards


def _relative(path: Path, root: Path) -> str:
    return str(path.relative_to(root)) if path.is_relative_to(root) else str(path)


def _interval(delta: timedelta) -> str:
    minutes = delta.total_seconds() / 60
    if minutes < 1:
        return "<1m"
    if minutes < 60:
        return f"{minutes:.0f}m"
    if minutes < 60 * 24:
        return f"{minutes / 60:.0f}h"
    days = minutes / (60 * 24)
    if days < 31:
        return f"{days:.0f}d"
    if days < 365:
        return f"{days / 30:.1f}mo"
    return f"{days / 365:.1f}y"


def _bar(fraction: float, width: int = 12) -> str:
    filled = round(fraction * width)
    return "█" * filled + "░" * (width - filled) + f" {fraction:4.0%}"


def _local_midnight(now: datetime) -> datetime:
    return now.astimezone().replace(hour=0, minute=0, second=0, microsecond=0)


@app.command()
def review(deck: DeckOption = None, config: ConfigOption = None) -> None:
    """Review due cards and introduce new ones."""
    cfg, collection = _load(config)
    cards = _select(collection, deck)
    now = utcnow()
    with Store(cfg.db_path) as store:
        new_limit = max(0, cfg.new_per_day - store.first_reviews_since(_local_midnight(now)))
        session = Session(cards, store, Scheduler(cfg.desired_retention), new_limit, now)
        if not len(session):
            console.print("[green]Nothing due right now.[/] Come back later or add new cards.")
            return
        reviewed = _run(session)
    console.print(f"\n[bold]Session done:[/] {reviewed} review(s).")


def _run(session: Session) -> int:
    reviewed = 0
    try:
        while (card := session.current) is not None:
            console.clear()
            console.print(f"[dim]{escape(card.deck)} · {card.kind} · {len(session)} left[/]")
            console.print(Panel(Markdown(card.prompt), border_style="cyan", padding=(1, 2)))
            started = time.monotonic()
            if console.input("[dim]Enter = show answer · q = quit[/] ").strip().lower() == "q":
                break

            console.print(Panel(Markdown(card.answer), border_style="green", padding=(1, 2)))
            outcomes = session.outcomes(utcnow())
            console.print(_rating_line(outcomes))
            choice = Prompt.ask("Rating", choices=["1", "2", "3", "4", "q"], show_choices=False, console=console)
            if choice == "q":
                break
            duration_ms = int((time.monotonic() - started) * 1000)
            session.answer(outcomes[Rating(int(choice))], duration_ms)
            reviewed += 1
    except (KeyboardInterrupt, EOFError):
        console.print()
    return reviewed


def _rating_line(outcomes: dict[Rating, Outcome]) -> str:
    parts = []
    for rating, (state, log) in outcomes.items():
        style = RATING_STYLES[rating]
        parts.append(f"[{style}]{rating.value} {rating.name}[/] [dim]{_interval(state.due - log.review_datetime)}[/]")
    return "   ".join(parts)


@app.command()
def status(deck: DeckOption = None, config: ConfigOption = None) -> None:
    """Show the knowledge state per deck."""
    cfg, collection = _load(config)
    cards = _select(collection, deck)
    now = utcnow()
    scheduler = Scheduler(cfg.desired_retention)
    with Store(cfg.db_path) as store:
        states = store.states()
        history = store.reviews(since=now - timedelta(days=400))

    table = Table(title="Der Senser · knowledge state", title_justify="left")
    table.add_column("Deck")
    table.add_column("Cards", justify="right")
    table.add_column("New", justify="right")
    table.add_column("Due", justify="right")
    table.add_column("Mastery")
    for row in deck_stats(cards, states, scheduler, now):
        table.add_row(escape(row.deck), str(row.total), str(row.new), str(row.due), _bar(row.mastery))
    total = summarize("Total", cards, states, scheduler, now)
    table.add_section()
    table.add_row("[bold]Total[/]", str(total.total), str(total.new), str(total.due), _bar(total.mastery))
    console.print(table)

    act = activity(history, now)
    pass_rate = f"{act.pass_rate_30d:.0%}" if act.pass_rate_30d is not None else "–"
    console.print(
        f"Today: [bold]{act.reviews_today}[/] reviews · "
        f"Pass rate (30d): [bold]{pass_rate}[/] · "
        f"Streak: [bold]{act.streak_days}[/] day(s)"
    )


@app.command()
def lint(config: ConfigOption = None) -> None:
    """Check card files for missing ids, duplicates and malformed cards."""
    cfg, collection = _load(config)
    for issue in collection.issues:
        console.print(f"{_relative(issue.source, cfg.cards_dir)}:{issue.line}: {issue.message}", markup=False)
    style = "red" if collection.issues else "green"
    console.print(f"[{style}]{len(collection.cards)} card face(s), {len(collection.issues)} problem(s)[/]")
    if collection.issues:
        raise typer.Exit(1)


@app.command("list")
def list_cards(deck: DeckOption = None, config: ConfigOption = None) -> None:
    """List cards with their next due date."""
    cfg, collection = _load(config)
    cards = _select(collection, deck)
    with Store(cfg.db_path) as store:
        states = store.states()

    table = Table()
    table.add_column("ID", style="dim")
    table.add_column("Deck")
    table.add_column("Type")
    table.add_column("Prompt", overflow="ellipsis", no_wrap=True, max_width=60)
    table.add_column("Due")
    for card in cards:
        state = states.get(card.id)
        due = state.due.astimezone().strftime("%Y-%m-%d %H:%M") if state else "new"
        table.add_row(card.id, escape(card.deck), card.kind, escape(card.prompt.splitlines()[0]), due)
    console.print(table)
