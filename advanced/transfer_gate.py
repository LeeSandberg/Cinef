#!/usr/bin/env python3
"""
Cinef Advanced — Transfer Oracle QC Gate

Demonstrates using the growt-audit MCP server as a pre-commit QC gate
in the AI-Augmented OpenUSD pipeline. Before an AI skill's output is
committed to the USD stage, we validate that the ML model backing
that skill will actually transfer to the target shot's visual domain.

The dangerous scenario this catches:
  A segmentation model scores 98% on validation data but silently fails
  on shot_020 because the lighting/color distribution shifted from training.
  Standard metrics miss this. The Transfer Oracle does not.

IP Protection:
  Feature vectors are extracted locally — raw plates, models, and weights
  never leave your infrastructure. Only numerical embeddings are sent to
  the audit endpoint. No pixel data, no model weights, no scene descriptions.

Usage:
  python advanced/transfer_gate.py                    # Run full demo
  python advanced/transfer_gate.py --shot shot_010    # Specific shot
  python advanced/transfer_gate.py --skill segment    # Specific skill

For production integration with the growt-audit MCP server, see:
  https://transferoracle.ai
  https://operator.droidtech.ai
"""

from __future__ import annotations

import json
import random
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# Add parent for cinef imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from cinef import (
    QCMetric,
    QCReport,
    Provenance,
    SkillRegistry,
    SimplifiedUsdaParser,
    generate_segment_layer,
    generate_relight_layer,
    generate_focus_pull_layer,
)


# ---------------------------------------------------------------------------
# 1. Feature Extraction Simulation
# ---------------------------------------------------------------------------

@dataclass
class FeatureVector:
    """
    Represents an embedding from the penultimate layer of an AI model.

    In production, you'd extract these from your actual model:
      - Segmentation model: features from the encoder backbone
      - Relighting model: features from the scene understanding module
      - Pose model: features from the body detection stage

    IP SAFETY: Only numerical vectors leave your infrastructure.
    No raw pixels, no model weights, no scene content.
    """
    values: list[float]
    label: str | int
    source: str  # "training" or shot ID
    frame: int = 0

    @property
    def dimension(self) -> int:
        return len(self.values)


def simulate_training_features(
    n_samples: int = 100,
    n_dims: int = 32,
    n_classes: int = 4,
    seed: int = 42,
) -> list[FeatureVector]:
    """
    Simulate feature vectors from training data.

    In production, these come from running your training set through
    the model and extracting the penultimate layer activations.
    Each class represents a visual category the model learned:
      0 = "indoor_neutral"   (studio lighting, controlled environment)
      1 = "outdoor_daylight" (natural light, sky visible)
      2 = "outdoor_golden"   (golden hour, warm tones)
      3 = "indoor_dramatic"  (high contrast, theatrical lighting)
    """
    random.seed(seed)
    features = []

    # Each class has a distinct cluster center in feature space
    class_centers = {
        0: [random.gauss(0, 0.3) for _ in range(n_dims)],
        1: [random.gauss(2, 0.3) for _ in range(n_dims)],
        2: [random.gauss(1.5, 0.3) for _ in range(n_dims)],
        3: [random.gauss(-1, 0.3) for _ in range(n_dims)],
    }

    class_names = {
        0: "indoor_neutral",
        1: "outdoor_daylight",
        2: "outdoor_golden",
        3: "indoor_dramatic",
    }

    for i in range(n_samples):
        cls = i % n_classes
        center = class_centers[cls]
        # Add noise around class center
        vec = [c + random.gauss(0, 0.5) for c in center]
        features.append(FeatureVector(
            values=vec,
            label=cls,
            source="training",
            frame=i,
        ))

    return features


def simulate_shot_features(
    shot_id: str,
    n_frames: int = 24,
    n_dims: int = 32,
    distribution: str = "matching",
    seed: int = 123,
) -> list[FeatureVector]:
    """
    Simulate feature vectors from a shot's plate frames.

    'distribution' controls how close the shot is to training data:
      - "matching": shot looks like training data (SAFE)
      - "shifted": shot has mild distribution shift (may trigger warnings)
      - "alien": shot is completely unlike training data (RED_FLAG)

    This simulates the real scenario where a model trained on indoor
    studio footage is deployed on outdoor golden-hour footage.
    """
    random.seed(seed)
    features = []

    if distribution == "matching":
        # Close to indoor_neutral training cluster
        center = [random.gauss(0, 0.3) for _ in range(n_dims)]
        noise_std = 0.5
        label = 0
    elif distribution == "shifted":
        # Between clusters — partial overlap with training
        center = [random.gauss(0.8, 0.3) for _ in range(n_dims)]
        noise_std = 0.8
        label = 0
    elif distribution == "alien":
        # Completely outside training distribution
        center = [random.gauss(5, 0.3) for _ in range(n_dims)]
        noise_std = 0.3
        label = 0
    else:
        raise ValueError(f"Unknown distribution: {distribution}")

    for frame in range(n_frames):
        vec = [c + random.gauss(0, noise_std) for c in center]
        features.append(FeatureVector(
            values=vec,
            label=label,
            source=shot_id,
            frame=frame + 1,
        ))

    return features


# ---------------------------------------------------------------------------
# 2. Transfer Oracle Gate (MCP Integration Point)
# ---------------------------------------------------------------------------

@dataclass
class TransferAuditResult:
    """
    Result from the growt-audit Transfer Oracle.

    In production, this comes from calling the MCP server:
      mcp__growt-audit__audit_model_transfer(
          features_train=...,
          labels_train=...,
          features_deploy=...,
          labels_deploy=...,
          val_accuracy=...,
      )

    The diagnosis tells you whether to trust the model's output.
    See https://transferoracle.ai/docs for field documentation.
    """
    diagnosis: str
    transfer_oracle: float
    val_accuracy: float
    val_oracle_gap: float
    coverage_pct: float
    consensus_quality: str
    n_flagged_samples: int
    classes_at_risk: list[str]
    recommendations: list[str]
    safe_to_deploy: bool

    def describe(self) -> str:
        status = "SAFE" if self.safe_to_deploy else "BLOCKED"
        lines = [
            f"Transfer Oracle Report [{status}]",
            f"  Diagnosis:        {self.diagnosis}",
            f"  Val Accuracy:     {self.val_accuracy:.3f}",
            f"  Transfer Oracle:  {self.transfer_oracle:.3f}",
            f"  Val-Oracle Gap:   {self.val_oracle_gap:.3f}",
            f"  Coverage:         {self.coverage_pct:.1%}",
            f"  Consensus:        {self.consensus_quality}",
            f"  Flagged Samples:  {self.n_flagged_samples}",
        ]
        if self.classes_at_risk:
            lines.append(f"  Classes at Risk:  {', '.join(self.classes_at_risk)}")
        if self.recommendations:
            lines.append("  Recommendations:")
            for r in self.recommendations:
                lines.append(f"    - {r}")
        return "\n".join(lines)

    def to_qc_metrics(self) -> list[QCMetric]:
        """Convert to standard Cinef QC metrics for the pipeline."""
        return [
            QCMetric(
                name="transfer_oracle",
                value=self.transfer_oracle,
                threshold=0.70,
                operator=">",
                passed=self.transfer_oracle > 0.70,
            ),
            QCMetric(
                name="val_oracle_gap",
                value=self.val_oracle_gap,
                threshold=0.15,
                operator="<",
                passed=self.val_oracle_gap < 0.15,
            ),
            QCMetric(
                name="deploy_coverage",
                value=self.coverage_pct,
                threshold=0.50,
                operator=">",
                passed=self.coverage_pct > 0.50,
            ),
        ]


def run_transfer_audit_simulated(
    train_features: list[FeatureVector],
    deploy_features: list[FeatureVector],
    val_accuracy: float = 0.95,
) -> TransferAuditResult:
    """
    Simulate the growt-audit MCP call for demonstration.

    In production, replace this entire function with the actual MCP call
    or the REST API. See commented examples below.

    The simulation here returns canned/hardcoded responses.
    The actual Transfer Oracle algorithm is proprietary and runs
    exclusively on the MCP server or REST API.
    """
    # -----------------------------------------------------------------
    # PRODUCTION OPTION 1: MCP Server (recommended for Claude Code)
    # -----------------------------------------------------------------
    # When growt-audit is configured as an MCP server in your
    # Claude Code settings, Claude calls it directly as a tool:
    #
    #   result = mcp__growt-audit__audit_model_transfer(
    #       features_train=[f.values for f in train_features],
    #       labels_train=[f.label for f in train_features],
    #       features_deploy=[f.values for f in deploy_features],
    #       labels_deploy=[f.label for f in deploy_features],
    #       val_accuracy=val_accuracy,
    #   )
    #
    # The MCP server runs locally or on your infrastructure.
    # Contact https://operator.droidtech.ai for licensing.
    #
    # -----------------------------------------------------------------
    # PRODUCTION OPTION 2: REST API (for non-Claude integrations)
    # -----------------------------------------------------------------
    # import requests
    #
    # response = requests.post(
    #     "https://api.transferoracle.ai/v1/audit",
    #     headers={
    #         "Authorization": "Bearer YOUR_API_KEY_HERE",  # Get from https://transferoracle.ai/dashboard
    #         "Content-Type": "application/json",
    #     },
    #     json={
    #         "features_train": [f.values for f in train_features],
    #         "labels_train": [f.label for f in train_features],
    #         "features_deploy": [f.values for f in deploy_features],
    #         "labels_deploy": [f.label for f in deploy_features],
    #         "val_accuracy": val_accuracy,
    #     },
    # )
    # result = response.json()
    #
    # # Response shape:
    # # {
    # #     "diagnosis": "SAFE" | "RED_FLAG" | "BAD_MODEL" | "UNDERTRAINED",
    # #     "safe_to_deploy": true | false,
    # #     "transfer_oracle": 0.87,
    # #     "val_oracle_gap": 0.08,
    # #     "coverage_pct": 0.92,
    # #     "consensus_quality": "STRONG" | "MODERATE" | "WEAK",
    # #     "n_flagged_samples": 3,
    # #     "classes_at_risk": ["outdoor_golden"],
    # #     "top_recommendations": [...],
    # #     "report": "Full human-readable diagnostic report..."
    # # }
    #
    # -----------------------------------------------------------------
    # PRODUCTION OPTION 3: Python SDK
    # -----------------------------------------------------------------
    # from growt import TransferOracle
    #
    # oracle = TransferOracle(api_key="YOUR_API_KEY_HERE")  # or set GROWT_API_KEY env var
    # result = oracle.audit(
    #     features_train=[f.values for f in train_features],
    #     labels_train=[f.label for f in train_features],
    #     features_deploy=[f.values for f in deploy_features],
    #     labels_deploy=[f.label for f in deploy_features],
    #     val_accuracy=val_accuracy,
    # )
    # print(result.report)           # human-readable summary
    # print(result.safe_to_deploy)   # bool: commit or block
    #
    # API keys: https://transferoracle.ai/dashboard
    # Docs:     https://transferoracle.ai/docs
    # Operator: https://operator.droidtech.ai
    # -----------------------------------------------------------------
    #
    # -----------------------------------------------------------------
    # DEMO MODE — hardcoded mock responses only.
    #
    # This simulation returns CANNED results to demonstrate the
    # pipeline flow. It does NOT perform any analysis on the feature
    # vectors. The actual Transfer Oracle algorithm is proprietary
    # and runs exclusively on the MCP server / REST API.
    #
    # The vectors passed in are ignored — the result is determined
    # solely by which scenario the caller configured.
    # -----------------------------------------------------------------

    # Detect which canned scenario to return based on deploy vector
    # characteristics (just checking magnitude to pick a scenario —
    # this is NOT how the real oracle works)
    sample_magnitude = sum(abs(v) for v in deploy_features[0].values)
    n_deploy = len(deploy_features)

    if sample_magnitude > 100:
        # Canned RED_FLAG scenario
        return TransferAuditResult(
            diagnosis="RED_FLAG",
            transfer_oracle=0.0,
            val_accuracy=val_accuracy,
            val_oracle_gap=val_accuracy,
            coverage_pct=0.10,
            consensus_quality="WEAK",
            n_flagged_samples=n_deploy,
            classes_at_risk=["indoor_neutral (primary class)"],
            recommendations=[
                "[HIGH] Do not commit this skill output to the USD stage",
                "[HIGH] Model validation accuracy is misleading — structure does not transfer",
                "[MEDIUM] Fine-tune model on samples from this shot's visual domain",
                "[MEDIUM] Add representative frames from this shot to training set",
                "[MEDIUM] Low coverage — deploy data may not be well represented",
                f"[LOW] {n_deploy} frames flagged as low-confidence — inspect manually",
            ],
            safe_to_deploy=False,
        )
    elif sample_magnitude > 30:
        # Canned SAFE scenario
        return TransferAuditResult(
            diagnosis="SAFE",
            transfer_oracle=0.8264,
            val_accuracy=val_accuracy,
            val_oracle_gap=round(val_accuracy - 0.8264, 4),
            coverage_pct=0.8601,
            consensus_quality="STRONG",
            n_flagged_samples=0,
            classes_at_risk=[],
            recommendations=[],
            safe_to_deploy=True,
        )
    else:
        # Canned UNDERTRAINED scenario
        return TransferAuditResult(
            diagnosis="UNDERTRAINED",
            transfer_oracle=0.6781,
            val_accuracy=val_accuracy,
            val_oracle_gap=round(val_accuracy - 0.6781, 4),
            coverage_pct=0.7118,
            consensus_quality="MODERATE",
            n_flagged_samples=0,
            classes_at_risk=["indoor_neutral (primary class)"],
            recommendations=[
                "[HIGH] Do not commit this skill output to the USD stage",
            ],
            safe_to_deploy=False,
        )


# ---------------------------------------------------------------------------
# 3. Transfer-Gated Agent Loop
# ---------------------------------------------------------------------------

def run_transfer_gated_pipeline(
    shot_id: str = "shot_010",
    skill_id: str = "cinef.skill.segment",
    distribution: str = "matching",
):
    """
    Full demo: skill execution with Transfer Oracle QC gate.

    Shows three scenarios:
      1. "matching" — shot matches training data → SAFE → commit
      2. "shifted"  — partial drift → UNDERTRAINED → blocked
      3. "alien"    — completely different → RED_FLAG → blocked

    IP Protection Flow:
      Raw plates → local model → feature vectors (numbers only) → audit
      No pixels, weights, or scene descriptions leave your infrastructure.
    """
    repo_root = Path(__file__).parent.parent
    show_root = repo_root / "show"

    print("=" * 70)
    print("  Cinef Advanced — Transfer Oracle QC Gate")
    print("=" * 70)

    # --- Step 1: Load skill registry ---
    print(f"\n[1] Loading skill: {skill_id}")
    registry = SkillRegistry(
        registry_path=str(show_root / "skills" / "skills.usda"),
    )
    skill = registry.find_skill(skill_id)
    if not skill:
        print(f"  ERROR: Skill {skill_id} not found")
        return
    print(f"  {skill.id} v{skill.version} [{skill.category}]")

    # --- Step 2: Extract features (simulated) ---
    print(f"\n[2] Extracting feature vectors...")
    print(f"  Training set: 100 samples, 32 dimensions, 4 visual classes")
    print(f"  Deploy set:   {shot_id}, 24 frames, distribution='{distribution}'")
    print(f"  IP Protection: only numerical embeddings — no pixels leave local")

    train_features = simulate_training_features(n_samples=100, n_dims=32)
    deploy_features = simulate_shot_features(
        shot_id=shot_id,
        n_frames=24,
        n_dims=32,
        distribution=distribution,
    )

    print(f"  Training vectors: {len(train_features)} x {train_features[0].dimension}d")
    print(f"  Deploy vectors:   {len(deploy_features)} x {deploy_features[0].dimension}d")

    # --- Step 3: Run Transfer Oracle ---
    print(f"\n[3] Running Transfer Oracle audit...")
    print(f"  (In production: mcp__growt-audit__audit_model_transfer)")

    audit_result = run_transfer_audit_simulated(
        train_features=train_features,
        deploy_features=deploy_features,
        val_accuracy=0.95,  # Model reports 95% validation accuracy
    )
    print()
    print(audit_result.describe())

    # --- Step 4: QC Gate Decision ---
    print(f"\n[4] Transfer QC Gate...")
    transfer_metrics = audit_result.to_qc_metrics()
    for m in transfer_metrics:
        print(m.describe())

    if not audit_result.safe_to_deploy:
        print(f"\n  BLOCKED — Transfer Oracle diagnosis: {audit_result.diagnosis}")
        print(f"  The model reports {audit_result.val_accuracy:.0%} validation accuracy")
        print(f"  but Transfer Oracle shows only {audit_result.transfer_oracle:.0%} transfer.")
        print(f"  This is the gap that standard metrics miss.")
        print(f"\n  Pipeline action: REFUSE TO COMMIT override layer.")
        print(f"  The agent will not write a .usda layer that it cannot trust.")

        # Write the failed QC report anyway for audit trail
        failed_qc = QCReport(
            skill_id=skill.id,
            shot_id=shot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metrics=transfer_metrics,
        )
        qc_dir = show_root / "shots" / shot_id / "qc"
        qc_dir.mkdir(parents=True, exist_ok=True)
        qc_path = qc_dir / f"transfer_gate_FAILED.json"
        qc_path.write_text(failed_qc.to_json(), encoding="utf-8")
        print(f"  Failed QC report: {qc_path.relative_to(repo_root)}")
        return

    # --- Step 5: Safe — proceed with skill execution ---
    print(f"\n  PASSED — safe to deploy model on {shot_id}")
    print(f"\n[5] Executing skill: {skill.id}...")

    if skill_id == "cinef.skill.segment":
        filename, usda = generate_segment_layer(
            shot_id="Shot_010",
            target="protagonist",
            prompt="Isolate protagonist for selective grading",
            frame_range=(1, 96),
            version=1,
        )
    elif skill_id == "cinef.skill.relight":
        filename, usda = generate_relight_layer(
            shot_id="Shot_010",
            variant_name="transfer_validated",
            intensity=2.0,
            color=(1.0, 0.9, 0.8),
            prompt="Warm key light, transfer-validated",
            version=1,
        )
    else:
        filename, usda = generate_focus_pull_layer(
            shot_id="Shot_010",
            camera_path="/Shot_010/main_cam",
            focus_values={1: 500, 48: 300, 96: 150},
            prompt="Transfer-validated focus pull",
            version=1,
        )

    output_dir = show_root / "shots" / shot_id / "ai"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    output_path.write_text(usda, encoding="utf-8")
    print(f"  Written: {output_path.relative_to(repo_root)}")

    # Write passing QC report with transfer metrics
    passing_qc = QCReport(
        skill_id=skill.id,
        shot_id=shot_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        metrics=transfer_metrics,
    )
    qc_dir = show_root / "shots" / shot_id / "qc"
    qc_path = qc_dir / "transfer_gate_PASSED.json"
    qc_path.write_text(passing_qc.to_json(), encoding="utf-8")
    print(f"  QC report: {qc_path.relative_to(repo_root)}")

    # Provenance
    print(f"\n[6] Provenance with transfer validation...")
    provenance = Provenance(
        skill_id=skill.id,
        skill_version=skill.version,
        author=skill.id,
        model="claude-opus-4-6",
        prompt="Isolate protagonist for selective grading",
        timestamp=datetime.now(timezone.utc).isoformat(),
        shot_id=shot_id,
        qc_passed=True,
        generated_files=[
            str(output_path.relative_to(repo_root)),
            str(qc_path.relative_to(repo_root)),
        ],
    )
    print(provenance.human_readable())

    print(f"\n{'=' * 70}")
    print(f"  Transfer-Gated Pipeline Complete")
    print(f"{'=' * 70}")
    print(f"""
  The Transfer Oracle validated that the {skill.category} model's learned
  structure transfers to {shot_id}'s visual domain BEFORE committing
  the override layer.

  Without this gate, a model reporting {audit_result.val_accuracy:.0%} validation accuracy
  could silently produce bad output on distribution-shifted footage.
  Standard metrics would not catch this.

  IP Protection summary:
    - Raw plates never left local infrastructure
    - Model weights never transmitted
    - Only {train_features[0].dimension}-dimensional numerical vectors were audited
    - Scene descriptions (USD) stayed local
    - Provenance tracks the audit result for legal compliance
""")


# ---------------------------------------------------------------------------
# 4. Three-Scenario Comparison
# ---------------------------------------------------------------------------

def demo_three_scenarios():
    """Run all three scenarios to show the full diagnostic spectrum."""
    print("\n")
    print("#" * 70)
    print("#  SCENARIO 1: Matching Distribution (expect SAFE)")
    print("#" * 70)
    run_transfer_gated_pipeline(
        shot_id="shot_010",
        skill_id="cinef.skill.segment",
        distribution="matching",
    )

    print("\n\n")
    print("#" * 70)
    print("#  SCENARIO 2: Shifted Distribution (expect UNDERTRAINED)")
    print("#" * 70)
    run_transfer_gated_pipeline(
        shot_id="shot_010",
        skill_id="cinef.skill.segment",
        distribution="shifted",
    )

    print("\n\n")
    print("#" * 70)
    print("#  SCENARIO 3: Alien Distribution (expect RED_FLAG)")
    print("#  This is the DANGEROUS case: 95% val accuracy but won't transfer")
    print("#" * 70)
    run_transfer_gated_pipeline(
        shot_id="shot_010",
        skill_id="cinef.skill.segment",
        distribution="alien",
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Cinef Transfer Oracle QC Gate Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python advanced/transfer_gate.py                        # All three scenarios
  python advanced/transfer_gate.py --shot shot_020        # Specific shot
  python advanced/transfer_gate.py --distribution alien   # Force RED_FLAG
  python advanced/transfer_gate.py --all                  # Full comparison

Links:
  Transfer Oracle:  https://transferoracle.ai
  Operator:         https://operator.droidtech.ai
        """,
    )
    parser.add_argument("--shot", default="shot_010", help="Shot ID (default: shot_010)")
    parser.add_argument("--skill", default="cinef.skill.segment", help="Skill ID")
    parser.add_argument("--distribution", default="matching",
                        choices=["matching", "shifted", "alien"],
                        help="Simulated distribution type")
    parser.add_argument("--all", action="store_true",
                        help="Run all three scenarios for comparison")

    args = parser.parse_args()

    if args.all:
        demo_three_scenarios()
    else:
        run_transfer_gated_pipeline(
            shot_id=args.shot,
            skill_id=args.skill,
            distribution=args.distribution,
        )
