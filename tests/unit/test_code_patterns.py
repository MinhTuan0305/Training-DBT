"""
Unit tests for DBT code patterns.
These tests verify that models follow correct patterns (source/ref usage, aggregations).
No database connection required.
"""
import glob
import os
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_sql(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _project_root() -> str:
    """Return the absolute path to the dbt project root."""
    # tests/unit/ -> project root (two levels up)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


# ---------------------------------------------------------------------------
# Property 1: Staging models only reference raw data via source()
# Validates: Requirements 3.2, 4.5
# ---------------------------------------------------------------------------

def test_staging_models_use_source():
    """
    Feature: dbt-practice-project, Property 1
    For any staging model file, it must use {{ source( and must NOT
    contain hard-coded schema names.
    """
    root = _project_root()
    staging_files = glob.glob(os.path.join(root, "models", "staging", "*.sql"))

    assert staging_files, "No staging SQL files found — check project structure"

    forbidden_patterns = ["dbt_dev.", "public.", "analytics.", "raw."]

    for sql_file in staging_files:
        content = _read_sql(sql_file)
        model_name = os.path.basename(sql_file)

        # Must use source()
        assert "{{ source(" in content, (
            f"{model_name} does not use {{ source() }} macro — "
            "staging models must reference raw tables via source()"
        )

        # Must NOT hard-code schema names
        for pattern in forbidden_patterns:
            assert pattern not in content, (
                f"{model_name} contains hard-coded schema reference '{pattern}' — "
                "use {{ source() }} instead"
            )


# ---------------------------------------------------------------------------
# Property 2: Mart models only reference other models via ref()
# Validates: Requirements 5.2
# ---------------------------------------------------------------------------

def test_mart_models_use_ref():
    """
    Feature: dbt-practice-project, Property 2
    For any mart model file, it must use {{ ref( and must NOT
    contain hard-coded schema names.
    """
    root = _project_root()
    mart_files = glob.glob(os.path.join(root, "models", "marts", "*.sql"))

    assert mart_files, "No mart SQL files found — check project structure"

    forbidden_patterns = ["dbt_dev.", "public.", "analytics.", "staging."]

    for sql_file in mart_files:
        content = _read_sql(sql_file)
        model_name = os.path.basename(sql_file)

        # Must use ref()
        assert "{{ ref(" in content, (
            f"{model_name} does not use {{ ref() }} macro — "
            "mart models must reference other models via ref()"
        )

        # Must NOT hard-code schema names
        for pattern in forbidden_patterns:
            assert pattern not in content, (
                f"{model_name} contains hard-coded schema reference '{pattern}' — "
                "use {{ ref() }} instead"
            )


# ---------------------------------------------------------------------------
# Property 3: Mart models perform aggregation or JOIN
# Validates: Requirements 5.3
# ---------------------------------------------------------------------------

def test_mart_models_have_aggregation_or_join():
    """
    Feature: dbt-practice-project, Property 3
    For any mart model file, the SQL must contain at least one of:
    GROUP BY, JOIN, SUM(, COUNT(, AVG(, MIN(, MAX(
    """
    root = _project_root()
    mart_files = glob.glob(os.path.join(root, "models", "marts", "*.sql"))

    assert mart_files, "No mart SQL files found — check project structure"

    aggregation_keywords = ["GROUP BY", "JOIN", "SUM(", "COUNT(", "AVG(", "MIN(", "MAX("]

    for sql_file in mart_files:
        content = _read_sql(sql_file).upper()
        model_name = os.path.basename(sql_file)

        has_aggregation = any(kw in content for kw in aggregation_keywords)
        assert has_aggregation, (
            f"{model_name} does not contain aggregation or JOIN — "
            f"mart models must perform at least one of: {aggregation_keywords}"
        )


# ---------------------------------------------------------------------------
# Property 14: Materialization config correct per layer
# Validates: Requirements 4.2, 10.2
# ---------------------------------------------------------------------------

def test_materialization_config():
    """
    Feature: dbt-practice-project, Property 14
    staging layer must be materialized as 'view'
    marts layer must be materialized as 'table'
    """
    import yaml

    root = _project_root()
    dbt_project_path = os.path.join(root, "dbt_project.yml")

    assert os.path.exists(dbt_project_path), "dbt_project.yml not found"

    with open(dbt_project_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    models_config = config.get("models", {}).get("dbt_practice_project", {})

    staging_materialized = models_config.get("staging", {}).get("+materialized")
    marts_materialized = models_config.get("marts", {}).get("+materialized")

    assert staging_materialized == "view", (
        f"staging +materialized should be 'view', got '{staging_materialized}'"
    )
    assert marts_materialized == "table", (
        f"marts +materialized should be 'table', got '{marts_materialized}'"
    )
