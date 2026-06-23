# Chemical Modeling Prep Workflow

This workflow is for chemical process cases where the hard part is not model fitting, but making the target calculation physically defensible.

## Stage 0: Data-First Inventory

When data files are available, inspect them before asking the user questions.

Capture:

- File list, sheet list, row counts, column counts, time column candidates, sampling interval candidates.
- Raw process tags and lab component columns.
- Candidate tag roles: fresh feed, recycle, reflux, product, purge, waste, catalyst, temperature, pressure, level, lab composition, online analyzer, utility, control output.
- Candidate units and value ranges.
- Data quality: missingness, constants, negative values, spikes, time gaps, duplicate timestamps, implausible values.
- Component groups that may share a composition basis.
- A first-pass process hypothesis: likely equipment, likely inlet streams, outlet streams, recycle streams, and lab measurement locations.

Output a “待确认 list” at the end of Stage 0. The list should be comprehensive enough that the next user iteration can resolve most high-risk uncertainties at once.

## Stage 1: Confirmation Package

Before asking the user, convert the data findings into a prioritized confirmation package.

Use:

- P0: blocks the target calculation or can flip the result materially.
- P1: affects precision, alignment, or interpretation but may allow a bounded approximation.
- P2: useful documentation or polish, not blocking.

Ask for confirmations in grouped themes:

- Target definition and system boundary.
- Unit basis and component basis.
- Stream direction and boundary crossing.
- Unknown flow, purge, loss, and accumulation terms.
- Lab sample location, sampling lag, and update frequency.
- Tag documentation and abnormal operating periods.

## Stage 2: Target Definition

Make the target general and explicit. Do not assume every chemical target is a conversion rate.

Clarify:

- What physical or business quantity the target represents.
- Which equipment, process section, or system boundary it belongs to.
- Which stream, material state, or quality measurement it corresponds to.
- Whether it is measured, calculated, soft-measured, or a proxy indicator.
- Its numerator, denominator, unit, and time window.
- Whether current tags can compute it directly, compute it with assumptions, approximate it, or only support predictive modeling.

Common chemical targets include composition, conversion, yield, selectivity, generation rate, recovery, impurity load, loss rate, emission load, energy intensity, raw-material consumption, catalyst consumption, and quality index.

## Stage 3: Process Boundary Diagram

Draw a Mermaid diagram before finalizing formulas.

The diagram should show:

- Chosen system boundary.
- Fresh inputs.
- Recycles crossing the boundary.
- Internal recycles that should not be double-counted.
- Product, byproduct, purge, waste, vent, and wastewater outputs.
- Lab/sample points.
- Unknown streams and assumptions.

Use dashed edges for uncertain streams and annotate unknown flow or unknown composition.

## Stage 4: Tag and Unit Table

Create a table for every raw process tag and lab component used or likely relevant.

Recommended columns:

- `tag`
- `source_file_or_sheet`
- `role`
- `equipment_or_stream`
- `raw_unit`
- `inferred_unit`
- `basis`
- `value_range`
- `evidence`
- `status`
- `notes`

Statuses:

- Confirmed
- Inferred
- Weakly inferred
- Unknown
- Excluded

## Stage 5: Stream and Component Ledger

Build one combined ledger instead of separate disconnected lists.

Recommended columns:

- `stream`
- `direction`
- `crosses_boundary`
- `total_flow_tag`
- `total_flow_unit`
- `composition_source`
- `composition_basis`
- `components_available`
- `components_missing`
- `component_calculation`
- `known_or_unknown`
- `confirmation_needed`

This ledger is the bridge from tags to formulas.

## Stage 6: Material Balance and Target Formula

Choose a calculation basis first.

- Use mass flow for total mass balance.
- Use molar flow for reaction conversion, yield, selectivity, stoichiometry, and component generation/consumption.
- Use the same time basis for all flows, usually hourly flow.

For every component term, show:

- Total flow source.
- Composition source.
- Basis conversion.
- Molecular weight if molar flow is needed.
- Whether the stream enters, leaves, is generated, is consumed, or accumulates.

Unknown outlet flow may be calculated by mass balance:

```text
F_unknown_out = sum(F_in) - sum(F_known_out) - F_loss - dM_system/dt
```

Use the correct sign convention and adapt the formula if the unknown is an inlet or if accumulation is non-negligible.

## Stage 7: Computability and Risk Grade

Grade the target formula:

- A: Directly calculable from confirmed tags and confirmed units.
- B: Calculable with explicit, bounded assumptions.
- C: Approximation or proxy; useful for analysis but not a physical truth.
- D: Not computable from current data; missing tags or lab measurements are blocking.

State why the grade was assigned and what would upgrade it.

## Stage 8: Modeling Gate

Only after the target definition and formula are settled:

- Generate the target time series.
- Perform time alignment and resampling.
- Run quality checks and plots.
- Analyze lag relationships and candidate predictors.
- Train or evaluate models.

If the formula is grade C or D, avoid presenting model results as a true chemical target. Label them as proxy predictions or scenario analysis.
