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

## Variant-Specific Execution

Before executing, read the active `performanceVariant` on the `face_track` prim
and find the `cinef:skillVariant` in its `customData`. Jump to the matching
section below for variant-specific constraints and defaults.

### subtle

**Intent:** Restrained, internal emotion — micro-expressions only.

| Parameter | Max Value | Constraint |
|---|---|---|
| jawOpen | 0.3 | Peaks ≤ 0.3 |
| mouthSmile | 0.2 | Barely perceptible |
| browRaise | 0.25 | Subtle thought indicator |
| eyesBlink | 0.5 | Natural blink rate only |
| intensity_multiplier | 0.6 | Applied to all curves |

**QC thresholds (stricter for subtle):**
- `sync_accuracy > 0.90`
- `temporal_smoothness > 0.97`

**Execution notes:**
- Prefer holds over movement — the character is thinking, not performing
- No sudden jumps > 0.1 per frame between keyframes
- Mouth shapes should be understated; the audience reads intent from eyes
- When mapping phonemes, scale amplitudes by `intensity_multiplier` (0.6)

### intense

**Intent:** Full emotional range — broad expressions, visible reaction.

| Parameter | Max Value | Constraint |
|---|---|---|
| jawOpen | 0.8 | Full open for emphasis |
| mouthSmile | 0.6 | Clear emotional read |
| browRaise | 0.9 | Dramatic surprise/concern |
| eyesBlink | 1.0 | Allow hard blinks for impact |
| intensity_multiplier | 1.0 | Full amplitude |

**QC thresholds (relaxed for intense):**
- `sync_accuracy > 0.90`
- `temporal_smoothness > 0.93`

**Execution notes:**
- Allow jumps up to 0.3 per frame for emotional impact moments
- Blinks must complete within 3 frames (open → closed → open)
- Phoneme mapping at full amplitude — the character is speaking with force
- eyesBlink can be used for dramatic punctuation, not just physiology

## Constraints
- Blendshape weights must be in [0.0, 1.0] range
- Frame rate must match shot's framesPerSecond
- Pure data edit — no audio or video generation
- **Always read the active variant's `customData` for constraints before executing**
- If the variant has `cinef:constraints`, those override the defaults above
- When the variant specifies `cinef:jawOpen_max` etc., clamp outputs accordingly
