# CLAUDE.md — Sequence 010 (Opening)

## Scene Context

This is the opening sequence — two shots that cut together:
- **shot_010:** Wide establishing — protagonist enters frame left
- **shot_020:** Close-up reaction — protagonist emotional response with dialogue

These shots must work as a continuous sequence. The cut between them
happens at the end of shot_010 (frame 96) to the beginning of shot_020
(frame 1).

## Continuity Rules

- **Lighting direction:** The key light in shot_010's final frames must
  match the light direction on the face in shot_020. If shot_010 uses
  "dramatic" variant (key at 60deg, warm), the close-up must feel like
  the same light source hitting the face.
- **Color temperature:** Both shots must stay within the same color
  temperature range. Don't relight shot_010 warm and leave shot_020 cool.
- **Eye line:** The protagonist's gaze direction at the end of shot_010
  (tracked via `protagonist_track`) should match the implied eye line
  in shot_020's close-up.

## Scene-Level Skills

- `seq_continuity` — validates lighting, color, and spatial continuity
  between shot_010 and shot_020

## What This Scene Is About

The protagonist arrives (wide), then we cut to their reaction (close-up).
The audience needs to feel this is one continuous moment, not two separate
setups. Continuity between these shots is critical to selling the emotion.
