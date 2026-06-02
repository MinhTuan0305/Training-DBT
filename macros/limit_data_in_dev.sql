{#
  Macro: limit_data_in_dev
  Purpose: Limits data volume in development environment by adding a WHERE clause
           that filters rows to only the most recent N days.
           In non-dev environments (prod, staging, ci), returns an empty string.
  Parameters:
    - column_name (required): the date/timestamp column to filter on
    - dev_limit (optional, default=100): number of days to look back in dev
  Example:
    {{ limit_data_in_dev('ordered_at') }}
    -- In dev:  WHERE ordered_at >= current_date - interval '100 days'
    -- In prod: (empty string)

    {{ limit_data_in_dev('created_at', 30) }}
    -- In dev:  WHERE created_at >= current_date - interval '30 days'
    -- In prod: (empty string)
#}
{% macro limit_data_in_dev(column_name, dev_limit=100) %}
    {% if target.name == 'dev' %}
        where {{ column_name }} >= current_date - interval '{{ dev_limit }} days'
    {% endif %}
{% endmacro %}
