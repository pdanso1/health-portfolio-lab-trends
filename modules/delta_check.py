import pandas as pd
from config.lab_config import DELTA_RULES, LOINC_NAMES, DELTA_CRITICAL_LOINCS


def compute_delta_flags(patient_df: pd.DataFrame, loinc: str) -> list[dict]:
    """
    Compare consecutive results for a LOINC code and return delta check flags.
    patient_df must have columns: CODE, DATE (datetime), VALUE (float).
    """
    rule = DELTA_RULES.get(loinc)
    if rule is None:
        return []

    series = (
        patient_df[patient_df["CODE"] == loinc]
        .sort_values("DATE")[["DATE", "VALUE"]]
        .dropna()
    )
    if len(series) < 2:
        return []

    rows = series.to_dict("records")
    flags = []

    for i in range(1, len(rows)):
        prev, curr = rows[i - 1], rows[i]
        prev_val, curr_val = float(prev["VALUE"]), float(curr["VALUE"])

        if rule["type"] == "absolute":
            delta = abs(curr_val - prev_val)
            triggered = delta >= rule["threshold"]
        else:  # percent
            if prev_val == 0:
                continue
            pct = abs((curr_val - prev_val) / prev_val) * 100
            triggered = pct >= rule["threshold"]
            delta = pct

        if not triggered:
            continue

        direction = "increased" if curr_val > prev_val else "dropped"
        severity = "critical" if loinc in DELTA_CRITICAL_LOINCS else "advisory"

        flags.append({
            "loinc": loinc,
            "name": LOINC_NAMES.get(loinc, loinc),
            "prev_date": prev["DATE"],
            "curr_date": curr["DATE"],
            "prev_val": prev_val,
            "curr_val": curr_val,
            "delta": delta,
            "direction": direction,
            "severity": severity,
            "meaning": rule["meaning"],
        })

    return flags
