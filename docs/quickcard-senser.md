# Der Senser: quick card

Start with `senser`. Stop with `Ctrl+C` in the terminal.

## Review keys (browser)

| Key | Action |
|---|---|
| `Space` / `Enter` | Show the answer |
| `D` | German version of the question, answer stays hidden |
| `1` `2` `3` `4` | Rate the card, next one loads |
| `Esc` | Back to the dashboard |

In the terminal (`senser review`): `Enter`, `d`, `1` to `4`, `q` to quit.

## Rating honestly

| Key | Rating | When |
|---|---|---|
| `1` | **Again** | Did not know it, or got it wrong. Comes back in a minute. |
| `2` | **Hard** | Got it, but only after a real struggle or partly. |
| `3` | **Good** | Knew it with normal effort. Your default. |
| `4` | **Easy** | Instantly, no thinking. Use it sparingly. |

Each button shows the interval it will schedule. Mastery counts a card only after it has
left its learning steps, so it rises over days rather than in one session.

## A clean session

- Answer in your head (or aloud) **before** revealing. Recognising the answer is not the same as recalling it.
- Try the English question first. Press `D` only if you are stuck. It does not change the schedule, it is only counted.
- Once a day is enough. Due cards come first, then up to 15 new ones.
- Finish the session, since **Again** cards return within minutes.

## Adding a card

1. Open the topic file in `~/senser-cards/<deck>/`
2. `senser ids` gives the next free id
3. Write the card and add a `DE:` line
4. `senser lint` should report 0 problems
5. Reload the browser, then commit in the cards folder

```markdown
## Q: English question? ^se-012
DE: Deutsche Frage?
**Core answer first.** Then short context.

## Cloze: Title ^se-013
DE: Satz mit {{Lücke}}.
Sentence with a {{blank}}.

## Term: Vorspannkraft = preload ^as-004

## Sequence: Process name ^qa-004
DE: Name des Ablaufs
1. First step
2. Second step
```

## Rules that protect your progress

- **Never change an id** once a card has been reviewed. Editing the text is fine and keeps the progress.
- Term cards get no `DE:` line, since they are asked in both directions.
- One idea per card. If the answer grows past about 6 lines, split it.
- File names are one lowercase word. Folder = deck.
- Only textbook knowledge. Nothing company-internal, not even in the private repo.

## Terminal

| Command | Purpose |
|---|---|
| `senser` | Web interface |
| `senser status` | Knowledge state per deck |
| `senser review -d sensors` | Review one deck in the terminal |
| `senser list` | All cards with next review |
| `senser ids` | Next free id per deck |
| `senser lint` | Check card files |

## Where things live

| What | Where |
|---|---|
| Cards | `~/senser-cards`, a private git repo. Commit after changes. |
| Progress | `~/.senser/state.db`, not in git. Do not delete it, since it holds your whole review history. |
| Settings | `~/.config/senser/senser.toml` (new cards per day, target retention) |
| Full guide | [docs/cards.md](cards.md) |
