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
