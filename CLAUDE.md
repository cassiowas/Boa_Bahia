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

- Python for pipeline/production scripts, kept in `scripts/`.
- Jupyter notebooks (`notebooks/`) for exploratory analysis and modeling experiments.
- Dependencies are listed in `requirements.txt` (currently just `requests`).
  Install with `pip install -r requirements.txt`. Run a script with
  `python scripts/<nome_do_script>.py`.

There is no lint or test tooling configured yet. When it's introduced, this
file should be updated with the exact commands.

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

## Scripts

### `scripts/coleta_temperatura_feriados.py`

Collects daily local temperature and holiday calendars for both stores.

- **Temperature**: fetched from the Open-Meteo Historical Weather API
  (free, no API key) using each store's approximate lat/long. Both stores
  are in the city of São Paulo, so coordinates differ only slightly
  (Butantã district vs. the Santa Cruz metro station area).
- **Holidays**: computed locally (no network dependency, no external
  holiday library) and classified as `nacional`, `regional` (state of São
  Paulo), or `local` (municipality of São Paulo, since both stores sit in
  the same city). Movable feasts (Carnaval, Sexta-feira Santa, Corpus
  Christi) are derived from the Easter date via the Gauss/Meeus algorithm.
  Dia da Consciência Negra (Nov 20) is classified `local` before 2024 and
  `nacional` from 2024 onward, since it became a federal holiday that year
  (Lei 14.759/2023).
- Run with `python scripts/coleta_temperatura_feriados.py [--inicio AAAA-MM-DD] [--fim AAAA-MM-DD]`
  (defaults to the last 2 years). Writes to
  `outputs/coleta_temperatura_feriados/<loja>/temperatura.csv` and
  `.../feriados.csv` per the output convention above.
