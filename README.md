# Cinef — AI-Augmented OpenUSD Film Pipeline (Educational Demo)

A simplified, educational implementation of the **Forkable Film** architecture:
treating a film not as a fixed render, but as a versioned, composable system
of layered creative intent — powered by OpenUSD and AI skills.

## What This Demonstrates

**Claude Code as both interpreter AND author of OpenUSD:**
- Reads `.usda` scene descriptions to understand shot structure
- Generates sparse override layers (non-destructive edits)
- Loads skill instructions from `.skill.md` files coupled to scene elements
- Validates changes through QC gates before committing
- Documents provenance for every AI intervention

**Each show, each scene, can have its own standard** — shot_010 might have
relighting variants while shot_020 has lip-sync overrides. The USD LayerStack
lets everything compose without conflict.

## Quick Start

```bash
# Run the full pipeline demo (no dependencies beyond Python 3.10+)
python3 cinef.py

# Run the Transfer Oracle QC gate demo
python3 advanced/transfer_gate.py --all
```

## What is CLAUDE.md? (The System Prompt for Your Project)

The `CLAUDE.md` file at the root of this repository is the **system prompt**
that tells Claude Code who it is and how to behave inside this project.
Every time Claude Code opens a directory, it reads `CLAUDE.md` first —
before looking at any other file.

In this project, CLAUDE.md tells Claude Code:

- **You are an AI technical director** for a film pipeline built on OpenUSD
- **Start by reading `show/show.usda`** — the root stage tells you where
  the meta-skill, skill registry, and instructions live
- **Parse each shot's `base.usda`** — look for `cinef:skill` bindings on
  each prim to discover which skills govern which scene elements
- **Read the skill.md before modifying anything** — follow the instructions exactly
- **Write override layers, never modify base files** — all changes are non-destructive
- **Validate and commit with provenance** — QC must pass before committing

### How to Create a CLAUDE.md for Your Own Project

When you install Claude Code and open a terminal, you get the `>` prompt.
Type `/init` and press Enter:

```
$ claude
> /init
```

Claude Code analyzes your project — reads your files, understands the
structure, checks for build systems, configs, and conventions — then
generates a `CLAUDE.md` tailored to your codebase. This is how the
CLAUDE.md in this repo was created.

You can edit it anytime. It's a living document — as your project evolves,
update the CLAUDE.md to reflect new conventions, skills, or workflows.
Claude Code reads it fresh at the start of every session.

### The Chain: CLAUDE.md to OpenUSD to Skills

```
CLAUDE.md (system prompt)
  "You are an AI TD. Start with show.usda"
    |
show/show.usda (root stage)
  cinef:metaSkill → meta.skill.md        "Read this first"
  cinef:skillRegistry → skills.usda       "All available skills"
  cinef:instructions → "Parse shots, find cinef:skill on prims"
    |
shots/shot_010/base.usda
  main_cam  → cinef:skill = focus_pull   "Read focus_pull.skill.md"
  lighting  → cinef:skill = relight      "Read relight.skill.md"
  tracking  → cinef:skills = [segment, pose_track]
  plate     → cinef:locked = true        "DO NOT TOUCH"
    |
shots/shot_020/base.usda (DIFFERENT skills, DIFFERENT prims)
  face_track → cinef:skills = [lipsync, pose_track]
  audio_sync → cinef:skill = lipsync, role = input
  main_cam   → cinef:locked = true       "Fixed close-up"
```

Claude Code discovers what to do by reading the scene itself. No external
config, no hardcoded pipeline — the OpenUSD files carry their own instructions.

## New to Git? Start Here

Never used git before? Claude Code walks you through everything:

```
I'm new to git. Help me set up this project and push it to GitHub.
```

Claude reads the `git_onboard` skill and interactively helps you:
initialize a repo, create a GitHub account, make your first commit,
create a branch, push, and create pull requests — all in the context
of your actual Cinef project. No abstract tutorials.

See [WALKTHROUGH.md](WALKTHROUGH.md) Section 0 for the full guide.

## Try It — Claude Code Interactive Prompts

Open Claude Code in this directory and try these prompts:

```
What shots are in the show? What skills can I run on each?

Run a focus pull on shot_010 tracking the protagonist from wide to close.

Give shot_010 dramatic golden-hour lighting as a new variant.

Generate lip-sync animation for shot_020 from the dialogue audio,
use the intense performance variant.

Show me all AI override layers for shot_010 and their provenance.

The focus pull transitions are too abrupt. Update focus_pull.skill.md
to specify cubic interpolation with max 15 units per frame.

Commit my shot_010 overrides and create a pull request for review.
```

See [WALKTHROUGH.md](WALKTHROUGH.md) for the full step-by-step interactive guide.

## Claude Code Integration

### The `/loop` Feature — Continuous Execution

Claude Code's `/loop` command runs a prompt or slash command on a recurring
interval (default: 10 minutes). Supports `s`, `m`, `h`, `d` units.
This is powerful for pipeline monitoring:

```
/loop 5m check the QC reports in show/shots/*/qc/ and flag any failures
/loop 10m review recent AI overrides and validate layer composition
/loop 2h run full show composition validation
```

This keeps the pipeline under continuous AI supervision — Claude Code watches
for issues, validates new layers, and can trigger corrective skills automatically.
Session-scoped, max 50 scheduled tasks, expires after 3 days.

See: [Claude Code Scheduled Tasks](https://code.claude.com/docs/en/scheduled-tasks.md)

### `--resume` — Pick Up Where You Left Off

```bash
claude --resume              # Resume most recent conversation
claude --resume <id>         # Resume a specific session by ID
claude --resume auth-work    # Resume by session name
claude -r <id> "continue"   # Short form with follow-up prompt
```

Your pipeline context — which shots you were working on, what skills were
queued, what QC issues were flagged — all survives between sessions.
Use `--fork-session` to resume but create a new session branch.

See: [Claude Code CLI Reference](https://code.claude.com/docs/en/cli-reference.md)

### `/btw` — Side Questions Without Context Clutter

The `/btw` command asks quick side questions without cluttering your main
conversation history:

```
/btw what was the skill ID for the relight module again?
/btw what frame range does shot_020 use?
```

Useful when you need a quick fact check mid-pipeline without derailing the
current task.

See: [Claude Code Interactive Mode](https://code.claude.com/docs/en/interactive-mode.md)

### Chrome Extension — "Claude in Chrome"

The Claude Code Chrome extension (`/chrome` to configure) brings browser
automation to your pipeline workflow. When reviewing shots in a web-based
review tool, Claude Code can interact with the browser directly:

```bash
claude --chrome              # Enable for session
/chrome                      # Configure from within Claude Code
```

Capabilities: browser automation, web testing, form filling, data extraction
from review tools, console debugging.

Requires Claude Code v2.0.73+, Chrome or Edge.

See: [Claude Code Chrome Integration](https://code.claude.com/docs/en/chrome.md)

### Self-Documenting: Claude Code Reads Its Own Skills

Claude Code can read its own documentation with built-in commands:

```
/help              # Built-in command reference
/release-notes     # Full changelog
/status            # Version, model, account info
/doctor            # Diagnose installation issues
```

See: [Claude Code Commands](https://code.claude.com/docs/en/commands.md)

## Meta-Prompts and Meta-Skills

### What Are Meta-Prompts?

A **meta-prompt** is a prompt about prompting — you tell Claude Code how to
improve its own instructions. In this pipeline, meta-prompts are how the
skills evolve:

```
"The focus_pull skill worked but the transitions are too abrupt.
 Update focus_pull.skill.md to specify cubic Hermite interpolation
 with a max delta of 15 units per frame."
```

Claude Code reads the existing `.skill.md`, understands what changed, and
rewrites the instructions. Next time it executes that skill, it follows
the improved version.

### The Self-Improving Feedback Loop

When Claude Code successfully executes a skill:

1. **Ask Claude to update the skill** — "That focus pull worked great, but
   update the skill.md to prefer cubic interpolation over linear"
2. **Ask Claude to create new skills** — "We keep doing the same color grade
   adjustment, make a new `color_match` skill for it"
3. **Ask Claude to memorize patterns** — "Remember that shot_010 always needs
   the dramatic lighting variant first"

This creates a **self-improving pipeline**: the skills evolve with your
creative process. Each `.skill.md` is a living document that Claude Code
both reads and writes.

### Meta-Skill Pattern

```
You → Claude Code → reads skill.md → executes skill → result
                  ↓
            updates skill.md based on what worked
                  ↓
            creates new skill.md if needed
                  ↓
            memorizes preferences for next session (CLAUDE.md / memory)
```

### Practical Examples

```
# Meta-prompt: improve an existing skill after seeing results
"The relight QC keeps failing on temporal_flicker. Update the
 relight.skill.md to add a frame-blending smoothing step."

# Meta-prompt: create a new skill from a repeated pattern
"I keep manually adjusting color temperature between indoor/outdoor
 shots. Create a new color_match.skill.md that does this automatically."

# Meta-prompt: memorize a project preference
"Remember: for this show, all close-up shots (shot_020+) should
 default to the 'dramatic' lighting variant."

# Meta-prompt: Claude Code learns about itself
"Read /help and /release-notes, then update the CLAUDE.md with
 any new features that could improve our pipeline workflow."
```

## Architecture Overview

```
show/
├── show.usda                    # Root stage (Canon — immutable)
├── shots/
│   └── shot_###/
│       ├── base.usda            # Shot base (locked footage + camera)
│       ├── ai/                  # AI override layers (sparse deltas)
│       │   ├── relight_v001.usda
│       │   ├── focus_pull_v001.usda
│       │   └── mask_v001.usda
│       └── qc/                  # QC reports per skill execution
├── assets/                      # Reusable character/prop definitions
├── media/
│   ├── plates_proxy/            # Lightweight working proxies
│   └── plates_hi/               # Hi-res manifests (Ar-resolved)
└── skills/                      # USB Registry
    ├── skills.usda              # Skill definitions in USD format
    ├── skills.schema.json       # Validation contract
    └── impl/                    # Skill instruction files
        ├── relight.skill.md     # ← Claude Code reads these
        ├── segment.skill.md
        ├── focus_pull.skill.md
        ├── lipsync.skill.md
        ├── pose_track.skill.md
        └── git_onboard.skill.md # Git + GitHub setup for beginners
```

## Key Concepts

| OpenUSD Concept | Film Term | What It Does |
|---|---|---|
| **Prim** | Shot / Asset | Atomic scene element |
| **Layer** | Edit Pass | One opinion in the stack (each AI edit = one layer) |
| **VariantSet** | Take / Branch | Multiple alternatives within one Prim |
| **Reference** | Asset Link | Modular reuse without data duplication |
| **Payload** | Deferred Load | Load heavy data only when needed |

## Building AI Agents into Websites and Portals

### Anthropic Agent SDK

The **Claude Agent SDK** (`claude_agent_sdk`) lets you embed autonomous AI agents
directly into web applications, portals, and production services. In the Cinef
context, this means you can build:

- **Web-based shot review portals** where an embedded agent reads the USD stage,
  executes skills, and presents QC results — all within the browser
- **Client-facing "director's desk"** apps where non-technical users describe
  creative intent in natural language and the agent translates it to USD overrides
- **Automated pipeline dashboards** that monitor show composition and trigger
  skills when new plates arrive

The Agent SDK provides tool use, multi-turn conversations, and structured output
that map directly to the USB skill contracts in this pipeline.

See: [Claude Agent SDK](https://docs.anthropic.com/en/docs/agents-and-tools/claude-agent-sdk)

### MCP — Model Context Protocol ("MCP Anything")

**MCP (Model Context Protocol)** lets Claude Code connect to any external tool
or data source as a first-class capability. Currently supports Python-based
MCP servers. In this pipeline:

- **Custom MCP servers** can wrap DaVinci Resolve, Nuke, or Blender APIs —
  giving Claude Code direct tool access to professional VFX applications
- **Database MCP servers** connect to shot tracking databases, asset management
  systems, or review platforms
- **The `growt-audit` MCP server** (configured in this project) provides model
  validation before deployment — ensuring AI skills produce reliable results

MCP turns the skill system from a closed loop into an open ecosystem where
any Python-accessible tool becomes a potential skill binding.

Example: an MCP server wrapping OpenColorIO gives Claude Code native color
space management, or one wrapping FFmpeg enables automatic proxy generation.

See: [MCP Documentation](https://modelcontextprotocol.io/)

## Advanced: Transfer Oracle QC Gate (`advanced/`)

The `advanced/` folder contains production-grade model validation for the
pipeline. Before an AI skill's output is committed to the USD stage, the
**Transfer Oracle** validates that the ML model's learned structure will
actually transfer to the target shot's visual domain.

### Why This Matters for Film

A segmentation model might report 95% validation accuracy — but silently
produce garbage on shot_020 because the footage has different lighting,
color grading, or camera characteristics than the training data.
**Standard metrics do not catch this.** The Transfer Oracle does.

### IP Protection

Feature vectors are extracted locally — **raw plates, model weights, and
scene descriptions never leave your infrastructure.** Only numerical
embeddings (arrays of floats) are sent to the audit endpoint:

```
┌─── YOUR INFRASTRUCTURE ───────────────────────┐
│  Plates → Model → Features [0.23, -1.4, ...]  │──→ growt-audit
│  USD scene descriptions stay local             │←── SAFE / RED_FLAG
│  Model weights stay local                      │
│  No pixels transmitted                         │
└────────────────────────────────────────────────┘
```

### Running the Demo

```bash
# All three scenarios (SAFE / UNDERTRAINED / RED_FLAG)
python3 advanced/transfer_gate.py --all

# Specific scenario — the dangerous RED_FLAG case
python3 advanced/transfer_gate.py --distribution alien

# Feature extraction guide for each skill type
python3 advanced/mcp_integration.py
```

The three scenarios demonstrate:

| Distribution | Diagnosis | What Happens |
|---|---|---|
| `matching` | SAFE | Model transfers well, override layer committed |
| `shifted` | UNDERTRAINED | Partial drift detected, commit blocked |
| `alien` | RED_FLAG | 95% val accuracy but 0% transfer — **the dangerous case** |

### Production Use

In production, Claude Code calls the real MCP server directly:

```python
result = mcp__growt-audit__audit_model_transfer(
    features_train=training_embeddings,
    labels_train=training_labels,
    features_deploy=shot_frame_embeddings,
    val_accuracy=0.95,
)
# result.diagnosis → SAFE / RED_FLAG / BAD_MODEL / UNDERTRAINED
# result.safe_to_deploy → commit or block the override layer
```

This works for **any ML model**, not just film — computer vision, NLP,
audio, medical imaging, autonomous systems. If your model has a
penultimate layer, the Transfer Oracle can validate it.

**Services:**
- [Transfer Oracle](https://transferoracle.ai) — Model validation platform
- [Operator](https://operator.droidtech.ai) — AI operations and monitoring

### Operator Franchise — We're Looking for Partners

DroidTech operates as a **franchise model** — we're actively looking for
**operators in different domains and regions** to deploy Transfer Oracle
and AI pipeline validation in their verticals:

- **Film & VFX studios** — validate AI skills before they touch the USD stage
- **Medical imaging** — ensure diagnostic models transfer across scanner types
- **Autonomous systems** — validate perception models across environments
- **Manufacturing** — QC vision models across production lines and lighting
- **Any domain with ML models** — if you deploy models, we validate transfer

Regional operators get the platform, training, and support to run Transfer
Oracle as a service in their market. Contact via [operator.droidtech.ai](https://operator.droidtech.ai).

## Legal Compliance

Every AI-generated layer includes provenance metadata:
- **EU AI Act (Article 50)**: Machine-readable labeling of synthetic content
- **Swedish Moral Rights**: Patch-layer authorship preserves contributor attribution
- **C2PA**: Content Credentials for tamper-proof lineage (production extension)

## Acknowledgments

This project builds on the work of extraordinary teams and open standards:

- **[Pixar Animation Studios](https://graphics.pixar.com/)** — Created Universal Scene Description
  (USD), the foundational format this project is built on. USD was originally developed for
  Pixar's internal production pipeline and open-sourced in 2016. Cinef is a simplified educational
  reimplementation and does not include Pixar's USD source code.
  OpenUSD is licensed under the [TOST License (Tomorrow Open Source Technology License 1.0)](https://github.com/PixarAnimationStudios/OpenUSD/blob/release/LICENSE.txt).

- **[Alliance for OpenUSD (AOUSD)](https://aousd.org/)** — The joint effort by Pixar, Apple,
  Autodesk, Adobe, and NVIDIA to standardize and evolve USD as an open ecosystem. AOUSD operates
  under the [Academy Software Foundation (ASWF)](https://www.aswf.io/) / Linux Foundation umbrella.

- **[Academy Software Foundation (ASWF)](https://www.aswf.io/)** — Hosts OpenUSD and other
  critical open-source projects for the film and media industry including OpenEXR, OpenColorIO,
  OpenTimelineIO, and MaterialX.

- **[Anthropic](https://www.anthropic.com/)** — Creator of Claude and Claude Code, the AI
  coding tool that serves as the agent in this pipeline. Claude Code's tool-use architecture
  and CLAUDE.md system make the skill-binding pattern possible.

- **[C2PA (Coalition for Content Provenance and Authenticity)](https://c2pa.org/)** — The
  content credentials standard referenced in the provenance system for tamper-proof attribution.

- **[Droidtech 42 AI Labs AB](https://operator.droidtech.ai)** — Developer of
  [Transfer Oracle](https://transferoracle.ai) (model transfer validation) and the
  [Operator](https://operator.droidtech.ai) platform. The Transfer Oracle integration
  in `advanced/` demonstrates pre-commit model validation as a QC gate in the pipeline.

## Links & References

**Pipeline & Formats:**
- [OpenUSD Documentation](https://openusd.org/release/index.html)
- [OpenUSD Source (Pixar)](https://github.com/PixarAnimationStudios/OpenUSD)
- [Alliance for OpenUSD (AOUSD)](https://aousd.org/)
- [OpenTimelineIO](https://opentimeline.io/)
- [ASWF (Academy Software Foundation)](https://www.aswf.io/)
- [C2PA Content Credentials](https://c2pa.org/)

**Claude Code & AI:**
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code CLI Reference](https://code.claude.com/docs/en/cli-reference.md)
- [Claude Code Commands](https://code.claude.com/docs/en/commands.md)
- [Claude Code Scheduled Tasks (`/loop`)](https://code.claude.com/docs/en/scheduled-tasks.md)
- [Claude Code Chrome Integration](https://code.claude.com/docs/en/chrome.md)
- [Claude Agent SDK](https://docs.anthropic.com/en/docs/agents-and-tools/claude-agent-sdk)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)

**Model Validation & Operations:**
- [Transfer Oracle](https://transferoracle.ai) — Validate model transfer before deployment
- [Operator](https://operator.droidtech.ai) — AI operations platform

## License

Copyright 2026 Lee Sandberg

This project is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0).
See [LICENSE](LICENSE) for the full text.

This means:
- You can use, modify, and distribute this code freely
- Any derivative work must also be open-sourced under AGPL-3.0
- If you run a modified version as a network service, you must share the source
- Attribution is required

**Want a different license?** For commercial licensing, proprietary use, or custom
arrangements, contact **lee.sandberg@gmail.com** with subject line **"Cinef"**.
