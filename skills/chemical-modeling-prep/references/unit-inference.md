# Unit and Basis Inference

Unit inference is a hypothesis-generation step. It does not replace tag documentation or user confirmation.

## Evidence Hierarchy

Prefer evidence in this order:

1. Explicit unit metadata from historian, DCS, PI, LIMS, or workbook headers.
2. User or plant engineer confirmation.
3. Physical balance consistency across streams and components.
4. Component group sum checks.
5. Value range and process plausibility.
6. Tag name patterns.

Tag names alone are weak evidence.

## Composition Basis Rules

If component values sum to about 100, infer only that they are percentage-like. Do not conclude mass percent or mole percent without more evidence.

Distinguish:

- Mass fraction: `w_i`, kg component per kg mixture.
- Mole fraction: `x_i`, mol component per mol mixture.
- Mole percent: `100 * x_i`.
- Mass percent: `100 * w_i`.
- Molar concentration: `C_i`, mol per volume, such as mol/L or kmol/m3.
- Mass concentration: kg per volume, ppmw, ppmv, mg/L, etc.

`mol%` and molar concentration are not the same. `mol%` is a fraction of mixture moles. Molar concentration includes volume.

## Flow Unit Checks

Common flow units:

- kg/h, t/h: mass flow.
- kmol/h, mol/h: molar flow.
- m3/h, Nm3/h: volumetric flow.
- L/h: volumetric flow.

If a stream flow is used with composition, confirm whether the composition basis is compatible with the flow basis. Convert before component balances.

## Common Tag Role Patterns

Use these only as first-pass hints:

| pattern | likely role |
|---|---|
| `进料`, `feed`, `fresh` | input stream |
| `出料`, `采出`, `product`, `bottom`, `top` | output stream |
| `回收`, `回流`, `recycle`, `reflux` | recycle or reflux |
| `流量`, `flow`, `FI`, `FIC` | flow |
| `温度`, `temp`, `TI`, `TIC` | temperature |
| `压力`, `pressure`, `PI`, `PIC` | pressure |
| `液位`, `level`, `LI`, `LIC` | level or inventory proxy |
| `lab`, `LIMS`, `分析`, `化验` | lab measurement |
| `浓度`, `含量`, `composition`, `content` | composition or concentration |

## Range-Based Hints

Use ranges as plausibility checks, not proof:

- Temperature often falls in plausible process ranges such as -50 to 500 degC.
- Gauge pressure can be negative near vacuum; absolute pressure should not be negative.
- Level often appears as 0-100 percent or engineering-unit inventory.
- Composition percentage often falls in 0-100 and component groups may sum near 100.
- Mass flow tags should usually be non-negative during operation.
- Control valve opening or controller output often falls in 0-100 percent.

## Physical Consistency Checks

Use mass balance, component balance, and molecular weights to challenge units.

Examples:

- If lab components sum near 100 and total stream flow is kg/h, mass fraction gives direct component mass flow.
- If lab components are mole percent and total stream flow is kg/h, compute mixture molecular weight before component mass or molar flows.
- If values are called concentration but the available stream flow is kg/h, density or volume flow may be needed.
- If a calculated outlet flow becomes persistently negative, boundary, units, missing outlet terms, or accumulation assumptions are likely wrong.

## Confirmation Language

Use precise wording:

- “推断为质量分数，证据是……，仍需确认。”
- “只能判断为百分比组成，不能区分质量百分数和摩尔百分数。”
- “若为 mol%，则公式为……；若为 wt%，则公式为……；两者会导致不同摩尔流。”
