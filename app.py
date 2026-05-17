import streamlit as st

from data.loader import load_observations, load_patients, load_conditions
from modules.patient_search import render_patient_search, render_patient_card, compute_age
from modules.trend_view import render_trend_chart
from modules.delta_check import compute_delta_flags
from modules.critical_values import check_critical
from modules.narrative import generate_narrative
from config.lab_config import LOINC_PANELS, LOINC_NAMES

DEMO_PATIENT_ID = "f9ed1c66-904c-3c3f-0a50-0226629df9ff"


def _render_critical_banner(patient_obs, gender: str) -> None:
    """Show a red banner if any of the patient's most recent results are critical."""
    latest = patient_obs.sort_values("DATE").groupby("CODE").last().reset_index()
    critical_hits = []
    for _, row in latest.iterrows():
        result = check_critical(row["CODE"], row["VALUE"])
        if result:
            direction = "LOW" if result["direction"] == "low" else "HIGH"
            critical_hits.append(
                f"**{result['name']}**: {row['VALUE']:.2f} — critically {direction} "
                f"(threshold: {result['threshold']})"
            )

    if critical_hits:
        st.error(
            "🚨 CRITICAL VALUE ALERT — Immediate clinician notification required\n\n"
            + "\n\n".join(critical_hits)
        )


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

    # Build tabs for panels that have data for this patient
    panel_names = [
        p for p in LOINC_PANELS
        if any(loinc in patient_obs["CODE"].values for loinc in LOINC_PANELS[p])
    ]
    if not panel_names:
        st.warning("No lab data found for this patient.")
        return

    tabs = st.tabs(panel_names)
    for tab, panel_name in zip(tabs, panel_names):
        with tab:
            for loinc in LOINC_PANELS[panel_name]:
                if loinc not in patient_obs["CODE"].values:
                    continue

                render_trend_chart(patient_obs, gender, loinc, chart_key=f"{panel_name}_{loinc}")

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
                    age=compute_age(patient_row["BIRTHDATE"]),
                    gender_label="male" if gender == "M" else "female",
                    active_conditions=active_cond,
                )
                st.session_state.narrative_pid = patient_id

    if "narrative" in st.session_state and st.session_state.get("narrative_pid") == patient_id:
        st.subheader("Clinical Summary")
        st.write(st.session_state.narrative)


if __name__ == "__main__":
    main()
