# Skill: Eye Light (midnight.skill.bar.shot030.eye_light)

## Purpose
Add a subtle eye light to catch the detective's pupils in the close-up.
This is a SHOT-LEVEL skill — it exists only for shot_030 in the bar scene.
No other shot should use this skill.

## When to Use
- When setting up the detective's close-up lighting
- After the base relight is done (chain: relight → noir_grade → eye_light)
- This is the LAST lighting skill in the chain for this shot

## Execution Steps
1. **Read** the shot's composed lighting (base + relight + noir_grade)
2. **Read** the face_track prim to get the detective's eye position at the
   key frame (frame 36 — the moment of realization)
3. **Generate** an override layer with a small SphereLight:
   - Position: 30cm in front of the face, 5cm above eye level
   - Intensity: 0.3 (barely visible — just enough for a catchlight)
   - Color: warm (1.0, 0.95, 0.85) — matches tungsten practicals
   - Radius: 2cm (small, sharp catchlight)
   - No shadow casting — this is a cosmetic light only
4. **Write** the layer to `shots/shot_030/ai/eye_light_v###.usda`
5. **Validate** that the eye light doesn't change the scene's overall
   brightness by more than 1% (it should be invisible except in the pupils)

## Output Layer Template
```usda
#usda 1.0
(
    doc = "Shot-level eye light — detective close-up catchlight"
    customLayerData = {
        string author = "midnight.skill.bar.shot030.eye_light"
        string model = "claude-opus-4-6"
        string timestamp = "<ISO 8601>"
        string skillId = "midnight.skill.bar.shot030.eye_light"
        string version = "1.0.0"
        string level = "shot"
    }
)
over "Shot_030" {
    over "lighting" {
        def SphereLight "eye_light" {
            float intensity = 0.3
            float radius = 0.02
            color3f color = (1.0, 0.95, 0.85)
            bool shadow:enable = false
            float3 xformOp:translate = (0, 1.65, 0.3)
            uniform token[] xformOpOrder = ["xformOp:translate"]
        }
    }
}
```

## Constraints
- ONLY for shot_030 — never copy this to another shot
- Must run AFTER relight and noir_grade (last in the lighting chain)
- Intensity MUST stay at or below 0.3 — the DP will reject anything brighter
- No shadow casting — this is a cosmetic fill, not a motivating source
- The eye light position should track the face if the actor moves
  (read face_track translations to offset the light position)
