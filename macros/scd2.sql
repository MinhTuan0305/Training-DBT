{#
  Macro: scd2_from_source
  Purpose: Build a Slowly Changing Dimension Type 2 query from a source relation.
  
  This macro expects a history-style input set where the same business key can appear
  multiple times over time, sorted by an effective-from column.

  Parameters:
    - source_relation (required): a ref(), source(), or CTE relation to read from
    - business_key (required): column name that identifies the entity being tracked
    - tracked_columns (required): list of columns to compare for change detection
    - effective_from_column (required): timestamp/date column used to order history
    - valid_from_column (optional, default='dbt_valid_from')
    - valid_to_column (optional, default='dbt_valid_to')
    - current_flag_column (optional, default='is_current')
    - change_hash_column (optional, default='scd2_change_hash')

  Output columns:
    - all columns from the source relation
    - change hash
    - dbt_valid_from / dbt_valid_to window
    - is_current flag

  Notes:
    - Consecutive rows with the same tracked values are collapsed into one version.
    - The current version gets a far-future valid_to value.
#}
{% macro scd2_from_source(
    source_relation,
    business_key,
    tracked_columns,
    effective_from_column,
    valid_from_column='dbt_valid_from',
    valid_to_column='dbt_valid_to',
    current_flag_column='is_current',
    change_hash_column='scd2_change_hash'
) %}

with source_data as (
    select
        *,
        md5(
            concat_ws(
                '||',
                {% for column_name in tracked_columns -%}
                    coalesce(cast({{ column_name }} as text), '__dbt_null__')
                    {%- if not loop.last %}, {% endif -%}
                {%- endfor %}
            )
        ) as {{ change_hash_column }},
        lag(
            md5(
                concat_ws(
                    '||',
                    {% for column_name in tracked_columns -%}
                        coalesce(cast({{ column_name }} as text), '__dbt_null__')
                        {%- if not loop.last %}, {% endif -%}
                    {%- endfor %}
                )
            )
        ) over (
            partition by {{ business_key }}
            order by {{ effective_from_column }}, {{ business_key }}
        ) as previous_{{ change_hash_column }},
        lead({{ effective_from_column }}) over (
            partition by {{ business_key }}
            order by {{ effective_from_column }}, {{ business_key }}
        ) as next_{{ valid_from_column }}
    from {{ source_relation }}
),

change_rows as (
    select
        *
    from source_data
    where previous_{{ change_hash_column }} is null
       or previous_{{ change_hash_column }} <> {{ change_hash_column }}
),

final as (
    select
        *,
        {{ effective_from_column }} as {{ valid_from_column }},
        coalesce(next_{{ valid_from_column }}, timestamp '9999-12-31 23:59:59') as {{ valid_to_column }},
        case when next_{{ valid_from_column }} is null then true else false end as {{ current_flag_column }}
    from change_rows
)

select
    *
from final
order by {{ business_key }}, {{ valid_from_column }}

{% endmacro %}
