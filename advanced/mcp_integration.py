#!/usr/bin/env python3
"""
Cinef Advanced — MCP Integration Examples

Shows how to wire the growt-audit MCP server into the Cinef pipeline
for production use. This file documents the real MCP call patterns
that Claude Code executes when running transfer-gated skill pipelines.

IP Protection Architecture:
  ┌─────────────────────────────────────────────┐
  │  YOUR INFRASTRUCTURE (nothing leaves here)  │
  │                                             │
  │  Raw Plates ──→ AI Model ──→ Output         │
  │       │                                     │
  │       ▼                                     │
  │  Feature Extraction (penultimate layer)     │
  │       │                                     │
  │       ▼                                     │
  │  Numerical Vectors Only ──────────────────────→ growt-audit MCP
  │  [0.23, -1.4, 0.8, ...]                    │        │
  │                                             │        ▼
  │  ◄─────────────────── Diagnosis ◄───────────── SAFE / RED_FLAG
  │                                             │
  │  USD Override Layer (committed or blocked)  │
  └─────────────────────────────────────────────┘

What NEVER leaves your infrastructure:
  - Raw plate pixels
  - Model weights or architecture
  - USD scene descriptions
  - Shot metadata or creative content
  - Audio, video, or any media files

What IS sent (numerical vectors only):
  - Feature embeddings: arrays of floats [n_samples x n_dims]
  - Class labels: integers or strings
  - Validation accuracy: single float

Links:
  Transfer Oracle:  https://transferoracle.ai
  Operator:         https://operator.droidtech.ai
  MCP Protocol:     https://modelcontextprotocol.io
"""

# ---------------------------------------------------------------------------
# Production MCP Call Pattern
# ---------------------------------------------------------------------------
#
# When Claude Code runs a transfer-gated skill, it executes this MCP call.
# This is what happens behind the scenes when you say:
#
#   "Run segmentation on shot_020 with transfer validation"
#
# Claude Code:
#   1. Reads the skill.md for segmentation
#   2. Extracts feature vectors from training data and shot plates
#   3. Calls the MCP server (below)
#   4. Interprets the diagnosis
#   5. Commits or blocks the override layer
#
# The MCP call (executed by Claude Code via tool use):
#
#   result = mcp__growt-audit__audit_model_transfer(
#       features_train=[...],        # list[list[float]] — training embeddings
#       labels_train=[0, 1, 2, ...],  # class labels per sample
#       features_deploy=[...],        # list[list[float]] — target shot embeddings
#       labels_deploy=[0, 0, ...],    # ground truth if available (optional)
#       val_accuracy=0.95,            # model's reported val accuracy (optional)
#   )
#
# Key result fields:
#
#   result.diagnosis          → SAFE / RED_FLAG / BAD_MODEL / UNDERTRAINED
#   result.safe_to_deploy     → bool: commit or block
#   result.report             → str: full human-readable diagnostic
#
# For per-sample detail (flagging individual bad frames):
#
#   raw = mcp__growt-audit__audit_raw(
#       features_train=...,
#       labels_train=...,
#       features_deploy=...,
#   )
#   # Returns per-sample and per-class detail — see API docs for response shape


# ---------------------------------------------------------------------------
# REST API Integration (for non-Claude / non-MCP environments)
# ---------------------------------------------------------------------------
#
# If you're integrating from a CI/CD pipeline, web service, or any
# environment without MCP support, use the REST API directly:
#
# import requests
#
# API_KEY = os.environ["GROWT_API_KEY"]  # Never hardcode — use env vars or vault
#
# # --- Single audit call ---
# response = requests.post(
#     "https://api.transferoracle.ai/v1/audit",
#     headers={
#         "Authorization": f"Bearer {API_KEY}",
#         "Content-Type": "application/json",
#     },
#     json={
#         "features_train": train_vectors,      # list[list[float]]
#         "labels_train": train_labels,          # list[int | str]
#         "features_deploy": deploy_vectors,     # list[list[float]]
#         "labels_deploy": deploy_labels,        # list[int | str] (optional)
#         "val_accuracy": 0.95,                  # float (optional)
#     },
# )
# audit = response.json()
#
# # Key fields in the response:
# print(audit["diagnosis"])          # "SAFE" | "RED_FLAG" | "BAD_MODEL" | "UNDERTRAINED"
# print(audit["safe_to_deploy"])     # True or False
# print(audit["report"])             # Full human-readable diagnostic report
#
# # See https://transferoracle.ai/docs for the complete response schema
#
#
# --- Per-sample detail (for frame-level inspection) ---
# response_raw = requests.post(
#     "https://api.transferoracle.ai/v1/audit/raw",
#     headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
#     json={
#         "features_train": train_vectors,
#         "labels_train": train_labels,
#         "features_deploy": deploy_vectors,
#     },
# )
# raw = response_raw.json()
# # Returns per-sample and per-class detail — see API docs for field names
#
#
# ---------------------------------------------------------------------------
# Python SDK Integration
# ---------------------------------------------------------------------------
#
# pip install growt-sdk  # or: pip install growt
#
# from growt import TransferOracle
#
# # Initialize — API key from env var GROWT_API_KEY, or pass explicitly
# oracle = TransferOracle()  # reads GROWT_API_KEY from environment
# # oracle = TransferOracle(api_key="YOUR_API_KEY_HERE")  # or explicit
#
# # Run audit
# result = oracle.audit(
#     features_train=train_vectors,
#     labels_train=train_labels,
#     features_deploy=deploy_vectors,
#     labels_deploy=deploy_labels,  # optional
#     val_accuracy=0.95,            # optional
# )
#
# # Use the result
# if result.safe_to_deploy:
#     print("Safe to commit USD override layer")
#     commit_layer(layer_path)
# else:
#     print(f"BLOCKED: {result.diagnosis}")
#     print(result.report)  # full diagnostic
#     write_failed_qc(result)
#
# # Batch mode — audit multiple shots against the same model
# for shot_id in ["shot_010", "shot_020", "shot_030"]:
#     shot_features = extract_features(shot_id)
#     result = oracle.audit(
#         features_train=train_vectors,
#         labels_train=train_labels,
#         features_deploy=shot_features,
#         val_accuracy=0.95,
#     )
#     print(f"  {shot_id}: {result.diagnosis} (safe={result.safe_to_deploy})")
#
#
# API keys & docs:
#   Dashboard:  https://transferoracle.ai/dashboard
#   API docs:   https://transferoracle.ai/docs
#   Operator:   https://operator.droidtech.ai
#   MCP setup:  https://modelcontextprotocol.io
#
# IMPORTANT:
#   - Never hardcode API keys — use environment variables or a secrets vault
#   - Only numerical feature vectors are transmitted — no pixels, weights, or media
#   - The MCP server can also run fully on-premise for air-gapped environments


# ---------------------------------------------------------------------------
# Feature Extraction Patterns for Film AI Models
# ---------------------------------------------------------------------------

EXTRACTION_PATTERNS = {
    "segmentation": {
        "description": "Extract from encoder backbone (e.g., ResNet/ViT penultimate layer)",
        "typical_dims": 512,
        "example": "model.backbone(frame_tensor).mean(dim=[2,3])  # global avg pool",
        "training_source": "Labeled segmentation training set",
        "deploy_source": "Shot plate frames (proxy resolution sufficient)",
    },
    "relighting": {
        "description": "Extract from scene understanding module",
        "typical_dims": 256,
        "example": "model.scene_encoder(frame_tensor).flatten()",
        "training_source": "Light stage captures with known illumination",
        "deploy_source": "Shot plate + environment map if available",
    },
    "pose_tracking": {
        "description": "Extract from body detection stage",
        "typical_dims": 128,
        "example": "model.pose_encoder(frame_tensor).squeeze()",
        "training_source": "Motion capture reference with joint labels",
        "deploy_source": "Shot plate frames containing the tracked subject",
    },
    "lipsync": {
        "description": "Extract from audio-visual alignment module",
        "typical_dims": 64,
        "example": "model.av_encoder(audio_mel, frame_tensor).flatten()",
        "training_source": "Paired audio-video with phoneme annotations",
        "deploy_source": "Shot audio + face crop frames",
    },
    "focus_pull": {
        "description": "Extract from depth estimation network",
        "typical_dims": 128,
        "example": "model.depth_encoder(frame_tensor).mean(dim=[2,3])",
        "training_source": "Stereo pairs or LiDAR ground truth",
        "deploy_source": "Shot plate frames (monocular)",
    },
}


def print_extraction_guide():
    """Print the feature extraction guide for each skill type."""
    print("Feature Extraction Guide for Transfer Oracle")
    print("=" * 60)
    print()
    for skill, info in EXTRACTION_PATTERNS.items():
        print(f"  {skill}:")
        print(f"    Layer:    {info['description']}")
        print(f"    Dims:     {info['typical_dims']}")
        print(f"    Code:     {info['example']}")
        print(f"    Train:    {info['training_source']}")
        print(f"    Deploy:   {info['deploy_source']}")
        print()


if __name__ == "__main__":
    print_extraction_guide()
    print()
    print("For production integration, see:")
    print("  Transfer Oracle:  https://transferoracle.ai")
    print("  Operator:         https://operator.droidtech.ai")
    print("  MCP Protocol:     https://modelcontextprotocol.io")
