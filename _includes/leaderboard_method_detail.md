# {{ page.title }}

{% assign rows = site.data.leaderboard.methods | where: "llm_id", page.llm_id | where: "method_id", page.method_id %}
{% assign row = rows[0] %}

**Model name**: `{{ row.model_name }}`

**Average normalized reward (all benchmark instances)**: **{{ row.mean_ratio | round: 3 }}**

## By dataset family

| Family | Avg Normalized Reward |
|--------|-----------------------|
{% if row.by_family_mean_ratio %}
{% for fam in row.by_family_mean_ratio %}
| {{ fam[0] }} | {{ fam[1] | round: 3 }} |
{% endfor %}
{% else %}
| – | – |
{% endif %}

## By lead-time setting

| Lead time | Avg Normalized Reward |
|-----------|-----------------------|
{% if row.by_lead_mean_ratio %}
{% for lead in row.by_lead_mean_ratio %}
| {{ lead[0] }} | {{ lead[1] | round: 3 }} |
{% endfor %}
{% else %}
| – | – |
{% endif %}

Return to the [overall leaderboard]({{ '/leaderboard' | relative_url }}).

