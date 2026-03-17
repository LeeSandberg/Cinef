Bootstrap the Cinef AI-Augmented OpenUSD pipeline.

## Instructions

Perform the full pipeline bootstrap sequence:

1. **Read the root stage** — parse `show/show.usda` and extract `customLayerData` (meta-skill path, skill registry path, skill schema path, instructions).

2. **Read the meta-skill** — load and follow `show/skills/impl/meta.skill.md` to understand skill selection, evaluation, chaining, and creation rules.

3. **Load the skill registry** — parse `show/skills/skills.usda` to discover all registered skills (IDs, categories, inputs, outputs, validation rules).

4. **Parse each shot** — read every `show/shots/shot_###/base.usda` file. For each shot:
   - List all prims and their types
   - Extract `cinef:skill` and `cinef:skills` bindings from `customData`
   - Note which prims are locked vs modifiable
   - Check for existing override layers in `shots/shot_###/ai/`
   - Check for existing QC reports in `shots/shot_###/qc/`

5. **Report back** with a summary:
   - Shots found and their descriptions
   - Skills available on each shot (grouped by prim)
   - Any existing overrides already in place
   - Any QC failures that need attention

After bootstrap, wait for the user's creative direction.
