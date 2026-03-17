# Skill: AI Lip-Sync (cinef.skill.lipsync)

## Purpose
Generate blendshape animation curves from audio input. Produces a USD override
layer with time-sampled blendshape weights that drive facial animation on the
target character rig.

## When to Use
- Syncing dialogue to character facial animation
- ADR (Automated Dialogue Replacement) with new audio
- Generating reference animation for hand-polish by animators

## Execution Steps
1. **Read** shot's `base.usda` to find face_track Prim and blendshape targets
2. **Analyze** audio file for phoneme timing
3. **Map** phonemes to blendshape weight curves (jawOpen, mouthSmile, etc.)
4. **Smooth** curves to avoid popping between frames
5. **Write** override layer with time-sampled blendshape values
6. **Validate** sync_accuracy > 0.90, temporal_smoothness > 0.95

## Output Layer Template
```usda
#usda 1.0
(
    customLayerData = {
        string author = "cinef.skill.lipsync"
        string audio_source = "<path>"
        string timestamp = "<ISO 8601>"
        string skillId = "cinef.skill.lipsync"
    }
)
over "Shot_###" {
    over "face_track" {
        float blendshape:jawOpen.timeSamples = { ... }
        float blendshape:mouthSmile.timeSamples = { ... }
        float blendshape:browRaise.timeSamples = { ... }
    }
}
```

## Constraints
- Blendshape weights must be in [0.0, 1.0] range
- Frame rate must match shot's framesPerSecond
- Pure data edit — no audio or video generation
