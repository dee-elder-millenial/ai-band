from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BUDGET_USD = 5.00
DEFAULT_USAGE_PATH = Path("state/api_usage.json")

# Prices are USD per 1M tokens. Keep these conservative and configurable; exact
# billing remains authoritative in the OpenAI dashboard.
MODEL_PRICES_PER_MILLION = {
    "gpt-5.4-mini": {"input": 0.75, "cached_input": 0.075, "output": 4.50},
}


@dataclass(frozen=True)
class BudgetStatus:
    path: Path
    budget_usd: float
    spent_usd: float
    remaining_usd: float
    call_count: int
    warning: str | None = None

    @property
    def exhausted(self) -> bool:
        return self.remaining_usd <= 0


def configured_budget_usd() -> float:
    raw = os.getenv("AI_BAND_API_BUDGET_USD")
    if not raw:
        return DEFAULT_BUDGET_USD
    return max(0.0, float(raw))


def configured_usage_path() -> Path:
    raw = os.getenv("AI_BAND_API_USAGE_PATH")
    return Path(raw) if raw else DEFAULT_USAGE_PATH


def read_usage(path: Path | None = None) -> dict[str, Any]:
    usage_path = path or configured_usage_path()
    if not usage_path.exists():
        return {"version": 1, "total_estimated_usd": 0.0, "calls": []}
    return json.loads(usage_path.read_text(encoding="utf-8-sig"))


def write_usage(data: dict[str, Any], path: Path | None = None) -> None:
    usage_path = path or configured_usage_path()
    usage_path.parent.mkdir(parents=True, exist_ok=True)
    usage_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def budget_status(path: Path | None = None, budget_usd: float | None = None) -> BudgetStatus:
    usage_path = path or configured_usage_path()
    budget = configured_budget_usd() if budget_usd is None else budget_usd
    data = read_usage(usage_path)
    spent = float(data.get("total_estimated_usd", 0.0))
    calls = data.get("calls", [])
    remaining = budget - spent
    warning = None
    if budget > 0 and remaining <= 0:
        warning = "AI Band estimated API budget is exhausted."
    elif budget > 0 and remaining <= budget * 0.10:
        warning = "AI Band estimated API budget is below 10%."
    return BudgetStatus(
        path=usage_path,
        budget_usd=budget,
        spent_usd=spent,
        remaining_usd=remaining,
        call_count=len(calls) if isinstance(calls, list) else 0,
        warning=warning,
    )


def estimate_response_cost_usd(model: str, usage: dict[str, Any]) -> float:
    prices = MODEL_PRICES_PER_MILLION.get(model)
    if not prices:
        return 0.0

    input_tokens = int(usage.get("input_tokens", 0) or 0)
    output_tokens = int(usage.get("output_tokens", 0) or 0)
    cached_tokens = _cached_input_tokens(usage)
    billable_input_tokens = max(0, input_tokens - cached_tokens)

    return (
        billable_input_tokens * prices["input"]
        + cached_tokens * prices["cached_input"]
        + output_tokens * prices["output"]
    ) / 1_000_000


def record_response_usage(
    *,
    model: str,
    usage: dict[str, Any],
    path: Path | None = None,
    cue_instruction: str = "",
) -> BudgetStatus:
    usage_path = path or configured_usage_path()
    data = read_usage(usage_path)
    calls = data.setdefault("calls", [])
    if not isinstance(calls, list):
        calls = []
        data["calls"] = calls

    cost = estimate_response_cost_usd(model, usage)
    calls.append(
        {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "estimated_usd": round(cost, 8),
            "usage": {
                "input_tokens": int(usage.get("input_tokens", 0) or 0),
                "output_tokens": int(usage.get("output_tokens", 0) or 0),
                "total_tokens": int(usage.get("total_tokens", 0) or 0),
                "cached_input_tokens": _cached_input_tokens(usage),
            },
            "cue": cue_instruction[:120],
        }
    )
    data["total_estimated_usd"] = round(float(data.get("total_estimated_usd", 0.0)) + cost, 8)
    write_usage(data, usage_path)
    return budget_status(usage_path)


def _cached_input_tokens(usage: dict[str, Any]) -> int:
    details = usage.get("input_tokens_details", {})
    if not isinstance(details, dict):
        return 0
    return int(details.get("cached_tokens", 0) or 0)


def format_budget_status(status: BudgetStatus) -> str:
    warning = f"\nWARNING: {status.warning}" if status.warning else ""
    return (
        f"AI Band estimated API spend: ${status.spent_usd:.4f} / ${status.budget_usd:.2f} "
        f"({max(0.0, status.remaining_usd):.4f} remaining, {status.call_count} calls).{warning}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Show AI Band's local estimated API usage.")
    parser.add_argument("--path", default=None, help="Usage ledger path. Defaults to AI_BAND_API_USAGE_PATH or state/api_usage.json.")
    parser.add_argument("--budget", type=float, default=None, help="Budget in USD. Defaults to AI_BAND_API_BUDGET_USD or 5.00.")
    args = parser.parse_args()

    path = Path(args.path) if args.path else None
    print(format_budget_status(budget_status(path=path, budget_usd=args.budget)))


if __name__ == "__main__":
    main()
