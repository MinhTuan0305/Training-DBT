{#
  Macro: cents_to_dollars
  Purpose: Converts a monetary value from cents (integer) to dollars (decimal).
           Handles NULL input gracefully — returns NULL if input is NULL.
  Parameters:
    - column_name (required): the column or expression containing the value in cents
    - precision (optional, default=2): number of decimal places to round to
  Example:
    {{ cents_to_dollars('amount_cents') }}
    -- compiles to: round(amount_cents / 100.0, 2)

    {{ cents_to_dollars('price_cents', 4) }}
    -- compiles to: round(price_cents / 100.0, 4)
#}
{% macro cents_to_dollars(column_name, precision=2) %}
    round({{ column_name }} / 100.0, {{ precision }})
{% endmacro %}
