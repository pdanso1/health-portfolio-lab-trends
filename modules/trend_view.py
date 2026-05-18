import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config.lab_config import LOINC_NAMES, LOINC_UNITS
from modules.reference_ranges import flag_value, get_range

_COLORS = {"normal": "#2ECC71", "abnormal": "#F39C12", "critical": "#E74C3C"}


def render_trend_chart(
    patient_obs: pd.DataFrame, gender: str, loinc: str, chart_key: str | None = None
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

    # Reference range band (skip if upper bound is infinite or no range configured)
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

    # Connecting line (neutral color — points provide the status color)
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
        xaxis=dict(tickformat="%b %d, %Y"),
    )

    st.plotly_chart(fig, use_container_width=True, key=chart_key or f"trend_{loinc}")
