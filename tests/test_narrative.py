import os
from types import SimpleNamespace as NS
from unittest.mock import patch

import pandas as pd
import pytest

from modules import narrative

OBS = pd.DataFrame({"CODE": ["4548-4", "4548-4"], "VALUE": [7.1, 6.8],
                    "DATE": pd.to_datetime(["2025-01-01", "2025-06-01"])})


def _run(content, stop="end_turn"):
    resp = NS(content=content, stop_reason=stop)
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test"}), \
         patch.object(narrative.anthropic, "Anthropic") as cls:
        cls.return_value.messages.create.return_value = resp
        out = narrative.generate_narrative(OBS, 55, "male", ["Type 2 diabetes"])
        return out, cls.return_value.messages.create.call_args.kwargs


def test_haiku55_low_effort_and_text_after_thinking():
    out, kw = _run([NS(type="thinking", thinking="", signature="s"), NS(type="text", text="Narrative.")])
    assert out == "Narrative."
    assert kw["model"] == "claude-haiku-5-5"
    assert kw["output_config"] == {"effort": "low"}
    assert kw["max_tokens"] >= 4000  # thinking counts toward it; was 512


def test_cut_off_narrative_raises():
    with pytest.raises(RuntimeError, match="max_tokens"):
        _run([NS(type="text", text="Partial")], stop="max_tokens")
