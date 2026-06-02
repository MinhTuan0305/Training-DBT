{#
  Macro: generate_schema_name
  Purpose: Overrides DBT's default schema naming behavior.
           If a custom schema name is provided, use it directly (trimmed).
           If no custom schema name is provided, fall back to the target schema.
  Parameters:
    - custom_schema_name: the custom schema name (can be none/null)
    - node: the DBT node object (required by DBT's macro signature, not used here)
  Example:
    -- In dbt_project.yml with +schema: staging
    -- target.schema = 'dbt_dev'
    -- Result: 'staging' (not 'dbt_dev_staging')

    -- Without +schema config
    -- target.schema = 'dbt_dev'
    -- Result: 'dbt_dev'
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
