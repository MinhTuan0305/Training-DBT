"""
Shared pytest fixtures and helper functions for DBT unit tests.
"""
import os
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def project_root() -> str:
    """Return the absolute path to the dbt project root."""
    # tests/unit/conftest.py -> project root (two levels up)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


# ---------------------------------------------------------------------------
# Helper functions for macro logic testing
# ---------------------------------------------------------------------------

def parse_macro_output(macro_name: str, args: dict) -> str:
    """
    Simulate DBT macro output using Python equivalents.
    This allows testing macro logic without a DBT installation or database.

    Supported macros:
      - cents_to_dollars(column_name, precision=2)
      - generate_schema_name(custom_schema_name, target_schema)
      - limit_data_in_dev(column_name, dev_limit=100, target_name='dev')

    Args:
        macro_name: Name of the macro to simulate
        args: Dictionary of arguments to pass to the macro

    Returns:
        String representation of the macro output

    Example:
        parse_macro_output('cents_to_dollars', {'column_name': 'amount_cents'})
        # returns: "round(amount_cents / 100.0, 2)"

        parse_macro_output('limit_data_in_dev', {
            'column_name': 'ordered_at',
            'dev_limit': 30,
            'target_name': 'dev'
        })
        # returns: "where ordered_at >= current_date - interval '30 days'"
    """
    if macro_name == "cents_to_dollars":
        column_name = args.get("column_name", "")
        precision = args.get("precision", 2)
        return f"round({column_name} / 100.0, {precision})"

    elif macro_name == "generate_schema_name":
        custom_schema_name = args.get("custom_schema_name", None)
        target_schema = args.get("target_schema", "dbt_dev")
        if custom_schema_name is None:
            return target_schema
        return custom_schema_name.strip()

    elif macro_name == "limit_data_in_dev":
        column_name = args.get("column_name", "")
        dev_limit = args.get("dev_limit", 100)
        target_name = args.get("target_name", "dev")
        if target_name == "dev":
            return f"where {column_name} >= current_date - interval '{dev_limit} days'"
        return ""

    else:
        raise ValueError(f"Unknown macro: {macro_name}")
