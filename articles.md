---
layout: page
title: Testing
permalink: /articles/
theme: blue
---

Hello

<ul>
  {% for post in site.posts %}
    <li>
      {{ post.date | date: "%F" }} <a href="{{ post.url }}">{{ post.title }}</a>
    </li>
  {% endfor %}
</ul>
