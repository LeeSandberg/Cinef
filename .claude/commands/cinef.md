Bootstrap the Cinef AI-Augmented OpenUSD pipeline.

## Instructions

Perform the full pipeline bootstrap sequence across all five skill levels:

1. **Read the root stage** — parse `show/show.usda` and extract `customLayerData` (meta-skill path, skill registry path, skill schema path, show-level skills, sequence path, instructions).

2. **Read the meta-skill** — load and follow `show/skills/impl/meta.skill.md` to understand skill selection, evaluation, chaining, and creation rules (including variant-aware selection in Section 1b).

3. **Load the skill registry** — parse `show/skills/skills.usda` to discover all registered skills. Note which skills are:
   - **Show-level** (`level = "show"`) — apply to all shots
   - **Scene-level** (`level = "scene"`) — scoped to specific sequences
   - **Shot-level** (default) — bound to prims via `cinef:skill`
   - **Variant-aware** (`variantAware = true`) — have per-variant sections

4. **Discover scene-level context** — check `show/sequences/` for sequence directories. For each:
   - Read the sequence `CLAUDE.md` for scene context and continuity rules
   - Check for scene-level skills in `sequences/seq_###/skills/impl/`
   - Check for scene-level QC reports in `sequences/seq_###/qc/`

5. **Parse each shot** — read every `show/shots/shot_###/base.usda` file. For each shot:
   - List all prims and their types
   - Extract `cinef:skill` and `cinef:skills` bindings from `customData`
   - Note which prims are locked vs modifiable
   - **Check VariantSets** — for each variant, read the `customData` for:
     - `cinef:skillVariant` — which variant is active
     - `cinef:skillRef` — pointer to variant section in skill.md
     - `cinef:constraints` — variant-specific hard rules
     - `cinef:qc_*` — variant-specific QC thresholds
   - Check for existing override layers in `shots/shot_###/ai/`
   - Check for existing QC reports in `shots/shot_###/qc/`

6. **Report back** with a summary organized by skill level:
   - **Show-level:** Which show skills are registered, any show-wide QC
   - **Scene-level:** Which sequences have scene skills, continuity status
   - **Shot-level:** Shots found, skills per prim, overrides in place, QC status
   - **Variant-level:** Active variants, variant-specific constraints and thresholds
   - Any QC failures that need attention across all levels

After bootstrap, wait for the user's creative direction.
