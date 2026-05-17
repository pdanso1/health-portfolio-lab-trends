# Lab Trend Analyzer

A Streamlit application for visualizing longitudinal patient lab data with clinically accurate delta check logic, reference range interpretation, and AI-generated clinical narratives.

**Live demo:** [pdanso1-health-portfolio-lab-trends.streamlit.app](https://pdanso1-health-portfolio-lab-trends.streamlit.app)

---

## Features

- **Patient search** — select any patient from SYNTHEA synthetic data by name or UUID
- **Trend charts** — longitudinal Plotly charts per lab test with color-coded status points (green/amber/red) and reference range bands
- **Delta check flagging** — identifies clinically significant result-to-result changes with severity levels (advisory vs critical)
- **Critical value alerts** — prominent banner for results requiring immediate clinician notification
- **Clinical narrative** — Claude Haiku generates a structured 4–6 sentence summary of the patient's lab trajectory

---

## Clinical Context

### What is a delta check?

A delta check is a quality assurance technique used in clinical laboratories to flag when a patient's result changes by more than a clinically significant amount since their last result. Labs use delta checks to catch specimen mix-ups (e.g., two patients' tubes switched), transcription errors, and rapid clinical deterioration.

For example, a hemoglobin drop of more than 2 g/dL between two results triggers a flag. That delta alone doesn't mean the result is wrong — it prompts lab staff to verify the specimen identity before releasing the result. This app implements delta check rules for 8 analytes with clinically validated thresholds, distinguishing between absolute-change tests (Hemoglobin, Sodium, Potassium, Glucose, HbA1c) and percent-change tests (Creatinine, WBC, Platelets).

### What are critical values?

Critical values are results so extreme they require immediate notification of the treating clinician. Every accredited clinical laboratory maintains a list of critical values and protocols for notifying providers within a defined timeframe (typically 30–60 minutes after result verification).

This app flags critical values using standard thresholds (e.g., Hemoglobin <7.0 g/dL, Potassium >6.0 mmol/L) and displays a prominent alert banner — mirroring how a laboratory information system would escalate these results.

### Why gender-specific reference ranges matter

Several analytes have distinct normal ranges for males and females due to physiological differences. Hemoglobin, hematocrit, RBC, creatinine, and HDL all require the patient's biological sex to determine whether a result is normal or abnormal. Applying a single universal range would misclassify a meaningful fraction of results.

This app pulls gender from the patient record and applies the correct range for each analyte — the same logic a validated laboratory instrument or LIS would use.

### Why this signals real clinical lab knowledge

Any developer can build a line chart from lab data. Delta check logic and critical value thresholds reflect the reality of how clinical laboratories operate — not textbook theory, but the daily practice of specimen verification, result release, and clinician communication. These features exist in this app because the developer spent three years as a Medical Laboratory Scientist II in Microbiology at Regions Hospital/HealthPartners, working with these protocols daily.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11 | Language |
| Streamlit | UI framework |
| Plotly | Interactive trend charts |
| pandas | Data processing |
| Anthropic Claude Haiku | Clinical narrative generation |
| SYNTHEA | Synthetic patient data |

---

## Local Setup

```bash
git clone https://github.com/pdanso1/health-portfolio-lab-trends
cd health-portfolio-lab-trends
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-...

# Run on port 8502
streamlit run app.py --server.port 8502
```

Requires SYNTHEA data at `~/synthea_data/csv/csv/`. See project documentation for generation instructions.

---

## Project Structure

```
health-portfolio-lab-trends/
├── app.py                    # Streamlit entry point
├── config/lab_config.py      # LOINC mappings, reference ranges, critical values, delta rules
├── data/loader.py            # SYNTHEA data loading
├── modules/
│   ├── reference_ranges.py   # flag_value(), get_range() — pure functions
│   ├── critical_values.py    # check_critical() — pure function
│   ├── delta_check.py        # compute_delta_flags() — pure function
│   ├── patient_search.py     # Sidebar patient selector + summary card
│   ├── trend_view.py         # Plotly chart renderer
│   └── narrative.py          # Claude Haiku narrative generation
└── tests/                    # Pytest unit tests for all business logic
```
