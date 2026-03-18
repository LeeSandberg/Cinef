# Cinef Deep Dive — Architecture, Integration, and Advanced Topics

This document covers everything that didn't fit in the README.
Start with the README and WALKTHROUGH first — come here when you want
to understand the full architecture, extend the pipeline, or integrate
with production tools.

---

## Table of Contents

1. [The Discovery Chain](#the-discovery-chain)
2. [OpenUSD Concepts for Film](#openusd-concepts-for-film)
3. [The Skill System in Detail](#the-skill-system-in-detail)
4. [Variant-Aware Skills](#variant-aware-skills)
5. [Skill Hierarchy — Five Levels of Scoping](#skill-hierarchy--five-levels-of-scoping)
6. [Meta-Prompts and Self-Improvement](#meta-prompts-and-self-improvement)
7. [Claude Code Power Features](#claude-code-power-features)
8. [Building AI Agents and Web Portals](#building-ai-agents-and-web-portals)
9. [MCP — Connecting Any Tool](#mcp--connecting-any-tool)
10. [Transfer Oracle — Model Validation](#transfer-oracle--model-validation)
11. [Legal Compliance and Provenance](#legal-compliance-and-provenance)

---

## The Discovery Chain

When Claude Code opens this project, here's exactly what happens:

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

### What is CLAUDE.md?

The `CLAUDE.md` file is the **system prompt** for your project. Claude Code
reads it first, every session. It tells Claude who it is and how to behave.

To create one for your own project:

```
$ claude
> /init
```

Claude analyzes your codebase — files, build systems, configs, conventions —
and generates a tailored CLAUDE.md. Edit it anytime. It's a living document
that evolves with your project.

---

## OpenUSD Concepts for Film

| OpenUSD Concept | Film Term | What It Does |
|---|---|---|
| **Prim** | Shot / Asset | Atomic scene element |
| **Layer** | Edit Pass | One opinion in the stack (each AI edit = one layer) |
| **VariantSet** | Take / Branch | Multiple alternatives within one Prim |
| **Reference** | Asset Link | Modular reuse without data duplication |
| **Payload** | Deferred Load | Load heavy data only when needed |

### Non-Destructive Layering

In a traditional pipeline, trying lighting A and lighting B means two full
renders. Trying A+B with camera moves X+Y means four renders. It explodes.

In Cinef, each is a 20-line overlay file. Compose them in any combination
without re-rendering. USD calls these "sparse overrides" — you only store
what changed.

### VariantSets — Creative Branching

Shot 010 has a lighting VariantSet: "natural" and "dramatic" — switchable.
Shot 020 has a performance VariantSet: "subtle" and "intense" — different
blendshape intensity for the same facial animation.

Director's cut, community ending, VFX option A vs B — all VariantSets.
They live in the same scene file, not as separate project copies.

---

## The Skill System in Detail

### Skill Registry

All skills are registered in [`show/skills/skills.usda`](show/skills/skills.usda) — a USD file that
can be sublayered into any stage. Each skill defines:

- **id** — unique identifier (e.g., `cinef.skill.relight`)
- **inputs** — what it needs (stage, plates, audio, prompts)
- **outputs** — what it produces (override layers, assets)
- **validation** — QC metrics that must pass before commit
- **toolBindings** — required execution environments
- **creditsPolicy** — attribution requirements

### Skill Instructions (skill.md files)

Each skill has a markdown file with:
- **Purpose** — one paragraph on what it does
- **When to Use** — triggers that should activate this skill
- **Execution Steps** — numbered steps Claude follows exactly
- **Output Layer Template** — the actual .usda template with placeholders
- **Constraints** — hard rules (never modify base, always validate, etc.)

### The Meta-Skill

[`meta.skill.md`](show/skills/impl/meta.skill.md) is the skill about skills. It governs:
1. **Selection** — matching natural language intent to skill IDs
2. **Execution checklist** — pre-flight verification before any skill runs
3. **Evaluation** — judging success beyond QC metrics (did it match intent?)
4. **Updating skills** — when and how to improve skill.md files
5. **Creating skills** — templates and triggers for new skills
6. **Chaining** — sequencing multiple skills (e.g., segment then relight)
7. **Memory** — what to remember after success or failure

---

## Variant-Aware Skills

### The Problem

A single skill like `relight` handles very different creative intents.
"Natural daylight" and "dramatic noir" both use the same relight skill, but
the constraints, QC thresholds, and execution approach are fundamentally
different. Without variant awareness, the skill either applies generic
defaults (suboptimal) or requires the user to spell out every constraint
each time (tedious).

### The Solution: Two-Layer Variant Binding

Variant-aware skills solve this with two complementary layers that don't
conflict because they serve different purposes:

**Layer 1 — USD file (discovery + guardrails):**
Each variant block in `base.usda` carries its own `customData` with skill
metadata, parameter ranges, constraints, and QC thresholds. This makes the
scene fully self-describing — any tool (not just Claude) can read a variant
and know exactly what governs it.

**Layer 2 — skill.md (execution instructions):**
The skill.md file contains `### variant_name` sections with detailed
execution notes, parameter tables, and creative guidance. Claude reads the
USD binding first, then jumps to the correct section in the skill.md.

### How It Works in the USD File

Inside a VariantSet block, each variant carries its own skill configuration:

```usda
variantSet "lightingVariant" = {
    "dramatic" (
        doc = "High-contrast dramatic lighting"
        customData = {
            # Skill binding — which skill and which variant section
            string cinef:skill = "cinef.skill.relight"
            string cinef:skillVariant = "dramatic"
            string cinef:skillRef = "skills/impl/relight.skill.md#dramatic"

            # Variant-specific parameter ranges
            float cinef:intensityRange_min = 0.1
            float cinef:intensityRange_max = 5.0
            string cinef:colorTempHint = "2700K-4000K warm key, 7000K+ cool fill"

            # Variant-specific constraints (override skill defaults)
            string[] cinef:constraints = [
                "key-to-fill ratio >= 3:1",
                "shadow density > 0.6"
            ]

            # Variant-specific QC thresholds (can be stricter or looser)
            float cinef:qc_temporal_flicker_threshold = 0.08
            float cinef:qc_color_shift_threshold = 0.05
        }
    ) {
        # ... actual light definitions ...
    }
}
```

### How It Works in the skill.md File

The skill.md file has a `## Variant-Specific Execution` section with
sub-headings for each known variant:

```markdown
## Variant-Specific Execution

Before executing, read the active variant's customData for constraints.

### natural
**Intent:** Balanced daylight — even illumination.
- Intensity range: 0.5 – 2.0
- Color cast: No deviation > 0.05 from (1,1,1)
- QC: temporal_flicker < 0.05, color_shift < 0.02

### dramatic
**Intent:** High contrast, cinematic drama.
- Intensity range: 0.1 – 5.0
- Key-to-fill ratio: >= 3:1
- QC: temporal_flicker < 0.08, color_shift < 0.05
```

### The Discovery Flow

```
base.usda → prim → VariantSet → active variant
  |                                  |
  cinef:skill (prim-level)           cinef:skillVariant = "dramatic"
  = which skill to use               cinef:skillRef = "relight.skill.md#dramatic"
                                     cinef:constraints = [...]
                                     cinef:qc_* = variant thresholds
                                         |
                                 skill.md ### dramatic
                                 = execution notes, parameter tables
```

1. Claude reads the prim's `cinef:skill` to identify the skill
2. Claude reads the active variant's `customData` for variant-specific bindings
3. Claude reads the `cinef:skillRef` to find the right section in skill.md
4. Variant constraints override skill defaults; skill.md provides the how-to
5. QC validation uses the variant's thresholds, not the skill's generic ones

### Currently Implemented Variants

**shot_010 — Lighting (`lightingVariant`):**

| Variant | Intent | Key Constraint | QC Flicker | QC Color Shift |
|---|---|---|---|---|
| `natural` | Balanced daylight | Color cast < 0.05 | < 0.05 | < 0.02 |
| `dramatic` | High contrast, warm/cool | Key:fill ≥ 3:1 | < 0.08 | < 0.05 |

**shot_020 — Performance (`performanceVariant`):**

| Variant | Intent | Peak Blendshape | QC Sync | QC Smoothness |
|---|---|---|---|---|
| `subtle` | Internal emotion | ≤ 0.3 | > 0.90 | > 0.97 |
| `intense` | Full emotional range | ≤ 1.0 | > 0.90 | > 0.93 |

### Adding New Variants

To add a new variant (e.g., `"golden_hour"` lighting):

1. Add the variant block inside the VariantSet in `base.usda` with full
   `customData` including `cinef:skill`, `cinef:skillVariant`,
   `cinef:skillRef`, constraints, and QC thresholds
2. Add a `### golden_hour` section in `relight.skill.md` with execution
   notes, parameter ranges, and creative guidance
3. Update `skills.usda` to add `"golden_hour"` to the `knownVariants` array
4. The next Claude session discovers it automatically — no code changes needed

### Why Both Layers?

| Question | USD answers | skill.md answers |
|---|---|---|
| Which skill governs this variant? | `cinef:skill` | — |
| What are the parameter limits? | `cinef:intensityRange_*` | Parameter tables |
| What are the QC thresholds? | `cinef:qc_*` | Noted in variant section |
| What's the creative intent? | `cinef:variantDoc` | **Execution notes** |
| How exactly do I execute? | — | **Step-by-step instructions** |
| Can non-Claude tools read this? | **Yes — it's USD** | No (Claude-specific) |

The USD file ensures the scene is self-describing for any tool in the
ecosystem. The skill.md ensures Claude has detailed execution guidance.
Neither is redundant — they serve different consumers.

### Conflict Resolution

If the USD `customData` and the skill.md disagree (e.g., different QC
thresholds), the USD file wins for parameter constraints and QC thresholds
(it's the scene owner's explicit configuration), and the skill.md wins for
execution approach (it has the detailed how-to). If the conflict is
significant, Claude flags it to the user before proceeding.

---

## Skill Hierarchy — Five Levels of Scoping

Skills exist at five levels, each scoped to prevent cross-contamination.
Skills inherit downward but never leak sideways. A show skill applies to
all its shots. A shot_010 variant skill never touches shot_020. The folder
structure enforces this — skills live next to the USD files they govern.

### Level 0: Framework (Cinef repo)

```
cinef/show/skills/impl/
  meta.skill.md          — How to select/chain/create skills (universal)
  git_onboard.skill.md   — Version control setup (universal)
```

These ship with the Cinef framework and rarely change. They work on any
film, any genre, any pipeline. Think of them as the "standard library."

Framework skills in this repo:
- [`meta.skill.md`](show/skills/impl/meta.skill.md) — skill selection, chaining, creation, evaluation
- [`git_onboard.skill.md`](show/skills/impl/git_onboard.skill.md) — version control setup
- [`relight.skill.md`](show/skills/impl/relight.skill.md) — lighting overrides (default, overridable)
- [`focus_pull.skill.md`](show/skills/impl/focus_pull.skill.md) — camera focus (default, overridable)
- [`lipsync.skill.md`](show/skills/impl/lipsync.skill.md) — blendshape animation (default, overridable)
- [`segment.skill.md`](show/skills/impl/segment.skill.md) — object segmentation (default, overridable)
- [`pose_track.skill.md`](show/skills/impl/pose_track.skill.md) — skeleton animation (default, overridable)

### Level 1: Show / Project (film repo root)

Show-level skills define rules that apply across the **entire film**.
The show-level `CLAUDE.md` acts as the system prompt for the whole project.

Example files (from the "Midnight Crossing" noir thriller):
- [`show-level/CLAUDE.md`](examples/multi-project/show-level/CLAUDE.md) — project system prompt (ACEScg, 24fps, anamorphic, Swedish dialogue)
- [`show-level/skills/skills.usda`](examples/multi-project/show-level/skills/skills.usda) — show skill registry (noir_grade, continuity_check, dailies_export)
- [`show-level/skills/impl/noir_grade.skill.md`](examples/multi-project/show-level/skills/impl/noir_grade.skill.md) — noir color grade skill (crushed blacks, desaturated midtones, cool shadows)

### Level 2: Scene

Scene-level skills enforce **continuity between shots** in the same narrative
sequence. The bar scene needs consistent lighting across all its shots, but
the rooftop scene has completely different lighting rules.

Example files:
- [`scene-level/CLAUDE.md`](examples/multi-project/scene-level/CLAUDE.md) — scene context (bar interior, warm tungsten practicals, cool moonlight, shot inventory)
- [`scene-level/skills/impl/bar_continuity.skill.md`](examples/multi-project/scene-level/skills/impl/bar_continuity.skill.md) — cross-shot continuity validation (Delta E < 2.0, intensity matching, color temp tolerance)

### Level 3: Shot

Shot-level skills are bound to **specific prims** via `cinef:skill` in
`customData`. This is what the demo currently uses — `relight`, `focus_pull`,
`lipsync`, `segment` are all shot-level in the demo structure.

Most skills live here. A shot is the natural unit of work.

Example files:
- [`shot-level/CLAUDE.md`](examples/multi-project/shot-level/CLAUDE.md) — shot context (hero shot, rack focus, eye light, strict QC, locked camera)
- [`shot-level/skills/impl/eye_light.skill.md`](examples/multi-project/shot-level/skills/impl/eye_light.skill.md) — shot-specific eye light (only this shot, last in chain, 0.3 max intensity)

Demo shot base files with skill bindings:
- [`show/shots/shot_010/base.usda`](show/shots/shot_010/base.usda) — wide establishing (focus_pull, relight, segment, pose_track)
- [`show/shots/shot_020/base.usda`](show/shots/shot_020/base.usda) — close-up reaction (lipsync, pose_track, locked camera)

### Level 4: Variant

Variant-level skills are the most granular. Each variant carries its own
constraints, QC thresholds, and execution notes via `cinef:skillVariant`
and `cinef:skillRef`. See [Variant-Aware Skills](#variant-aware-skills).

Example files:
- [`variant-level/example_variant_block.usda`](examples/multi-project/variant-level/example_variant_block.usda) — fully annotated "conflicted" vs "stoic" detective performance variants with customData skill bindings

Live variant bindings in the demo:
- [`show/shots/shot_010/base.usda`](show/shots/shot_010/base.usda) — `lightingVariant`: "natural" (strict QC, neutral color) vs "dramatic" (relaxed QC, warm/cool contrast)
- [`show/shots/shot_020/base.usda`](show/shots/shot_020/base.usda) — `performanceVariant`: "subtle" (micro-expressions, 0.3 peak) vs "intense" (full range, 1.0 peak)

### Full Chain Walkthrough

See [`SKILL_CHAIN_EXAMPLE.md`](examples/multi-project/SKILL_CHAIN_EXAMPLE.md) —
traces a single request ("Relight shot_030 with the conflicted performance")
through all five levels, showing which files Claude reads, what each level
contributes, and the final execution chain with output files.

### Inheritance and Override Rules

```
Level 0 (Framework)  →  relight.skill.md (default)
  ↓ inherits
Level 1 (Show)       →  relight.skill.md (override: "use ACEScg, stricter QC")
  ↓ inherits
Level 2 (Scene)      →  relight.skill.md (override: "match bar lighting")
  ↓ inherits
Level 3 (Shot)       →  (no override — uses scene version)
  ↓ inherits
Level 4 (Variant)    →  cinef:qc_temporal_flicker_threshold = 0.08
```

**Resolution order** (strongest to weakest):
```
Variant customData → Shot skills/ → Scene skills/ → Show skills/ → Framework skills/
```

If a shot has `skills/impl/relight.skill.md`, Claude reads **that** instead
of the scene, show, or framework version. The most specific file wins.

### Visibility Rules

| Skill defined at | Visible to | NOT visible to |
|---|---|---|
| Framework | Everything | — |
| Show | All scenes, shots, variants | Other films |
| Scene | All shots in this scene | Other scenes |
| Shot | This shot and its variants | Other shots (even in same scene) |
| Variant | This variant only | Other variants on the same prim |

### Each Level Gets a CLAUDE.md

| Level | Location | Purpose |
|---|---|---|
| Framework | `cinef/CLAUDE.md` | "You are an AI TD for OpenUSD" |
| Show | `my-film/CLAUDE.md` | "This is a noir thriller, ACEScg, 24fps" |
| Scene | `scenes/scene_01/CLAUDE.md` | "Bar interior, warm practicals, cool moonlight" |
| Shot | `shots/shot_010/CLAUDE.md` | "Hero shot, extra QC, director wants rack focus" |

Claude reads them in order: framework → show → scene → shot. More specific
instructions override less specific ones — just like USD layer composition.

### The Key Insight

**The folder structure is the access control.** There's no config file that
says "shot_010 can't use shot_020's skills." The skills simply live in
`shot_010/skills/` and Claude resolves them by walking up the directory
tree. If the skill isn't in the shot, check the scene. If not in the scene,
check the show. If not in the show, check the framework.

This mirrors how USD composition works: the most local opinion wins, and
you can always override from a more specific layer. Skills compose exactly
like USD layers.

See [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md) for the complete folder
structure, naming conventions, and migration guide.

See [`examples/multi-project/`](examples/multi-project/) for working
examples at every level — show CLAUDE.md, scene continuity skills,
shot-specific eye lights, variant performance constraints, and a
[full chain walkthrough](examples/multi-project/SKILL_CHAIN_EXAMPLE.md)
showing all five levels in action on a single request.

---

## Meta-Prompts and Self-Improvement

A **meta-prompt** is a prompt about prompting — you tell Claude Code how to
improve its own instructions:

```
"The focus_pull skill worked but transitions are too abrupt.
 Update focus_pull.skill.md to specify cubic Hermite interpolation
 with a max delta of 15 units per frame."
```

Claude edits the skill file. Next execution follows the improved version.

### The Self-Improving Loop

```
You → Claude Code → reads skill.md → executes skill → result
                  |
            updates skill.md based on what worked
                  |
            creates new skill.md if patterns emerge
                  |
            memorizes preferences for next session
```

### Examples

```
# Improve an existing skill
"The relight QC keeps failing on temporal_flicker. Update the
 skill to add a frame-blending smoothing step."

# Create a new skill from a pattern
"I keep manually color-matching between shots. Create a
 color_match skill that does this automatically."

# Memorize a preference
"Remember: all close-up shots should default to dramatic lighting."
```

---

## Claude Code Power Features

### `/loop` — Continuous Monitoring

```
/loop 5m check show/shots/*/qc/ for failed QC reports
/loop 2h run full show composition validation
```

Session-scoped, max 50 tasks, expires after 3 days.
See: [Scheduled Tasks](https://code.claude.com/docs/en/scheduled-tasks.md)

### `--resume` — Session Continuity

```bash
claude --resume              # Resume most recent session
claude --resume <id>         # Resume specific session
claude -r <id> "continue"   # Short form
```

Pipeline context survives between sessions.
See: [CLI Reference](https://code.claude.com/docs/en/cli-reference.md)

### `/btw` — Side Questions

```
/btw what frame range does shot_020 use?
```

Quick answers without cluttering conversation history.
See: [Interactive Mode](https://code.claude.com/docs/en/interactive-mode.md)

### Chrome Extension

```bash
/chrome    # Configure browser automation
```

Browser automation for web-based review tools.
See: [Chrome Integration](https://code.claude.com/docs/en/chrome.md)

---

## Building AI Agents and Web Portals

### Anthropic Agent SDK

The **Claude Agent SDK** lets you embed autonomous AI agents directly into
web applications:

- **Shot review portals** — embedded agent reads USD, executes skills, shows QC
- **Director's desk apps** — natural language to USD overrides in the browser
- **Pipeline dashboards** — monitor composition, trigger skills on new plates

See: [Claude Agent SDK](https://docs.anthropic.com/en/docs/agents-and-tools/claude-agent-sdk)

---

## MCP — Connecting Any Tool

**MCP (Model Context Protocol)** lets Claude Code connect to any external tool:

- **DaVinci Resolve / Nuke / Blender** — wrap their APIs as MCP servers
- **Shot tracking databases** — asset management as a skill binding
- **OpenColorIO** — native color space management
- **FFmpeg** — automatic proxy generation
- **growt-audit** — model validation before deployment

MCP turns the skill system into an open ecosystem.
See: [MCP Documentation](https://modelcontextprotocol.io/)

---

## Transfer Oracle — Model Validation

The `advanced/` folder demonstrates the Transfer Oracle QC gate.

**The problem:** A model reports 95% validation accuracy but silently fails
on new footage because the visual domain shifted from training data.

**The solution:** Before committing an override layer, extract feature vectors
locally and send only numerical embeddings to the audit service. No pixels,
no model weights, no scene descriptions leave your infrastructure.

```bash
python3 advanced/transfer_gate.py --all    # SAFE / UNDERTRAINED / RED_FLAG
```

Works for any ML model — film, medical, autonomous systems, manufacturing.

**Services:** [Transfer Oracle](https://transferoracle.ai) |
[Operator](https://operator.droidtech.ai) |
[Franchise partners wanted](https://operator.droidtech.ai) in all verticals.

---

## Legal Compliance and Provenance

Every AI-generated layer includes provenance metadata:

- **EU AI Act (Article 50)** — machine-readable labeling of synthetic content
- **Swedish Moral Rights (Ideella Rättigheter)** — patch-layer authorship
  preserves the right to be named
- **C2PA** — Content Credentials for tamper-proof lineage (production extension)

The provenance system tracks: author, AI model, prompt, timestamp, skillId,
QC status. Every contributor to a specific override layer is automatically
preserved in the version history.
