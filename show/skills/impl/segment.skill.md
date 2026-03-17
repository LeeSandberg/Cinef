# Skill: AI Object Segmentation (cinef.skill.segment)

## Purpose
Generate an object segmentation matte and corresponding USD override layer.
The matte isolates a subject from the plate for compositing, grading, or
replacement workflows.

## When to Use
- Isolating a character for selective color grading
- Creating holdout mattes for VFX insertions
- Separating foreground/background for depth-of-field adjustments

## Execution Steps
1. **Read** the shot's `base.usda` to get plate path and frame range
2. **Parse** the text prompt to identify segmentation target
3. **Generate** matte sequence (one per frame) as EXR assets
4. **Write** a USD layer that references the matte as an asset relationship
5. **Validate** edge leakage < 0.03 and temporal coherence > 0.95
6. **Write** QC report to `shots/shot_###/qc/segment_qc.json`

## Output Layer Template
```usda
#usda 1.0
(
    doc = "AI Segmentation mask"
    customLayerData = {
        string author = "cinef.skill.segment"
        string prompt = "<segmentation target description>"
        string timestamp = "<ISO 8601>"
        string skillId = "cinef.skill.segment"
    }
)
over "Shot_###" {
    def Xform "masks" {
        def Xform "protagonist_mask" {
            asset matte_sequence = @../../media/plates_proxy/shot_###_mask.####.exr@
            custom string target = "<prompted object>"
            custom float edge_leakage = <measured>
            custom float temporal_coherence = <measured>
        }
    }
}
```

## Constraints
- Matte must be single-channel float EXR (0.0 = background, 1.0 = subject)
- Frame numbering must match plate frame range exactly
- NEVER modify pixels of the original plate
