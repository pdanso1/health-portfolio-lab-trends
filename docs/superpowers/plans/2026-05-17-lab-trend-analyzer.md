# Lab Trend Analyzer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Streamlit app that visualizes patient lab trends from SYNTHEA data with clinically accurate delta check logic, reference range interpretation, and Claude-generated narratives.

**Architecture:** Single-page Streamlit app with a sidebar patient selector; the patient's observations drive all panels. Pure-function business logic (reference ranges, delta check, critical values) lives in `modules/` with full unit test coverage. UI rendering is decoupled from logic so tests don't need Streamlit.

**Tech Stack:** Python 3.11+, Streamlit ≥1.32, Plotly ≥5.18, pandas ≥2.0, Anthropic SDK ≥0.25, pytest

---

## Data Source Locations

- `~/synthea_data/csv/csv/observations.csv` — `DATE, PATIENT, ENCOUNTER, CATEGORY, CODE, DESCRIPTION, VALUE, UNITS, TYPE`
- `~/synthea_data/csv/csv/patients.csv` — `Id, BIRTHDATE, DEATHDATE, FIRST, LAST, GENDER, ...`
- `~/synthea_data/csv/csv/conditions.csv` — `START, STOP, PATIENT, ENCOUNTER, SYSTEM, CODE, DESCRIPTION`
- Python: `/opt/anaconda3/bin/python`
- Port: `8502`
- Demo patient UUID: `f9ed1c66-904c-3c3f-0a50-0226629df9ff` (Lupe Pacocha, M, born 1938, 10 years of labs)

---

## File Map

```
health-portfolio-lab-trends/
├── app.py                          # Streamlit entry point — wires all modules
├── config/
│   └── lab_config.py               # All LOINC mappings, ref ranges, critical values, delta rules
├── data/
│   └── loader.py                   # Reads SYNTHEA CSVs, filters/cleans, caches with st.cache_data
├── modules/
│   ├── reference_ranges.py         # get_range(), flag_value() — pure functions
│   ├── critical_values.py          # check_critical() — pure function
│   ├── delta_check.py              # compute_delta_flags() — pure function
│   ├── patient_search.py           # Sidebar patient selector UI
│   ├── trend_view.py               # Per-test Plotly chart renderer
│   └── narrative.py                # Claude API call for clinical summary
├── tests/
│   ├── conftest.py                 # sys.path setup
│   ├── test_reference_ranges.py
│   ├── test_critical_values.py
│   └── test_delta_check.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
└── README.md
```

---

## Task 0: Project Scaffold

**Files:**
- Create: `requirements.txt`
- Create: `.streamlit/config.toml`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create directory tree**

```bash
cd ~/Projects/health-portfolio-lab-trends
mkdir -p config data modules tests .streamlit
touch app.py config/__init__.py data/__init__.py modules/__init__.py
```

- [ ] **Step 2: Write `requirements.txt`**

```
streamlit>=1.32.0
pandas>=2.0.0
plotly>=5.18.0
numpy>=1.24.0
anthropic>=0.25.0
pytest>=8.0.0
```

- [ ] **Step 3: Write `.streamlit/config.toml`**

```toml
[server]
port = 8502
headless = true

[theme]
base = "dark"
```

- [ ] **Step 4: Write `tests/conftest.py`**

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
```

- [ ] **Step 5: Install dependencies**

```bash
/opt/anaconda3/bin/python -m pip install -r requirements.txt
```

Expected: successful install, no errors.

- [ ] **Step 6: Verify pytest runs**

```bash
cd ~/Projects/health-portfolio-lab-trends
/opt/anaconda3/bin/python -m pytest tests/ -v
```

Expected: `no tests ran` — that's fine at this stage.

- [ ] **Step 7: Init git and commit**

```bash
git init
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
git add .
git commit -m "feat: project scaffold with streamlit config and pytest setup"
```

---

## Task 1: Lab Config (`config/lab_config.py`)

**Files:**
- Create: `config/lab_config.py`

This is pure data — no tests required (no logic). Every downstream module imports from here.

- [ ] **Step 1: Write `config/lab_config.py`**

```python
LOINC_PANELS = {
    "CBC":      ["6690-2", "718-7", "20570-8", "777-3", "789-8"],
    "CMP":      ["2345-7", "3094-0", "38483-4", "2951-2", "2823-3", "2885-2", "1751-7"],
    "Lipid":    ["2093-3", "18262-6", "2085-9", "2571-8"],
    "Diabetes": ["4548-4", "2345-7"],
    "Vitals":   ["8480-6", "8462-4", "39156-5", "29463-7"],
}

LOINC_NAMES = {
    "6690-2":  "WBC",
    "718-7":   "Hemoglobin",
    "20570-8": "Hematocrit",
    "777-3":   "Platelets",
    "789-8":   "RBC",
    "2345-7":  "Glucose",
    "3094-0":  "BUN",
    "38483-4": "Creatinine",
    "2951-2":  "Sodium",
    "2823-3":  "Potassium",
    "2885-2":  "Total Protein",
    "1751-7":  "Albumin",
    "2093-3":  "Total Cholesterol",
    "18262-6": "LDL",
    "2085-9":  "HDL",
    "2571-8":  "Triglycerides",
    "4548-4":  "HbA1c",
    "8480-6":  "Systolic BP",
    "8462-4":  "Diastolic BP",
    "39156-5": "BMI",
    "29463-7": "Body Weight",
}

LOINC_UNITS = {
    "6690-2":  "10*3/uL",
    "718-7":   "g/dL",
    "20570-8": "%",
    "777-3":   "10*3/uL",
    "789-8":   "10*6/uL",
    "2345-7":  "mg/dL",
    "3094-0":  "mg/dL",
    "38483-4": "mg/dL",
    "2951-2":  "mmol/L",
    "2823-3":  "mmol/L",
    "2885-2":  "g/dL",
    "1751-7":  "g/dL",
    "2093-3":  "mg/dL",
    "18262-6": "mg/dL",
    "2085-9":  "mg/dL",
    "2571-8":  "mg/dL",
    "4548-4":  "%",
    "8480-6":  "mmHg",
    "8462-4":  "mmHg",
    "39156-5": "kg/m2",
    "29463-7": "kg",
}

# Reference ranges. Non-gender-specific: (low, high). Gender-specific: {"M": (low, high), "F": (low, high)}.
# float("inf") used where only one bound matters (e.g., HDL — higher is better).
REFERENCE_RANGES = {
    "6690-2":  (4.5, 11.0),
    "718-7":   {"M": (13.5, 17.5), "F": (12.0, 16.0)},
    "20570-8": {"M": (41.0, 53.0), "F": (36.0, 46.0)},
    "777-3":   (150.0, 400.0),
    "789-8":   {"M": (4.5, 5.9),   "F": (4.0, 5.2)},
    "2345-7":  (70.0, 100.0),
    "3094-0":  (7.0, 20.0),
    "38483-4": {"M": (0.74, 1.35), "F": (0.59, 1.04)},
    "2951-2":  (136.0, 145.0),
    "2823-3":  (3.5, 5.1),
    "2885-2":  (6.3, 8.2),
    "1751-7":  (3.5, 5.0),
    "2093-3":  (0.0, 200.0),
    "18262-6": (0.0, 100.0),
    "2085-9":  {"M": (40.0, float("inf")), "F": (50.0, float("inf"))},
    "2571-8":  (0.0, 150.0),
    "4548-4":  (0.0, 5.7),
    "8480-6":  (90.0, 120.0),
    "8462-4":  (60.0, 80.0),
    "39156-5": (18.5, 24.9),
}

# Critical thresholds: (critical_low, critical_high). None = no threshold on that side.
CRITICAL_VALUES = {
    "718-7":   (7.0, 20.0),
    "6690-2":  (2.0, 30.0),
    "777-3":   (50.0, 1000.0),
    "2823-3":  (3.0, 6.0),
    "2951-2":  (125.0, 155.0),
    "2345-7":  (50.0, 500.0),
    "38483-4": (None, 10.0),
}

# Delta check rules per LOINC.
DELTA_RULES = {
    "718-7":   {"type": "absolute", "threshold": 2.0,  "meaning": "Significant acute change — verify specimen identity and check for bleeding or transfusion"},
    "2951-2":  {"type": "absolute", "threshold": 10.0, "meaning": "Rapid electrolyte shift — clinical emergency risk"},
    "2823-3":  {"type": "absolute", "threshold": 1.0,  "meaning": "Dangerous electrolyte shift — verify potassium result"},
    "38483-4": {"type": "percent",  "threshold": 50.0, "meaning": "Acute kidney injury flag — review fluid status and nephrotoxins"},
    "2345-7":  {"type": "absolute", "threshold": 100.0,"meaning": "Significant metabolic shift — verify patient fasting status"},
    "6690-2":  {"type": "percent",  "threshold": 50.0, "meaning": "Possible infection/treatment response or specimen error"},
    "777-3":   {"type": "percent",  "threshold": 50.0, "meaning": "Thrombocytopenia flag — assess for bleeding risk"},
    "4548-4":  {"type": "absolute", "threshold": 1.5,  "meaning": "Clinically significant glycemic control change"},
}

# Delta flags for sodium and potassium are severity=critical; all others are advisory.
DELTA_CRITICAL_LOINCS = {"2951-2", "2823-3"}
```

- [ ] **Step 2: Verify import works**

```bash
cd ~/Projects/health-portfolio-lab-trends
/opt/anaconda3/bin/python -c "from config.lab_config import LOINC_PANELS; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add config/lab_config.py
git commit -m "feat: lab config with LOINC mappings, reference ranges, critical values, delta rules"
```

---

## Task 2: Data Loader (`data/loader.py`)

**Files:**
- Create: `data/loader.py`

No unit tests — logic is just CSV loading + filtering; integration tested implicitly when the app runs.

- [ ] **Step 1: Write `data/loader.py`**

```python
import pandas as pd
import streamlit as st
from pathlib import Path
from config.lab_config import LOINC_PANELS

SYNTHEA = Path.home() / "synthea_data" / "csv" / "csv"
ALL_LAB_LOINCS = [code for codes in LOINC_PANELS.values() for code in codes]


@st.cache_data
def load_observations() -> pd.DataFrame:
    obs = pd.read_csv(SYNTHEA / "observations.csv", low_memory=False)
    obs = obs[(obs["CODE"].isin(ALL_LAB_LOINCS)) & (obs["TYPE"] == "numeric")].copy()
    obs["DATE"] = pd.to_datetime(obs["DATE"], utc=True).dt.tz_localize(None)
    obs["VALUE"] = pd.to_numeric(obs["VALUE"], errors="coerce")
    return obs.dropna(subset=["VALUE"])


@st.cache_data
def load_patients() -> pd.DataFrame:
    pat = pd.read_csv(SYNTHEA / "patients.csv", low_memory=False)
    pat = pat.rename(columns={"Id": "PATIENT"})
    pat["BIRTHDATE"] = pd.to_datetime(pat["BIRTHDATE"])
    pat["DEATHDATE"] = pd.to_datetime(pat["DEATHDATE"], errors="coerce")
    return pat


@st.cache_data
def load_conditions() -> pd.DataFrame:
    cond = pd.read_csv(SYNTHEA / "conditions.csv", low_memory=False)
    cond["STOP"] = pd.to_datetime(cond["STOP"], errors="coerce")
    return cond
```

- [ ] **Step 2: Smoke test the loader from the shell**

```bash
cd ~/Projects/health-portfolio-lab-trends
/opt/anaconda3/bin/python -c "
import sys; sys.path.insert(0, '.')
# stub out streamlit cache decorator
import streamlit as _st
_st.cache_data = lambda f: f
from data.loader import load_observations, load_patients
obs = load_observations()
pat = load_patients()
print('obs rows:', len(obs), '| patients:', len(pat))
print('LOINC codes found:', obs['CODE'].nunique())
"
```

Expected output similar to:
```
obs rows: ~340000 | patients: 1687
LOINC codes found: 20
```

- [ ] **Step 3: Commit**

```bash
git add data/loader.py
git commit -m "feat: SYNTHEA data loader with st.cache_data and LOINC filtering"
```

---

## Task 3: Reference Ranges (`modules/reference_ranges.py`)

**Files:**
- Create: `modules/reference_ranges.py`
- Create: `tests/test_reference_ranges.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_reference_ranges.py
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
    # Creatinine has no critical low — value below male range is just abnormal
    assert flag_value("38483-4", 0.5, "M") == "abnormal"

def test_hdl_male_low_abnormal():
    # HDL below 40 for male is abnormal
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
```

- [ ] **Step 2: Run tests — confirm all fail**

```bash
cd ~/Projects/health-portfolio-lab-trends
/opt/anaconda3/bin/python -m pytest tests/test_reference_ranges.py -v
```

Expected: all FAILED (module not found).

- [ ] **Step 3: Write `modules/reference_ranges.py`**

```python
from config.lab_config import REFERENCE_RANGES, CRITICAL_VALUES


def get_range(loinc: str, gender: str) -> tuple[float, float] | None:
    """Return (low, high) reference range for a LOINC code and gender. None if not configured."""
    r = REFERENCE_RANGES.get(loinc)
    if r is None:
        return None
    if isinstance(r, dict):
        return r.get(gender)
    return r


def flag_value(loinc: str, value: float, gender: str) -> str:
    """Return 'critical', 'abnormal', or 'normal' for a single lab result."""
    crit = CRITICAL_VALUES.get(loinc)
    if crit:
        crit_low, crit_high = crit
        if crit_low is not None and value < crit_low:
            return "critical"
        if crit_high is not None and value > crit_high:
            return "critical"

    ref = get_range(loinc, gender)
    if ref is None:
        return "normal"
    low, high = ref
    if value < low or value > high:
        return "abnormal"
    return "normal"
```

- [ ] **Step 4: Run tests — confirm all pass**

```bash
/opt/anaconda3/bin/python -m pytest tests/test_reference_ranges.py -v
```

Expected: all PASSED.

- [ ] **Step 5: Commit**

```bash
git add modules/reference_ranges.py tests/test_reference_ranges.py
git commit -m "feat: reference range flagging with gender-specific ranges (TDD)"
```

---

## Task 4: Critical Values (`modules/critical_values.py`)

**Files:**
- Create: `modules/critical_values.py`
- Create: `tests/test_critical_values.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_critical_values.py
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
    # Creatinine only has a critical high threshold
    assert check_critical("38483-4", 0.1) is None

def test_no_critical_config_returns_none():
    # BMI has no critical values configured
    assert check_critical("39156-5", 50.0) is None

def test_result_contains_value():
    result = check_critical("718-7", 6.0)
    assert result["value"] == 6.0
    assert result["loinc"] == "718-7"
```

- [ ] **Step 2: Run tests — confirm all fail**

```bash
/opt/anaconda3/bin/python -m pytest tests/test_critical_values.py -v
```

Expected: all FAILED.

- [ ] **Step 3: Write `modules/critical_values.py`**

```python
from config.lab_config import CRITICAL_VALUES, LOINC_NAMES


def check_critical(loinc: str, value: float) -> dict | None:
    """Return a dict describing the critical value, or None if not critical."""
    thresholds = CRITICAL_VALUES.get(loinc)
    if thresholds is None:
        return None
    crit_low, crit_high = thresholds
    name = LOINC_NAMES.get(loinc, loinc)

    if crit_low is not None and value < crit_low:
        return {"loinc": loinc, "name": name, "value": value, "direction": "low", "threshold": crit_low}
    if crit_high is not None and value > crit_high:
        return {"loinc": loinc, "name": name, "value": value, "direction": "high", "threshold": crit_high}
    return None
```

- [ ] **Step 4: Run tests — confirm all pass**

```bash
/opt/anaconda3/bin/python -m pytest tests/test_critical_values.py -v
```

Expected: all PASSED.

- [ ] **Step 5: Commit**

```bash
git add modules/critical_values.py tests/test_critical_values.py
git commit -m "feat: critical value detection for all configured LOINC codes (TDD)"
```

---

## Task 5: Delta Check (`modules/delta_check.py`)

**Files:**
- Create: `modules/delta_check.py`
- Create: `tests/test_delta_check.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_delta_check.py
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

# --- Creatinine: percent ≥50% increase ---

def test_creatinine_percent_flags():
    # 0.9 → 1.4 = 55.6% increase
    df = _df("38483-4", ["2023-01-01", "2023-02-01"], [0.9, 1.4])
    assert len(compute_delta_flags(df, "38483-4")) == 1

def test_creatinine_under_threshold_no_flag():
    # 0.9 → 1.3 = 44.4% increase
    df = _df("38483-4", ["2023-01-01", "2023-02-01"], [0.9, 1.3])
    assert compute_delta_flags(df, "38483-4") == []

def test_creatinine_decrease_no_flag():
    # Creatinine delta rule is for increase only? No — spec says >50% change.
    # DELTA_RULES doesn't distinguish direction for percent, so a 55% decrease should also flag.
    df = _df("38483-4", ["2023-01-01", "2023-02-01"], [1.4, 0.6])
    # 57% decrease — should flag
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
```

- [ ] **Step 2: Run tests — confirm all fail**

```bash
/opt/anaconda3/bin/python -m pytest tests/test_delta_check.py -v
```

Expected: all FAILED.

- [ ] **Step 3: Write `modules/delta_check.py`**

```python
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
```

- [ ] **Step 4: Run tests — confirm all pass**

```bash
/opt/anaconda3/bin/python -m pytest tests/test_delta_check.py -v
```

Expected: all PASSED.

- [ ] **Step 5: Run full test suite**

```bash
/opt/anaconda3/bin/python -m pytest tests/ -v
```

Expected: all PASSED across all three test files.

- [ ] **Step 6: Commit**

```bash
git add modules/delta_check.py tests/test_delta_check.py
git commit -m "feat: delta check logic for all 8 configured LOINC rules (TDD)"
```

---

## Task 6: Patient Search UI (`modules/patient_search.py`)

**Files:**
- Create: `modules/patient_search.py`

No unit tests — this is Streamlit UI code. Tested manually when the app runs.

- [ ] **Step 1: Write `modules/patient_search.py`**

```python
from datetime import date
import pandas as pd
import streamlit as st


def _compute_age(birthdate: pd.Timestamp) -> int:
    today = date.today()
    return (
        today.year
        - birthdate.year
        - ((today.month, today.day) < (birthdate.month, birthdate.day))
    )


def render_patient_search(
    obs: pd.DataFrame, patients: pd.DataFrame, default_id: str | None = None
) -> str | None:
    """Render sidebar patient selector. Returns selected patient UUID."""
    st.sidebar.header("Patient Selection")

    available = set(obs["PATIENT"].unique())
    pat = patients[patients["PATIENT"].isin(available)].copy()
    pat["_age"] = pat["BIRTHDATE"].apply(_compute_age)
    pat["_label"] = pat.apply(
        lambda r: f"{r['FIRST']} {r['LAST']} — age {r['_age']}, {r['GENDER']}", axis=1
    )

    search = st.sidebar.text_input("Search by name or patient ID", value="")
    if search:
        mask = pat["_label"].str.lower().str.contains(search.lower(), na=False) | \
               pat["PATIENT"].str.lower().str.contains(search.lower(), na=False)
        pat = pat[mask]

    if pat.empty:
        st.sidebar.warning("No matching patients.")
        return None

    options = pat["PATIENT"].tolist()
    label_map = pat.set_index("PATIENT")["_label"].to_dict()

    idx = options.index(default_id) if default_id in options else 0

    selected = st.sidebar.selectbox(
        "Select patient",
        options=options,
        index=idx,
        format_func=lambda x: label_map.get(x, x),
    )
    return selected


def render_patient_card(
    patient_row: pd.Series,
    patient_obs: pd.DataFrame,
    conditions: pd.DataFrame,
) -> None:
    """Display the patient summary card below the title."""
    age = _compute_age(patient_row["BIRTHDATE"])
    gender_label = "Male" if patient_row["GENDER"] == "M" else "Female"
    name = f"{patient_row['FIRST']} {patient_row['LAST']}"

    active_cond = conditions[
        (conditions["PATIENT"] == patient_row["PATIENT"]) & conditions["STOP"].isna()
    ]["DESCRIPTION"].tolist()

    lab_count = len(patient_obs)
    date_range = (
        f"{patient_obs['DATE'].min().date()} – {patient_obs['DATE'].max().date()}"
        if lab_count else "—"
    )

    with st.container():
        cols = st.columns([2, 1, 1, 2])
        cols[0].metric("Patient", name)
        cols[1].metric("Age / Sex", f"{age} / {gender_label}")
        cols[2].metric("Lab Results", lab_count)
        cols[3].metric("Date Range", date_range)
        if active_cond:
            st.caption(f"Active conditions: {', '.join(active_cond[:5])}" + (" ..." if len(active_cond) > 5 else ""))
```

- [ ] **Step 2: Commit**

```bash
git add modules/patient_search.py
git commit -m "feat: sidebar patient selector and patient summary card"
```

---

## Task 7: Trend Charts (`modules/trend_view.py`)

**Files:**
- Create: `modules/trend_view.py`

- [ ] **Step 1: Write `modules/trend_view.py`**

```python
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config.lab_config import LOINC_NAMES, LOINC_UNITS
from modules.reference_ranges import flag_value, get_range

_COLORS = {"normal": "#2ECC71", "abnormal": "#F39C12", "critical": "#E74C3C"}


def render_trend_chart(
    patient_obs: pd.DataFrame, gender: str, loinc: str
) -> None:
    """Render a single Plotly trend chart for one LOINC code."""
    name = LOINC_NAMES.get(loinc, loinc)
    units = LOINC_UNITS.get(loinc, "")

    series = (
        patient_obs[patient_obs["CODE"] == loinc]
        .sort_values("DATE")[["DATE", "VALUE"]]
        .dropna()
    )
    if series.empty:
        return

    flags = series["VALUE"].apply(lambda v: flag_value(loinc, v, gender))
    ref = get_range(loinc, gender)

    fig = go.Figure()

    # Reference range band (skip if upper bound is infinite)
    if ref:
        low, high = ref
        if high != float("inf"):
            fig.add_hrect(
                y0=low,
                y1=high,
                fillcolor="#2ECC71",
                opacity=0.08,
                line_width=0,
                annotation_text="Normal range",
                annotation_position="top left",
                annotation_font_size=10,
                annotation_font_color="#2ECC71",
            )

    # Connecting line
    fig.add_trace(
        go.Scatter(
            x=series["DATE"],
            y=series["VALUE"],
            mode="lines",
            line=dict(color="#555555", width=1),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # Color-coded points by status
    for status, color in _COLORS.items():
        mask = flags == status
        if not mask.any():
            continue
        fig.add_trace(
            go.Scatter(
                x=series["DATE"][mask],
                y=series["VALUE"][mask],
                mode="markers",
                marker=dict(color=color, size=7),
                name=status.capitalize(),
                showlegend=(status != "normal"),
                hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.2f}} {units}<extra></extra>",
            )
        )

    fig.update_layout(
        template="plotly_dark",
        title=dict(text=f"{name} ({units})", font=dict(size=14)),
        xaxis_title="Date",
        yaxis_title=units,
        height=280,
        margin=dict(l=50, r=20, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig, use_container_width=True)
```

- [ ] **Step 2: Commit**

```bash
git add modules/trend_view.py
git commit -m "feat: plotly trend chart with reference range band and color-coded status points"
```

---

## Task 8: Narrative Generation (`modules/narrative.py`)

**Files:**
- Create: `modules/narrative.py`

- [ ] **Step 1: Write `modules/narrative.py`**

```python
import os
import pandas as pd
import streamlit as st
import anthropic

from config.lab_config import LOINC_NAMES


def _build_lab_summary(patient_obs: pd.DataFrame) -> str:
    lines = []
    for loinc, group in patient_obs.groupby("CODE"):
        name = LOINC_NAMES.get(loinc, loinc)
        sorted_vals = group.sort_values("DATE")["VALUE"].tolist()
        last3 = [round(v, 2) for v in sorted_vals[-3:]]
        if len(last3) >= 2:
            if last3[-1] < last3[-2]:
                trend = "decreasing"
            elif last3[-1] > last3[-2]:
                trend = "increasing"
            else:
                trend = "stable"
        else:
            trend = "single result"
        lines.append(f"- {name}: last 3 values={last3}, trend={trend}")
    return "\n".join(lines)


def generate_narrative(
    patient_obs: pd.DataFrame,
    age: int,
    gender_label: str,
    active_conditions: list[str],
) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY", "")
    client = anthropic.Anthropic(api_key=api_key)

    timespan = f"{patient_obs['DATE'].min().date()} to {patient_obs['DATE'].max().date()}"
    lab_summary = _build_lab_summary(patient_obs)
    conditions_str = ", ".join(active_conditions) if active_conditions else "none recorded"

    prompt = f"""You are a clinical laboratory informatics analyst reviewing longitudinal lab data for a synthetic patient.

Patient: {age}-year-old {gender_label}. Active diagnoses: {conditions_str}

Lab summary over {timespan}:
{lab_summary}

Write a structured clinical narrative (4-6 sentences) that:
1. Summarizes overall lab trajectory
2. Highlights clinically significant trends or flags
3. Notes consistency between lab patterns and active diagnoses
4. Identifies what a care team would want to monitor next

Write for a clinical audience. Use medical terminology appropriately. Do not include disclaimers about being an AI."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
```

- [ ] **Step 2: Commit**

```bash
git add modules/narrative.py
git commit -m "feat: Claude Haiku narrative generation from patient lab history"
```

---

## Task 9: Main App (`app.py`)

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Write `app.py`**

```python
from datetime import date
import streamlit as st

from data.loader import load_observations, load_patients, load_conditions
from modules.patient_search import render_patient_search, render_patient_card
from modules.trend_view import render_trend_chart
from modules.delta_check import compute_delta_flags
from modules.critical_values import check_critical
from modules.narrative import generate_narrative
from config.lab_config import LOINC_PANELS, LOINC_NAMES

DEMO_PATIENT_ID = "f9ed1c66-904c-3c3f-0a50-0226629df9ff"


def _compute_age(birthdate) -> int:
    today = date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))


def _render_critical_banner(patient_obs, gender: str) -> None:
    """Show a red banner if any of the patient's most recent results are critical."""
    from modules.reference_ranges import flag_value

    latest = patient_obs.sort_values("DATE").groupby("CODE").last().reset_index()
    critical_hits = []
    for _, row in latest.iterrows():
        result = check_critical(row["CODE"], row["VALUE"])
        if result:
            direction = "LOW" if result["direction"] == "low" else "HIGH"
            critical_hits.append(
                f"**{result['name']}**: {row['VALUE']:.2f} — critically {direction} (threshold: {result['threshold']})"
            )

    if critical_hits:
        st.error("🚨 CRITICAL VALUE ALERT — Immediate clinician notification required\n\n" + "\n\n".join(critical_hits))


def main():
    st.set_page_config(page_title="Lab Trend Analyzer", layout="wide", page_icon="🧪")
    st.title("Lab Trend Analyzer")

    obs = load_observations()
    patients = load_patients()
    conditions = load_conditions()

    patient_id = render_patient_search(obs, patients, default_id=DEMO_PATIENT_ID)

    if not patient_id:
        st.info("Search for and select a patient to begin.")
        return

    patient_obs = obs[obs["PATIENT"] == patient_id].copy()
    patient_row = patients[patients["PATIENT"] == patient_id].iloc[0]
    gender = patient_row["GENDER"]

    render_patient_card(patient_row, patient_obs, conditions)
    st.divider()

    _render_critical_banner(patient_obs, gender)

    # Panel tabs
    panel_names = [p for p in LOINC_PANELS if any(l in patient_obs["CODE"].values for l in LOINC_PANELS[p])]
    if not panel_names:
        st.warning("No lab data found for this patient.")
        return

    tabs = st.tabs(panel_names)
    for tab, panel_name in zip(tabs, panel_names):
        with tab:
            for loinc in LOINC_PANELS[panel_name]:
                if loinc not in patient_obs["CODE"].values:
                    continue

                render_trend_chart(patient_obs, gender, loinc)

                flags = compute_delta_flags(patient_obs, loinc)
                for flag in flags:
                    msg = (
                        f"⚠ **{flag['name']} delta flag**: {flag['direction']} "
                        f"{abs(flag['curr_val'] - flag['prev_val']):.2f} since "
                        f"{flag['prev_date'].date()} "
                        f"(from {flag['prev_val']:.2f} to {flag['curr_val']:.2f}). "
                        f"{flag['meaning']}"
                    )
                    if flag["severity"] == "critical":
                        st.error(msg)
                    else:
                        st.warning(msg)

    st.divider()

    if st.button("Generate Clinical Summary", type="primary"):
        if "narrative_pid" not in st.session_state or st.session_state.narrative_pid != patient_id:
            with st.spinner("Generating clinical narrative..."):
                active_cond = conditions[
                    (conditions["PATIENT"] == patient_id) & conditions["STOP"].isna()
                ]["DESCRIPTION"].tolist()
                st.session_state.narrative = generate_narrative(
                    patient_obs,
                    age=_compute_age(patient_row["BIRTHDATE"]),
                    gender_label="male" if gender == "M" else "female",
                    active_conditions=active_cond,
                )
                st.session_state.narrative_pid = patient_id

    if "narrative" in st.session_state and st.session_state.get("narrative_pid") == patient_id:
        st.subheader("Clinical Summary")
        st.write(st.session_state.narrative)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Start app and verify it loads**

```bash
cd ~/Projects/health-portfolio-lab-trends
/opt/anaconda3/bin/python -m streamlit run app.py --server.port 8502 --server.headless true &
sleep 4
open http://localhost:8502
```

Expected: App loads with Lupe Pacocha pre-selected. Trend charts visible for CBC, CMP, Lipid, Diabetes, Vitals panels.

- [ ] **Step 3: Verify delta check flags appear**

In the CBC tab, scroll through Hemoglobin and WBC. With 10 years of SYNTHEA data, delta flags should appear for at least some results.

- [ ] **Step 4: Verify critical value banner**

If the demo patient has any critical values, a red banner appears. If not, select another patient with extreme values to confirm the banner renders.

- [ ] **Step 5: Verify narrative generation**

Click "Generate Clinical Summary". Verify the narrative renders a 4-6 sentence clinical paragraph. Check the browser console for no errors.

- [ ] **Step 6: Kill dev server and commit**

```bash
lsof -ti:8502 | xargs kill -9 2>/dev/null
git add app.py
git commit -m "feat: main app wiring all modules — patient search, trend charts, delta check, critical values, narrative"
```

---

## Task 10: Dock Launcher (`.app` bundle)

**Files:**
- Create: `/Applications/Lab Trend Analyzer.app/Contents/MacOS/run.sh`
- Create: `/Applications/Lab Trend Analyzer.app/Contents/Info.plist`

- [ ] **Step 1: Create the bundle structure**

```bash
APP="/Applications/Lab Trend Analyzer.app"
mkdir -p "$APP/Contents/MacOS"
```

- [ ] **Step 2: Write the run script**

```bash
cat > "/Applications/Lab Trend Analyzer.app/Contents/MacOS/run.sh" << 'EOF'
#!/bin/bash
lsof -ti:8502 | xargs kill -9 2>/dev/null
nohup /opt/anaconda3/bin/python -m streamlit run ~/Projects/health-portfolio-lab-trends/app.py \
  --server.headless true \
  > /tmp/lab_trends.log 2>&1 &
sleep 3
open http://localhost:8502
EOF
chmod +x "/Applications/Lab Trend Analyzer.app/Contents/MacOS/run.sh"
```

- [ ] **Step 3: Write `Info.plist`**

```bash
cat > "/Applications/Lab Trend Analyzer.app/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>run.sh</string>
  <key>CFBundleIdentifier</key>
  <string>com.pdanso1.lab-trend-analyzer</string>
  <key>CFBundleName</key>
  <string>Lab Trend Analyzer</string>
  <key>CFBundleVersion</key>
  <string>1.0</string>
</dict>
</plist>
EOF
```

- [ ] **Step 4: Test the launcher**

Double-click `Lab Trend Analyzer` in `/Applications/`. Verify the browser opens to `http://localhost:8502` with the app running and no terminal window appears.

- [ ] **Step 5: Commit the launch script to repo (not the .app)**

```bash
cd ~/Projects/health-portfolio-lab-trends
mkdir -p scripts
cp "/Applications/Lab Trend Analyzer.app/Contents/MacOS/run.sh" scripts/launch.sh
git add scripts/launch.sh
git commit -m "chore: add dock launcher script for local development"
```

---

## Task 11: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write `README.md`**

```markdown
# Lab Trend Analyzer

A Streamlit application for visualizing longitudinal patient lab data with clinically accurate delta check logic, reference range interpretation, and AI-generated clinical narratives.

**Live demo:** [pdanso1-health-portfolio-lab-trends.streamlit.app](https://pdanso1-health-portfolio-lab-trends.streamlit.app)

---

## Features

- **Patient search** — select any patient from SYNTHEA synthetic data
- **Trend charts** — longitudinal Plotly charts per lab test with color-coded status points and reference range bands
- **Delta check flagging** — identifies clinically significant result-to-result changes
- **Critical value alerts** — prominent banner for results requiring immediate clinician notification
- **Clinical narrative** — Claude Haiku generates a structured 4-6 sentence summary of the patient's lab trajectory

---

## Clinical Context

### What is a delta check?

A delta check is a quality assurance technique used in clinical laboratories to flag when a patient's result changes by more than a clinically significant amount since their last result. Labs use delta checks to catch specimen mix-ups (e.g., two patients' tubes switched), transcription errors, and rapid clinical deterioration.

For example, a hemoglobin drop of more than 2 g/dL between two results triggers a flag. That delta alone doesn't mean the result is wrong — it prompts lab staff to verify the specimen identity before releasing the result.

This app implements delta check rules for 8 analytes with clinically validated thresholds, distinguishing between absolute-change tests (Hemoglobin, Sodium, Potassium, Glucose, HbA1c) and percent-change tests (Creatinine, WBC, Platelets).

### What are critical values?

Critical values are results so extreme they require immediate notification of the treating clinician. Every accredited clinical laboratory maintains a list of critical values and protocols for notifying providers within a defined timeframe (typically 30–60 minutes).

This app flags critical values using standard thresholds (e.g., Hemoglobin <7.0 g/dL, Potassium >6.0 mmol/L) and displays a prominent alert banner — mirroring how a laboratory information system would escalate these results.

### Why gender-specific reference ranges matter

Several analytes have distinct normal ranges for males and females due to physiological differences. Hemoglobin, hematocrit, RBC, creatinine, and HDL all require the patient's biological sex to determine whether a result is normal or abnormal. Applying a single universal range would misclassify a meaningful fraction of results.

This app pulls gender from the patient record and applies the correct range for each analyte — the same logic a validated laboratory instrument or LIS would apply.

### Why this signals real lab knowledge

Any developer can build a line chart from lab data. Delta check logic and critical value thresholds reflect the reality of how clinical laboratories operate — not textbook theory, but the daily practice of specimen verification, result release, and clinician communication. These features exist in this app because the developer spent three years as a Medical Laboratory Scientist II in Microbiology at Regions Hospital/HealthPartners, working with these protocols daily.

---

## Tech Stack

- Python 3.11
- Streamlit — UI framework
- Plotly — interactive trend charts
- pandas — data processing
- Anthropic Claude Haiku — clinical narrative generation
- SYNTHEA — synthetic patient data

---

## Local Setup

```bash
git clone https://github.com/pdanso1/health-portfolio-lab-trends
cd health-portfolio-lab-trends
pip install -r requirements.txt
# Set your API key
export ANTHROPIC_API_KEY=sk-...
streamlit run app.py --server.port 8502
```

Requires SYNTHEA data at `~/synthea_data/csv/csv/`. See `00_synthea_setup.md` for generation instructions.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README with clinical context section explaining delta checks and critical values"
```

---

## Success Criteria Verification

Before calling this complete, verify each item from the spec:

- [ ] Patient search works, patient summary card displays correctly
- [ ] Trend charts render for each panel with reference range bands
- [ ] Data points color correctly (green/amber/red) based on ranges and critical thresholds
- [ ] Gender-specific ranges apply correctly (Hemoglobin different for M vs F)
- [ ] Delta check flags appear correctly for patients with significant changes
- [ ] Critical value banner appears for any critical result
- [ ] Claude narrative generates without error and is clinically coherent
- [ ] App runs on port 8502 with no terminal window via Dock launcher
