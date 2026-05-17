import pandas as pd
import streamlit as st
from pathlib import Path
from config.lab_config import LOINC_PANELS

SYNTHEA = Path.home() / "synthea_data" / "csv" / "csv"
ALL_LAB_LOINCS = list({code for codes in LOINC_PANELS.values() for code in codes})


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
