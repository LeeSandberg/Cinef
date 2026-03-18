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

## Variant-Specific Execution

Before executing, read the active `lightingVariant` on the target prim and
find the `cinef:skillVariant` in its `customData`. Jump to the matching
section below for variant-specific constraints and defaults.

### natural

**Intent:** Balanced daylight — even illumination, neutral color temperature.

| Parameter | Constraint |
|---|---|
| Intensity range | 0.5 – 2.0 |
| Color temp hint | 5500K–6500K (daylight) |
| Key-to-fill ratio | ≤ 2:1 |
| Color cast | No deviation > 0.05 from (1,1,1) |

**QC thresholds (stricter for natural):**
- `temporal_flicker < 0.05`
- `color_shift < 0.02`

**Execution notes:**
- Preserve neutral white balance — the audience should not notice the lighting
- Fill shadows gently; avoid harsh contrast
- When in doubt, less is more

### dramatic

**Intent:** High contrast, cinematic drama — warm key, cool fill, deep shadows.

| Parameter | Constraint |
|---|---|
| Intensity range | 0.1 – 5.0 |
| Color temp hint | 2700K–4000K warm key, 7000K+ cool fill |
| Key-to-fill ratio | ≥ 3:1 |
| Shadow density | > 0.6 |

**QC thresholds (relaxed for dramatic):**
- `temporal_flicker < 0.08`
- `color_shift < 0.05`

**Execution notes:**
- Color cast is intentional — warm key, cool fill creates depth
- Push contrast; the audience should *feel* the lighting
- Allow specular highlights to clip if it serves the mood

## Constraints
- NEVER modify the base.usda — only create override layers
- Use VariantSet "lightingVariant" when creating alternative looks
- Preserve color space (ACEScg unless explicitly changed)
- Layer filename must include version number: `relight_v###.usda`
- **Always read the active variant's `customData` for constraints before executing**
- If the variant has `cinef:constraints`, those override the defaults above
