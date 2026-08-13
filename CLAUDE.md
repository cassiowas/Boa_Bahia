# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Boa Bahia is a demand forecasting project for two physical stores:

- **Butantã Shopping**
- **Shopping Metro Santa Cruz**

The goal is to predict product/sales demand for each store so that stock and
purchasing decisions can be planned ahead of time.

This repository is in its initial stage — the conventions below are the
agreed structure for organizing data, scripts, and outputs as the project is
built out. Follow them for any new script so results stay consistent and
discoverable across sessions.

## Stack

- Python for pipeline/production scripts.
- Jupyter notebooks for exploratory analysis and modeling experiments.

There is no build, lint, or test tooling configured yet. When dependencies
and tooling are introduced (e.g. `requirements.txt`/`pyproject.toml`, a
linter, a test runner), this file should be updated with the exact commands.

## Data conventions

Input data is kept in single files shared across both stores, not split into
per-store folders. Each file has a column identifying the store (e.g. `loja`)
with values distinguishing **Butantã Shopping** and **Shopping Metro Santa
Cruz**. Any script reading demand/sales data should filter on this column
rather than expecting separate per-store files.

## Output conventions

Every script must write its results under `outputs/`, namespaced by script
first, then by store:

```
outputs/<nome_do_script>/<loja>/
```

For example, a forecasting script named `forecast_demanda` would write
Butantã Shopping's results to `outputs/forecast_demanda/butanta_shopping/`
and Shopping Metro Santa Cruz's results to
`outputs/forecast_demanda/shopping_metro_santa_cruz/`.

When adding a new script, create its output subfolder following this
`<script>/<loja>` nesting rather than inventing a new layout.
