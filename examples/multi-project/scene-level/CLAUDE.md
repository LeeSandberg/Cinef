# CLAUDE.md — Scene Level (Example)

## Scene Context: scene_01_bar

Interior bar, night. This is a 4-shot sequence where the detective
meets the informant. The entire scene takes place in one location.

## Lighting Motivation

- **Practicals:** Warm tungsten pendants over the bar (3200K, intensity 1.2–1.8)
- **Ambient:** Cool blue moonlight through the windows (7500K, intensity 0.3–0.5)
- **Accent:** Neon sign outside casting red spill on the window wall only

ALL shots in this scene must maintain this light motivation. If a shot
needs a relight, it must stay within these parameters or the continuity
between cuts will break.

## Scene-Level Skills

- `bar_continuity` — validates that lighting values match across all shots
  in this scene within tolerance (Delta E < 2.0 between adjacent shots)

## Shot Inventory

| Shot | Description | Key Skill |
|---|---|---|
| shot_010 | Wide — detective enters, walks to bar | relight (natural → bar_warm) |
| shot_020 | Over-shoulder — informant speaks | lipsync (subtle) |
| shot_030 | Close-up — detective's reaction | focus_pull + relight |
| shot_040 | Two-shot — both leave | pose_track |

## Constraints

- Lighting color temperature MUST stay within the motivation ranges above
- No shot should have key intensity above 2.0 (it's a dark bar)
- The neon red accent is ONLY on shots where the window wall is visible
  (shot_010 and shot_040 — not the close-ups)
