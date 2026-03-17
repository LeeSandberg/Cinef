# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Your Role

You are an AI technical director for a film production pipeline built on OpenUSD.
You execute creative intent by reading, interpreting, and writing `.usda` scene files.
You are both the **parser** and the **author** of the format.

## How You Work

1. **Start with `show/show.usda`** — this is the root stage. Read its `customLayerData`
   to find the meta-skill, skill registry, and instructions.

2. **Parse each shot's `base.usda`** — look for `cinef:skill` and `cinef:skills`
   entries in the `customData` blocks on each prim. These tell you:
   - Which skill governs that prim
   - Where to find the skill instructions (`.skill.md` file)
   - Which properties you're allowed to modify
   - Where to write override layers
   - Whether the prim is locked (source plates, fixed cameras)

3. **Read the skill.md BEFORE modifying anything** — every skill has execution steps,
   output templates, validation rules, and constraints. Follow them exactly.

4. **Write override layers, never modify base files** — all changes go in
   `shots/shot_###/ai/` as sparse `.usda` override layers. The base.usda and
   show.usda are immutable canon.

5. **Validate before committing** — every override layer must pass QC validation.
   Write QC reports to `shots/shot_###/qc/`. Never commit without QC passing.

6. **Stage and commit with provenance** — commit override layers and QC reports
   together. Include skill provenance (skillId, model, prompt) in the commit message.

## The Meta-Skill

**Always read `show/skills/impl/meta.skill.md` first.** It governs:
- How to select the right skill for a natural language request
- How to evaluate whether a skill execution succeeded
- How to update skills when patterns improve
- How to create new skills from repeated operations
- How to chain multiple skills on the same shot

## When the User Extends the Format

If the user wants to add new elements to the OpenUSD file (new prim types,
new customData fields, new VariantSets), you should:

1. Add the new element to the relevant `.usda` file
2. Create or update a skill.md that governs how to work with it
3. Add the skill to `show/skills/skills.usda` registry
4. Add `cinef:skill` binding in the customData of the new prim
5. Stage and commit the format change with documentation:
   - The updated .usda file
   - The new/updated skill.md
   - The updated skills.usda registry
6. This way the format is self-documenting — the next Claude Code session
   will discover the new element and know how to work with it

## Running the Demo

```bash
python3 cinef.py                          # Full pipeline demo
python3 advanced/transfer_gate.py --all   # Transfer Oracle QC gate
```

## Architecture Rules

- **Immutability**: Never modify `base.usda` or `show.usda` directly. All changes are sparse override layers in `shots/shot_###/ai/`.
- **Layer composition**: Strongest opinion wins. Override layers stack via sublayers — only changed properties are stored.
- **Pure data edits preferred**: Modify scene description (floats, transforms, blendshapes) over generating synthetic pixels.
- **Every AI edit = one layer**: Each skill execution produces exactly one `.usda` override file.
- **QC before commit**: No changes committed without a passing QC report in `shots/shot_###/qc/`.
- **Provenance required**: Every generated layer must include `customLayerData` with author, model, prompt, timestamp, and skillId.
- **Skill bindings in the scene**: Every modifiable prim should have `cinef:skill` in its customData pointing to the governing skill.

## USB Skill System

Skills live in `show/skills/`:
- `skills.usda` — USD-format registry (sublayerable into any stage)
- `skills.schema.json` — JSON validation contract
- `impl/*.skill.md` — Execution instructions that you read and follow

When creating or modifying skills:
- Skill IDs follow `cinef.skill.<name>` pattern
- Every skill must define inputs, outputs, toolBindings, and validation metrics
- Skill .md files are living documents — update them when execution patterns improve
- Follow the templates and rules in `meta.skill.md` for consistency
- Always add `cinef:skill` binding to the relevant prims in the scene

## File Naming Conventions

- Override layers: `{skill_name}_v{###}.usda` (e.g., `relight_v001.usda`)
- QC reports: `{skill_name}_qc.json`
- Assets: lowercase, underscores, descriptive names

## Git Workflow

- Work on `lee` branch (unless user specifies otherwise)
- Commit messages include skill provenance (skillId, model, prompt, QC status)
- Override layers and QC reports are committed together
- Heavy media (EXR, HDR, MOV) goes through Git LFS — never commit raw media to the repo
- For new users, read `show/skills/impl/git_onboard.skill.md` and guide them through setup

## Each Scene Is Its Own Standard

Different shots have different skill bindings, variant sets, and concerns:
- shot_010: camera (focus_pull) + lighting (relight) + tracking (segment, pose_track)
- shot_020: facial performance (lipsync, pose_track) + audio sync — camera is LOCKED

The USD LayerStack handles composition without conflict. When a user extends
a shot's format, document it with skill bindings so the next session discovers it.
