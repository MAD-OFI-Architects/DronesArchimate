"""Tokens de API (S4): fuera del proyecto, permisos 600, nunca visibles ni en logs; llegan al agente solo por entorno."""
import os
import stat
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from forge import agents, credentials  # noqa: E402
from forge.config import AgentCfg  # noqa: E402


def test_store_roundtrip_with_private_permissions(tmp_path):
    store = credentials.CredentialStore(tmp_path / "cfg" / "credentials.json")
    store.set("ANTHROPIC_API_KEY", "sk-ant-secreto-123456")
    assert store.get("ANTHROPIC_API_KEY") == "sk-ant-secreto-123456"
    assert stat.S_IMODE(os.stat(store.path).st_mode) == 0o600
    assert stat.S_IMODE(os.stat(store.path.parent).st_mode) == 0o700
    again = credentials.CredentialStore(store.path)                 # persiste
    assert again.names() == ["ANTHROPIC_API_KEY"] and again.env() == {"ANTHROPIC_API_KEY": "sk-ant-secreto-123456"}
    again.delete("ANTHROPIC_API_KEY")
    assert credentials.CredentialStore(store.path).names() == []


def test_mask_never_reveals_the_secret():
    m = credentials.mask("sk-ant-secreto-123456")
    assert "secreto" not in m and m.endswith("3456") and "•" in m
    assert credentials.mask("abc") == "•••"                           # corto: no muestra nada
    assert credentials.mask("") == ""


@pytest.mark.parametrize("name,value", [("anthropic key", "x"), ("1BAD", "x"), ("OK_NAME", ""), ("OK_NAME", "a\nb")])
def test_store_rejects_invalid_names_and_values(tmp_path, name, value):
    with pytest.raises(ValueError):
        credentials.CredentialStore(tmp_path / "c.json").set(name, value)


def test_default_path_follows_xdg_and_lives_outside_any_project(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    assert credentials.default_path() == tmp_path / "xdg" / "archiforge" / "credentials.json"


def test_corrupt_store_is_reported_not_silently_emptied(tmp_path):
    p = tmp_path / "c.json"
    p.write_text("{no es json", encoding="utf-8")
    with pytest.raises(credentials.CredentialError):
        credentials.CredentialStore(p).names()


def test_agent_receives_tokens_only_through_the_environment(tmp_path):
    script = tmp_path / "agent.py"
    script.write_text("import os,sys\nprint('TOKEN=' + os.environ.get('MI_TOKEN', 'ausente'))\n", encoding="utf-8")
    work, log = tmp_path / "work.md", tmp_path / "logs" / "a.log"
    work.write_text("x", encoding="utf-8")
    cfg = AgentCfg(engine="custom", custom_argv=[sys.executable, str(script)], timeout_minutes=1)
    ok, _ = agents.run_agent(cfg, work, tmp_path, log, env={"MI_TOKEN": "valor-secreto-9999"})
    text = log.read_text(encoding="utf-8")
    assert ok and "TOKEN=valor-secreto-9999" in text                  # el proceso hijo sí lo ve
    assert sys.executable in text.splitlines()[0] and "valor-secreto" not in text.splitlines()[0]   # la cabecera del log no lo incluye
    ok, _ = agents.run_agent(cfg, work, tmp_path, log)                # sin env: no se filtra de ninguna parte
    assert "TOKEN=ausente" in log.read_text(encoding="utf-8")


# ------------------------------------------------------------------ T2: la raíz del proyecto no es la raíz de la herramienta
def test_project_outside_the_tool_root_still_finds_catalog_prompts_and_guide(tmp_path):
    from forge import config, decisions
    from forge.runner import Runner
    tool = Path(__file__).resolve().parents[1]
    proj = tmp_path / "mi-proyecto"
    proj.mkdir()
    (proj / "forge.toml").write_text(f'[inputs]\narchimate = "{tool.parent}/modelo/drones-mantenimiento.archimate"\n'
                                     '[output]\ndir = "out"\n[decisions]\ndir = "decisiones"\n', encoding="utf-8")
    cfg = config.load(proj / "forge.toml")
    assert cfg.root == proj and cfg.tool_root == tool
    assert cfg.docs_dir is None                                   # los documentos de fase son opcionales
    assert cfg.guide == tool / "reference" / "guia_ddd.md" and cfg.guide.exists()
    d = config.Domain("Intervenciones", "csharp", "clean-ddd", "microservicio", "mongodb", 5101)
    errors, _ = decisions.validate(cfg, d)                        # lee catalog/patrones.toml de la herramienta
    assert isinstance(errors, list)
    run = Runner(cfg, d)
    assert run.env.get_template("mfe.md.j2")                      # y las plantillas de prompts
    assert (proj / ".forge" / "intervenciones").exists()          # pero el estado vive en el proyecto
