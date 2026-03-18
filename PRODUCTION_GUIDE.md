# Production Guide — Scaling Cinef to Real Film Projects

How to organize a forked Cinef project for actual production: multiple
films, scenes, shots, variants — without skills bleeding across boundaries.

---

## Table of Contents

1. [Two Repos, Not One](#two-repos-not-one)
2. [The Full Folder Structure](#the-full-folder-structure)
3. [Skill Hierarchy and Scoping](#skill-hierarchy-and-scoping)
4. [How Skills Inherit and Override](#how-skills-inherit-and-override)
5. [Variant Skills Stay in Their Lane](#variant-skills-stay-in-their-lane)
6. [Example: Two Films, Full Tree](#example-two-films-full-tree)
7. [CLAUDE.md Per Level](#claudemd-per-level)
8. [Naming Conventions](#naming-conventions)
9. [Migration from Demo](#migration-from-demo)

---

## Two Repos, Not One

**Cinef is the engine. Your film is the project.**

Do NOT put your film files inside the Cinef repo. Fork or install Cinef as
a framework, then create a separate repo for each production.

```
# The Cinef framework (this repo — fork it, don't modify upstream)
cinef/
  cinef.py                    # Pipeline engine
  advanced/                   # Transfer gate, utilities
  show/skills/                # GLOBAL skill library (ships with Cinef)
    skills.usda               # Global skill registry
    impl/                     # Global skill instructions
      meta.skill.md
      relight.skill.md        # Default relight — no variant assumptions
      lipsync.skill.md        # Default lipsync — no variant assumptions
      focus_pull.skill.md
      segment.skill.md
      pose_track.skill.md
      git_onboard.skill.md
  CLAUDE.md                   # Framework-level system prompt

# Your film project (separate repo)
my-film/
  CLAUDE.md                   # Project-level system prompt (overrides framework)
  show.usda                   # Root stage for this film
  skills/                     # Project-level skills (extend/override Cinef defaults)
  scenes/                     # All scenes in this film
  assets/                     # Shared assets across scenes
  media/                      # Plates, audio, HDR maps
```

### How they connect

Your project references Cinef as a submodule, package, or just copies the
engine files:

```bash
# Option A: Git submodule
cd my-film/
git submodule add https://github.com/YourOrg/Cinef.git cinef

# Option B: Just copy the engine
cp -r cinef/cinef.py my-film/
cp -r cinef/advanced/ my-film/

# Option C: pip install (future)
pip install cinef
```

The key rule: **Cinef ships global skills. Your project adds project-level,
scene-level, shot-level, and variant-level skills on top.**

---

## The Full Folder Structure

```
my-film/                              # PROJECT ROOT (its own git repo)
│
├── CLAUDE.md                         # Project system prompt
├── show.usda                         # Root stage — references all scenes
│
├── cinef/                            # Cinef framework (submodule or copy)
│   ├── cinef.py
│   └── ...
│
├── skills/                           # PROJECT-LEVEL skills
│   ├── skills.usda                   # Project skill registry (extends Cinef's)
│   ├── skills.schema.json
│   └── impl/
│       ├── meta.skill.md             # Project meta-skill (can override Cinef's)
│       ├── color_match.skill.md      # Custom skill for this production
│       └── dailies_review.skill.md   # Custom skill for this production
│
├── assets/                           # SHARED ASSETS (referenced by any scene)
│   ├── characters/
│   │   ├── protagonist.usda
│   │   └── antagonist.usda
│   ├── environments/
│   │   ├── city_street.usda
│   │   └── apartment_interior.usda
│   └── props/
│       └── briefcase.usda
│
├── media/                            # SHARED MEDIA (Git LFS)
│   ├── hdri/
│   ├── audio/
│   └── luts/
│
└── scenes/                           # ALL SCENES IN THIS FILM
    │
    ├── scene_01_opening/             # SCENE (a narrative unit)
    │   ├── scene.usda                # Scene root — references its shots
    │   ├── CLAUDE.md                 # Scene-level instructions (optional)
    │   │
    │   ├── skills/                   # SCENE-LEVEL skills
    │   │   ├── skills.usda           # Scene skill registry
    │   │   └── impl/
    │   │       └── rain_fx.skill.md  # Only used in this rainy scene
    │   │
    │   ├── shots/
    │   │   ├── shot_010/             # SHOT
    │   │   │   ├── base.usda         # Shot base (immutable)
    │   │   │   ├── CLAUDE.md         # Shot-level instructions (optional)
    │   │   │   │
    │   │   │   ├── skills/           # SHOT-LEVEL skills
    │   │   │   │   ├── skills.usda   # Shot skill registry
    │   │   │   │   └── impl/
    │   │   │   │       └── crowd_sim.skill.md  # Only this shot has crowds
    │   │   │   │
    │   │   │   ├── ai/               # AI override layers (output)
    │   │   │   │   ├── relight_v001.usda
    │   │   │   │   ├── relight_v002.usda
    │   │   │   │   └── focus_pull_v001.usda
    │   │   │   │
    │   │   │   ├── qc/               # QC reports
    │   │   │   │   ├── relight_qc.json
    │   │   │   │   └── focus_pull_qc.json
    │   │   │   │
    │   │   │   └── media/            # Shot-specific plates (Git LFS)
    │   │   │       ├── plates/
    │   │   │       └── proxy/
    │   │   │
    │   │   └── shot_020/
    │   │       ├── base.usda
    │   │       ├── ai/
    │   │       ├── qc/
    │   │       └── media/
    │   │
    │   └── media/                    # Scene-level shared media
    │       └── rain_plates/
    │
    ├── scene_02_confrontation/
    │   ├── scene.usda
    │   ├── skills/
    │   ├── shots/
    │   │   ├── shot_010/
    │   │   ├── shot_020/
    │   │   └── shot_030/
    │   └── media/
    │
    └── scene_03_resolution/
        ├── scene.usda
        ├── skills/
        ├── shots/
        │   └── shot_010/
        └── media/
```

---

## Skill Hierarchy and Scoping

Skills exist at five levels. Each level can only see skills at its level
and above — never sideways or down into sibling branches.

```
Level 0: GLOBAL (Cinef framework)
  │  relight, lipsync, focus_pull, segment, pose_track, meta
  │  These are defaults. Any level below can override them.
  │
Level 1: PROJECT (my-film/skills/)
  │  color_match, dailies_review
  │  Available to ALL scenes and shots in this film.
  │  Can override global skill defaults (e.g., stricter QC).
  │
Level 2: SCENE (scenes/scene_01/skills/)
  │  rain_fx
  │  Available to ALL shots in this scene only.
  │  Cannot be used by scene_02 shots.
  │
Level 3: SHOT (scenes/scene_01/shots/shot_010/skills/)
  │  crowd_sim
  │  Available ONLY to this shot.
  │  Cannot be used by shot_020 even in the same scene.
  │
Level 4: VARIANT (inside the VariantSet customData)
     "dramatic" lighting constraints, "subtle" performance limits
     Scoped to the specific variant on a specific prim.
     Cannot affect the "natural" variant on the same prim.
```

### The Scoping Rule

**A skill is visible to the level it's defined at and everything below it.**

| Skill defined at | Visible to |
|---|---|
| Global (Cinef) | Everything everywhere |
| Project | All scenes, all shots, all variants in this film |
| Scene | All shots in this scene, not other scenes |
| Shot | Only this shot and its variants |
| Variant | Only this specific variant on this specific prim |

### What kind of skill goes where?

| Level | Examples | Why here? |
|---|---|---|
| **Global** | relight, lipsync, focus_pull, segment, pose_track | Universal skills that work on any film |
| **Project** | color_match, dailies_review, studio_lut_apply | Specific to this production's pipeline |
| **Scene** | rain_fx, underwater_caustics, car_chase_cam | Only relevant to one narrative sequence |
| **Shot** | crowd_sim, explosion_dynamics, custom_rig_solve | So specialized only one shot needs it |
| **Variant** | dramatic lighting constraints, subtle performance limits | Parameter/QC tuning within a creative choice |

---

## How Skills Inherit and Override

Skills compose like USD layers — strongest (most specific) wins.

```
Variant:  cinef:qc_temporal_flicker_threshold = 0.08   ← WINS (most specific)
Shot:     (no override)
Scene:    (no override)
Project:  validation = ["temporal_flicker < 0.04"]      ← would win if no variant
Global:   validation = ["temporal_flicker < 0.05"]      ← default
```

### Override Rules

1. **A shot-level `relight.skill.md` overrides the global one** — if
   `scene_01/shots/shot_010/skills/impl/relight.skill.md` exists, Claude
   reads that instead of the global `relight.skill.md` for this shot.

2. **A scene-level `skills.usda` extends the project registry** — it adds
   scene-specific skills but doesn't remove project or global skills.

3. **Variant `customData` overrides the skill.md defaults** — if the
   variant specifies `cinef:qc_temporal_flicker_threshold = 0.08`, that
   beats the 0.05 in the skill.md.

4. **Resolution order** (strongest to weakest):
   ```
   Variant customData → Shot skills/ → Scene skills/ → Project skills/ → Global skills/
   ```

### How Claude Resolves Which Skill to Read

```
1. Read the prim's cinef:skill (e.g., "cinef.skill.relight")
2. Check: does this shot have skills/impl/relight.skill.md?
   → Yes? Read that. Stop.
3. Check: does this scene have skills/impl/relight.skill.md?
   → Yes? Read that. Stop.
4. Check: does the project have skills/impl/relight.skill.md?
   → Yes? Read that. Stop.
5. Fall back to: cinef/show/skills/impl/relight.skill.md (global)
```

---

## Variant Skills Stay in Their Lane

The variant-aware system ensures skills don't cross-contaminate:

### Same shot, different variants

```usda
# shot_010/base.usda
variantSet "lightingVariant" = {
    "natural" (
        customData = {
            string cinef:skillVariant = "natural"
            string cinef:skillRef = "skills/impl/relight.skill.md#natural"
            float cinef:qc_temporal_flicker_threshold = 0.05
            # ↑ Strict — natural lighting must be seamless
        }
    ) { ... }
    "dramatic" (
        customData = {
            string cinef:skillVariant = "dramatic"
            string cinef:skillRef = "skills/impl/relight.skill.md#dramatic"
            float cinef:qc_temporal_flicker_threshold = 0.08
            # ↑ Relaxed — dramatic can have visible light shifts
        }
    ) { ... }
}
```

When Claude runs relight on the "natural" variant, it reads the natural
constraints. Switching to "dramatic" picks up completely different rules.
**They never mix.**

### Same variant name, different shots

`scene_01/shots/shot_010` and `scene_01/shots/shot_020` can both have a
"dramatic" lighting variant, but with different constraints:

- shot_010 dramatic: outdoor, warm key (2700K–4000K)
- shot_020 dramatic: indoor, cool overhead (5000K–7000K)

The constraints live in each shot's own `base.usda`. The variant name is
the same, but the skill configuration is scoped to the shot.

### Same skill, different scenes

`scene_01` might have a `rain_fx.skill.md` in its scene-level skills.
`scene_02` has no rain — it doesn't see that skill at all. If scene_02
also needs rain effects, it gets its own `rain_fx.skill.md` with its own
constraints (maybe it's a different kind of rain).

---

## Example: Two Films, Full Tree

```
studio-projects/                    # Parent directory (not a repo)
│
├── film-noir/                      # FILM 1 (its own git repo)
│   ├── CLAUDE.md                   # "You are working on a noir thriller"
│   ├── show.usda
│   ├── cinef/                      # Submodule → Cinef framework
│   ├── skills/                     # Film-wide: noir_grade, shadow_enhance
│   │   ├── skills.usda
│   │   └── impl/
│   │       ├── noir_grade.skill.md
│   │       └── shadow_enhance.skill.md
│   ├── assets/
│   │   └── characters/
│   │       └── detective.usda
│   ├── scenes/
│   │   ├── scene_01_alley/
│   │   │   ├── scene.usda
│   │   │   ├── skills/             # Scene: rain_reflections (alley-specific)
│   │   │   │   └── impl/
│   │   │   │       └── rain_reflections.skill.md
│   │   │   └── shots/
│   │   │       ├── shot_010/       # Wide — detective arrives
│   │   │       │   ├── base.usda   # Variants: natural_night, neon_noir
│   │   │       │   ├── ai/
│   │   │       │   ├── qc/
│   │   │       │   └── media/
│   │   │       └── shot_020/       # Close-up — detective's face
│   │   │           ├── base.usda   # Variants: stoic, conflicted
│   │   │           ├── skills/     # Shot: cigarette_smoke_sim
│   │   │           │   └── impl/
│   │   │           │       └── cigarette_smoke_sim.skill.md
│   │   │           ├── ai/
│   │   │           └── qc/
│   │   │
│   │   └── scene_02_office/
│   │       ├── scene.usda
│   │       └── shots/
│   │           └── shot_010/
│   │               ├── base.usda   # Variants: overhead_harsh, desk_lamp_warm
│   │               ├── ai/
│   │               └── qc/
│   └── media/
│
└── sci-fi-short/                   # FILM 2 (its own git repo)
    ├── CLAUDE.md                   # "You are working on a sci-fi short film"
    ├── show.usda
    ├── cinef/                      # Same Cinef framework, different film
    ├── skills/                     # Film-wide: hologram_fx, zero_g_sim
    │   ├── skills.usda
    │   └── impl/
    │       ├── hologram_fx.skill.md
    │       └── zero_g_sim.skill.md
    ├── assets/
    ├── scenes/
    │   ├── scene_01_bridge/
    │   │   └── shots/
    │   │       └── shot_010/
    │   │           └── base.usda   # Variants: alert_red, calm_blue
    │   └── scene_02_spacewalk/
    │       ├── skills/             # Scene: star_field_gen
    │       └── shots/
    └── media/
```

### What Claude sees in each context

**Working on `film-noir/scenes/scene_01_alley/shots/shot_010`:**
- Global skills: relight, focus_pull, segment, lipsync, pose_track
- Project skills: noir_grade, shadow_enhance
- Scene skills: rain_reflections
- Shot skills: (none for this shot)
- Variant skills: neon_noir constraints OR natural_night constraints

**Working on `film-noir/scenes/scene_01_alley/shots/shot_020`:**
- Global skills: relight, focus_pull, segment, lipsync, pose_track
- Project skills: noir_grade, shadow_enhance
- Scene skills: rain_reflections
- Shot skills: cigarette_smoke_sim ← only this shot
- Variant skills: stoic OR conflicted performance constraints

**Working on `sci-fi-short`:**
- Global skills: relight, focus_pull, segment, lipsync, pose_track
- Project skills: hologram_fx, zero_g_sim ← completely different film
- noir_grade? **NOT VISIBLE** — different project repo entirely

---

## CLAUDE.md Per Level

Each level can have its own `CLAUDE.md` that scopes Claude's behavior:

| Level | CLAUDE.md location | What it says |
|---|---|---|
| Framework | `cinef/CLAUDE.md` | "You are an AI TD for OpenUSD pipelines" |
| Project | `my-film/CLAUDE.md` | "This is a noir thriller. Default to moody lighting." |
| Scene | `scenes/scene_01/CLAUDE.md` | "This scene is rainy. All shots need wet reflections." |
| Shot | `shots/shot_010/CLAUDE.md` | "This is the hero shot. Extra QC scrutiny." |

Claude reads them in order: framework → project → scene → shot.
More specific instructions override less specific ones.

---

## Naming Conventions

### Scenes
```
scene_01_opening/           # Number + short description
scene_02_confrontation/
scene_03_resolution/
```

### Shots (within a scene)
```
shot_010/                   # Numbered in 10s (room for inserts)
shot_020/
shot_015/                   # Insert shot added between 010 and 020
```

### Skills
```
# Global:    cinef.skill.{name}           (ships with framework)
# Project:   {project}.skill.{name}       (e.g., noir.skill.noir_grade)
# Scene:     {project}.skill.{scene}.{name}  (e.g., noir.skill.alley.rain_reflections)
# Shot:      {project}.skill.{scene}.{shot}.{name}  (rare — usually scene-level suffices)
```

### Override layers
```
{skill_name}_v{###}.usda    # Always versioned
relight_v001.usda
relight_v002.usda            # Refinement — composes on top of v001
noir_grade_v001.usda         # Project skill output
rain_reflections_v001.usda   # Scene skill output
```

### Variant names
```
# Lighting:     natural, dramatic, golden_hour, moonlit, neon_noir
# Performance:  subtle, intense, manic, restrained
# Camera:       locked, handheld, dolly, steadicam
# Use lowercase, underscores, descriptive
```

---

## Migration from Demo

To go from the Cinef demo structure to a production structure:

```bash
# 1. Create your film project
mkdir my-film && cd my-film
git init

# 2. Add Cinef as a submodule
git submodule add https://github.com/YourOrg/Cinef.git cinef

# 3. Copy the root stage template and adapt it
cp cinef/show/show.usda ./show.usda
# Edit show.usda: change show name, update paths

# 4. Create project-level skills (extend Cinef's)
mkdir -p skills/impl
cp cinef/show/skills/skills.usda ./skills/skills.usda
# Edit: add your project-specific skills

# 5. Create your first scene
mkdir -p scenes/scene_01/shots/shot_010/{ai,qc,media}

# 6. Create your CLAUDE.md
cat > CLAUDE.md << 'EOF'
# CLAUDE.md
## Your Role
You are an AI TD for [Film Name]. Follow Cinef conventions.
Start with show.usda, discover scenes and skills.
## Project Notes
[Your film-specific instructions here]
EOF

# 7. Start working
claude
> /cinef
```

The demo's flat `show/shots/` structure maps to `scenes/scene_01/shots/`
in production. The demo's `show/skills/` becomes the project-level `skills/`
that extends Cinef's global skills.
