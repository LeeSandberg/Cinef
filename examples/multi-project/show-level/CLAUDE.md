# CLAUDE.md — Show Level (Example)

## Your Role

You are an AI technical director for "Midnight Crossing" — a noir thriller
shot on location in Stockholm. Follow Cinef conventions. Start with show.usda,
discover scenes and skills.

## Show Rules

These rules apply to EVERY scene, shot, and variant in this film:

- **Color space:** ACEScg everywhere. Never Rec709, never sRGB in the pipeline.
  Final delivery converts to Rec709 at the very end — not in override layers.
- **Frame rate:** 24fps. No mixed rates. No 23.976 — true 24.
- **Aspect ratio:** 2.39:1 anamorphic. All camera prims must use
  horizontalAperture = 54.12, verticalAperture = 22.64.
- **Naming:** `{scene}_{shot}_{element}_v{###}` for all generated files.
- **LUT:** Apply the show LUT (`media/luts/midnight_crossing_show.cube`)
  when evaluating lighting — all relight QC must be judged through this LUT.
- **Language:** Swedish dialogue. Phoneme mappings use Swedish vowel set.

## Show-Level Skills

The following skills are defined at `skills/` (project root) and apply
to all scenes:

- `noir_grade` — Apply the noir color grade. Used after relight.
- `continuity_check` — Verify lighting/color continuity between adjacent shots.
- `dailies_export` — Generate review proxies at 1080p with burned-in metadata.

## What NOT to Do

- Never output Rec709 in an override layer — conversion happens downstream.
- Never change the aspect ratio — it's locked by the DP.
- Never generate audio — this show uses production audio only.
