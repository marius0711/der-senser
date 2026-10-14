# Der Senser

Spaced-repetition flashcards in plain Markdown, built for learning **process engineering**
in modern mechatronics and robotics manufacturing: sensors, actuators, materials, assembly,
metrology, controls, quality and more.

- **Cards are Markdown**: write them in any editor, version them with git.
- **Review state is separate**: a local SQLite database, so reviewing never touches your card files.
- **FSRS scheduling**: the modern algorithm also used by Anki, via [py-fsrs](https://github.com/open-spaced-repetition/py-fsrs).
- **Knowledge state per deck**: mastery is the mean recall probability of all cards in a deck.
- **Bilingual prompts**: questions in technical English, with an optional German version on request.
- **Local web interface** with keyboard-driven review, plus a CLI. Runs offline on `127.0.0.1` only.

## Quickstart

Requirements: Python 3.11 or newer and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo-url> der-senser && cd der-senser
uv tool install --editable .              # installs the global `senser` command
senser serve -c examples/senser.toml      # try it with the example cards
```

For your own cards, create `~/.config/senser/senser.toml` (see [Configuration](#configuration)).
After that, `senser` alone starts the web interface with your cards.

Because the install is editable, code changes in this repository apply immediately.

## Documentation

| File | Content |
|---|---|
| [docs/quickcard.md](docs/quickcard.md) | One-page reference: keys, honest rating, commands, file locations. Also as [standalone HTML](docs/quickcard.html) for printing |
| [docs/cards.md](docs/cards.md) | Full guide for writing cards: types, ids and prefixes, the `DE:` line, style, checklist |

## Card format

A card is a level-2 heading `## <Type>: <title> ^<id>` followed by its body. Any other
heading is treated as a regular note, so card files can double as study notes.

```markdown
## Q: What are the three components of a strain wave gear? ^ac-001
DE: Aus welchen drei Bauteilen besteht ein Wellgetriebe?
Wave generator, flexspline, circular spline.

## Cloze: Gear ratio ^ac-002
DE: Der Flexspline hat typischerweise {{2}} Zähne weniger als der Circular Spline.
The flexspline typically has {{2}} fewer teeth than the circular spline.

## Term: Traglast = payload ^ro-003

## Sequence: The 8D steps ^qa-002
DE: Die Schritte der 8D-Methode
1. D1: Form the team
2. D2: Describe the problem
```

| Type | Asks | Answer |
|---|---|---|
| `Q` | the question | the body |
| `Cloze` | the body with `{{blanks}}` hidden | the body with blanks filled in |
| `Term` | `German = English`, in both directions | the other side plus an optional note |
| `Sequence` | the name and the number of steps | the ordered list |

The `DE:` line holds a German version of the question, shown on request (**D** key).
Ids such as `^ac-001` tie the review history to a card, so the text can be edited without losing
progress. All rules are in [docs/cards.md](docs/cards.md).

## Commands

| Command | Purpose |
|---|---|
| `senser` or `senser serve [--port 8000] [--no-open]` | Start the web interface and open it in the browser |
| `senser review [-d DECK] [--extra]` | Review due cards, then new ones (limit: `new_per_day`; `--extra` adds 10 more), in the terminal |
| `senser status [-d DECK]` | Cards, new, due and mastery per deck, plus reviews today, pass rate, German help rate and streak |
| `senser list [-d DECK]` | All cards with their next due date |
| `senser lint` | Validate card files: missing or duplicate ids, malformed cards |
| `senser ids` | Id prefixes in use and the next free id per deck |

Every command accepts `-c PATH` to use a different config file.

### Web interface

- **Dashboard**: mastery, due cards, new cards left today, reviews today, 30-day pass rate and streak, plus a table per deck
- **Review**: **Space** reveals the answer, **D** shows the German question, **1–4** rates it (Again, Hard, Good, Easy), **Esc** goes back.
  Each rating button shows the interval it will schedule.
- **Cards**: all cards per deck with recall probability and next review date

Card files are re-read on every page load, so edits show up without restarting the server.

## Configuration

`senser.toml` is looked up in this order: `--config`, `$SENSER_CONFIG`, `./senser.toml`,
`~/.config/senser/senser.toml`. Relative paths are resolved against the config file.

```toml
cards_dir = "~/senser-cards"      # your own cards
db_path = "~/.senser/state.db"    # review state
new_per_day = 15                  # new cards introduced per day
desired_retention = 0.9           # target recall probability for scheduling
```

`examples/senser.toml` points at the example cards and keeps its review state in `examples/.senser/`.

## Your own cards

Keep your personal cards **outside this repository**, in a local folder or a private git repo,
and point `cards_dir` at it:

```
~/senser-cards/              private git repo with your cards
├── README.md                short workflow and template (ignored by the parser)
├── sensors/                 folder = deck
│   ├── forcetorque.md       one file per topic, several cards per file
│   └── encoders.md
├── actuators/
└── ...
~/.config/senser/senser.toml your config
~/.senser/state.db           your review history (not in git, do not delete)
```

The example cards in this repository cover general textbook knowledge only.
Never put confidential or company-internal information into cards, not even in a private repository.

## Project structure

```
der-senser/
├── senser/                  Python package
│   ├── model.py             Card and Issue data types
│   ├── parser.py            Markdown files → cards, validation
│   ├── config.py            senser.toml lookup and loading
│   ├── scheduler.py         FSRS wrapper, interval labels
│   ├── store.py             SQLite: review states and history, schema migration
│   ├── study.py             review session and queue, shared by CLI and web
│   ├── stats.py             mastery per deck, pass rate, streak
│   ├── cli.py               Typer commands
│   └── web/                 FastAPI app
│       ├── app.py           routes: dashboard, review, cards
│       ├── templates/       Jinja2 pages
│       └── static/          CSS and keyboard shortcuts (no external assets)
├── examples/
│   ├── cards/               textbook-level sample cards, one folder per deck
│   └── senser.toml          config for trying the examples
├── docs/                    quick card and card writing guide
├── tests/                   pytest suite
└── pyproject.toml
```

## How it works

```
Markdown files ──parser──► Cards ──┐
                                   ├──► study.Session ──► CLI / web UI
SQLite (state.db) ◄──store──► FSRS ┘          │
                                              └──► stats ──► dashboard / status
```

- The **parser** reads every `*.md` file below `cards_dir`. The folder path is the deck.
- The **store** keeps one FSRS state per card id plus every review. It never writes to card files.
- The **session** queues due cards first, then new cards up to the daily limit. Cards scheduled
  again within 20 minutes (learning steps) stay in the session.
- **Mastery** is the mean recall probability per deck. New cards and cards still in their
  learning steps count as 0, so the value reflects consolidated knowledge.

## Development

```bash
uv venv --python 3.12 && uv pip install -e ".[dev]"
.venv/bin/pytest -q
.venv/bin/senser lint -c examples/senser.toml
```

For manual testing, use a separate config with a scratch database so your real review history stays untouched.

## Roadmap

1. ~~Core: parser, FSRS scheduling, SQLite store, CLI review~~
2. ~~Local web interface (FastAPI, server-rendered, no JS framework)~~
   - ~~German prompt line (`DE:`) with usage tracking, `senser ids`, authoring guide~~
3. Import and export
   - Import card bundles (single `.md` file or folder) into existing decks, via web upload and
     CLI, with a preview of new, changed and conflicting cards before anything is written
   - Progress export per deck as a Markdown/HTML report and CSV/JSON raw data
4. Polish and release
   - More card types (decision cards: requirement to choice, ordering)
   - Hover translations for terms, based on the Term cards
   - Help page in the web interface (the quick card)
   - Public GitHub release

## License

MIT
