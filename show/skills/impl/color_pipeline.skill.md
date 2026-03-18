# Skill: Color Pipeline (cinef.skill.color_pipeline)

## Purpose
Enforce the show's color pipeline rules across all shots. This is a
SHOW-LEVEL skill — it applies universally. Every override layer that
modifies color or lighting must comply with these rules.

This skill is not executed directly — it acts as a constraint layer that
other skills (relight, segment) must check before committing.

## When to Use
- Before committing any relight override (validate color space compliance)
- When a user asks about color management or LUT application
- When reviewing a shot for color pipeline violations
- Before dailies or final delivery

## Show Color Rules

1. **Working color space:** ACEScg (ACES 2065-1 acceptable for interchange)
2. **Never output:** sRGB, Rec709, or Display P3 in override layers
3. **Color metadata:** Every override layer with color properties must include
   `custom string colorSpace = "ACEScg"` on the affected prim
4. **Gamut preservation:** No clipping — if AI-generated values exceed ACEScg
   gamut, flag in QC report rather than clamping
5. **LUT application:** LUTs are for viewing only — never bake a LUT into
   an override layer

## Validation Checks

When validating a layer for color pipeline compliance:

- [ ] All `color3f` values are in ACEScg range (no negative components
      unless physically motivated)
- [ ] No sRGB/Rec709 transfer function applied in the layer
- [ ] `colorSpace` metadata present on prims with color properties
- [ ] Lighting intensity values are physically plausible (0.0 – 10.0 range
      for most lights, flag anything > 10.0 for review)
- [ ] HDR environment maps referenced with correct color space annotation

## Output

This skill does not produce override layers. It produces a compliance
report in the shot's `qc/` directory:

```json
{
    "skill_id": "cinef.skill.color_pipeline",
    "shot_id": "shot_010",
    "timestamp": "<ISO 8601>",
    "passed": true,
    "checks": [
        {"rule": "color_space", "value": "ACEScg", "passed": true},
        {"rule": "gamut_clipping", "value": false, "passed": true},
        {"rule": "intensity_range", "max_found": 3.0, "limit": 10.0, "passed": true}
    ]
}
```

## Constraints
- This is a SHOW-LEVEL skill — it never changes per scene or shot
- It constrains OTHER skills, not the scene data itself
- Never modify base.usda to add color space — only validate override layers
- If a shot has a valid artistic reason to deviate (e.g., stylized sequence),
  the user must explicitly approve the exception
