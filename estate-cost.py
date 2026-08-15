#!/usr/bin/env python3
"""estate_cost.py — a napkin-math cost model for the 2030 org's AI estate.

Run: python3 estate_cost.py
It contrasts the two ways an AI-native org pays for inference:
  (1) self-host on owned/reserved GPUs  -> amortized $/month, fixed
  (2) call a cloud API per token        -> variable $/month, scales with use

All prices are mid-2026 SNAPSHOTS (see AI_FACT_BRIEF). They move weekly.
Pin model IDs and re-check the vendor console before you quote a real bill.
"""

# ---- Inputs you change per design ----------------------------------------
MONTHLY_INPUT_TOKENS = 400_000_000      # 400M input tokens/month
MONTHLY_OUTPUT_TOKENS = 100_000_000     # 100M output tokens/month (output costs 4-8x)

# Per-1M-token snapshots, mid-2026 (USD). Pin model IDs in a real model.
API_PRICES = {
    "claude-haiku-4-5":  {"in": 1.0,  "out": 5.0},
    "claude-sonnet-4-6": {"in": 3.0,  "out": 15.0},
    "gpt-5.5":           {"in": 5.0,  "out": 30.0},
    "gpt-5.4":           {"in": 2.5, "out": 15.0},
    "gemini-3-flash":    {"in": 0.50, "out": 3.0},
}

# Self-host: one 8xH100 node, reserved. Illustrative all-in monthly cost.
SELFHOST_NODE_USD_PER_MONTH = 22_000    # reserved GPU node, amortized (illustrative)
SELFHOST_TOKENS_PER_MONTH = 1_500_000_000  # sustained throughput it can serve


def api_monthly_cost(model: str) -> float:
    p = API_PRICES[model]
    return (MONTHLY_INPUT_TOKENS / 1e6) * p["in"] + (MONTHLY_OUTPUT_TOKENS / 1e6) * p["out"]


def selfhost_cost_per_million() -> float:
    total = MONTHLY_INPUT_TOKENS + MONTHLY_OUTPUT_TOKENS
    return SELFHOST_NODE_USD_PER_MONTH / (total / 1e6)


if __name__ == "__main__":
    total_tokens = MONTHLY_INPUT_TOKENS + MONTHLY_OUTPUT_TOKENS
    print(f"Workload: {total_tokens/1e6:.0f}M tokens/month "
          f"({MONTHLY_INPUT_TOKENS/1e6:.0f}M in / {MONTHLY_OUTPUT_TOKENS/1e6:.0f}M out)\n")
    print("Per-token API (serverless, scales with use):")
    for model in API_PRICES:
        print(f"  {model:20s} ${api_monthly_cost(model):>12,.0f}/mo")
    print(f"\nSelf-host (reserved node, fixed):")
    print(f"  8xH100 node          ${SELFHOST_NODE_USD_PER_MONTH:>12,.0f}/mo "
          f"(headroom: {SELFHOST_TOKENS_PER_MONTH/total_tokens:.1f}x this workload)")
    print(f"  effective $/1M tokens at this volume: ${selfhost_cost_per_million():.2f}")
    print("\nRule of thumb (3rd-party, illustrative): reserved/self-host only wins")
    print("above high, SUSTAINED volume. Below it, pay-per-token is cheaper. Measure.")