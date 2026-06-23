# Risk and Confirmation Grading

Use grading to make uncertainty visible.

## Confirmation Priority

| priority | meaning | examples |
|---|---|---|
| P0 | Blocks the target formula or can materially flip the result | mass percent vs mole percent, system boundary, unknown outlet flow, recycle crossing boundary, target numerator/denominator |
| P1 | Affects accuracy, lag alignment, or operating interpretation | lab sampling delay, pressure unit, density assumption, abnormal period exclusion, resampling method |
| P2 | Useful context but not blocking | tag long names, display names, diagram polish, equipment notes |

## Formula Computability Grade

| grade | meaning | how to report |
|---|---|---|
| A | Directly calculable from confirmed tags, units, and formulas | “可直接计算” |
| B | Calculable with explicit bounded assumptions | “可计算，但依赖以下假设……” |
| C | Approximation or proxy, not a strict physical target | “可作为代理指标，不应当解释为真实物理量” |
| D | Not computable from current data | “当前数据不支持计算，缺少……” |

## Evidence Status

Use one of:

- Confirmed: stated by user, metadata, or reliable documentation.
- Inferred: supported by multiple consistent evidence sources.
- Weakly inferred: supported mainly by names or ranges.
- Unknown: no reliable evidence.
- Conflicting: evidence points to inconsistent interpretations.
- Excluded: reviewed and intentionally not used.

## Reporting Rules

- Put P0 items before P1/P2.
- Tie every confirmation question to the formula term it affects.
- If a question is not actionable, rewrite it until it is.
- Do not ask a broad “please confirm the process.” Ask for specific stream direction, unit basis, component basis, or boundary decisions.
- When a formula relies on assumptions, label each assumption and show how the result would change if the assumption is wrong.
