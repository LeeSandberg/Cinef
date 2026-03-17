# Skill: AI Relighting (cinef.skill.relight)

## Purpose
Generate a lighting override layer for a shot. This skill creates a new `.usda`
layer containing modified `UsdLux` light prims and `UsdShade` material overrides
that composite non-destructively over the shot's base lighting.

## When to Use
- Director requests mood change ("make it more dramatic", "golden hour feel")
- Matching lighting between shots in a sequence
- Adding fill/rim lights to isolate a character

## Execution Steps
1. **Read** the shot's `base.usda` to understand existing lighting setup
2. **Analyze** the plate and any surface maps to estimate current light direction
3. **Generate** a sparse override layer that ONLY contains changed light properties
4. **Write** the layer to `shots/shot_###/ai/relight_v###.usda`
5. **Validate** temporal flicker score < 0.05 across frame range
6. **Record** provenance in `customLayerData` of the new layer

## Output Layer Template
```usda
#usda 1.0
(
    doc = "AI Relight override"
    customLayerData = {
        string author = "cinef.skill.relight"
        string model = "claude-opus-4-6"
        string prompt = "<the creative intent>"
        string timestamp = "<ISO 8601>"
        string skillId = "cinef.skill.relight"
        string version = "1.0.0"
    }
)
over "Shot_###" {
    over "lighting" {
        # Only override changed properties
    }
}
```

## Constraints
- NEVER modify the base.usda — only create override layers
- Use VariantSet "lightingVariant" when creating alternative looks
- Preserve color space (ACEScg unless explicitly changed)
- Layer filename must include version number: `relight_v###.usda`
