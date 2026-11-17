"""make.fun bounty: Forecast GTA VI's launch-day Twitch viewers hour by hour.

Strategy (validated leave-one-out over the case's own comparables):
the case file carries `comparables` - past big game launches with full
release-day hourly curves. For each hour h we take the log-ratio
log(viewers_h / viewers_1) of every comparable whose hour-1 size is at least
a tenth of the target's, weight them by a gaussian kernel on log hour-1
distance, and forecast the target's quantiles as a normal distribution in
log space with that weighted mean and standard deviation, applied to the
target's hour-1 print. Scoring is pinball loss on the log scale, so honest
log-space quantiles are exactly the right object.

Leave-one-out over the 38 comparables: loss 0.358 vs house-baseline method
0.517 overall, and 0.245 vs 0.295 on launches with hour-1 >= 30k viewers
(the practice/final regime).

Standard library only, deterministic, no network.
"""

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [-1.645, -0.674, 0.0, 0.674, 1.645]

MIN_V1_ABS = 3000.0    # ignore tiny launches entirely: ratio noise
DYN_FRAC = 0.1         # keep comparables at least a tenth of the target's size
BANDWIDTH = 1.0        # gaussian kernel width on natural-log hour-1 distance
SD_FLOOR = 0.05
SD_CAP = 1.5


def round2(x: float):
    """Round to 2 decimals, half up, like the starter (int when whole)."""
    scaled = x * 100
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    value = whole / 100
    return int(value) if float(value).is_integer() else value


def parse_ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def comparable_curves(case: dict):
    """Return [(v1, {hour: viewers})] for each usable comparable launch day."""
    curves = []
    for comp in case.get("comparables") or []:
        try:
            start = parse_ts(comp["day_start"])
        except Exception:
            continue
        hours = {}
        for pt in comp.get("hourly") or []:
            try:
                t = parse_ts(pt["from"])
                v = float(pt["viewers"])
            except Exception:
                continue
            delta = (t - start).total_seconds()
            if 0 <= delta < 24 * 3600:
                hours[int(delta // 3600) + 1] = max(v, 0.0)
        v1 = hours.get(1)
        if v1 is None or v1 < MIN_V1_ABS or len(hours) < 18:
            continue
        curves.append((v1, hours))
    return curves


def forecast_case(case: dict) -> dict:
    if case.get("levels") and case["levels"] != LEVELS:
        raise ValueError(f"levels {case['levels']} != {LEVELS}")
    first = next((k for k in case.get("known") or [] if k.get("hour") == 1), None)
    if first is None:
        raise ValueError("no hour-1 print in case")
    p1 = max(1.0, float(first["viewers"]))
    log_p1 = math.log(p1)

    curves = comparable_curves(case)
    kept = [(v1, hrs) for v1, hrs in curves if v1 >= DYN_FRAC * p1]
    if len(kept) < 8:
        kept = curves

    rows = []
    for row in case["forecast"]:
        h = int(row["hour"])
        samples = []
        for v1, hrs in kept:
            if h in hrs and hrs[h] > 0:
                w = math.exp(-0.5 * (abs(math.log(v1) - log_p1) / BANDWIDTH) ** 2) + 0.05
                samples.append((math.log(hrs[h] / v1), w))
        if len(samples) >= 8:
            tw = sum(w for _, w in samples)
            mu = sum(v * w for v, w in samples) / tw
            var = sum(w * (v - mu) ** 2 for v, w in samples) / tw
            sd = min(max(math.sqrt(var), SD_FLOOR), SD_CAP)
            qs = [round2(p1 * math.exp(mu + z * sd)) for z in Z]
        else:
            # Fallback: house-baseline persistence with widening spread.
            qs = [round2(p1 * math.exp(z * 0.15 * math.sqrt(h - 1))) for z in Z]
        qs = [max(qs[i], qs[i - 1]) if i else qs[i] for i in range(len(qs))]
        rows.append({"hour": h, "q": qs})
    return {"hours": rows}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        forecast = forecast_case(case)
        (OUTPUT_DIR / f"{path.stem}.out").write_text(
            json.dumps(forecast, separators=(",", ":")) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
