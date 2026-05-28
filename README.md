# Open-Silicon MPW overview

> **Warning**
> Read this document carefully before starting the implementation.

## Overview

This repository aggregates production-ready IPs as submodules. IP development and
release preparation happen in standalone repositories. When ready, a submission request
is made to include the IP as a submodule under the relevant MPW category directory.

Four directory structures are available, corresponding to Analog, Digital, RF, and
Mixed-Signal design categories.

## Categories

Categories and subcategories are standardized. Select the correct subcategory before
generation and keep the category consistent with the repository placement under
`July-2026/<Category>`. Subcategories map to fixed abbreviations and those abbreviations
must be used in the top-level IP name and kept consistent with `doc/info.json`. If you
would like to add more subcategories or abbreviations, request them via a GitHub issue on
[Open-Silicon-MPW](https://github.com/IHP-GmbH/Open-Silicon-MPW).

See `IP-Categories.md` for the current category table.

## IP development process

See `IP-development-steps.md` for the full development steps.

## Submission process

See `Submission-process.md` for the full submission steps.
