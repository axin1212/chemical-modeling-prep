# Formula Patterns

Use these patterns as starting points. Adapt them to the confirmed process boundary and target definition.

## Notation

| symbol | meaning |
|---|---|
| `F` | total mass flow, kg/h unless otherwise stated |
| `V` | volumetric flow |
| `w_i` | mass fraction of component i |
| `x_i` | mole fraction of component i |
| `C_i` | molar concentration of component i |
| `MW_i` | molecular weight of component i |
| `N_i` | molar flow of component i |
| `m_i` | mass flow of component i |

## Pure Component Feed

If stream `s` is pure component `i` and flow is mass flow:

```text
m_i,s = F_s
N_i,s = F_s / MW_i
```

## Mass Fraction Composition

If total flow is mass flow and composition is mass fraction:

```text
m_i,s = F_s * w_i
N_i,s = F_s * w_i / MW_i
```

If composition is mass percent:

```text
w_i = wt_percent_i / 100
```

## Mole Fraction or Mole Percent Composition

If total flow is mass flow and composition is mole fraction:

```text
MW_mix = sum(x_i * MW_i)
N_total,s = F_s / MW_mix
N_i,s = N_total,s * x_i
m_i,s = N_i,s * MW_i
```

If composition is mole percent:

```text
x_i = mol_percent_i / 100
```

## Molar Concentration

If composition is molar concentration and flow is volumetric:

```text
N_i,s = C_i * V_s
```

Make volume units consistent. If only mass flow is available, density may be needed.

## Total Mass Balance

For a selected boundary:

```text
dM_system/dt = sum(F_in) - sum(F_out) + sum(F_generated_by_mass) - sum(F_consumed_by_mass)
```

For most ordinary total mass balances, chemical reaction does not create or destroy total mass:

```text
dM_system/dt = sum(F_in) - sum(F_out)
```

If one outlet flow is unknown:

```text
F_unknown_out = sum(F_in) - sum(F_known_out) - dM_system/dt
```

For steady operation or negligible inventory change:

```text
F_unknown_out = sum(F_in) - sum(F_known_out)
```

Include purge, vent, wastewater, product, loss, and side-draw terms when they cross the boundary.

## Component Balance

For component `i`:

```text
dN_i/dt = sum(N_i,in) - sum(N_i,out) + generation_i - consumption_i
```

At steady state or over a time window with negligible accumulation:

```text
0 = sum(N_i,in) - sum(N_i,out) + generation_i - consumption_i
```

## Conversion

For reactant `A`:

```text
conversion_A = (N_A,in - N_A,out - dN_A,system/dt) / N_A,in
```

If accumulation is negligible:

```text
conversion_A = (N_A,in - N_A,out) / N_A,in
```

Clarify whether recycle is inside or outside the boundary. If recycle crosses the boundary, include its reactant inflow.

## Yield and Generation Rate

For product `P` from limiting reactant `A`:

```text
generation_P = sum(N_P,out) - sum(N_P,in) + dN_P,system/dt
yield_P_on_A = generation_P / (stoich_P_per_A * N_A,in)
```

If product is absent from feeds and accumulation is negligible:

```text
generation_P = sum(N_P,out)
```

## Selectivity

For product `P` relative to reactant `A` consumed:

```text
selectivity_P = generation_P / (stoich_P_per_A * A_consumed)
```

## Recovery

For component `i`:

```text
recovery_i = desired_output_N_i / total_input_N_i
```

or on mass basis:

```text
recovery_i = desired_output_m_i / total_input_m_i
```

State the basis.

## Loss Rate

For component `i`:

```text
loss_i = input_i - desired_output_i - known_recycle_i - known_byproduct_i - accumulation_i
loss_rate_i = loss_i / input_i
```

## Specific Consumption or Intensity

Examples:

```text
raw_material_consumption = feed_mass / product_mass
energy_intensity = utility_energy / product_mass
emission_intensity = pollutant_mass / product_mass
```

These are often business or operational metrics rather than reaction performance metrics.
