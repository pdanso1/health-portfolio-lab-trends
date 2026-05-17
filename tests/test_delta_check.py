import pandas as pd
import pytest
from modules.delta_check import compute_delta_flags


def _df(loinc, dates, values):
    return pd.DataFrame({
        "CODE": loinc,
        "DATE": pd.to_datetime(dates),
        "VALUE": [float(v) for v in values],
    })


# --- Hemoglobin: absolute ≥2.0 g/dL ---

def test_hemoglobin_drop_flags():
    df = _df("718-7", ["2023-01-01", "2023-06-01"], [14.2, 11.4])
    flags = compute_delta_flags(df, "718-7")
    assert len(flags) == 1
    assert flags[0]["direction"] == "dropped"
    assert flags[0]["severity"] == "advisory"
    assert flags[0]["prev_val"] == 14.2
    assert flags[0]["curr_val"] == 11.4

def test_hemoglobin_rise_flags():
    df = _df("718-7", ["2023-01-01", "2023-06-01"], [10.0, 13.5])
    flags = compute_delta_flags(df, "718-7")
    assert len(flags) == 1
    assert flags[0]["direction"] == "increased"

def test_hemoglobin_small_change_no_flag():
    df = _df("718-7", ["2023-01-01", "2023-06-01"], [14.2, 13.1])
    assert compute_delta_flags(df, "718-7") == []

def test_hemoglobin_exactly_at_threshold_flags():
    df = _df("718-7", ["2023-01-01", "2023-06-01"], [14.0, 12.0])
    # Change of exactly 2.0 — should trigger (threshold is ≥2.0)
    assert len(compute_delta_flags(df, "718-7")) == 1

# --- Sodium: absolute ≥10, severity=critical ---

def test_sodium_drop_critical_severity():
    df = _df("2951-2", ["2023-01-01", "2023-01-03"], [140.0, 128.0])
    flags = compute_delta_flags(df, "2951-2")
    assert len(flags) == 1
    assert flags[0]["severity"] == "critical"

def test_sodium_small_change_no_flag():
    df = _df("2951-2", ["2023-01-01", "2023-01-03"], [140.0, 133.0])
    assert compute_delta_flags(df, "2951-2") == []

# --- Potassium: absolute ≥1.0, severity=critical ---

def test_potassium_flags():
    df = _df("2823-3", ["2023-01-01", "2023-01-02"], [4.5, 3.4])
    flags = compute_delta_flags(df, "2823-3")
    assert len(flags) == 1
    assert flags[0]["severity"] == "critical"

# --- Creatinine: percent ≥50% change ---

def test_creatinine_percent_flags():
    # 0.9 → 1.4 = 55.6% increase
    df = _df("38483-4", ["2023-01-01", "2023-02-01"], [0.9, 1.4])
    assert len(compute_delta_flags(df, "38483-4")) == 1

def test_creatinine_under_threshold_no_flag():
    # 0.9 → 1.3 = 44.4% increase
    df = _df("38483-4", ["2023-01-01", "2023-02-01"], [0.9, 1.3])
    assert compute_delta_flags(df, "38483-4") == []

def test_creatinine_decrease_flags():
    # 1.4 → 0.6 = 57% decrease — should also flag
    df = _df("38483-4", ["2023-01-01", "2023-02-01"], [1.4, 0.6])
    assert len(compute_delta_flags(df, "38483-4")) == 1

# --- WBC: percent ≥50% ---

def test_wbc_percent_flags():
    df = _df("6690-2", ["2023-01-01", "2023-02-01"], [5.0, 8.0])
    # 60% increase
    assert len(compute_delta_flags(df, "6690-2")) == 1

def test_wbc_under_threshold_no_flag():
    df = _df("6690-2", ["2023-01-01", "2023-02-01"], [5.0, 7.0])
    # 40% increase
    assert compute_delta_flags(df, "6690-2") == []

# --- HbA1c: absolute ≥1.5 ---

def test_hba1c_flags():
    df = _df("4548-4", ["2023-01-01", "2023-07-01"], [5.5, 7.2])
    assert len(compute_delta_flags(df, "4548-4")) == 1

def test_hba1c_no_flag():
    df = _df("4548-4", ["2023-01-01", "2023-07-01"], [5.5, 6.8])
    assert compute_delta_flags(df, "4548-4") == []

# --- Edge cases ---

def test_single_result_no_flag():
    df = _df("718-7", ["2023-01-01"], [14.0])
    assert compute_delta_flags(df, "718-7") == []

def test_no_rule_returns_empty():
    df = _df("39156-5", ["2023-01-01", "2023-06-01"], [25.0, 30.0])
    assert compute_delta_flags(df, "39156-5") == []

def test_multiple_flags_in_series():
    df = _df("718-7", ["2023-01-01", "2023-03-01", "2023-06-01"], [14.0, 11.0, 8.5])
    flags = compute_delta_flags(df, "718-7")
    assert len(flags) == 2

def test_flag_contains_required_keys():
    df = _df("718-7", ["2023-01-01", "2023-06-01"], [14.2, 11.4])
    flag = compute_delta_flags(df, "718-7")[0]
    for key in ("loinc", "name", "prev_date", "curr_date", "prev_val", "curr_val", "direction", "severity", "meaning"):
        assert key in flag, f"missing key: {key}"
