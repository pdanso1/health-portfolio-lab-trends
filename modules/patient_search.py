from datetime import date
import pandas as pd
import streamlit as st


def compute_age(birthdate: pd.Timestamp) -> int:
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
    pat["_age"] = pat["BIRTHDATE"].apply(compute_age)
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
    age = compute_age(patient_row["BIRTHDATE"])
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
            st.caption(
                f"Active conditions: {', '.join(active_cond[:5])}"
                + (" ..." if len(active_cond) > 5 else "")
            )
