"""
Tests for DBT documentation coverage.
Verifies that models and PK/FK columns have descriptions in schema.yml files.
No database connection required.
"""
import glob
import os
import pytest
import yaml


def _project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _load_schema_files() -> list[dict]:
    """Load all schema.yml files from models/ directory."""
    root = _project_root()
    schema_files = glob.glob(os.path.join(root, "models", "**", "*.yml"), recursive=True)
    schemas = []
    for path in schema_files:
        with open(path, encoding="utf-8") as f:
            content = yaml.safe_load(f)
            if content:
                schemas.append({"path": path, "content": content})
    return schemas


# ---------------------------------------------------------------------------
# Property 12: Documentation coverage >= 80%
# Validates: Requirements 9.1
# ---------------------------------------------------------------------------

def test_model_description_coverage():
    """
    Feature: dbt-practice-project, Property 12
    At least 80% of models in schema.yml files must have a non-empty description.
    """
    schemas = _load_schema_files()
    assert schemas, "No schema.yml files found in models/ — check project structure"

    total_models = 0
    documented_models = 0

    for schema in schemas:
        for model in schema["content"].get("models", []):
            total_models += 1
            if model.get("description", "").strip():
                documented_models += 1

    assert total_models > 0, "No models found in any schema.yml file"

    coverage = documented_models / total_models
    assert coverage >= 0.8, (
        f"Documentation coverage {coverage:.0%} is below 80% "
        f"({documented_models}/{total_models} models have descriptions)"
    )


# ---------------------------------------------------------------------------
# Property 13: PK/FK columns have descriptions
# Validates: Requirements 9.2
# ---------------------------------------------------------------------------

def _get_test_names(column: dict) -> list[str]:
    """Extract test names from a column's tests list."""
    test_names = []
    for test in column.get("tests", []):
        if isinstance(test, str):
            test_names.append(test)
        elif isinstance(test, dict):
            test_names.extend(test.keys())
    return test_names


def test_pk_fk_columns_have_descriptions():
    """
    Feature: dbt-practice-project, Property 13
    Any column declared as PK (not_null + unique) or FK (relationships)
    must have a non-empty description.
    """
    schemas = _load_schema_files()
    assert schemas, "No schema.yml files found in models/ — check project structure"

    violations = []

    for schema in schemas:
        schema_path = os.path.relpath(schema["path"], _project_root())
        for model in schema["content"].get("models", []):
            model_name = model.get("name", "unknown")
            for col in model.get("columns", []):
                col_name = col.get("name", "unknown")
                test_names = _get_test_names(col)

                is_pk = "not_null" in test_names and "unique" in test_names
                is_fk = "relationships" in test_names

                if is_pk or is_fk:
                    description = col.get("description", "").strip()
                    if not description:
                        role = "PK" if is_pk else "FK"
                        violations.append(
                            f"{schema_path} → {model_name}.{col_name} ({role}) has no description"
                        )

    assert not violations, (
        f"The following PK/FK columns are missing descriptions:\n"
        + "\n".join(f"  - {v}" for v in violations)
    )
