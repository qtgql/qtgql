{% if context.selections or context.choices %}qtgql::SelectionsConfig(
    selections={
        {% for name, selection in context.selections.items() %}
        "👉name👈" : {%if selection %} 👉selection👈 {% else %} {} {% endif %},{% endfor %}
    },
{% if context.choices %}
choices={
{% for choice_name, selections in context.choices.items() %}
    "👉choice_name👈": SelectionConfig(selections={
                       {% for field_name, inner_template in selections.items() %} "👉field_name👈": 👉inner_template👈, {% endfor %}
}),
{% endfor %}
}
{% endif %}
)
{% endif %}