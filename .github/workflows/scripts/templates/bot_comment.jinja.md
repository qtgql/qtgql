<!-- ID: 878ae1db-766f-49c7-a1a8-59f7be1fee8f -->
### Release Notes
{% if context.release_context.success -%}
{{context.release_context.content}}
{% else %}
**Please provide a RELEASE.md file in the project root.**  
Here is an example format:
```md
Release type: <patch/minor/major>

<describe your changes here...>
```
{% endif %}
### Status of codegen testcases implementation
| TestCase         | Has implementation? |
| -----------------|---------------------|
{%for tc in context.testcases_context.testcases-%}
|  {{ tc.test.test_name }} | {{ tc.status }} |
{% endfor -%}

### Summary 
{{ context.testcases_context.summery }}