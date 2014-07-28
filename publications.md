---
layout: page
title: Rich Wareham's Publications
permalink: /publications/
theme: indigo
---

{% jsonball pubs from file publications.json %}

<section class="theme white bg fg">
  {% assign year = "" %}
  {% for pub in pubs %}

  {% capture pubyear %}{{ pub.timestamp | divided_by: 1000 | date: '%Y' }}{% endcapture %}
  {% if pubyear != year %}

  <h1>{{ pubyear }}</h1>

  {% endif %}
  {% assign year = pubyear %}

  {% if pub.type == 'article' %}
    <publication-record articleTitle="{{ pub.title }}"
      publicationTitle="{{ pub.publication }}" pagerange="{{ pub.pagerange }}"
      volume="{{ pub.volume }}" issue="{{ pub.issue }}" href="{{ pub.uri }}" issn="{{ pub.issn }}"
      year="{{ pub.timestamp | divided_by: 1000 | date: '%Y' }}">
    {% for c in pub.creators %}
    {% if c.name.family %}
    <publication-author given="{{ c.name.given }}" family="{{ c.name.family }}">
    </publication-author>
    {% endif %}
    {% endfor %}
    </publication-record>
  {% elsif pub.type == 'conference_item' %}
    <publication-record articleTitle="{{ pub.title }}"
      eventTitle="{{ pub.event_title }}" eventLocation="{{ pub.event_location }}"
      href="{{ pub.uri }}" issn="{{ pub.issn }}"
      year="{{ pub.timestamp | divided_by: 1000 | date: '%Y' }}">
    {% for c in pub.creators %}
    {% if c.name.family %}
    <publication-author given="{{ c.name.given }}" family="{{ c.name.family }}">
    </publication-author>
    {% endif %}
    {% endfor %}
    </publication-record>
  {% else %}
    <publication-record articleTitle="{{ pub.title }}"
      href="{{ pub.uri }}" issn="{{ pub.issn }}"
      year="{{ pub.timestamp | divided_by: 1000 | date: '%Y' }}">
    {% for c in pub.creators %}
    {% if c.name.family %}
    <publication-author given="{{ c.name.given }}" family="{{ c.name.family }}">
    </publication-author>
    {% endif %}
    {% endfor %}
    </publication-record>
  {% endif %}
  {% endfor %}
</section>
