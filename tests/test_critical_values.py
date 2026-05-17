import pytest
from modules.critical_values import check_critical


def test_hemoglobin_critical_low():
    result = check_critical("718-7", 6.5)
    assert result is not None
    assert result["direction"] == "low"
    assert result["name"] == "Hemoglobin"
    assert result["threshold"] == 7.0

def test_hemoglobin_critical_high():
    result = check_critical("718-7", 21.0)
    assert result is not None
    assert result["direction"] == "high"
    assert result["threshold"] == 20.0

def test_hemoglobin_not_critical():
    assert check_critical("718-7", 12.0) is None

def test_wbc_critical_low():
    result = check_critical("6690-2", 1.5)
    assert result["direction"] == "low"
    assert result["threshold"] == 2.0

def test_wbc_critical_high():
    result = check_critical("6690-2", 31.0)
    assert result["direction"] == "high"

def test_platelets_critical_low():
    result = check_critical("777-3", 40.0)
    assert result["direction"] == "low"
    assert result["threshold"] == 50.0

def test_potassium_critical_low():
    result = check_critical("2823-3", 2.9)
    assert result["direction"] == "low"

def test_potassium_critical_high():
    result = check_critical("2823-3", 6.2)
    assert result["direction"] == "high"

def test_sodium_critical_low():
    result = check_critical("2951-2", 124.0)
    assert result["direction"] == "low"

def test_sodium_critical_high():
    result = check_critical("2951-2", 156.0)
    assert result["direction"] == "high"

def test_glucose_critical_low():
    result = check_critical("2345-7", 45.0)
    assert result["direction"] == "low"

def test_glucose_critical_high():
    result = check_critical("2345-7", 501.0)
    assert result["direction"] == "high"

def test_creatinine_critical_high():
    result = check_critical("38483-4", 10.5)
    assert result["direction"] == "high"
    assert result["threshold"] == 10.0

def test_creatinine_no_critical_low():
    # Creatinine only has critical high (None, 10.0) — low value is not critical
    assert check_critical("38483-4", 0.1) is None

def test_no_critical_config_returns_none():
    # BMI has no critical values configured
    assert check_critical("39156-5", 50.0) is None

def test_result_contains_required_keys():
    result = check_critical("718-7", 6.0)
    for key in ("loinc", "name", "value", "direction", "threshold"):
        assert key in result, f"missing key: {key}"
    assert result["value"] == 6.0
    assert result["loinc"] == "718-7"
