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
