#!/usr/bin/env python3
"""Inspect chemical process data for modeling preparation.

The script creates a first-pass inventory for process tags, lab components,
candidate units, data quality risks, and confirmation questions.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pd = None


COMPONENT_PATTERNS = [
    "AA",
    "nBA",
    "NBA",
    "BuOH",
    "BSA",
    "H2O",
    "水",
    "丁醇",
    "丙烯酸",
    "硫酸",
    "催化剂",
]


ROLE_PATTERNS = [
    ("time", ["timestamp", "datetime", "date", "time", "时间", "日期"]),
    ("temperature", ["温度", "temp", "ti", "tic"]),
    ("pressure", ["压力", "pressure", "pi", "pic"]),
    ("level", ["液位", "level", "li", "lic"]),
    ("flow", ["流量", "进料量", "回收量", "回流量", "采出", "出料", "flow", "fi", "fic"]),
    ("composition", ["lab", "lims", "化验", "浓度", "含量", "组分", "composition", "content"]),
    ("catalyst", ["催化剂", "catalyst"]),
    ("recycle", ["回收", "回流", "recycle", "reflux"]),
    ("feed", ["进料", "fresh", "feed"]),
    ("output", ["出料", "采出", "product", "bottom", "top", "塔底", "塔顶"]),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", nargs="+", required=True, help="Input files or directories.")
    parser.add_argument("--output-dir", required=True, help="Directory for JSON and Markdown outputs.")
    parser.add_argument("--sheet", default=None, help="Optional Excel sheet name.")
    parser.add_argument("--max-rows", type=int, default=200_000, help="Rows to inspect per table.")
    parser.add_argument("--encoding", default="utf-8-sig", help="CSV encoding for stdlib fallback.")
    return parser.parse_args()


def discover_files(paths: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for raw in paths:
        path = Path(raw).expanduser()
        if path.is_dir():
            for suffix in ("*.csv", "*.tsv", "*.xlsx", "*.xls", "*.parquet"):
                files.extend(sorted(path.rglob(suffix)))
        elif path.is_file():
            files.append(path)
    return files


def read_table(path: Path, sheet: str | None, max_rows: int, encoding: str) -> list[dict[str, Any]]:
    if pd is not None:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            df = pd.read_csv(path, nrows=max_rows)
        elif suffix == ".tsv":
            df = pd.read_csv(path, sep="\t", nrows=max_rows)
        elif suffix in {".xlsx", ".xls"}:
            df = pd.read_excel(path, sheet_name=sheet or 0, nrows=max_rows)
        elif suffix == ".parquet":
            df = pd.read_parquet(path)
            if len(df) > max_rows:
                df = df.head(max_rows)
        else:
            raise ValueError(f"Unsupported file suffix: {path.suffix}")
        df.columns = [str(c) for c in df.columns]
        return df.to_dict(orient="records")

    if path.suffix.lower() not in {".csv", ".tsv"}:
        raise RuntimeError("pandas is required for Excel or Parquet inputs.")
    dialect = "excel-tab" if path.suffix.lower() == ".tsv" else "excel"
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle, dialect=dialect)
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            rows.append(dict(row))
    return rows


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if math.isnan(value) if isinstance(value, float) else False:
            return None
        return float(value)
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null", "nat"}:
        return None
    text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    values = sorted(values)
    pos = (len(values) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return values[lo]
    return values[lo] + (values[hi] - values[lo]) * (pos - lo)


def infer_roles(name: str) -> list[str]:
    lower = name.lower()
    tokens = [t for t in re.split(r"[^a-z0-9]+", lower) if t]

    def matches(pattern: str) -> bool:
        p = pattern.lower()
        if any(ord(ch) > 127 for ch in pattern):
            return pattern in name
        if len(p) <= 3:
            return p in tokens
        return p in lower

    roles = []
    for role, patterns in ROLE_PATTERNS:
        if any(matches(p) for p in patterns):
            roles.append(role)
    composition_context = any(marker in lower or marker in name for marker in ["lab", "lims", "online", "化验", "组分", "浓度", "含量"])
    if composition_context and any(p.lower() in lower or p in name for p in COMPONENT_PATTERNS):
        if "composition" not in roles:
            roles.append("composition")
    return roles or ["unknown"]


def infer_unit(role: str, stats: dict[str, Any]) -> tuple[str, str]:
    p05 = stats.get("p05")
    p95 = stats.get("p95")
    min_v = stats.get("min")
    max_v = stats.get("max")
    if role == "temperature":
        return "degC or process temperature unit", "name-pattern"
    if role == "pressure":
        return "pressure unit unknown; confirm kPa/MPa/bar/gauge/absolute", "name-pattern"
    if role == "level":
        if min_v is not None and max_v is not None and -5 <= min_v <= 105 and -5 <= max_v <= 105:
            return "% or level engineering unit; confirm", "range"
        return "level engineering unit unknown", "name-pattern"
    if role == "flow":
        return "mass/volume/molar flow unknown; kg/h common but must confirm", "name-pattern"
    if role == "composition":
        if min_v is not None and max_v is not None and 0 <= min_v and max_v <= 100:
            return "percentage-like composition; confirm mass% vs mol%", "range"
        if p05 is not None and p95 is not None and 0 <= p05 and p95 <= 1.2:
            return "fraction-like composition; confirm mass fraction vs mole fraction", "range"
        return "composition/concentration basis unknown", "name-pattern"
    if role == "time":
        return "timestamp/datetime", "name-pattern"
    return "unknown", "insufficient-evidence"


def summarize_column(rows: list[dict[str, Any]], column: str) -> dict[str, Any]:
    total = len(rows)
    raw_values = [row.get(column) for row in rows]
    non_missing = [v for v in raw_values if v is not None and str(v).strip() not in {"", "nan", "NaN", "None"}]
    numeric = [x for x in (to_float(v) for v in raw_values) if x is not None]
    stats: dict[str, Any] = {
        "column": column,
        "rows": total,
        "non_null": len(non_missing),
        "missing_pct": round((1 - len(non_missing) / total) * 100, 3) if total else None,
        "unique_count": len(set(map(str, non_missing[:10_000]))),
        "numeric_count": len(numeric),
        "is_numeric": len(numeric) >= max(3, int(0.7 * len(non_missing))) if non_missing else False,
    }
    if numeric:
        stats.update(
            {
                "min": min(numeric),
                "p05": quantile(numeric, 0.05),
                "median": statistics.median(numeric),
                "p95": quantile(numeric, 0.95),
                "max": max(numeric),
                "negative_count": sum(1 for x in numeric if x < 0),
                "zero_count": sum(1 for x in numeric if x == 0),
            }
        )
    roles = infer_roles(column)
    stats["roles"] = roles
    stats["unit_hypothesis"], stats["unit_evidence"] = infer_unit(roles[0], stats)
    return stats


def time_candidates(columns: list[str]) -> list[str]:
    patterns = ["time", "date", "datetime", "timestamp", "时间", "日期"]
    return [c for c in columns if any(p in c.lower() or p in c for p in patterns)]


def component_groups(columns: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for col in columns:
        lower = col.lower()
        composition_context = any(
            marker in lower or marker in col
            for marker in ["lab", "lims", "online", "化验", "组分", "浓度", "含量"]
        )
        if not composition_context:
            continue
        if not any(p.lower() in col.lower() or p in col for p in COMPONENT_PATTERNS):
            continue
        parts = re.split(r"[_\-.]", col)
        key = "_".join(parts[:-1]) if len(parts) > 1 else "components"
        groups[key].append(col)
    return {k: v for k, v in groups.items() if len(v) >= 3}


def summarize_component_sums(rows: list[dict[str, Any]], groups: dict[str, list[str]]) -> list[dict[str, Any]]:
    summaries = []
    for group, cols in groups.items():
        sums = []
        for row in rows:
            vals = [to_float(row.get(c)) for c in cols]
            vals = [v for v in vals if v is not None]
            if len(vals) >= 3:
                sums.append(sum(vals))
        if not sums:
            continue
        median_sum = statistics.median(sums)
        near_100 = 95 <= median_sum <= 105
        near_1 = 0.95 <= median_sum <= 1.05
        summaries.append(
            {
                "group": group,
                "columns": cols,
                "rows_checked": len(sums),
                "median_sum": median_sum,
                "p05_sum": quantile(sums, 0.05),
                "p95_sum": quantile(sums, 0.95),
                "inference": (
                    "percentage-like composition; confirm mass% vs mol%"
                    if near_100
                    else "fraction-like composition; confirm mass fraction vs mole fraction"
                    if near_1
                    else "components do not sum to 100 or 1; may be incomplete or concentration-based"
                ),
            }
        )
    return summaries


def confirmation_items(column_stats: list[dict[str, Any]], component_sums: list[dict[str, Any]]) -> list[dict[str, str]]:
    items = [
        {
            "priority": "P0",
            "question": "确认目标量的系统边界、分子、分母、单位和时间窗口。",
            "why": "边界和定义决定哪些进料、回收、出料、损失和累积项进入公式。",
        }
    ]
    if component_sums:
        items.append(
            {
                "priority": "P0",
                "question": "确认实验室/组分数据是质量百分数、摩尔百分数、质量分数、摩尔分数还是浓度。",
                "why": "不同基准会给出不同的组分摩尔流，直接影响转化率、收率和物料衡算。",
            }
        )
    if any("flow" in s["roles"] for s in column_stats):
        items.append(
            {
                "priority": "P0",
                "question": "确认所有流量位号的单位和物流方向，尤其是回收、回流、采出、排放、废水、塔顶和塔底物流。",
                "why": "未知流量和边界穿越物流会改变总质量守恒和组分守恒。",
            }
        )
    if any(s.get("negative_count", 0) for s in column_stats if s.get("is_numeric")):
        items.append(
            {
                "priority": "P1",
                "question": "解释负值位号是否为仪表噪声、符号约定、停工段或真实反向流。",
                "why": "负值会影响累计量、回归样本和质量平衡。",
            }
        )
    if any("lab" in s["column"].lower() or "化验" in s["column"] for s in column_stats):
        items.append(
            {
                "priority": "P1",
                "question": "确认实验室样品位置、采样频率、结果发布时间和是否存在分析滞后。",
                "why": "实验室数据常与实时过程位号存在时间错位。",
            }
        )
    items.append(
        {
            "priority": "P2",
            "question": "补充关键位号的长描述、DCS/PI单位和异常工况标记。",
            "why": "有助于减少弱推断并提升后续图表和模型解释性。",
        }
    )
    return items


def format_number(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def write_markdown(summary: dict[str, Any], output_path: Path) -> None:
    lines = ["# Data Precheck", ""]
    for table in summary["tables"]:
        lines.extend(
            [
                f"## {table['file']}",
                "",
                f"- Rows inspected: {table['rows']}",
                f"- Columns: {table['columns_count']}",
                f"- Time candidates: {', '.join(table['time_candidates']) or 'none'}",
                "",
                "### Column Summary",
                "",
                "| column | roles | missing_pct | min | median | max | unit_hypothesis | evidence |",
                "|---|---|---:|---:|---:|---:|---|---|",
            ]
        )
        for stat in table["column_stats"]:
            lines.append(
                "| {column} | {roles} | {missing_pct} | {min} | {median} | {max} | {unit} | {evidence} |".format(
                    column=stat["column"],
                    roles=", ".join(stat["roles"]),
                    missing_pct=format_number(stat.get("missing_pct")),
                    min=format_number(stat.get("min")),
                    median=format_number(stat.get("median")),
                    max=format_number(stat.get("max")),
                    unit=stat.get("unit_hypothesis", ""),
                    evidence=stat.get("unit_evidence", ""),
                )
            )
        if table["component_sums"]:
            lines.extend(["", "### Component Sum Checks", "", "| group | columns | median_sum | inference |", "|---|---|---:|---|"])
            for item in table["component_sums"]:
                lines.append(
                    f"| {item['group']} | {', '.join(item['columns'])} | {format_number(item['median_sum'])} | {item['inference']} |"
                )
        lines.append("")
    lines.extend(["## 待确认 List", "", "| priority | question | why |", "|---|---|---|"])
    for item in summary["confirmation_items"]:
        lines.append(f"| {item['priority']} | {item['question']} | {item['why']} |")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def inspect_file(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    rows = read_table(path, args.sheet, args.max_rows, args.encoding)
    columns = list(rows[0].keys()) if rows else []
    column_stats = [summarize_column(rows, col) for col in columns]
    groups = component_groups(columns)
    component_sums = summarize_component_sums(rows, groups)
    return {
        "file": str(path),
        "rows": len(rows),
        "columns_count": len(columns),
        "time_candidates": time_candidates(columns),
        "column_stats": column_stats,
        "component_sums": component_sums,
    }


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    files = discover_files(args.input)
    if not files:
        raise SystemExit("No supported input files found.")

    tables = [inspect_file(path, args) for path in files]
    all_stats = [stat for table in tables for stat in table["column_stats"]]
    all_component_sums = [item for table in tables for item in table["component_sums"]]
    summary = {
        "inputs": [str(path) for path in files],
        "tables": tables,
        "confirmation_items": confirmation_items(all_stats, all_component_sums),
    }

    (output_dir / "inspection_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_markdown(summary, output_dir / "data_precheck.md")
    print(f"Wrote {output_dir / 'inspection_summary.json'}")
    print(f"Wrote {output_dir / 'data_precheck.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
