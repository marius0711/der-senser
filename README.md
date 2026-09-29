# Der Senser

Spaced-repetition flashcards in plain Markdown, built for learning **process engineering**
in modern mechatronics and robotics manufacturing: sensors, actuators, materials, assembly,
metrology, controls, quality and more.

- **Cards are Markdown**: write them in any editor, version them with git.
- **Review state is separate**: a local SQLite database, so reviewing never touches your card files.
- **FSRS scheduling**: the modern algorithm also used by Anki, via [py-fsrs](https://github.com/open-spaced-repetition/py-fsrs).
- **Knowledge state per deck**: mastery is the mean recall probability of all cards in a deck.
- **Local web interface** with keyboard-driven review, plus a CLI. Runs offline on `127.0.0.1` only.

## Quickstart

```bash
git clone <repo-url> der-senser && cd der-senser
uv venv --python 3.12 && uv pip install -e ".[dev]"
.venv/bin/senser serve -c examples/senser.toml   # web interface with the example cards
```

For your own cards, create `~/.config/senser/senser.toml` (see [Configuration](#configuration));
then `senser serve` without `-c` picks it up.

## Card format

A card is a level-2 heading `## <Type>: <title> ^<id>` followed by its body. Any other
heading is treated as a regular note, so card files can double as study notes.

```markdown
---
deck: actuators          # optional, defaults to the folder name
tags: [gearbox]
---

## Q: What are the three components of a strain wave gear? ^ac-001
Wave generator, flexspline, circular spline.

## Cloze: Gear ratio ^ac-002
The flexspline typically has {{2}} fewer teeth than the circular spline.

## Term: Traglast = payload ^ro-003
Asked in both directions, optional note below.

## Sequence: The 8D steps ^qa-002
1. D1: Form the team
2. D2: Describe the problem
3. ...
```

| Type | Asks | Answer |
|---|---|---|
| `Q` | the title | the body |
| `Cloze` | the body with `{{blanks}}` hidden | the body with blanks filled |
| `Term` | `left = right`, both directions | the other side plus the note |
| `Sequence` | the title and the number of steps | the ordered list |

**Ids** (`^ac-001`) are lowercase letters, digits and `-`. They must be unique and stable,
because review history is tied to the id rather than the text, so you can fix typos without
losing progress. `senser lint` reports missing and duplicate ids.

## Commands

| Command | Purpose |
|---|---|
| `senser serve [--port 8000] [--no-open]` | Start the web interface and open it in the browser |
| `senser review [-d DECK]` | Review due cards, then new ones (limit: `new_per_day`) |
| `senser status [-d DECK]` | Cards, new, due and mastery per deck, plus reviews today, pass rate and streak |
| `senser list [-d DECK]` | All cards with their next due date |
| `senser lint` | Validate card files |

### Web interface

- **Dashboard**: mastery, due and new cards per deck, reviews today, 30-day pass rate, streak
- **Review**: **Space** reveals the answer, **1–4** rates it (Again, Hard, Good, Easy), **Esc** goes back.
  Each rating button shows the interval it will schedule.
- **Cards**: all cards per deck with recall probability and next review date

Card files are re-read on every page load, so edits show up without restarting the server.
The terminal commands `review`, `status` and `list` offer the same functions without a browser.

## Configuration

`senser.toml` is looked up in this order: `--config`, `$SENSER_CONFIG`, `./senser.toml`,
`~/.config/senser/senser.toml`.

```toml
cards_dir = "~/senser-cards"      # your own cards
db_path = "~/.senser/state.db"    # review state
new_per_day = 15
desired_retention = 0.9
```

`examples/senser.toml` points at the example cards and keeps its review state in `examples/.senser/`.

## Your own cards

Keep your personal cards **outside this repository**, in a local folder or a private repo,
and point `cards_dir` at it. The example cards here cover general textbook knowledge only.
Never put confidential or company-internal information into cards that are synced to a cloud service.

## Roadmap

1. ~~Core: parser, FSRS scheduling, SQLite store, CLI review~~
2. ~~Local web interface (FastAPI, server-rendered, no JS framework)~~
3. Import of card bundles with a preview (new, changed and conflicting cards), progress export (Markdown/HTML/CSV)
4. More card types (decision cards, ordering), release

## License

MIT
