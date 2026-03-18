# Skill: Bar Scene Continuity (midnight.skill.bar.continuity)

## Purpose
Validate lighting and color continuity across all shots in the bar scene.
This is a SCENE-LEVEL skill — it reads multiple shots and compares them,
rather than operating on a single shot.

## When to Use
- After relighting any shot in scene_01_bar
- Before submitting the scene for dailies review
- When the director says "these two shots don't match"

## Execution Steps
1. **Read** all shot base.usda files in this scene (shot_010 through shot_040)
2. **Read** all relight override layers in each shot's ai/ directory
3. **Compose** each shot's full lighting state (base + overrides)
4. **Compare** adjacent shots (010↔020, 020↔030, 030↔040):
   - Key light color: Delta E < 2.0 between adjacent shots
   - Key light intensity: within 20% of each other
   - Fill ratio: consistent within scene motivation
   - Color temperature: all within 3200K ± 300K (tungsten practicals)
5. **Flag** any shot pair that exceeds tolerance
6. **Write** continuity QC report to `scenes/scene_01_bar/qc/continuity_qc.json`

## Output
This skill does NOT produce a .usda override layer. It produces a QC report
that identifies which shots need adjustment.

```json
{
    "skill_id": "midnight.skill.bar.continuity",
    "scene_id": "scene_01_bar",
    "timestamp": "<ISO 8601>",
    "passed": false,
    "pairs": [
        {
            "shot_a": "shot_010",
            "shot_b": "shot_020",
            "delta_e": 1.4,
            "intensity_diff": 0.12,
            "passed": true
        },
        {
            "shot_a": "shot_020",
            "shot_b": "shot_030",
            "delta_e": 4.7,
            "intensity_diff": 0.45,
            "passed": false,
            "note": "shot_030 key light too bright — bar scene maximum is 2.0"
        }
    ]
}
```

## Constraints
- This skill READS multiple shots but NEVER modifies them
- It only flags problems — the fix is done by running relight on the offending shot
- Scene lighting motivation is defined in the scene CLAUDE.md, not here
- Delta E is measured in CIE Lab space (not raw RGB distance)
- Always compare in composited state (base + all overrides), not base alone
