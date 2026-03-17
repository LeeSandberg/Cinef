# Cinef — NotebookLM Video Podcast Script

*Feed this document into Google NotebookLM to generate an AI video podcast
that introduces Cinef from beginner to pro. The conversational tone and
progressive structure are designed for NotebookLM's podcast generation.*

---

## Cold Open — The Hook

Imagine you're a filmmaker. You've shot a scene — a wide establishing shot
of your protagonist walking into frame, and a close-up of their emotional
reaction. Traditional workflow: you hand the footage to VFX, they render
something, you watch it, give notes, they re-render, you wait again.
Weeks pass. A single lighting change means re-doing everything.

Now imagine instead: you open a terminal, say in plain English "give this
shot a golden-hour dramatic look," and an AI reads your scene file, finds
the lighting section, reads the instructions for how to modify lighting,
generates just the lighting changes as a thin overlay on top of your
original — never touching the original footage — validates the quality,
documents who did what and why, and commits it to version control. All in
seconds. Your original shot is untouched. The lighting change is a layer
you can switch on and off, like a filter, forever.

That's Cinef. And the technology that makes it possible is called OpenUSD.

---

## Part 1: What is OpenUSD? (Beginner)

Let's start simple. OpenUSD stands for Universal Scene Description. It was
created by Pixar — yes, the Toy Story people — to describe 3D scenes.
But here's the key insight that Cinef builds on: USD isn't just a file
format. It's a composition engine.

Think of it like a Google Doc. In a Google Doc, you have the original text,
and then people leave comments and suggestions — those don't change the
original, they layer on top. In USD, the original scene is called the
"root stage" — that's your canon, your master, the thing nobody touches.
Then changes come as "layers" that stack on top. Each layer only contains
what changed — not a copy of everything, just the delta, the difference.

In Cinef, every AI edit is one of these layers. A lighting change is a
layer. A focus pull is a layer. A segmentation mask is a layer. They all
stack together, and you can add, remove, or reorder them without ever
risking the original.

The USD file is plain text — you can open it in any text editor and read it.
It looks like this:

```
def Camera "main_cam" {
    float focalLength = 35
    float focusDistance = 500
    float fStop = 2.8
}
```

That's a camera. 35mm lens, focused at 500 centimeters, f/2.8 aperture.
Any filmmaker can read that. And any AI can read it too.

---

## Part 2: Skills in the Scene (Intermediate)

Here's where Cinef gets interesting. Inside those USD files, each element
in the scene carries a tag that says which AI skill is allowed to modify it.

The camera prim has a tag saying "I'm governed by the focus_pull skill —
read focus_pull.skill.md before changing my focus distance." The lighting
section says "I'm governed by the relight skill." The facial tracking says
"I'm governed by lipsync and pose_track."

These aren't hidden in some config file. They're right there in the scene
description, as part of the USD data. When Claude Code — that's Anthropic's
AI coding tool — opens the project, it reads the scene file and discovers
what it's allowed to do. The scene tells the AI how to work with it.

And here's the beautiful part: different shots have different skills.
Shot 010 is a wide establishing shot — its skills are about lighting and
camera movement. Shot 020 is a close-up — its skills are about facial
animation and lip-sync. The camera in shot 020 is actually tagged as
"locked" — the AI knows not to touch it because it's a fixed close-up.

Each scene is its own standard. There's no one-size-fits-all pipeline.

---

## Part 3: The Skill System — USB Framework (Intermediate)

The skills themselves are remarkably simple. Each one is a markdown file —
a text document with instructions. The focus_pull skill says things like:
"Read the shot's base file to find the camera. Calculate per-frame focus
distance from the tracking target. Smooth the curve. Write an override
layer. Validate that focus accuracy is above 98 percent."

It's a recipe. The AI reads the recipe and follows it.

These skill files live in a registry — a central catalog that lists all
available skills, what inputs they need, what outputs they produce, and
what quality checks must pass. The registry itself is also a USD file,
so it can be loaded into any scene using standard USD composition.

The team calls this the USB framework — Universal Skill Bundle. Like a
USB device, you plug a skill in and it works. The contract is standardized:
inputs, outputs, validation, attribution.

And because the skills are just text files, anyone can read them, edit
them, or create new ones. When the AI does a focus pull and the director
says "the transitions are too abrupt," you tell the AI: "update the
focus pull skill to prefer cubic interpolation." The AI edits the skill
file itself. Next time it runs that skill, it follows the improved
instructions. The pipeline literally learns from feedback.

---

## Part 4: The Meta-Skill — The Brain (Intermediate to Advanced)

There's one special skill called the meta-skill. It's the skill about
skills. It governs how the AI decides which skill to use for a given
request, how to evaluate whether a skill worked, when to update a skill
versus create a new one, and how to chain multiple skills together.

For example: "isolate the protagonist and give them dramatic lighting."
That's two skills — segmentation first to create a mask, then relighting
using that mask. The meta-skill tells the AI how to sequence them, that
each produces its own layer, and that the segmentation must pass quality
checks before the relight can start.

The meta-skill also handles what happens when a pattern emerges. If the
team keeps manually doing the same color-matching operation between shots,
the meta-skill says: "you've done this three times — create a new skill
for it." The AI writes a new color_match.skill.md, registers it in the
catalog, and it's available for everyone from that point on.

This is the self-improving loop. The pipeline gets better every time
you use it.

---

## Part 5: Non-Destructive Everything (Advanced)

Let's talk about why the layering approach matters for real production.

In a traditional pipeline, if you render a shot with lighting A and the
director wants to try lighting B, you re-render. If they want to compare
A and B, you have two full renders stored somewhere. If they want to try
A with camera move X and B with camera move Y, that's four renders. It
explodes exponentially.

In Cinef, lighting A is a layer. Lighting B is a layer. Camera move X
is a layer. Camera move Y is a layer. You compose them in any combination
without re-rendering anything, because each layer only stores the properties
it changed. Lighting A might be a file that's 20 lines long — just the
intensity and color of two lights. Not a multi-gigabyte render.

USD calls these "sparse overrides." You only store what changed.

This is the same philosophy as git — which tracks changes to code, not
copies of entire files. And in fact, Cinef uses git to version-control the
USD layers. Every AI intervention is a git commit. Every commit has
provenance — which AI model ran, what prompt triggered it, did QC pass.
You can always trace back who did what and why.

---

## Part 6: VariantSets — Creative Branching (Advanced)

USD has a feature called VariantSets that maps perfectly to film production.
A VariantSet is a set of alternatives for the same element. In shot 010,
the lighting has a VariantSet with "natural" and "dramatic" options. You
can switch between them without changing anything else in the scene.

Shot 020 takes this further with a "performanceVariant" — "subtle" and
"intense" versions of the facial animation. The subtle version has
restrained blendshape values for an internal, understated performance.
The intense version has full emotional range. Same shot, same camera,
same audio — different performance intensity, switchable on demand.

The director's cut, the community ending, VFX option A versus B — these
are all VariantSets. They live inside the same scene file, not as
separate versions of the whole project.

---

## Part 7: Quality Gates and Provenance (Advanced)

No AI output gets committed without passing quality validation. Every
skill defines metrics that must pass — the focus pull skill requires
focus accuracy above 98 percent. The relight skill requires temporal
flicker below 5 percent. The segmentation skill requires edge leakage
below 3 percent.

These aren't suggestions. They're gates. If the quality check fails,
the AI refuses to commit the layer. It reports what failed and either
retries with adjusted parameters or asks for human guidance.

And every layer that does pass carries a "nutrition label" — embedded
metadata documenting who created it, which AI model was used, what
prompt triggered it, and when. This matters for legal compliance.
The EU AI Act requires machine-readable labeling of AI-generated content.
Swedish law requires moral rights attribution — the right to be named.
Cinef handles this automatically through the provenance system.

---

## Part 8: Transfer Oracle — Protecting Your Models (Pro)

Here's a scenario that haunts AI teams in production: your segmentation
model reports 95 percent accuracy on the validation set. Looks great.
You deploy it on new footage from a different location with different
lighting. It silently produces garbage. The validation accuracy was
real — but it only measured performance on data similar to training.
The model's learned patterns didn't transfer to the new visual domain.

Cinef integrates with the Transfer Oracle — a validation service that
catches exactly this. Before the AI commits an override layer, it extracts
numerical feature vectors from the model and sends only those numbers — not
pixels, not model weights, not scene descriptions — to the audit service.
The service returns a diagnosis: SAFE, or RED_FLAG, meaning "your model
looks good on paper but will fail on this footage."

This is the advanced quality gate. Standard metrics don't catch
distribution shift. The Transfer Oracle does.

---

## Part 9: Getting Started — From Zero (Beginner Friendly)

You don't need to know any of this to start. Here's the actual experience:

Step 1: Install Claude Code. Open a terminal. Type `claude`. You get a
prompt.

Step 2: Type `/init`. Claude Code analyzes the project and creates a
CLAUDE.md file — the system prompt that tells it how to behave in this
specific project.

Step 3: Say "what shots are in the show?" Claude reads the USD files and
gives you a structured overview.

Step 4: Say "run a focus pull on shot 010 tracking the protagonist."
Claude finds the camera, reads the focus pull skill instructions, generates
the override layer, validates it, and reports back.

Step 5: Say "commit that and create a pull request." Claude handles git
for you — staging, committing with provenance, pushing, creating the PR.

If you've never used git, just say "I'm new to git, help me set up."
There's an onboarding skill for that too.

The whole point is that you speak creative intent in plain English, and
the AI translates it into technically correct, non-destructive, validated,
attributed changes to the scene description.

---

## Part 10: The Big Picture — Why This Matters (Pro)

Cinef demonstrates a shift in how we think about creative media. A film
is no longer a fixed sequence of rendered pixels delivered as a final
master. It's a living system — a composed stage of layered intent that
can be forked, branched, extended, and remixed.

The USD file is the score. The AI is the performer. The skills are the
technique. The quality gates are the standards. The provenance is the
credits. And git is the memory.

Every creative decision is recorded. Every AI intervention is traceable.
Every change is reversible. The original is always intact.

This is what "Forkable Film" means: cinema that is not finished, but
continuously becoming — an open invitation for collaboration between
humans and AI, between departments, between versions, between visions.

The most important file format of the AI era doesn't describe a finished
object. It describes a system that is always ready for the next idea.

---

## Closing — What to Do Next

1. Run `python3 cinef.py` to see the pipeline in action
2. Open Claude Code and try the interactive prompts in WALKTHROUGH.md
3. Read the .usda files — they're plain text, you can understand them
4. Modify a skill.md and watch the pipeline behavior change
5. Create your own shot with its own skill bindings
6. Fork the project and make it yours

The code is at: https://github.com/LeeSandberg/Cinef
Transfer Oracle: https://transferoracle.ai
Operator franchise: https://operator.droidtech.ai

---

*This script is designed for Google NotebookLM video podcast generation.
Feed this entire document as a source, and NotebookLM will create a
conversational AI podcast that walks through Cinef from beginner to pro.
The progressive structure (Parts 1-10) matches how NotebookLM segments
long-form content into natural conversation beats.*
