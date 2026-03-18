# Cinef — What If Your Film Could Talk Back?

> "Give shot 010 a golden-hour look."
>
> The AI reads the scene, finds the lighting, reads the skill instructions,
> generates a 20-line overlay, validates quality, commits with attribution.
> Original footage? Untouched. Forever.

**This is a toy demo.** Not the real deal — just showing the principles.
No actual AI models run. QC scores are simulated. The USDA parser handles
maybe 20% of real USD syntax. But the *ideas* are real, and they work.

Not yet anyway.

```bash
python3 cinef.py     # See it in action (Python 3.10+, nothing else needed)
```

## The One Idea That Matters

Every element in the scene carries a tag saying which AI skill can modify it:

```
shot_010/base.usda
  camera   → cinef:skill = focus_pull     "I control the focus"
  lighting → cinef:skill = relight        "I control the lights"
  plate    → cinef:locked = true          "DON'T TOUCH ME"

shot_020/base.usda                        (completely different skills!)
  face     → cinef:skills = [lipsync, pose_track]
  camera   → cinef:locked = true          "Fixed close-up, hands off"
```

The AI discovers what to do by reading the scene itself.
Each shot is its own standard. The scene IS the pipeline.

Skills are **variant-aware** — each VariantSet option carries its own skill
configuration, constraints, and QC thresholds baked directly into the USD file.
The "dramatic" lighting variant and the "natural" variant are governed by the
same skill but with different rules. See [DEEP_DIVE.md](DEEP_DIVE.md#variant-aware-skills).

## Try It

Get [Claude Code](https://docs.anthropic.com/en/docs/claude-code), open
this folder, and just talk to it:

```
What shots are in the show?

Run a focus pull on shot_010 tracking the protagonist.

Give shot_010 dramatic golden-hour lighting.

The focus pull is too abrupt — update the skill to use cubic interpolation.

Commit my work and create a pull request.
```

The AI reads the skill instructions, follows them, validates the result,
and improves the instructions based on your feedback. The pipeline learns.

## New to Claude Code?

It's an AI coding tool that runs in your terminal. [Install it](https://docs.anthropic.com/en/docs/claude-code),
type `claude`, and you're in. Start with these:

- [Getting Started](https://docs.anthropic.com/en/docs/claude-code) — install and first run
- [Commands](https://code.claude.com/docs/en/commands.md) — `/help`, `/init`, `/loop`
- [CLI Reference](https://code.claude.com/docs/en/cli-reference.md) — `--resume`, flags

Type `/init` in any project to generate a `CLAUDE.md` — the system prompt
that tells Claude how to behave in your codebase. That's how this repo works.

Never used git? Just say `"I'm new to git, help me set up."` There's a
skill for that too.

## What's in Here

```
cinef.py                       # The demo — run this
show/show.usda                 # Root stage (the "canon")
show/shots/shot_010/base.usda  # Wide shot — lighting + camera skills
show/shots/shot_020/base.usda  # Close-up — facial + lip-sync skills
show/skills/impl/*.skill.md    # 7 skill files the AI reads and follows
advanced/transfer_gate.py      # Model validation demo (Transfer Oracle)
examples/multi-project/        # Scaling to real productions (5-level hierarchy)
```

## Go Deeper

| Doc | What you'll find |
|---|---|
| [WALKTHROUGH.md](WALKTHROUGH.md) | Step-by-step: git setup through skill chaining |
| [DEEP_DIVE.md](DEEP_DIVE.md) | Full architecture, MCP, Agent SDK, legal compliance |
| [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md) | Scaling to real films: folder structure, skill scoping, multi-project |
| [PODCAST_SCRIPT.md](PODCAST_SCRIPT.md) | Feed into [NotebookLM](https://notebooklm.google.com) for a video podcast |
| [CLAUDE.md](CLAUDE.md) | How Claude Code sees this project |

## Transfer Oracle (`advanced/`)

Your AI model says 95% accuracy. But will it work on *this* footage?
[Transfer Oracle](https://transferoracle.ai) catches the gap between
validation metrics and real-world transfer. No pixels leave your machine.

```bash
python3 advanced/transfer_gate.py --all   # SAFE / UNDERTRAINED / RED_FLAG
```

[Transfer Oracle](https://transferoracle.ai) |
[Operator](https://operator.droidtech.ai) |
[Franchise partners wanted](https://operator.droidtech.ai)

## Acknowledgments

- **[Pixar](https://graphics.pixar.com/)** — Created [OpenUSD](https://openusd.org),
  open-sourced 2016 ([TOST License](https://github.com/PixarAnimationStudios/OpenUSD/blob/release/LICENSE.txt)).
  Cinef is educational — no Pixar source code included.
- **[AOUSD](https://aousd.org/)** / **[ASWF](https://www.aswf.io/)** — OpenUSD standardization
  (Pixar, Apple, Autodesk, Adobe, NVIDIA, Linux Foundation)
- **[Anthropic](https://www.anthropic.com/)** — [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- **[C2PA](https://c2pa.org/)** — Content provenance standard
- **[Droidtech 42 AI Labs AB](https://operator.droidtech.ai)** —
  [Transfer Oracle](https://transferoracle.ai) + [Operator](https://operator.droidtech.ai)

## License

Copyright 2026 Lee Sandberg. **AGPL-3.0** — see [LICENSE](LICENSE).

Fork it, learn from it, build on it. Derivatives stay open source.
For commercial licensing: **lee.sandberg@gmail.com** (subject: **"Cinef"**).
