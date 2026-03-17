# Skill: Meta (cinef.skill.meta)

## Purpose
This is the skill about skills. It governs how Claude Code selects,
evaluates, improves, creates, and chains all other skills in the
pipeline. Every other skill.md handles a specific task — this one
handles the skill system itself.

Read this skill when:
- Deciding which skill to use for a natural language request
- Evaluating whether a skill execution succeeded
- Updating a skill after learning what works better
- Creating a new skill from a repeated pattern
- Chaining multiple skills on the same shot

## 1. Skill Selection — Matching Intent to Skill

When the user describes creative intent in natural language, match
it to a registered skill by category and keywords:

| User says something like... | Skill ID | Why |
|---|---|---|
| "change the lighting", "make it warmer", "dramatic look" | cinef.skill.relight | Lighting modification |
| "isolate the character", "create a mask", "separate foreground" | cinef.skill.segment | Object segmentation |
| "track focus", "rack focus", "depth of field", "blur background" | cinef.skill.focus_pull | Camera focus |
| "sync the lips", "match dialogue", "animate the face to audio" | cinef.skill.lipsync | Facial animation |
| "track the body", "extract motion", "capture the performance" | cinef.skill.pose_track | Body animation |
| "set up git", "push to github", "how do I commit" | cinef.skill.git_onboard | Version control |

If the intent doesn't clearly match one skill:
1. Read the skill registry (`skills/skills.usda`) for all available skills
2. Read the skill.md files of the top 2-3 candidates
3. Pick the one whose "When to Use" section best matches
4. If no skill matches, suggest creating a new one (see Section 5)

If the intent requires multiple skills, see Section 6 (Chaining).

## 2. Skill Execution Checklist

Before executing any skill, verify:

- [ ] Read the skill.md file completely (not just the name)
- [ ] Read the target shot's base.usda to understand the scene
- [ ] Check for existing override layers in the shot's ai/ directory
      (avoid version conflicts — increment the version number)
- [ ] Confirm the output path follows naming convention:
      `{skill_name}_v{###}.usda`
- [ ] After execution, run QC validation per the skill's validation rules
- [ ] Write provenance into the override layer's customLayerData
- [ ] Write QC report to the shot's qc/ directory
- [ ] Never modify base.usda — only create override layers

## 3. Evaluating Success — Beyond QC Metrics

QC metrics (temporal_flicker < 0.05, focus_accuracy > 0.98) are
necessary but not sufficient. Also consider:

- **Did the output match the creative intent?** A technically perfect
  focus pull that doesn't track what the director wanted is a failure.
- **Is the override layer minimal?** It should only contain changed
  properties. If it's duplicating base.usda data, it's too verbose.
- **Does it compose cleanly?** Load the base + override and verify
  the composed stage makes sense. No conflicting opinions.
- **Would the user need to re-run it?** If the skill would typically
  need 2-3 iterations, the skill.md instructions need improvement.

## 4. Updating an Existing Skill

Update a skill.md when:
- The same correction is given twice ("make transitions smoother"
  after every focus pull = update the default interpolation)
- QC metrics consistently fail on one check (adjust the approach,
  not the threshold)
- A new constraint is discovered ("always preserve ACEScg color space"
  should be added as a Constraint)
- A better execution pattern is found through experience

How to update:
1. Read the current skill.md completely
2. Identify which section needs to change (Execution Steps, Constraints,
   Output Layer Template, or When to Use)
3. Make the minimal edit that addresses the issue
4. Do NOT change the skill's id, version, or category in skills.usda
   unless the change is breaking
5. Increment version in skills.usda if the contract changes
   (new required inputs, different output format)
6. Commit the skill.md update with a message explaining why:
   "Update focus_pull skill — prefer cubic interpolation after
   repeated feedback about abrupt transitions"

What NOT to update:
- Don't add speculative features ("in case someone wants...")
- Don't add constraints from a single edge case
- Don't change validation thresholds to make failing QC pass

## 5. Creating a New Skill

Create a new skill when:
- The user performs the same manual operation 3+ times
- An existing skill is being stretched beyond its purpose
- A new AI capability becomes available
- The user explicitly asks ("make a skill for color matching")

Template for a new skill.md:
```markdown
# Skill: [Name] (cinef.skill.[id])

## Purpose
[One paragraph — what this skill does and why it exists]

## When to Use
[3-5 bullet points — triggers that should activate this skill]

## Execution Steps
[Numbered steps — what Claude Code does, in order]
1. **Read** the shot's base.usda to understand [what]
2. **Analyze** [what input] for [what purpose]
3. **Generate** [what output]
4. **Write** the layer to [where]
5. **Validate** [which metrics]
6. **Record** provenance in customLayerData

## Output Layer Template
[Actual .usda template with placeholders]

## Constraints
[Hard rules — never do X, always do Y]
```

After creating the skill.md:
1. Add the skill entry to `show/skills/skills.usda` with a unique id,
   version "1.0.0", appropriate category, and validation rules
2. Test by running the skill on a real shot
3. Commit both files together

## 6. Chaining Skills

Some creative intents require multiple skills in sequence:

**Example:** "Isolate the protagonist and give them dramatic lighting"
1. Run `segment` first → generates protagonist mask
2. Run `relight` second → uses the mask to selectively relight

**Example:** "Track the actor's performance and sync new dialogue"
1. Run `pose_track` first → extracts body motion
2. Run `lipsync` second → generates face animation on top

Chaining rules:
- Each skill produces its own override layer (never merge into one)
- Order matters — later layers compose on top of earlier ones
- If skill B depends on skill A's output, run A first and verify
  QC passes before starting B
- Name layers to show the chain: `segment_v001.usda`, `relight_v002.usda`
  (increment version to show ordering in the stack)

## 7. Memory and Learning

After a successful skill execution:
- If the user gives positive feedback, note what worked in memory
  ("shot_010 always needs dramatic lighting first")
- If the user gives corrective feedback, consider updating the skill.md
  (see Section 4)
- If a pattern emerges across sessions, create a new skill
  (see Section 5)
- Update CLAUDE.md if a project-wide convention is established

After a failed skill execution:
- Read the QC report to understand which metrics failed
- Check if the skill.md instructions are ambiguous or incomplete
- If the failure is systematic, update the skill.md
- If the failure is one-off, adjust parameters and retry

## 8. Skill Inventory Check

Periodically (or when asked "what can you do?"), report:
1. Read `skills/skills.usda` for the full registry
2. For each skill, read its skill.md "Purpose" and "When to Use"
3. Present a summary grouped by category
4. Flag any skills that have been updated recently
5. Suggest new skills if repeated manual patterns are observed

## Constraints
- Never delete a skill — deprecate by updating its "When to Use"
  to say "DEPRECATED — use [replacement] instead"
- Never modify skills.usda without also updating the corresponding
  skill.md (and vice versa)
- Skills must be self-contained — a skill.md should have everything
  Claude Code needs to execute, without referencing other skills
  (except in chaining scenarios documented in Section 6)
- Every skill must have validation rules — no unvalidated output
