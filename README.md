# output-styles

Claude Code output styles I use. A style changes how Claude writes back to you: what it
leads with, how it formats, what it refuses to pad.

## Install

There is no CLI for output styles. They are plain files Claude Code reads, so installing
one is a copy:

```bash
git clone https://github.com/LarrySequino/output-styles
cd output-styles && ./install.sh
```

`./install.sh shipmate` installs just one. Both print the exact `settings.json` line to
paste.

Then pick it in `/config`, or set it in `~/.claude/settings.json`:

```json
{ "outputStyle": "Shipmate" }
```

**Claude Code only.** Skills work across about 70 agents; output styles do not. Codex,
Cursor and Grok will ignore these entirely.

## Styles

| style | for |
|---|---|
| `Shipmate` | day-to-day work where you want the outcome first and no padding |

### Shipmate

Direct teammate mode. Outcome first, bullets over prose, explicit recommendations, no
filler. Wisecracks allowed when they attach to something that actually happened.

It carries `keep-coding-instructions: true`, so it layers on top of Claude Code's coding
behavior instead of replacing it.

The rules it enforces, in short: lead with what happened or what to do, report what failed
as loudly as what worked, separate what was verified from what was assumed, never compress
away a risk or a blocker, and never pad with filler openers, summary recaps, or offers to
continue.

## Related

- [LarrySequino/skills](https://github.com/LarrySequino/skills) for the skills, which
  install with `npx skills add` and work across most agents.
