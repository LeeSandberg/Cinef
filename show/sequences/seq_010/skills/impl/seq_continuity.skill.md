# Skill: Sequence Continuity (cinef.skill.seq_010.continuity)

## Purpose
Validate visual continuity between shot_010 and shot_020 in the opening
sequence. This is a SCENE-LEVEL skill — it reads both shots and compares
them across the cut point. It does NOT apply to shots in other sequences.

## When to Use
- After relighting either shot_010 or shot_020
- After changing the active lighting variant on shot_010
- Before marking the sequence as "ready for review"
- When the director says "these two shots don't match"

## Execution Steps
1. **Read** shot_010's composed lighting state (base + overrides + active variant)
2. **Read** shot_020's composed state (base + overrides)
3. **Compare at the cut point:**
   - shot_010 frame 96 (last frame) vs shot_020 frame 1 (first frame)
4. **Check continuity metrics:**
   - Key light direction: angle difference < 15 degrees
   - Key light color: Delta E < 3.0 (CIE Lab)
   - Key light intensity ratio: within 30% (close-up is tighter framing,
     so some intensity shift is expected)
   - Fill ratio: consistent motivation
   - Color temperature: same range (both warm, both cool, or both neutral)
5. **Check spatial continuity:**
   - Protagonist position at shot_010 frame 96 vs implied position in shot_020
   - The protagonist_track endpoint should be consistent with the close-up framing
6. **Write** continuity report to `sequences/seq_010/qc/continuity_qc.json`

## Output

```json
{
    "skill_id": "cinef.skill.seq_010.continuity",
    "sequence_id": "seq_010",
    "timestamp": "<ISO 8601>",
    "passed": true,
    "cut_point": {
        "shot_a": "shot_010",
        "shot_a_frame": 96,
        "shot_b": "shot_020",
        "shot_b_frame": 1
    },
    "checks": [
        {
            "metric": "key_light_angle_diff",
            "value": 8.5,
            "threshold": 15.0,
            "passed": true
        },
        {
            "metric": "key_light_color_delta_e",
            "value": 2.1,
            "threshold": 3.0,
            "passed": true
        },
        {
            "metric": "key_light_intensity_ratio",
            "value": 0.85,
            "threshold_min": 0.7,
            "threshold_max": 1.3,
            "passed": true
        },
        {
            "metric": "color_temp_match",
            "shot_a_range": "5500K-6500K",
            "shot_b_range": "5500K-6500K",
            "passed": true
        }
    ]
}
```

## Constraints
- This skill is scoped to seq_010 ONLY — it cannot validate other sequences
- It READS both shots but NEVER modifies either of them
- It only flags problems — the fix is done by running relight on the offending shot
- shot_020's camera is LOCKED — if there's a spatial mismatch, fix it in shot_010
- When shot_010 uses the "dramatic" variant, the continuity thresholds for
  color Delta E relax to 5.0 (dramatic lighting has intentional color shifts)
- QC report goes in `sequences/seq_010/qc/`, not in individual shot directories
