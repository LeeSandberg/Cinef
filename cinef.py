#!/usr/bin/env python3
"""
Cinef — Simplified OpenUSD Pipeline Engine (Educational Demo)

This module demonstrates the core concepts of the AI-Augmented OpenUSD
Film Pipeline without requiring the actual OpenUSD C++ libraries.
It parses simplified .usda text files, manages layer composition,
and provides the foundation for the agent execution loop.

Key concepts demonstrated:
  - Layer composition (sublayers, references, overrides)
  - VariantSets for creative branching
  - Sparse overrides (only storing deltas)
  - Skill registry loading and validation
  - Provenance tracking and QC gating
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# 1. Simplified USDA Parser
# ---------------------------------------------------------------------------

@dataclass
class UsdPrim:
    """A simplified USD Primitive — the atomic scene element."""
    name: str
    prim_type: str  # "Xform", "Camera", "DomeLight", etc.
    specifier: str  # "def" (define) or "over" (override)
    properties: dict[str, Any] = field(default_factory=dict)
    children: dict[str, "UsdPrim"] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    variant_sets: dict[str, dict[str, list["UsdPrim"]]] = field(default_factory=dict)
    references: list[str] = field(default_factory=list)

    def get_path(self, parent_path: str = "") -> str:
        return f"{parent_path}/{self.name}"

    def find(self, path: str) -> "UsdPrim | None":
        """Traverse to a prim by path (e.g., '/Shot_010/main_cam')."""
        parts = [p for p in path.strip("/").split("/") if p]
        if not parts:
            return self
        child_name = parts[0]
        if child_name in self.children:
            if len(parts) == 1:
                return self.children[child_name]
            return self.children[child_name].find("/".join(parts[1:]))
        return None

    def apply_override(self, override: "UsdPrim") -> None:
        """Apply a sparse override (the core of non-destructive composition)."""
        # Override properties (sparse: only replace what's specified)
        for key, value in override.properties.items():
            self.properties[key] = value

        # Recurse into children
        for child_name, child_override in override.children.items():
            if child_name in self.children:
                self.children[child_name].apply_override(child_override)
            else:
                # New prim introduced by the override
                self.children[child_name] = child_override

    def to_usda(self, indent: int = 0) -> str:
        """Serialize back to .usda text format."""
        pad = "    " * indent
        lines = []

        # Prim header
        type_str = f" {self.prim_type}" if self.prim_type else ""
        meta_parts = []
        if self.metadata.get("doc"):
            meta_parts.append(f'doc = "{self.metadata["doc"]}"')
        if self.references:
            refs = ", ".join(f"@{r}@" for r in self.references)
            meta_parts.append(f"references = [ {refs} ]")

        meta_str = ""
        if meta_parts:
            meta_str = " (\n" + pad + "    " + ("\n" + pad + "    ").join(meta_parts) + "\n" + pad + ")"

        lines.append(f'{pad}{self.specifier}{type_str} "{self.name}"{meta_str}')
        lines.append(f"{pad}{{")

        # Properties
        for key, value in self.properties.items():
            if isinstance(value, dict) and "timeSamples" in str(key):
                lines.append(f"{pad}    {key} = {{")
                for t, v in value.items():
                    lines.append(f"{pad}        {t}: {v},")
                lines.append(f"{pad}    }}")
            elif isinstance(value, str):
                lines.append(f'{pad}    {key} = "{value}"')
            else:
                lines.append(f"{pad}    {key} = {value}")

        # Children
        for child in self.children.values():
            lines.append(child.to_usda(indent + 1))

        lines.append(f"{pad}}}")
        return "\n".join(lines)


@dataclass
class UsdLayer:
    """A USD Layer — one 'opinion' in the composition stack."""
    path: str
    doc: str = ""
    custom_layer_data: dict[str, Any] = field(default_factory=dict)
    root_prims: dict[str, UsdPrim] = field(default_factory=dict)
    sub_layers: list[str] = field(default_factory=list)
    time_codes: tuple[float, float] = (1, 240)
    fps: float = 24

    @property
    def default_prim(self) -> UsdPrim | None:
        if self.root_prims:
            return next(iter(self.root_prims.values()))
        return None


class SimplifiedUsdaParser:
    """
    Minimal .usda parser for educational purposes.
    Handles the subset of USDA syntax used in this demo.
    Real production would use pxr.Usd from the OpenUSD SDK.
    """

    def parse_file(self, filepath: str) -> UsdLayer:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Layer not found: {filepath}")

        text = path.read_text(encoding="utf-8")
        return self.parse_text(text, str(path))

    def parse_text(self, text: str, source_path: str = "<string>") -> UsdLayer:
        layer = UsdLayer(path=source_path)

        # Extract header metadata
        header_match = re.search(r'^\(\s*$(.*?)^\)\s*$', text, re.MULTILINE | re.DOTALL)
        if header_match:
            header = header_match.group(1)
            # Doc string
            doc_match = re.search(r'doc\s*=\s*"([^"]*)"', header)
            if doc_match:
                layer.doc = doc_match.group(1)
            # FPS
            fps_match = re.search(r'framesPerSecond\s*=\s*(\d+)', header)
            if fps_match:
                layer.fps = float(fps_match.group(1))
            # Time codes
            start_match = re.search(r'startTimeCode\s*=\s*(\d+)', header)
            end_match = re.search(r'endTimeCode\s*=\s*(\d+)', header)
            if start_match and end_match:
                layer.time_codes = (float(start_match.group(1)), float(end_match.group(1)))
            # Custom layer data
            cld_match = re.search(
                r'customLayerData\s*=\s*\{(.*?)\}', header, re.DOTALL
            )
            if cld_match:
                for kv in re.finditer(r'string\s+(\w+)\s*=\s*"([^"]*)"', cld_match.group(1)):
                    layer.custom_layer_data[kv.group(1)] = kv.group(2)
            # Sublayers
            for sl in re.finditer(r'@([^@]+)@', header):
                layer.sub_layers.append(sl.group(1))

        # Extract top-level prims (simplified: one level of def/over)
        for prim_match in re.finditer(
            r'^(def|over)\s+(\w+)?\s*"(\w+)"', text, re.MULTILINE
        ):
            specifier = prim_match.group(1)
            prim_type = prim_match.group(2) or ""
            prim_name = prim_match.group(3)
            prim = UsdPrim(
                name=prim_name,
                prim_type=prim_type,
                specifier=specifier,
            )
            # Extract doc metadata
            after = text[prim_match.end():]
            doc_match = re.search(r'doc\s*=\s*"([^"]*)"', after[:200])
            if doc_match:
                prim.metadata["doc"] = doc_match.group(1)

            layer.root_prims[prim_name] = prim

        return layer


# ---------------------------------------------------------------------------
# 2. Layer Composition Engine (The "Stage")
# ---------------------------------------------------------------------------

@dataclass
class UsdStage:
    """
    The composed view of all layers — the 'flattened' scene.
    Demonstrates USD's LIVRPS composition arc (simplified).
    """
    root_layer: UsdLayer
    session_layers: list[UsdLayer] = field(default_factory=list)
    _composed_prims: dict[str, UsdPrim] = field(default_factory=dict)

    def compose(self) -> None:
        """
        Flatten all layers into a single composed view.
        Stronger layers (later in session_layers) win for conflicting opinions.
        """
        # Start with root layer prims
        self._composed_prims = {}
        for name, prim in self.root_layer.root_prims.items():
            self._composed_prims[name] = prim

        # Apply session layers (AI overrides) — strongest last
        for layer in self.session_layers:
            for name, prim in layer.root_prims.items():
                if prim.specifier == "over" and name in self._composed_prims:
                    self._composed_prims[name].apply_override(prim)
                elif prim.specifier == "def":
                    self._composed_prims[name] = prim

    def find_prim(self, path: str) -> UsdPrim | None:
        parts = [p for p in path.strip("/").split("/") if p]
        if not parts:
            return None
        root = self._composed_prims.get(parts[0])
        if root and len(parts) > 1:
            return root.find("/".join(parts[1:]))
        return root

    def add_override_layer(self, layer: UsdLayer) -> None:
        """Add a new AI override layer and recompose."""
        self.session_layers.append(layer)
        self.compose()

    def describe(self) -> str:
        """Human-readable stage summary."""
        lines = [
            f"Stage: {self.root_layer.path}",
            f"  Doc: {self.root_layer.doc}",
            f"  FPS: {self.root_layer.fps}",
            f"  Time: {self.root_layer.time_codes[0]} - {self.root_layer.time_codes[1]}",
            f"  Override layers: {len(self.session_layers)}",
            f"  Root prims: {list(self._composed_prims.keys())}",
        ]
        for layer in self.session_layers:
            author = layer.custom_layer_data.get("author", "unknown")
            lines.append(f"    Layer: {layer.path} (by {author})")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 3. Skill Registry (USB Framework)
# ---------------------------------------------------------------------------

@dataclass
class Skill:
    """An AI Skill definition from the USB registry."""
    id: str
    version: str
    category: str
    skill_file: str
    inputs: list[str]
    outputs: list[str]
    tool_bindings: list[str]
    validation: list[str]
    credits_policy: str

    def describe(self) -> str:
        return (
            f"Skill: {self.id} v{self.version}\n"
            f"  Category: {self.category}\n"
            f"  Inputs: {', '.join(self.inputs)}\n"
            f"  Outputs: {', '.join(self.outputs)}\n"
            f"  Validation: {', '.join(self.validation)}\n"
            f"  Instructions: {self.skill_file}"
        )


class SkillRegistry:
    """Loads and queries the USB skill registry."""

    def __init__(self, registry_path: str, schema_path: str | None = None):
        self.registry_path = registry_path
        self.schema_path = schema_path
        self.skills: dict[str, Skill] = {}
        self._load()

    def _load(self) -> None:
        """Parse skills from the USDA registry."""
        parser = SimplifiedUsdaParser()
        try:
            layer = parser.parse_file(self.registry_path)
        except FileNotFoundError:
            print(f"Warning: Skill registry not found at {self.registry_path}")
            return

        # Read the raw text to extract customData blocks
        text = Path(self.registry_path).read_text(encoding="utf-8")

        # Find each skill def with its customData
        skill_pattern = re.compile(
            r'def\s+Scope\s+"(\w+)".*?customData\s*=\s*\{(.*?)\}',
            re.DOTALL,
        )
        for match in skill_pattern.finditer(text):
            name = match.group(1)
            data_block = match.group(2)

            def extract(key: str) -> str:
                m = re.search(rf'string\s+{key}\s*=\s*"([^"]*)"', data_block)
                return m.group(1) if m else ""

            def extract_list(key: str) -> list[str]:
                m = re.search(rf'string\[\]\s+{key}\s*=\s*\[(.*?)\]', data_block, re.DOTALL)
                if m:
                    return [s.strip().strip('"') for s in m.group(1).split(",") if s.strip()]
                return []

            skill = Skill(
                id=extract("id"),
                version=extract("version"),
                category=extract("category"),
                skill_file=extract("skillFile"),
                inputs=extract_list("inputs"),
                outputs=extract_list("outputs"),
                tool_bindings=extract_list("toolBindings"),
                validation=extract_list("validation"),
                credits_policy=extract("creditsPolicy"),
            )
            self.skills[skill.id] = skill

    def find_skill(self, skill_id: str) -> Skill | None:
        return self.skills.get(skill_id)

    def find_by_category(self, category: str) -> list[Skill]:
        return [s for s in self.skills.values() if s.category == category]

    def list_all(self) -> list[Skill]:
        return list(self.skills.values())

    def describe(self) -> str:
        lines = [f"USB Skill Registry ({len(self.skills)} skills):"]
        for skill in self.skills.values():
            lines.append(f"  - {skill.id} v{skill.version} [{skill.category}]")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 4. QC Validation
# ---------------------------------------------------------------------------

@dataclass
class QCMetric:
    name: str
    value: float
    threshold: float
    operator: str  # "<", ">", "<=", ">="
    passed: bool

    def describe(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"  [{status}] {self.name}: {self.value:.4f} {self.operator} {self.threshold}"


@dataclass
class QCReport:
    skill_id: str
    shot_id: str
    timestamp: str
    metrics: list[QCMetric] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(m.passed for m in self.metrics)

    def describe(self) -> str:
        status = "PASSED" if self.passed else "FAILED"
        lines = [
            f"QC Report [{status}]",
            f"  Skill: {self.skill_id}",
            f"  Shot: {self.shot_id}",
            f"  Time: {self.timestamp}",
        ]
        for m in self.metrics:
            lines.append(m.describe())
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps({
            "skill_id": self.skill_id,
            "shot_id": self.shot_id,
            "timestamp": self.timestamp,
            "passed": self.passed,
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "threshold": m.threshold,
                    "operator": m.operator,
                    "passed": m.passed,
                }
                for m in self.metrics
            ],
        }, indent=2)


def evaluate_qc(skill: Skill, simulated_values: dict[str, float] | None = None) -> QCReport:
    """
    Evaluate QC metrics for a skill execution.
    In production, these would be computed from actual output analysis.
    Here we simulate for demonstration.
    """
    import random

    metrics = []
    for rule_str in skill.validation:
        # Parse "metric_name < 0.05" or "metric_name > 0.95"
        parts = re.match(r'(\w+)\s*([<>]=?)\s*([\d.]+)', rule_str)
        if not parts:
            continue
        name, op, threshold = parts.group(1), parts.group(2), float(parts.group(3))

        # Use simulated value or generate one that usually passes
        if simulated_values and name in simulated_values:
            value = simulated_values[name]
        else:
            # Simulate: 90% chance of passing
            if op in ("<", "<="):
                value = random.uniform(0, threshold * 1.2)
            else:
                value = random.uniform(threshold * 0.85, 1.0)

        # Evaluate
        if op == "<":
            passed = value < threshold
        elif op == ">":
            passed = value > threshold
        elif op == "<=":
            passed = value <= threshold
        elif op == ">=":
            passed = value >= threshold
        else:
            passed = False

        metrics.append(QCMetric(name=name, value=value, threshold=threshold, operator=op, passed=passed))

    return QCReport(
        skill_id=skill.id,
        shot_id="shot_010",
        timestamp=datetime.now(timezone.utc).isoformat(),
        metrics=metrics,
    )


# ---------------------------------------------------------------------------
# 5. Provenance Builder
# ---------------------------------------------------------------------------

@dataclass
class Provenance:
    """Tracks authorship and AI model attribution for legal compliance."""
    skill_id: str
    skill_version: str
    author: str
    model: str
    prompt: str
    timestamp: str
    shot_id: str
    qc_passed: bool
    generated_files: list[str] = field(default_factory=list)

    def to_custom_layer_data(self) -> dict[str, str]:
        """Format for embedding in USDA customLayerData."""
        return {
            "author": self.author,
            "model": self.model,
            "prompt": self.prompt,
            "timestamp": self.timestamp,
            "skillId": self.skill_id,
            "version": self.skill_version,
            "qcPassed": str(self.qc_passed).lower(),
        }

    def human_readable(self) -> str:
        return (
            f"Provenance Report\n"
            f"  Skill: {self.skill_id} v{self.skill_version}\n"
            f"  Author: {self.author}\n"
            f"  Model: {self.model}\n"
            f"  Prompt: {self.prompt}\n"
            f"  Shot: {self.shot_id}\n"
            f"  QC: {'PASSED' if self.qc_passed else 'FAILED'}\n"
            f"  Time: {self.timestamp}\n"
            f"  Files: {', '.join(self.generated_files)}"
        )


# ---------------------------------------------------------------------------
# 6. Override Layer Generator
# ---------------------------------------------------------------------------

def generate_focus_pull_layer(
    shot_id: str,
    camera_path: str,
    focus_values: dict[int, float],
    prompt: str,
    version: int = 1,
) -> tuple[str, str]:
    """
    Generate a focus-pull override layer (.usda text).
    Returns (filename, usda_content).

    This demonstrates a 'pure data edit' — only float overrides, no media.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    filename = f"focus_pull_v{version:03d}.usda"

    # Build time samples string
    time_samples = "\n".join(f"            {frame}: {dist}," for frame, dist in sorted(focus_values.items()))

    usda = f'''#usda 1.0
# AI-generated focus pull override
# This layer composes non-destructively over the shot base.
(
    doc = "AI Focus Pull — {prompt}"
    customLayerData = {{
        string author = "cinef.skill.focus_pull"
        string model = "claude-opus-4-6"
        string prompt = "{prompt}"
        string timestamp = "{timestamp}"
        string skillId = "cinef.skill.focus_pull"
        string version = "1.0.0"
        bool qcPassed = true
    }}
)

over "{shot_id}" {{
    over "main_cam" {{
        float focusDistance.timeSamples = {{
{time_samples}
        }}
    }}
}}
'''
    return filename, usda


def generate_relight_layer(
    shot_id: str,
    variant_name: str,
    intensity: float,
    color: tuple[float, float, float],
    prompt: str,
    version: int = 1,
) -> tuple[str, str]:
    """Generate a relighting override layer."""
    timestamp = datetime.now(timezone.utc).isoformat()
    filename = f"relight_v{version:03d}.usda"

    usda = f'''#usda 1.0
# AI-generated relight override
(
    doc = "AI Relight — {prompt}"
    customLayerData = {{
        string author = "cinef.skill.relight"
        string model = "claude-opus-4-6"
        string prompt = "{prompt}"
        string timestamp = "{timestamp}"
        string skillId = "cinef.skill.relight"
        string version = "1.0.0"
        bool qcPassed = true
    }}
)

over "{shot_id}" {{
    over "lighting" {{
        over "key_light" {{
            float intensity = {intensity}
            color3f color = ({color[0]}, {color[1]}, {color[2]})
        }}
    }}
}}
'''
    return filename, usda


def generate_segment_layer(
    shot_id: str,
    target: str,
    prompt: str,
    frame_range: tuple[int, int],
    version: int = 1,
) -> tuple[str, str]:
    """Generate a segmentation mask override layer."""
    timestamp = datetime.now(timezone.utc).isoformat()
    filename = f"mask_v{version:03d}.usda"

    usda = f'''#usda 1.0
# AI-generated segmentation mask
(
    doc = "AI Segmentation — {prompt}"
    customLayerData = {{
        string author = "cinef.skill.segment"
        string model = "claude-opus-4-6"
        string prompt = "{prompt}"
        string timestamp = "{timestamp}"
        string skillId = "cinef.skill.segment"
        string version = "1.0.0"
        bool qcPassed = true
    }}
)

over "{shot_id}" {{
    def Xform "masks" {{
        def Xform "{target}_mask" {{
            asset matte_sequence = @../../media/plates_proxy/{shot_id.lower()}_{target}_mask.####.exr@
            custom string target = "{target}"
            custom int[] frame_range = [{frame_range[0]}, {frame_range[1]}]
        }}
    }}
}}
'''
    return filename, usda


# ---------------------------------------------------------------------------
# 7. Git Integration
# ---------------------------------------------------------------------------

def git_stage_and_commit(
    repo_path: str,
    files: list[str],
    message: str,
    provenance: Provenance,
) -> str | None:
    """Stage files and commit with provenance in the commit message."""
    full_message = (
        f"{message}\n\n"
        f"Skill: {provenance.skill_id} v{provenance.skill_version}\n"
        f"Model: {provenance.model}\n"
        f"Prompt: {provenance.prompt}\n"
        f"QC: {'PASSED' if provenance.qc_passed else 'FAILED'}\n"
        f"\nCo-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
    )

    try:
        for f in files:
            subprocess.run(["git", "add", f], cwd=repo_path, check=True, capture_output=True)
        result = subprocess.run(
            ["git", "commit", "-m", full_message],
            cwd=repo_path, check=True, capture_output=True, text=True,
        )
        # Extract commit hash
        hash_match = re.search(r'\[[\w/]+\s+([a-f0-9]+)\]', result.stdout)
        return hash_match.group(1) if hash_match else "unknown"
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e.stderr}")
        return None


# ---------------------------------------------------------------------------
# 8. Main Demo: The Agent Execution Loop
# ---------------------------------------------------------------------------

def demo_agent_loop():
    """
    Demonstrate the full agent execution loop:
    1. Open root stage
    2. Load skill registry
    3. Analyze task → select skill → execute → QC → commit
    """
    repo_root = Path(__file__).parent
    show_root = repo_root / "show"

    print("=" * 70)
    print("  Cinef — AI-Augmented OpenUSD Pipeline Demo")
    print("=" * 70)

    # --- Step 1: Open root stage ---
    print("\n[1] Opening root stage...")
    parser = SimplifiedUsdaParser()
    root_layer = parser.parse_file(str(show_root / "show.usda"))
    stage = UsdStage(root_layer=root_layer)
    stage.compose()
    print(stage.describe())

    # --- Step 2: Load skill registry ---
    print("\n[2] Loading USB Skill Registry...")
    registry = SkillRegistry(
        registry_path=str(show_root / "skills" / "skills.usda"),
        schema_path=str(show_root / "skills" / "skills.schema.json"),
    )
    print(registry.describe())

    # --- Step 3: Simulate a creative task ---
    task = "Track focus on the protagonist through shot 010 — rack from wide to close"
    print(f"\n[3] Task received: '{task}'")

    # --- Step 4: Analyze & select skill ---
    print("\n[4] Analyzing task...")
    skill = registry.find_skill("cinef.skill.focus_pull")
    if not skill:
        print("  ERROR: No matching skill found!")
        return
    print(f"  Selected: {skill.id}")
    print(f"  Reading skill instructions from: {skill.skill_file}")

    # --- Step 5: Read the skill.md for execution instructions ---
    skill_md_path = show_root / skill.skill_file
    if skill_md_path.exists():
        instructions = skill_md_path.read_text()
        # Count the execution steps
        steps = [line for line in instructions.splitlines() if line.strip().startswith("1.") or line.strip().startswith("**")]
        print(f"  Loaded {len(steps)} instruction steps from skill.md")

    # --- Step 6: Execute — generate the override layer ---
    print("\n[5] Executing skill: generating focus pull override...")
    focus_values = {
        1: 500.0,    # Start wide
        12: 450.0,
        24: 380.0,
        36: 300.0,   # Protagonist at mid-distance
        48: 250.0,
        60: 210.0,
        72: 180.0,
        84: 160.0,
        96: 150.0,   # End close
    }
    filename, usda_content = generate_focus_pull_layer(
        shot_id="Shot_010",
        camera_path="/Shot_010/main_cam",
        focus_values=focus_values,
        prompt=task,
        version=1,
    )
    # Write the override layer
    output_dir = show_root / "shots" / "shot_010" / "ai"
    output_path = output_dir / filename
    output_path.write_text(usda_content, encoding="utf-8")
    print(f"  Written: {output_path.relative_to(repo_root)}")

    # --- Step 7: QC Validation Gate ---
    print("\n[6] Running QC validation...")
    qc_report = evaluate_qc(skill, simulated_values={"focus_accuracy": 0.993})
    print(qc_report.describe())

    # Write QC report
    qc_path = show_root / "shots" / "shot_010" / "qc" / "focus_pull_qc.json"
    qc_path.write_text(qc_report.to_json(), encoding="utf-8")
    print(f"  QC report: {qc_path.relative_to(repo_root)}")

    if not qc_report.passed:
        print("\n  QC FAILED — would refine and retry (demo stops here)")
        return

    # --- Step 8: Build provenance ---
    print("\n[7] Building provenance record...")
    provenance = Provenance(
        skill_id=skill.id,
        skill_version=skill.version,
        author="cinef.skill.focus_pull",
        model="claude-opus-4-6",
        prompt=task,
        timestamp=datetime.now(timezone.utc).isoformat(),
        shot_id="shot_010",
        qc_passed=qc_report.passed,
        generated_files=[str(output_path.relative_to(repo_root)), str(qc_path.relative_to(repo_root))],
    )
    print(provenance.human_readable())

    # --- Step 9: Compose the override into the stage ---
    print("\n[8] Composing override into stage...")
    override_layer = parser.parse_text(usda_content, str(output_path))
    stage.add_override_layer(override_layer)
    print(stage.describe())

    # --- Step 10: Demonstrate a second skill (relight) ---
    print("\n" + "-" * 70)
    print("  Bonus: Running relight skill on same shot")
    print("-" * 70)

    relight_skill = registry.find_skill("cinef.skill.relight")
    if relight_skill:
        relight_prompt = "Golden hour dramatic lighting"
        filename2, usda2 = generate_relight_layer(
            shot_id="Shot_010",
            variant_name="golden_hour",
            intensity=2.5,
            color=(1.0, 0.85, 0.6),
            prompt=relight_prompt,
            version=1,
        )
        output2 = output_dir / filename2
        output2.write_text(usda2, encoding="utf-8")
        print(f"  Written: {output2.relative_to(repo_root)}")

        qc2 = evaluate_qc(relight_skill, simulated_values={
            "temporal_flicker": 0.02,
            "color_shift": 0.01,
        })
        print(qc2.describe())

    # --- Composed Scene Tree ---
    print("\n" + "=" * 70)
    print("  Composed Scene Tree")
    print("=" * 70)
    print("""
  Show (root stage)
  |
  +-- Sequences/
  |   |
  |   +-- seq_010/
  |       |
  |       +-- shot_010  [wide establishing]
  |       |   |-- main_cam         35mm f/2.8
  |       |   |   +-- focusDistance *** AI OVERRIDE (focus_pull_v001) ***
  |       |   |-- plate            ACEScg
  |       |   |-- lighting
  |       |   |   +-- [natural]    base layer
  |       |   |   +-- [dramatic]   base variant
  |       |   |   +-- key_light    *** AI OVERRIDE (relight_v001) ***
  |       |   +-- protagonist_track
  |       |
  |       +-- shot_020  [close-up reaction]
  |           |-- main_cam         85mm f/1.4 (shallow DOF)
  |           |-- plate            ACEScg
  |           |-- face_track       blendshapes: jawOpen, mouthSmile, browRaise
  |           |   +-- [subtle]     performance variant
  |           |   +-- [intense]    performance variant
  |           +-- audio_sync       dialogue timing markers
  |
  +-- Assets/
      +-- protagonist              skeleton + face blendshapes

  Legend: *** = AI override layer (non-destructive, sparse, versioned)
          [brackets] = VariantSet options (switchable)
""")

    # --- Summary ---
    print("=" * 70)
    print("  Pipeline Summary")
    print("=" * 70)
    print(f"""
  Files created (all non-destructive overrides):
    show/shots/shot_010/ai/focus_pull_v001.usda  -- Camera focus
    show/shots/shot_010/ai/relight_v001.usda     -- Lighting
    show/shots/shot_010/qc/focus_pull_qc.json    -- QC report

  shot_010 vs shot_020 — each shot owns its own standard:
    shot_010: lighting VariantSets + camera tracking  (relight, focus_pull)
    shot_020: performance VariantSets + face tracking  (lipsync, pose_track)

  Try it yourself — open Claude Code in this directory and type:

    "What shots are in the show? What skills can I run on each?"

    "Run a focus pull on shot_010 tracking the protagonist"

    "Give shot_010 dramatic golden-hour lighting as a new variant"

    "Generate lip-sync animation for shot_020 from dialogue audio"

  See WALKTHROUGH.md for the full interactive guide.
""")


if __name__ == "__main__":
    demo_agent_loop()
