"""
Tests for DBT artifact structure (manifest.json, run_results.json).
These tests require running `dbt run` or `dbt compile` first to generate artifacts.
Run: dbt compile && pytest tests/unit/test_artifacts.py -v
"""
import json
import os
import pytest


def _project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _load_json(filename: str) -> dict:
    path = os.path.join(_project_root(), "target", filename)
    if not os.path.exists(path):
        pytest.skip(f"target/{filename} not found — run `dbt compile` or `dbt run` first")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Property 10: manifest.json has required fields
# Validates: Requirements 8.3
# ---------------------------------------------------------------------------

def test_manifest_required_fields():
    """
    Feature: dbt-practice-project, Property 10
    manifest.json must contain top-level keys: metadata, nodes, sources, exposures.
    Each node must have: unique_id, name, resource_type, depends_on, config.
    """
    manifest = _load_json("manifest.json")

    # Top-level keys
    required_top_level = {"metadata", "nodes", "sources", "exposures"}
    for key in required_top_level:
        assert key in manifest, f"manifest.json missing top-level key: '{key}'"

    # metadata fields
    metadata = manifest["metadata"]
    assert "dbt_version" in metadata, "manifest.json metadata missing 'dbt_version'"
    assert "generated_at" in metadata, "manifest.json metadata missing 'generated_at'"

    # Each node must have required fields
    required_node_fields = {"unique_id", "name", "resource_type", "depends_on", "config"}
    for node_id, node in manifest["nodes"].items():
        for field in required_node_fields:
            assert field in node, (
                f"Node '{node_id}' in manifest.json missing field: '{field}'"
            )


# ---------------------------------------------------------------------------
# Property 11: run_results.json only contains valid statuses
# Validates: Requirements 8.4
# ---------------------------------------------------------------------------

VALID_STATUSES = {"success", "error", "skipped", "warn", "pass", "fail"}


def test_run_results_valid_statuses():
    """
    Feature: dbt-practice-project, Property 11
    Every result in run_results.json must have a status from the valid set.
    """
    run_results = _load_json("run_results.json")

    assert "results" in run_results, "run_results.json missing 'results' key"

    for result in run_results["results"]:
        assert "status" in result, f"Result missing 'status' field: {result}"
        assert result["status"] in VALID_STATUSES, (
            f"Invalid status '{result['status']}' in run_results.json — "
            f"must be one of: {VALID_STATUSES}"
        )
