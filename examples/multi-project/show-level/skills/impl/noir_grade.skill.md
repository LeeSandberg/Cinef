# Skill: Noir Color Grade (midnight.skill.noir_grade)

## Purpose
Apply the show's noir color grade to a shot's lighting. This skill runs
AFTER relight and BEFORE dailies export. It creates a color override layer
that maps the relit output through the show LUT and applies film-noir
specific adjustments: crushed blacks, desaturated midtones, cool shadows.

## When to Use
- After any relight skill execution (always chain: relight → noir_grade)
- When the director asks for "the look" or "grade it"
- Before dailies review — ungraded shots should never reach the director

## Execution Steps
1. **Read** the shot's composed stage (base + any relight overrides)
2. **Read** the show LUT from `media/luts/midnight_crossing_show.cube`
3. **Analyze** the current lighting for contrast ratio and color balance
4. **Generate** a color override layer with:
   - Shadow color shift toward cool blue (0.7, 0.75, 1.0)
   - Midtone desaturation (saturation multiplier 0.7)
   - Highlight preservation (don't crush specular highlights)
   - Black level floor at 0.02 (never pure black — film grain lives there)
5. **Write** the layer to `shots/shot_###/ai/noir_grade_v###.usda`
6. **Validate** gamut_coverage > 0.85, black_crush < 0.03
7. **Record** provenance in customLayerData

## Output Layer Template
```usda
#usda 1.0
(
    doc = "Show-level noir color grade"
    customLayerData = {
        string author = "midnight.skill.noir_grade"
        string model = "claude-opus-4-6"
        string prompt = "<creative intent>"
        string timestamp = "<ISO 8601>"
        string skillId = "midnight.skill.noir_grade"
        string version = "1.0.0"
        string level = "show"
    }
)
over "Shot_###" {
    over "lighting" {
        # Color grade overrides applied to the composed lighting
        custom color3f grade:shadowTint = (0.7, 0.75, 1.0)
        custom float grade:midtoneSaturation = 0.7
        custom float grade:blackLevel = 0.02
        custom float grade:highlightPreserve = 0.95
    }
}
```

## Constraints
- This is a SHOW-LEVEL skill — same grade on every shot for consistency
- Always run AFTER relight, never before (chain order matters)
- Never modify the show LUT itself — it's locked by the colorist
- ACEScg in, ACEScg out — no color space conversion in the override layer
- Black level floor at 0.02 minimum — the DP wants film grain visible in shadows
