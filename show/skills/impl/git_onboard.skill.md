# Skill: Git Onboarding (cinef.skill.git_onboard)

## Purpose
Help a new user set up git, create a GitHub account, initialize a repository,
and learn the core workflow: branch, stage, commit, push, pull request.
This skill teaches by DOING — every step is executed in the context of
the user's actual Cinef project, not abstract examples.

## When to Use
- User says "I've never used git" or "how do I push this"
- New team member joining the project
- Setting up a fresh Cinef show on a new machine

## Concepts Explained Through the Pipeline

### What is Git?
Git tracks every change you make to your files — like "undo" but for your
entire project, forever. In Cinef, every AI override layer, every QC report,
every skill update is a tracked change. You can always go back.

### What is GitHub?
GitHub is where your git repository lives online so others can see it,
contribute to it, and review changes. Think of it as the shared drive
for your show — but with full version history.

### What is a Branch?
A branch is your personal workspace. The `main` branch is the "canon" —
the official version. Your branch (e.g., `lee`) is where you experiment.
This maps directly to USD philosophy: the root stage is immutable,
your override layers are your "branch" of creative intent.

```
main (canon)          ← the official show
  └── lee (your branch) ← your AI experiments
        ├── focus_pull_v001.usda
        ├── relight_v001.usda
        └── mask_v001.usda
```

### What is Staging?
Staging means "marking which files you want to include in your next save point."
Not every changed file needs to go — you pick the ones that are ready.

In Cinef terms: you stage the override layer AND its QC report together,
because they belong to the same skill execution.

### What is a Commit?
A commit is a save point with a message explaining what changed and why.
In Cinef, the commit message includes provenance — which skill ran,
which AI model, what prompt triggered it.

### What is a Push?
Push sends your local commits to GitHub so others can see them.
Your files don't leave your machine until you push.

### What is a Pull Request (PR)?
A PR says "I've made changes on my branch — please review and merge
them into the canon." In film terms: "Here are my AI lighting overrides
for shot_010 — director, please approve."

## Execution Steps

### Step 1: Check if git is installed
```bash
git --version
# If not installed:
# macOS: xcode-select --install
# Linux: sudo apt install git
# Windows: download from https://git-scm.com
```

### Step 2: Configure git identity
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 3: Initialize the repository
```bash
cd /path/to/your/cinef/project
git init
git checkout -b main
```

### Step 4: Create .gitignore
Ensure heavy media files don't get committed:
```
*.exr
*.hdr
*.mov
*.mp4
*.wav
__pycache__/
.DS_Store
```

### Step 5: First commit — the base show
```bash
git add show/show.usda
git add show/shots/*/base.usda
git add show/assets/
git add show/skills/
git add cinef.py
git add CLAUDE.md README.md WALKTHROUGH.md .gitignore
git commit -m "Initial show setup — base stages, skills, and pipeline"
```

### Step 6: Create a GitHub repository
1. Go to https://github.com and sign up (or sign in)
2. Click the "+" menu → "New repository"
3. Name it (e.g., "my-cinef-show")
4. Keep it Private (your show, your IP)
5. Do NOT initialize with README (you already have one)
6. Copy the URL it gives you

Or use the GitHub CLI:
```bash
# Install: https://cli.github.com
gh auth login
gh repo create my-cinef-show --private --source=. --push
```

### Step 7: Connect local repo to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/my-cinef-show.git
git push -u origin main
```

### Step 8: Create your working branch
```bash
git checkout -b your-name
# Now you're on your own branch — experiment freely
```

### Step 9: The daily workflow
After running AI skills that generate override layers:
```bash
# See what changed
git status

# Stage specific files (never git add . blindly)
git add show/shots/shot_010/ai/focus_pull_v001.usda
git add show/shots/shot_010/qc/focus_pull_qc.json

# Commit with a meaningful message
git commit -m "Add AI focus pull for shot_010 — tracks protagonist wide to close"

# Push to GitHub
git push -u origin your-name
```

### Step 10: Create a Pull Request
```bash
# Using GitHub CLI
gh pr create --title "AI focus pull for shot_010" --body "
## Summary
- Generated focus pull override tracking protagonist
- QC passed: focus_accuracy 0.993 > 0.98
- Skill: cinef.skill.focus_pull v1.0.0

## Review
Please check the focus curve smoothness in the override layer.
"
```

Or on GitHub.com:
1. Go to your repository
2. Click "Compare & pull request" (GitHub shows this when you push a branch)
3. Write a title and description
4. Click "Create pull request"
5. Ask your director/lead to review

## Common Situations

### "I made a mistake in my last commit"
```bash
# Fix the file, then:
git add the-fixed-file.usda
git commit -m "Fix focus curve smoothness in shot_010"
# Don't amend — make a new commit so history is preserved
```

### "I want to see what changed"
```bash
git diff                           # Unstaged changes
git diff --staged                  # Staged changes
git log --oneline -10              # Last 10 commits
git log --oneline show/shots/      # History of shots directory
```

### "I want to undo changes to a file"
```bash
git checkout -- show/shots/shot_010/ai/relight_v001.usda
# This discards your local changes and restores the last committed version
```

### "Someone else made changes I need"
```bash
git fetch origin
git merge origin/main
# Or if you want to rebase:
git pull --rebase origin main
```

## Constraints
- NEVER commit files containing API keys, passwords, or credentials
- NEVER force-push to main — always use a branch + PR
- Stage specific files by name, not `git add .` (avoids committing media)
- Heavy media (EXR, HDR, MOV, WAV) should be in .gitignore
- Commit messages should include skill provenance when committing AI output
