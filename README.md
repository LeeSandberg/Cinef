# Cinef — The Scene IS the Pipeline

Every element in the scene carries its own AI skill binding. The camera
knows which skill controls its focus. The lighting knows which skill
relights it. The source plate knows it's locked. The AI discovers what
to do by reading the scene itself — no external config, no hardcoded
pipeline. The OpenUSD files carry their own instructions.

**Fork it, swap `show.usda`, and you have a working AI-augmented pipeline.**

> "Give shot 010 a golden-hour look."
>
> The AI reads the scene, finds the lighting, reads the skill instructions,
> generates a 20-line overlay, validates quality, commits with attribution.
> Original footage? Untouched. Forever.

```bash
python3 cinef.py     # See it in action (Python 3.10+, nothing else needed)
```

---

## How It Works

```
shot_010/base.usda
  camera   → cinef:skill = focus_pull     "I control the focus"
  lighting → cinef:skill = relight        "I control the lights"
  plate    → cinef:locked = true          "DON'T TOUCH ME"

shot_020/base.usda                        (completely different skills!)
  face     → cinef:skills = [lipsync, pose_track]
  camera   → cinef:locked = true          "Fixed close-up, hands off"
```

Each shot is its own standard. Skills are embedded in USD `customData` —
any AI agent that can read files and follow markdown instructions can
execute them. The non-destructive override model means every AI edit is
a sparse 20-line `.usda` layer. Nothing is ever overwritten.

Skills are **variant-aware** — each VariantSet option carries its own
constraints and QC thresholds baked into the USD file. The "dramatic"
lighting variant and the "natural" variant use the same skill but with
different rules. See [DEEP_DIVE.md](DEEP_DIVE.md#variant-aware-skills).

## Works With Any AI Agent

The skill system is **agent-agnostic**. The entire interface is:

1. **Read** a `.usda` file — find `cinef:skill` in `customData`
2. **Read** a `.skill.md` file — follow the execution steps
3. **Write** a `.usda` override layer — validate with QC

That's it. Read structured metadata, read markdown instructions, write
structured output. Any agent that can read files and follow instructions
can run this pipeline.

**Agentic coding tools:**
[Claude Code](https://docs.anthropic.com/en/docs/claude-code),
[Cursor](https://cursor.com),
[Windsurf](https://windsurf.com),
[Cline](https://github.com/cline/cline),
[Aider](https://aider.chat),
[Devin](https://devin.ai),
[GitHub Copilot Workspace](https://githubnext.com/projects/copilot-workspace),
[Skill security Skill Scanner](https://github.com/cisco-ai-defense/skill-scanner),
[PDF Resource how to design skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf),
[Get Shit Done  GSD Free meta-prompt skills Recommended](https://github.com/gsd-build/get-shit-done),
[Anthropics Claude Code Skill Resources on GitHub](https://github.com/anthropics/skills)

**Custom agents built on any LLM SDK:**
OpenAI, Anthropic, Google Gemini, Llama, Mistral — if it can read a file
and write a file, it can execute a Cinef skill.

The `CLAUDE.md` is just this project's system prompt — the same concept
as `.cursorrules` or `.windsurfrules`. The `.skill.md` files are plain
markdown. The `customData` bindings are standard USD. No vendor lock-in,
no proprietary runtime, no SDK dependency.

## Try It

Open this folder in your AI coding agent and just talk to it:

```
What shots are in the show?

Run a focus pull on shot_010 tracking the protagonist.

Give shot_010 dramatic golden-hour lighting.

The focus pull is too abrupt — update the skill to use cubic interpolation.
```

The AI reads the skill instructions, follows them, validates the result,
and improves the instructions based on your feedback. The pipeline learns.

## Five Levels of Skills

Skills scope from global framework rules down to individual variant
constraints. Each level inherits downward but never leaks sideways:

| Level | Scope | Example |
|---|---|---|
| **Framework** | Universal, ships with Cinef | meta.skill.md, git_onboard.skill.md |
| **Show** | Entire film | "All shots use ACEScg, never Rec709" |
| **Scene** | One sequence | "Lighting must match across all bar shots" |
| **Shot** | One shot | relight, focus_pull, lipsync, segment |
| **Variant** | One creative option | "dramatic" lighting: warm key, cool fill, 3:1 ratio |

See [`examples/multi-project/`](examples/multi-project/) for working
examples at every level, and the
[full chain walkthrough](examples/multi-project/SKILL_CHAIN_EXAMPLE.md).

## This is a Demo

No actual AI models run. QC scores are simulated. The USDA parser handles
maybe 20% of real USD syntax. But the *architecture* is real — fork it,
plug in real models, and the composition model scales.

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
| [CLAUDE.md](CLAUDE.md) | The system prompt for this project |

## New to AI Coding Agents?

The easiest way to try this is with [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
— install it, type `claude` in this directory, and start talking.

Never used git? Just say `"I'm new to git, help me set up."` There's a
skill for that too.

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
