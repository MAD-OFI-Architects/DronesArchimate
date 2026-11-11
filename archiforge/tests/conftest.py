"""Las pruebas nunca leen ni escriben la configuración personal real (~/.config/archiforge)."""
import pytest


@pytest.fixture(autouse=True)
def _isolated_user_config(tmp_path_factory, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path_factory.mktemp("xdg")))
