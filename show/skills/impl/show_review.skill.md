# Skill: Show Review (cinef.skill.show_review)

## Purpose
Generate a show-wide status report across all sequences, scenes, and shots.
This is a SHOW-LEVEL skill — it reads the entire stage and reports on
pipeline health, QC status, missing overrides, and skill coverage.

## When to Use
- "What's the status of the show?"
- "Are there any QC failures?"
- "Which shots still need work?"
- Before a milestone review or dailies session

## Execution Steps
1. **Read** `show.usda` to discover all sequences and shots
2. **Parse** each shot's `base.usda` for skill bindings
3. **Scan** each shot's `ai/` directory for existing overrides
4. **Scan** each shot's `qc/` directory for QC reports
5. **Report** per shot:
   - Which skills have been executed (overrides exist)
   - Which skills are available but not yet run
   - QC pass/fail status for each executed skill
   - Active variant selections
6. **Summarize** show-wide:
   - Total shots, total skills executed, total QC passes/failures
   - Shots that need attention (failed QC or no overrides)
   - Color pipeline compliance across all layers

## Output

A show-level report written to `show/qc/show_review.json`:

```json
{
    "skill_id": "cinef.skill.show_review",
    "timestamp": "<ISO 8601>",
    "show": "CinefDemo",
    "summary": {
        "total_shots": 2,
        "shots_with_overrides": 1,
        "qc_passed": 1,
        "qc_failed": 1,
        "shots_needing_attention": ["shot_010"]
    },
    "shots": [
        {
            "shot_id": "shot_010",
            "overrides": ["focus_pull_v001", "relight_v001", "mask_v001"],
            "qc_passed": ["focus_pull"],
            "qc_failed": ["transfer_gate"],
            "available_skills": ["focus_pull", "relight", "segment", "pose_track"],
            "active_variants": {"lightingVariant": "natural"}
        }
    ]
}
```

## Constraints
- This is a READ-ONLY skill — it never creates override layers
- It reads all shots but never modifies any of them
- Report goes in `show/qc/`, not in individual shot `qc/` directories
- Run this before any milestone to catch forgotten QC failures
