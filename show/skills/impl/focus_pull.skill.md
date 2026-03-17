# Skill: AI Focus Pull (cinef.skill.focus_pull)

## Purpose
Generate a camera focus override layer. This is a "pure data edit" — it only
modifies `focusDistance` and `fStop` time samples on the camera Prim, based on
depth map analysis and a tracking target.

## When to Use
- "Track focus on the protagonist's eyes"
- "Rack focus from foreground object to background"
- Smoothing jittery focus from on-set follow-focus

## Execution Steps
1. **Read** shot's `base.usda` to get camera Prim path and current focus data
2. **Read** depth map or tracking data for the target
3. **Calculate** per-frame focusDistance from target position + depth
4. **Smooth** the focus curve (cubic interpolation, no jumps > threshold)
5. **Write** override layer with time-sampled focusDistance
6. **Validate** focus accuracy > 0.98 against ground truth

## Output Layer Template
```usda
#usda 1.0
(
    doc = "AI Focus Pull override"
    customLayerData = {
        string author = "cinef.skill.focus_pull"
        string prompt = "<creative intent>"
        string timestamp = "<ISO 8601>"
        string skillId = "cinef.skill.focus_pull"
    }
)
over "Shot_###" {
    over "main_cam" {
        float focusDistance.timeSamples = {
            # Per-frame focus values
        }
        float fStop = <value>
    }
}
```

## Constraints
- This is a PURE DATA EDIT — no media generation, only float overrides
- Focus transitions must be smooth (max delta per frame configurable)
- Preserve existing fStop unless explicitly requested to change
