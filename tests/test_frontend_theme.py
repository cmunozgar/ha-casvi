"""Regression checks for Home Assistant theme compatibility."""
from pathlib import Path


PANEL = Path(__file__).parents[1] / "custom_components/casvi/frontend/casvi-panel.js"


def test_panel_inherits_home_assistant_theme_tokens():
    source = PANEL.read_text(encoding="utf-8")
    assert "--casvi-card-background:var(--ha-card-background,var(--card-background-color,#fff))" in source
    assert "background:var(--casvi-card-background)" in source
    assert "color-scheme:light dark" in source
    # Never shadow Home Assistant's standard theme variables with fixed light values.
    assert ":host{--card-background-color:#fff" not in source
    assert "background:#fff;border:1px solid #e5ebef" not in source
