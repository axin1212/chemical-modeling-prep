# Chemical Modeling Prep

`chemical-modeling-prep` is a Codex plugin that provides a skill for preparing chemical process targets before time-series modeling, soft-sensor modeling, or LLM-assisted process analysis.

The core idea is simple: do not start with model fitting. First make the chemical target physically calculable.

In many chemical process cases, the hard part is not choosing XGBoost, LSTM, or a large model. The hard part is answering questions like:

- What exactly is the target?
- What process boundary does it belong to?
- Which streams cross that boundary?
- Are lab components mass fraction, mole fraction, mass percent, mole percent, or concentration?
- Which tags represent fresh feed, recycle, reflux, product, purge, wastewater, vent, or inventory?
- Can the target be calculated from material balance, or is it only a proxy?

This skill turns raw process data and process discussion into a structured modeling prep pack.

## What It Produces

A full run should produce:

- Data inventory and first-pass process hypothesis.
- Prioritized confirmation list.
- Target definition table.
- Mermaid process boundary diagram.
- Tag and unit table.
- Combined stream/component ledger.
- Material-balance and target formulas.
- Formula computability grade.
- Missing-information list.
- Optional Plotly QC charts for important flows, components, ratios, and computed targets.

## When To Use

Use this skill when working on chemical process cases such as:

- Calculating conversion, yield, selectivity, recovery, loss rate, or generation rate.
- Building a soft sensor for a lab quality target.
- Preparing a target variable from historian tags and lab measurements.
- Checking whether a proposed target can be calculated from available tags.
- Clarifying material-balance logic before any modeling.
- Auditing whether a data science label is a true physical quantity or only a proxy.

It is especially useful when the inputs include CSV, Excel, or Parquet process data with mixed historian tags and lab analysis columns.

## Workflow

### 1. Inspect Data First

Before asking the process engineer broad questions, inspect the available files.

The skill looks for:

- Available process tags and lab columns.
- Candidate time columns and sampling intervals.
- Flow, temperature, pressure, level, catalyst, recycle, feed, output, and composition tags.
- Value ranges, missingness, negative values, constant segments, and obvious quality risks.
- Component groups that may share a composition basis.
- First-pass assumptions that need confirmation.

The goal is to reduce iteration count: ask fewer but better questions.

### 2. Create A Confirmation List

The confirmation list is prioritized:

- `P0`: blocks the formula or can materially change the result.
- `P1`: affects accuracy, alignment, or operating interpretation.
- `P2`: useful documentation, but not blocking.

Typical `P0` questions include:

- Is the composition basis mass percent or mole percent?
- Which streams cross the chosen system boundary?
- Are recycle and reflux streams internal or external to the target boundary?
- Is the unknown outlet flow measured, inferred, or missing?
- Is the target a conversion, yield, recovery, composition, loss rate, or proxy?

### 3. Define The Target

The skill forces target definition to be explicit:

| field | example |
|---|---|
| target name | nBA conversion, product recovery, impurity load |
| target type | measured, calculated, soft-measured, proxy |
| system boundary | reactor, tower, process section, whole unit |
| numerator | consumed reactant, generated product, recovered component |
| denominator | fresh feed, total feed, theoretical production |
| unit | %, kg/h, kmol/h, kg product/kg feed |
| time window | instantaneous, hourly, shift average, batch |

This avoids mixing different concepts under one name.

### 4. Build Boundary And Ledger

The process boundary is represented as a Mermaid diagram. Then the streams are organized in one stream/component ledger:

| stream | direction | flow tag | composition source | basis | known status |
|---|---|---|---|---|---|
| fresh feed | in | feed flow tag | pure or lab | kg/h, wt% | confirmed/inferred |
| recycle | in/out/internal | recycle tag | lab/assumption | unknown | needs confirmation |
| product | out | product flow tag | lab/online | wt%/mol% | confirmed/inferred |

This ledger is the bridge from raw tags to formulas.

### 5. Build Formula And Grade It

The skill converts all formula terms to a consistent basis.

For reaction targets, the preferred basis is molar flow:

```text
N_i = component molar flow of component i
```

For total mass balance, the preferred basis is mass flow:

```text
F_unknown_out = sum(F_in) - sum(F_known_out) - dM_system/dt
```

The final formula is graded:

| grade | meaning |
|---|---|
| A | directly calculable from confirmed tags and units |
| B | calculable with explicit bounded assumptions |
| C | approximation or proxy |
| D | not computable from current data |

## Plugin Usage

This repository is structured as a Codex plugin. The plugin manifest is:

```text
.codex-plugin/plugin.json
```

The included skill is:

```text
skills/chemical-modeling-prep/SKILL.md
```

In Codex, invoke it as:

```text
$chemical-modeling-prep
```

Example prompt:

```text
Use $chemical-modeling-prep to inspect these process data files, clarify the target formula, and prepare a confirmation list before modeling.
```

## Local Update Behavior

Local edits are not automatically reflected in an already installed Codex plugin.

There are three separate states:

- The local repository files.
- The GitHub repository after `git push`.
- The plugin version currently cached by Codex.

If you update this repository locally:

1. Commit the change.
2. Push it to GitHub if you want the remote repo updated.
3. If Codex has the plugin installed, update the plugin cachebuster and reinstall it.
4. Start a new Codex thread to load the updated plugin.

For local plugin development, use the plugin creator helper:

```bash
python3 /Users/yangyifang/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py \
  /Users/yangyifang/supcon/playground/data/20260615_BASF/chemical-modeling-prep
```

Then reinstall the plugin from the marketplace that points to your local plugin source, and open a new thread. This cachebuster step exists because Codex intentionally caches installed plugins by version.

If you installed the plugin from GitHub, local edits do not reach that installation until you commit, push, and reinstall or update the plugin from the remote source.

## Data Inspection Script

The repository includes a helper script:

```bash
python skills/chemical-modeling-prep/scripts/inspect_process_data.py \
  --input /path/to/process_data.csv \
  --output-dir /path/to/output_dir
```

It can inspect CSV, TSV, Excel, and Parquet files. Excel and Parquet support require `pandas` plus the relevant optional engines such as `openpyxl` or `pyarrow`.

Outputs:

- `inspection_summary.json`
- `data_precheck.md`

Example:

```bash
python skills/chemical-modeling-prep/scripts/inspect_process_data.py \
  --input ./aligned_csv/R4000_series_aligned.csv \
  --output-dir ./chemical_modeling_prep_outputs
```

The script is intentionally conservative. It generates hypotheses, not final truth. For example, if several lab components sum to about 100, it will say “percentage-like composition” and still ask whether the basis is mass percent or mole percent.

## Repository Structure

```text
.
├── .codex-plugin/
│   └── plugin.json
├── README.md
└── skills/
    └── chemical-modeling-prep/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        ├── references/
        │   ├── formula-patterns.md
        │   ├── output-template.md
        │   ├── risk-grading.md
        │   ├── unit-inference.md
        │   └── workflow.md
        └── scripts/
            └── inspect_process_data.py
```

## Key References

- `skills/chemical-modeling-prep/references/workflow.md`: full staged workflow.
- `skills/chemical-modeling-prep/references/output-template.md`: standard report layout.
- `skills/chemical-modeling-prep/references/unit-inference.md`: rules for unit and basis inference.
- `skills/chemical-modeling-prep/references/formula-patterns.md`: material-balance and target formulas.
- `skills/chemical-modeling-prep/references/risk-grading.md`: confirmation priority and computability grading.

## Design Principles

- Data-first, but not data-only.
- Boundary before formula.
- Formula before model.
- Molar basis for reaction performance.
- Mass basis for total material balance.
- Explicit assumptions over silent inference.
- Confirmation questions should be specific and tied to formula terms.

## Example Chemical Questions It Helps With

For a reactor/tower system:

- How should conversion be calculated if fresh feed, recycle, reflux, bottom output, top output, and lab compositions are all involved?
- Can bottom flow be inferred by total mass balance?
- Should recycle be included in the denominator?
- Is a lab value a mass fraction, mole fraction, or concentration?
- Which missing stream prevents a physical conversion calculation?

For a product purification section:

- Is the target product recovery, product purity, impurity load, or yield?
- Which streams should be counted as product, recycle, purge, or loss?
- Can product loss be calculated from existing tags, or only approximated?

## Limits

This skill does not replace a process engineer, tag dictionary, PFD, P&ID, or LIMS documentation.

It is a structured preparation workflow. It helps Codex ask better questions, expose assumptions, and avoid building a model on a poorly defined target.
