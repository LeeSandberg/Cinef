# CLAUDE.md — Shot Level (Example)

## Shot Context: scene_01_bar / shot_030

Close-up of the detective's face as the informant reveals the twist.
This is the emotional pivot of the scene — the director wants to
feel the moment the detective understands.

## Shot-Specific Rules

- **Focus:** Rack from the informant (background, soft) to the detective
  (foreground, sharp) at frame 36. The rack should take 12 frames (0.5 sec).
- **Performance variant:** Use "conflicted" — the detective is processing,
  not reacting. Subtle brow movement, tight jaw, minimal mouth.
- **Lighting:** Inherit bar scene lighting BUT add a subtle eye light
  (small Fresnel, 0.3 intensity, warm) to catch the detective's pupils.
  This is the only shot with an eye light — don't propagate to other shots.
- **QC scrutiny:** This is the hero shot. Apply stricter QC thresholds:
  - focus_accuracy > 0.995 (not the default 0.98)
  - temporal_smoothness > 0.98 (not the default 0.95)

## Shot-Level Skills

- `eye_light` — custom skill for this shot only, adds the detective's
  eye light as a point light with very specific positioning

## Do NOT

- Do not change the camera — it's locked on a tripod, no movement
- Do not add fill light — the dark side of the face is intentional
- Do not touch the background — it's deliberately out of focus
