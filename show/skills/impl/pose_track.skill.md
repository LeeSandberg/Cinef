# Skill: AI Pose Tracking (cinef.skill.pose_track)

## Purpose
Extract skeleton animation from video plate. Produces a USD override layer
with time-sampled joint transforms (UsdSkelAnimation) that can drive character
rigs or be used as motion reference.

## When to Use
- Extracting actor performance for digital double retargeting
- Creating tracked reference for animator hand-keying
- Driving procedural effects tied to character motion

## Execution Steps
1. **Read** shot's `base.usda` to get plate path and frame range
2. **Detect** human pose per frame from video plate
3. **Map** detected joints to USD skeleton joint hierarchy
4. **Write** override layer with time-sampled joint transforms
5. **Validate** joint_jitter < 0.02, occlusion_recovery > 0.85
6. **Write** QC report for occluded/low-confidence frames

## Output Layer Template
```usda
#usda 1.0
(
    customLayerData = {
        string author = "cinef.skill.pose_track"
        string timestamp = "<ISO 8601>"
        string skillId = "cinef.skill.pose_track"
    }
)
over "Shot_###" {
    def SkelAnimation "tracked_performance" {
        uniform token[] joints = [ ... ]
        float3[] translations.timeSamples = { ... }
        quatf[] rotations.timeSamples = { ... }
    }
}
```

## Constraints
- Joint names must match the asset's Skeleton definition
- Flag frames with confidence < 0.7 in QC report
- Pure data edit — transforms only, no mesh generation
