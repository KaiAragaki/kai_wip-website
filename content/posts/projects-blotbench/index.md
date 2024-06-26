---
title: blotbench
tags:
  - projects
description: >-
  An R package with a Shiny helper app *inside*. Reproducibly edit western blots
  visually and easily.
---


[blotbench](https://kaiaragaki.github.io/blotbench/index.html) seeks to make editing and presenting Western blots easy and reproducible. It does this by providing a Shiny app within the package itself. This app serves as a rudimentary visual editor that will help you write the code you need to get the blots you see in the editor. You can then paste the output of this app (sent to your console) in to your code.

Additionally, blotbench provides a new object (a wb object) that can store row and column annotation. This information can be used to index your western blots much like you would index a data.frame - where rows represent different blots and columns represent the lanes of those blots. It can also automatically be used to produce annotated, publication ready images.

For more information on blotbench (and to see it in action), check out the [vignette](https://kaiaragaki.github.io/blotbench/articles/usage.html).
