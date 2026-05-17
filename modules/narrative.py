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
