# Writing cards

How to add and edit cards in Der Senser. Keep this page open while writing cards.

## Quick workflow

1. Open your cards folder (`~/senser-cards`, or whatever `cards_dir` says in `~/.config/senser/senser.toml`).
2. Add cards to an existing topic file, or create a new file (template below).
3. Run `senser ids` to get the next free id for the deck.
4. Run `senser lint` to check the file. Fix anything it reports.
5. Reload the browser. New cards appear right away, with no restart needed.
6. Commit: `git add -A && git commit -m "Add cards on <topic>"` in the cards folder.

## Folder and file layout

```
senser-cards/
├── sensors/            ← folder = deck
│   ├── forcetorque.md  ← one file per topic
│   └── encoders.md
├── actuators/
│   └── harmonicdrive.md
└── ...
```

- **Folder name = deck name.** Sub-folders create sub-decks (`sensors/vision/` → deck `sensors/vision`).
- **File names are one lowercase word**, no spaces: `harmonicdrive.md`, `screwjoints.md`.
- One file per topic, with several cards per file. Aim for 3 to 15 cards per file.
- Files named `README.md` are ignored, so you can keep notes there.

## File template

Copy this to start a new topic file:

```markdown
---
tags: [topic, subtopic]
---

# Topic title (a plain note heading, not a card)

## Q: English question? ^xx-001
DE: Deutsche Frage?
**Core answer first.** Then one or two lines of context: why, or what follows from it.

## Cloze: Short title ^xx-002
DE: Deutscher Satz mit {{Lücke}}.
English sentence with a {{blank}} and another {{blank}}.

## Term: Deutscher Begriff = English term ^xx-003
Optional one-line note, shown with the answer in both directions.

## Sequence: Name of the process ^xx-004
DE: Name des Ablaufs
1. First step
2. Second step
3. Third step
```

The frontmatter (between the `---` lines) is optional. Use `deck: name` there only to
override the folder-based deck.

## Card types

A card starts with a level-2 heading `## <Type>: <title> ^<id>`. Everything up to the next
heading is its body. Headings without a type (like `# Topic title` or `## Background`) are
plain notes and are not asked.

| Type | Heading | Question shown | Answer shown |
|---|---|---|---|
| `Q` | `## Q: <question> ^id` | the question | the body |
| `Cloze` | `## Cloze: <optional title> ^id` | body with each `{{…}}` hidden | body with blanks filled in |
| `Term` | `## Term: <German> = <English> ^id` | asked in **both directions** | other side plus note |
| `Sequence` | `## Sequence: <name> ^id` | name plus number of steps | the numbered list |

Rules:
- `Q` needs a question and a non-empty body.
- `Cloze` needs at least one `{{blank}}`. Several blanks are all hidden at once.
- `Term` needs exactly one ` = `. It produces two cards (`id` and `id.r`), and only one
  direction is asked per session.
- `Sequence` needs at least two top-level list items (`1.` or `-`).

## German prompt (`DE:` line)

Questions are written in technical English. If a question is hard to understand, press **D**
during review (web) or type `d` (terminal) to see the German version. It shows the question
only, not the answer.

- Add **one** line starting with `DE:` anywhere in the body. The first line after the heading is the convention.
- For `Cloze`, write the German sentence with the same `{{blanks}}`. They are hidden too.
- For `Sequence`, translate the name.
- `Term` cards must not have a `DE:` line, because they are bilingual already.
- Each use is counted. The dashboard tile **German help 30d** shows how often you needed it.
  If the number drops over time, your technical English is improving.

## Ids

Every card needs an id at the end of its heading: `^se-012`.

- Format: `<deck prefix>-<three digits>`. Lowercase letters, digits and `-` only.
- **Never change or reuse an id.** Review history is attached to the id, not the text:
  - Fixing a typo or improving the answer text keeps your progress.
  - Changing the id makes it a new card, and its progress starts from zero.
  - Deleting a card leaves its history in the database. This is harmless.
- `senser ids` lists every prefix with its next free id.

Prefixes in use:

| Deck | Prefix | Deck | Prefix |
|---|---|---|---|
| manufacturing | `mf` | controls | `co` |
| assembly | `as` | quality | `qa` |
| materials | `ma` | lean | `le` |
| sensors | `se` | industrialization | `in` |
| actuators | `ac` | robotics | `ro` |
| metrology | `me` | safety | `sa` |
| digitalization | `di` | | |

For a new deck, choose a new two-letter prefix and add it to this table.

## Writing good cards

- **One idea per card.** If an answer needs more than about 6 lines, split the card.
- **Core answer first, in bold**, then short context such as the reason, a consequence or an example.
  Understanding the reason helps you remember the fact.
- Prefer lists and small tables over long sentences.
- **Language:** questions and answers in technical English, with a `DE:` line for the question.
  Put German terms in parentheses where they help (`primary shaping (Urformen)`).
- Use `Term` cards for vocabulary you will hear in the plant (Vorspannkraft = preload).
- Use `Sequence` for processes where the order matters (8D, commissioning, changeover).
- Write questions that need recall. "What are the three components of X?" is better than "Is X made of three parts?".

## What must never go into cards

Only general knowledge: anything you could find in a textbook, a standard or a supplier's
public datasheet. **Never** write company-internal information: internal processes, drawings,
part numbers, supplier terms, KPIs, customer names or internal project names. This applies
to private repositories too.

Rule of thumb: *Would this appear in a textbook? Then it is fine.*

## Format of Markdown in cards

Answers support normal Markdown: **bold**, *italic*, lists, tables, `code` and code blocks.
Raw HTML is not rendered.

## Checklist before committing

- [ ] `senser lint` reports 0 problems
- [ ] every new card has a new id (`senser ids`)
- [ ] `Q`, `Cloze` and `Sequence` cards have a `DE:` line
- [ ] no company-internal content
