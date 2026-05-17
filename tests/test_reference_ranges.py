import pytest
from modules.reference_ranges import flag_value, get_range


def test_wbc_normal():
    assert flag_value("6690-2", 7.0, "M") == "normal"

def test_wbc_critical_high():
    assert flag_value("6690-2", 31.0, "M") == "critical"

def test_wbc_critical_low():
    assert flag_value("6690-2", 1.9, "M") == "critical"

def test_wbc_abnormal_high():
    # 12.0 is above 11.0 reference but below 30.0 critical
    assert flag_value("6690-2", 12.0, "M") == "abnormal"

def test_hemoglobin_male_normal():
    assert flag_value("718-7", 15.0, "M") == "normal"

def test_hemoglobin_female_normal():
    assert flag_value("718-7", 14.0, "F") == "normal"

def test_hemoglobin_female_low_abnormal():
    # 11.5 is below female lower bound (12.0) but above critical (7.0)
    assert flag_value("718-7", 11.5, "F") == "abnormal"

def test_hemoglobin_male_below_female_range():
    # 12.5 is in female normal (12–16) but below male lower (13.5)
    assert flag_value("718-7", 12.5, "M") == "abnormal"

def test_hemoglobin_critical_low():
    assert flag_value("718-7", 6.5, "F") == "critical"

def test_hemoglobin_critical_high():
    assert flag_value("718-7", 21.0, "M") == "critical"

def test_potassium_critical_high():
    assert flag_value("2823-3", 6.5, "M") == "critical"

def test_potassium_critical_low():
    assert flag_value("2823-3", 2.8, "F") == "critical"

def test_potassium_normal():
    assert flag_value("2823-3", 4.0, "M") == "normal"

def test_creatinine_male_normal():
    assert flag_value("38483-4", 1.0, "M") == "normal"

def test_creatinine_female_high_abnormal():
    # 1.1 is above female upper (1.04) but below critical (10.0)
    assert flag_value("38483-4", 1.1, "F") == "abnormal"

def test_creatinine_critical_high():
    assert flag_value("38483-4", 11.0, "M") == "critical"

def test_creatinine_no_critical_low():
    # Creatinine has (None, 10.0) — no critical low; below male range is just abnormal
    assert flag_value("38483-4", 0.5, "M") == "abnormal"

def test_hdl_male_low_abnormal():
    # HDL below 40 for male is abnormal (higher is better — lower bound only)
    assert flag_value("2085-9", 35.0, "M") == "abnormal"

def test_hdl_male_normal():
    assert flag_value("2085-9", 45.0, "M") == "normal"

def test_unknown_loinc_returns_normal():
    assert flag_value("99999-9", 100.0, "M") == "normal"

def test_get_range_gender_specific_male():
    assert get_range("718-7", "M") == (13.5, 17.5)

def test_get_range_gender_specific_female():
    assert get_range("718-7", "F") == (12.0, 16.0)

def test_get_range_non_gender_specific():
    assert get_range("6690-2", "M") == (4.5, 11.0)
    assert get_range("6690-2", "F") == (4.5, 11.0)

def test_get_range_unknown_loinc():
    assert get_range("99999-9", "M") is None
