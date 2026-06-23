---
name: chemical-modeling-prep
description: Prepare chemical process targets before time-series, soft-sensor, or large-model-assisted modeling. Use when Codex needs to inspect chemical/process data files, infer tag roles and units, clarify target definitions, build material-balance formulas, produce stream/component ledgers, create process boundary diagrams, and decide whether a target is computable before modeling.
---

# Chemical Modeling Prep

## Overview

Use this skill to do the engineering preparation before chemical process modeling. The goal is to turn raw process tags, lab data, and process knowledge into a defensible target definition, material-balance formula, tag/unit table, stream/component ledger, and prioritized confirmation list.

Do not jump directly into data modeling. First make the process boundary, units, streams, components, and target formula explicit.

## Quick Workflow

1. Inspect available data before asking questions.
   - If files are provided, run `scripts/inspect_process_data.py` on the CSV/XLSX/Parquet inputs.
   - Summarize available tags, likely time columns, candidate units, missingness, value ranges, lab components, possible stream roles, and obvious quality risks.
   - Produce a prioritized confirmation list from the data evidence.

2. Load the references needed for the task.
   - Use `references/workflow.md` for the full staged workflow.
   - Use `references/output-template.md` for the standard report shape.
   - Use `references/unit-inference.md` when inferring or challenging units.
   - Use `references/formula-patterns.md` when building material-balance or target formulas.
   - Use `references/risk-grading.md` when labeling assumptions and confirmation items.

3. Define the target generically.
   - Clarify the target name, system boundary, related stream/device state, measurement or calculation type, numerator, denominator, units, and time window.
   - Distinguish true physical targets from proxy metrics, concentration targets, performance indices, loss rates, recovery rates, or soft-sensor labels.

4. Build the process boundary and ledgers.
   - Draw a Mermaid boundary diagram with all known and suspected input, output, recycle, purge, side-draw, and accumulation terms.
   - Build one combined stream/component ledger: each stream, direction, flow tag, composition source, component basis, unit, known/unknown status, and confirmation need.

5. Draft formulas and grade computability.
   - Convert all component calculations to a common basis, usually molar flow for reaction targets and mass flow for total mass balance.
   - Show formulas for unknown flows that are inferred from mass conservation.
   - Grade each formula as directly calculable, calculable with assumptions, approximable, or not computable from current tags.

6. Gate modeling.
   - Only proceed to time-series modeling after the target can be computed or its proxy nature is explicitly accepted.
   - If the target cannot be computed, state the blocking missing tags or lab measurements and propose the minimum extra information needed.

## Script

Run the data inspection helper when raw data files are available:

```bash
python scripts/inspect_process_data.py \
  --input /path/to/process_data.csv \
  --output-dir /path/to/chemical_modeling_prep_outputs
```

The script writes:

- `inspection_summary.json`: machine-readable file, column, role, unit, and quality summaries.
- `data_precheck.md`: a first-pass Markdown analysis with candidate tags, inferred units, component checks, and confirmation items.

The script is an assistant, not a source of truth. Treat every unit and role inference as a hypothesis until confirmed by tag documentation, plant knowledge, or physical-balance checks.

## Required Outputs

For a full prep pass, produce these artifacts or sections:

- Data inventory and first-pass process hypothesis.
- Prioritized confirmation list before requesting user input.
- Target definition table.
- Mermaid process boundary diagram.
- Tag/unit table covering raw process tags and lab components.
- Combined stream/component ledger.
- Material-balance and target formulas with basis conversions.
- Formula computability grade and missing-information list.
- Optional Plotly QC charts for key flows, lab components, ratios, and computed targets.

## Guardrails

- Never infer mass fraction versus mole fraction from a column name alone.
- `mol%`, mole fraction, mass fraction, and molar concentration are different quantities.
- A component set summing to about 100 only proves a percentage-like composition; it does not prove mass basis or mole basis.
- For reaction targets, compute conversion, yield, selectivity, and generation rate on a molar basis unless the user explicitly defines a mass-based business metric.
- Recycle streams crossing the selected system boundary must be counted. Internal recycles inside the boundary must not be double-counted.
- Unknown outlet flow may be calculated by total mass balance only after boundary, accumulation, losses, purge, and measured outlet terms are explicit.
- Always label assumptions as confirmed, inferred, weakly inferred, or unknown.
