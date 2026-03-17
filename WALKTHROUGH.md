# Walkthrough: Using Claude Code with Cinef

This shows what it actually feels like to use Claude Code as your AI
technical director in the Cinef pipeline. These are real prompts you
can type (or speak via spacebar) in Claude Code.

---

## 0. First Time? Set Up Git and GitHub

If you've never used git before, Claude Code can walk you through
the entire setup. Just ask:

```
> I'm new to git. Help me set up this project as a repository
  and push it to GitHub.
```

Claude Code reads `show/skills/impl/git_onboard.skill.md` and walks
you through each step interactively. Here's what happens:

### What is Git? (The 30-second version)

Git tracks every change you make — like "undo" for your entire project,
forever. Every AI override layer, every QC report, every skill update
becomes a tracked save point you can always go back to.

### What is GitHub?

GitHub is where your repository lives online so your team can collaborate.
Think of it as the shared drive for your show — but with full version history
and review tools.

### Claude Code does the setup for you:

```
> Set up git for this project. My name is [your name] and my email
  is [your email].
```

Claude Code will:
1. Run `git init` to initialize the repository
2. Configure your identity (`git config`)
3. Create a `.gitignore` so heavy media files don't get committed
4. Make the first commit with the base show structure
5. Help you create a GitHub repository (via `gh` CLI or the website)
6. Push your code to GitHub

### Create your branch

```
> Create a branch for me called [your-name]
```

Claude Code runs `git checkout -b your-name`. Now you have your own
workspace. The `main` branch is the "canon" — the approved version.
Your branch is where you experiment with AI skills.

This maps directly to USD philosophy:
```
main branch   = root stage (immutable canon)
your branch   = override layers (your experiments)
```

### The daily workflow — stage, commit, push

After running AI skills that generate override layers:

```
> Commit the focus pull override and QC report for shot_010
```

Claude Code does this:
```bash
# 1. STAGE — mark specific files for the next save point
git add show/shots/shot_010/ai/focus_pull_v001.usda
git add show/shots/shot_010/qc/focus_pull_qc.json

# 2. COMMIT — save with a message explaining what and why
git commit -m "Add AI focus pull for shot_010 — tracks protagonist wide to close

Skill: cinef.skill.focus_pull v1.0.0
Model: claude-opus-4-6
QC: PASSED (focus_accuracy: 0.993)"

# 3. PUSH — send to GitHub so your team can see it
git push -u origin your-name
```

**Why stage specific files?** Because you don't want to accidentally
commit API keys, huge video files, or half-finished work. You pick
exactly what goes in.

### Pull Requests — getting your work approved

When your AI overrides are ready for review:

```
> Create a pull request for my shot_010 work
```

Claude Code runs:
```bash
gh pr create --title "AI lighting and focus for shot_010" --body "
## Summary
- Focus pull tracking protagonist (frames 1-96)
- Golden-hour relight variant added
- Both QC reports passing

## Review
Please check focus curve smoothness and lighting color temperature.
"
```

A pull request (PR) says: "I've made changes on my branch — please
review and merge them into the official show." Your director or lead
reviews the PR on GitHub, leaves comments, and approves or requests
changes. Once approved, the changes merge into `main`.

### Seeing what changed

```
> Show me what files I've changed since my last commit
```

Claude Code runs `git status` and `git diff` to show you exactly
what's been modified, added, or deleted — and whether it's staged
or not.

### Common git questions you can just ask Claude Code

```
"What did I commit last?"
"Undo my changes to relight_v001.usda"
"Show me the history of shot_010"
"What's the difference between my branch and main?"
"Someone else pushed changes, how do I get them?"
```

Claude Code handles all of these. You never need to memorize git commands.

---

## 1. Explore the Show

Open Claude Code in the Cinef directory and start by understanding what you have:

```
> What shots are in the show? Describe each one and what skills are available.
```

Claude reads `show.usda`, `shots/*/base.usda`, and `skills/skills.usda`.
It responds with a structured overview of your show — shots, cameras,
lighting setups, and which AI skills are registered.

---

## 2. Execute a Skill — Focus Pull

```
> Run a focus pull on shot_010. Track the protagonist from the wide
  establishing position to close-up. Smooth 4-second rack starting at frame 24.
```

Claude Code:
1. Reads `show/skills/impl/focus_pull.skill.md` for instructions
2. Reads `show/shots/shot_010/base.usda` to find the camera and tracking data
3. Calculates per-frame focusDistance values with smooth interpolation
4. Writes `show/shots/shot_010/ai/focus_pull_v001.usda` (sparse override)
5. Runs QC validation (focus_accuracy > 0.98)
6. Reports back with the provenance record

The base.usda is never modified. The override layer only contains the
changed camera properties.

---

## 3. Try a Different Look — Relighting

```
> Give shot_010 a dramatic golden-hour look. High contrast, warm key light,
  cool fill. Keep it as a variant so we can compare with the natural lighting.
```

Claude Code:
1. Reads `show/skills/impl/relight.skill.md`
2. Reads the existing lighting VariantSet in shot_010
3. Creates `show/shots/shot_010/ai/relight_v001.usda` with a new
   "golden_hour" variant in the lightingVariant VariantSet
4. Validates temporal flicker < 0.05
5. Both "natural" and "golden_hour" now exist as switchable options

---

## 4. Work on a Different Shot — Lip-Sync

```
> Shot 020 is the close-up reaction. Generate lip-sync blendshape
  animation from the dialogue audio. Use the "intense" performance variant.
```

Claude Code:
1. Reads `show/skills/impl/lipsync.skill.md`
2. Reads `show/shots/shot_020/base.usda` — notices this shot has a
   performanceVariant (subtle vs intense) and face_track blendshapes
3. Generates blendshape weight curves matched to audio timing
4. Writes the override layer in shot_020's ai/ directory

Note: shot_020 has a completely different skill focus than shot_010.
Each shot owns its own standard — 010 is about lighting and camera,
020 is about facial performance and lip-sync.

---

## 5. Validate with Transfer Oracle

```
> Before we commit the segmentation skill output, validate that the
  model will transfer to shot_010's footage.
```

Claude Code:
1. Extracts feature vectors from the segmentation model (locally)
2. Calls `mcp__growt-audit__audit_model_transfer` via MCP
3. Gets back: SAFE / RED_FLAG / BAD_MODEL / UNDERTRAINED
4. If SAFE: commits the override layer
5. If RED_FLAG: refuses to commit, explains why, suggests fixes

No pixels or model weights leave your infrastructure.

---

## 6. Review What Changed

```
> Show me all AI override layers for shot_010 and their provenance.
```

Claude reads every `.usda` file in `shots/shot_010/ai/` and extracts
the `customLayerData` from each — showing you who made what, when,
with which model, from which prompt, and whether QC passed.

---

## 7. Improve a Skill (Meta-Prompt)

```
> The focus pull transitions are too linear. Update focus_pull.skill.md
  to specify cubic Hermite interpolation with a max delta of 15 units
  per frame. Also add a constraint that focus must never jump more than
  30 units between consecutive frames.
```

Claude Code edits `show/skills/impl/focus_pull.skill.md` directly.
Next time anyone (human or AI) runs focus_pull, it follows the
improved instructions.

---

## 8. Create a New Skill

```
> We keep manually color-matching between shot_010 and shot_020.
  Create a new color_match skill that reads both shots and generates
  a color grade override layer for the second shot to match the first.
```

Claude Code:
1. Creates `show/skills/impl/color_match.skill.md` with execution steps
2. Adds a new skill entry to `show/skills/skills.usda`
3. Defines inputs, outputs, validation metrics, and tool bindings

The skill is immediately available in the registry for next use.

---

## 9. Continuous Monitoring

```
/loop 5m check show/shots/*/qc/ for any failed QC reports and summarize issues
```

Claude Code checks every 5 minutes. If a QC report shows a failed
metric, it alerts you with the shot, skill, and specific failure.

---

## 10. Commit and Push

```
> Commit all the AI override layers and QC reports for shot_010.
  Include provenance in the commit message.
```

Claude Code stages the specific files (not `git add .`), writes a
commit message with skill attribution, and pushes to the `lee` branch.

---

## Key Insight

In this workflow, Claude Code is simultaneously:
- **The reader** of .usda scene descriptions (understanding the shot)
- **The executor** of .skill.md instructions (doing the AI work)
- **The author** of .usda override layers (writing scene changes)
- **The validator** via QC gates (ensuring quality)
- **The documenter** via provenance (tracking everything)
- **The improver** of skill.md files (learning from feedback)

The film is never a fixed artifact. It's a living system that evolves
through layered, non-destructive, version-controlled creative intent.
