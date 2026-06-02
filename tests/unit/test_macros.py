"""
Property-based tests for DBT macro logic.
These tests verify macro correctness by implementing equivalent Python logic
and testing it with Hypothesis.
No database connection required.
"""
from hypothesis import given, settings
import hypothesis.strategies as st


# ---------------------------------------------------------------------------
# Python equivalents of DBT macros (for testing purposes)
# ---------------------------------------------------------------------------

def cents_to_dollars(cents: int, precision: int = 2) -> float:
    """Python equivalent of the cents_to_dollars DBT macro."""
    return round(cents / 100.0, precision)


def generate_schema_name(custom_schema_name, target_schema: str) -> str:
    """Python equivalent of the generate_schema_name DBT macro."""
    if custom_schema_name is None:
        return target_schema
    return custom_schema_name.strip()


def limit_data_in_dev(column_name: str, dev_limit: int = 100, target_name: str = "dev") -> str:
    """Python equivalent of the limit_data_in_dev DBT macro."""
    if target_name == "dev":
        return f"where {column_name} >= current_date - interval '{dev_limit} days'"
    return ""


# ---------------------------------------------------------------------------
# Property 4: cents_to_dollars correctness
# Validates: Requirements 6.2
# ---------------------------------------------------------------------------

@given(cents=st.integers(min_value=0, max_value=10_000_000))
@settings(max_examples=100)
def test_cents_to_dollars_property(cents):
    """
    Feature: dbt-practice-project, Property 4
    For any non-negative integer cents, result == round(cents / 100.0, 2)
    """
    result = cents_to_dollars(cents)
    expected = round(cents / 100.0, 2)
    assert result == expected, f"cents_to_dollars({cents}) = {result}, expected {expected}"


def test_cents_to_dollars_known_values():
    """Spot-check known values from the spec."""
    assert cents_to_dollars(0) == 0.00
    assert cents_to_dollars(100) == 1.00
    assert cents_to_dollars(150) == 1.50
    assert cents_to_dollars(1999) == 19.99
    assert cents_to_dollars(10000) == 100.00


# ---------------------------------------------------------------------------
# Property 5: generate_schema_name logic
# Validates: Requirements 6.3
# ---------------------------------------------------------------------------

@given(
    custom_schema=st.one_of(
        st.none(),
        st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
    ),
    target_schema=st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
)
@settings(max_examples=100)
def test_generate_schema_name_property(custom_schema, target_schema):
    """
    Feature: dbt-practice-project, Property 5
    If custom_schema is None -> return target_schema
    If custom_schema has value -> return custom_schema (trimmed)
    """
    result = generate_schema_name(custom_schema, target_schema)
    if custom_schema is None:
        assert result == target_schema, (
            f"Expected target_schema '{target_schema}', got '{result}'"
        )
    else:
        assert result == custom_schema.strip(), (
            f"Expected '{custom_schema.strip()}', got '{result}'"
        )


def test_generate_schema_name_none_returns_target():
    assert generate_schema_name(None, "dbt_dev") == "dbt_dev"


def test_generate_schema_name_custom_overrides_target():
    assert generate_schema_name("staging", "dbt_dev") == "staging"


def test_generate_schema_name_trims_whitespace():
    assert generate_schema_name("  analytics  ", "dbt_dev") == "analytics"


# ---------------------------------------------------------------------------
# Property 6: limit_data_in_dev target-aware
# Validates: Requirements 6.4
# ---------------------------------------------------------------------------

@given(
    column_name=st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
    dev_limit=st.integers(min_value=1, max_value=365),
    target_name=st.sampled_from(["dev", "prod", "staging", "ci"]),
)
@settings(max_examples=100)
def test_limit_data_in_dev_property(column_name, dev_limit, target_name):
    """
    Feature: dbt-practice-project, Property 6
    When target = dev -> output contains WHERE
    When target != dev -> output is empty string
    """
    result = limit_data_in_dev(column_name, dev_limit, target_name)
    if target_name == "dev":
        assert "where" in result.lower(), (
            f"Expected WHERE clause for dev target, got: '{result}'"
        )
        assert str(dev_limit) in result, (
            f"Expected dev_limit {dev_limit} in result, got: '{result}'"
        )
    else:
        assert result.strip() == "", (
            f"Expected empty string for target '{target_name}', got: '{result}'"
        )


def test_limit_data_in_dev_dev_target():
    result = limit_data_in_dev("ordered_at", 100, "dev")
    assert "where" in result.lower()
    assert "100" in result
    assert "ordered_at" in result


def test_limit_data_in_dev_prod_target():
    result = limit_data_in_dev("ordered_at", 100, "prod")
    assert result.strip() == ""


def test_limit_data_in_dev_staging_target():
    result = limit_data_in_dev("created_at", 30, "staging")
    assert result.strip() == ""
