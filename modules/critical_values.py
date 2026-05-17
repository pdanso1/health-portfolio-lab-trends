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
