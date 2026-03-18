# Skill Chain Example — All Five Levels in Action

This walks through what happens when someone says:

> "Relight shot_030 in the bar scene with the detective's conflicted performance"

Claude resolves skills from all five levels. Here's the chain:

---

## Step 1: Framework Level (Cinef)

Claude reads `meta.skill.md` (ships with Cinef) to understand how to:
- Parse the request → identifies `relight` + `lipsync` skills needed
- Determine execution order → relight first, then grade, then lipsync
- Know the QC validation requirements

**Files read:**
```
cinef/show/skills/impl/meta.skill.md       ← skill selection rules
cinef/CLAUDE.md                             ← "you are an AI TD"
```

---

## Step 2: Show Level (Project)

Claude reads the show-level CLAUDE.md and discovers:
- ACEScg color space mandatory
- Show LUT must be applied after relight
- `noir_grade` skill must chain after any relight

**Files read:**
```
my-film/CLAUDE.md                           ← "ACEScg, 24fps, noir thriller"
my-film/skills/skills.usda                  ← noir_grade, continuity_check
my-film/skills/impl/noir_grade.skill.md     ← how to apply the grade
```

---

## Step 3: Scene Level

Claude reads the scene CLAUDE.md and discovers:
- Bar scene has specific lighting motivation (warm tungsten, cool moonlight)
- Key intensity must stay below 2.0
- Continuity between shots matters

**Files read:**
```
scenes/scene_01_bar/CLAUDE.md               ← "warm practicals, cool moonlight"
scenes/scene_01_bar/skills/impl/bar_continuity.skill.md  ← will run after
```

---

## Step 4: Shot Level

Claude reads the shot CLAUDE.md and discovers:
- This is the hero shot — stricter QC
- Eye light skill needs to run last
- Camera is locked, don't touch it

**Files read:**
```
shots/shot_030/CLAUDE.md                    ← "hero shot, eye light, strict QC"
shots/shot_030/base.usda                    ← prim bindings, variant selections
shots/shot_030/skills/impl/eye_light.skill.md  ← shot-specific lighting
```

---

## Step 5: Variant Level

Claude reads the active variant's `customData` in base.usda:
- `performanceVariant = "conflicted"`
- jawOpen_max = 0.15, NO smile, jaw clenching preferred
- QC smoothness threshold = 0.98 (stricter than default)

**Files read:**
```
shots/shot_030/base.usda → face_track → "conflicted" customData
skills/impl/lipsync.skill.md#conflicted     ← variant execution notes
```

---

## The Full Execution Chain

```
1. relight         (shot-level skill, scene constraints applied)
       ↓
2. noir_grade      (show-level skill, always chains after relight)
       ↓
3. eye_light       (shot-level skill, only this shot)
       ↓
4. lipsync         (shot-level skill, "conflicted" variant constraints)
       ↓
5. bar_continuity  (scene-level skill, validates against adjacent shots)
```

Each step produces its own override layer:
```
shots/shot_030/ai/
  relight_v001.usda          ← bar lighting within scene motivation
  noir_grade_v001.usda       ← show-level color grade
  eye_light_v001.usda        ← shot-specific catchlight
  lipsync_v001.usda          ← "conflicted" performance
```

And QC reports:
```
shots/shot_030/qc/
  relight_qc.json
  noir_grade_qc.json
  eye_light_qc.json
  lipsync_qc.json

scenes/scene_01_bar/qc/
  continuity_qc.json         ← scene-level validation
```

---

## What Each Level Contributed

| Level | What it added | Without it... |
|---|---|---|
| **Framework** | Skill selection logic, execution checklist | Claude wouldn't know HOW to run skills |
| **Show** | ACEScg rule, noir_grade chain requirement | Color space chaos, no consistent look |
| **Scene** | Lighting motivation, continuity validation | Shot_030 might not match shot_020 |
| **Shot** | Eye light, strict QC, locked camera | Missing the catchlight, loose quality |
| **Variant** | "conflicted" performance limits | Wrong emotion, overacted, breaks the moment |

---

## The Key Insight

No single level has the full picture. The framework knows mechanics.
The show knows style. The scene knows context. The shot knows intent.
The variant knows emotion. Together they produce the right result.

Skills inherit downward, never sideways:
- Show rules apply to ALL shots ✓
- Scene rules apply to shots IN THIS SCENE ✓
- Shot_030's eye_light does NOT appear in shot_020 ✓
- The "conflicted" variant does NOT affect the "stoic" variant ✓

The folder structure enforces this automatically.
