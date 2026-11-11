"""Lo personal (motor/modelo del agente, tokens) vive fuera del repositorio; lo del equipo (forge.toml, decisiones) no se contamina."""
import dataclasses
import os
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from forge import agentdefs, config, personal  # noqa: E402
from forge.studio import projects  # noqa: E402

TOOL = Path(__file__).resolve().parents[1]
ARCHIMATE = TOOL.parent / "diseno/modelo/drones-mantenimiento.archimate"


@pytest.fixture
def team_project(tmp_path):
    root = tmp_path / "equipo"
    root.mkdir()
    toml = root / "forge.toml"
    toml.write_text(f'[inputs]\narchimate = "{ARCHIMATE}"\n[output]\ndir = "out"\n[decisions]\ndir = "decisiones"\n'
                    '[agent]\nengine = "opencode"\nmodel = "github-copilot/auto"\nmax_attempts = 3\n', encoding="utf-8")
    return toml


def test_personal_override_wins_over_the_team_default_without_touching_forge_toml(team_project):
    before = team_project.read_bytes()
    assert config.load(team_project).agent.engine == "opencode"                       # sin override: el valor del equipo
    personal.save(team_project, {"engine": "claude", "model": "sonnet", "max_attempts": 5})
    cfg = config.load(team_project)
    assert (cfg.agent.engine, cfg.agent.model, cfg.agent.max_attempts) == ("claude", "sonnet", 5)
    assert team_project.read_bytes() == before                                         # forge.toml (compartido) intacto
    assert str(personal.path(team_project)).startswith(os.environ["XDG_CONFIG_HOME"])   # y lo personal vive en la config del usuario


def test_override_is_per_project_and_can_be_reset(team_project, tmp_path):
    other = tmp_path / "otro" / "forge.toml"
    other.parent.mkdir()
    other.write_text(team_project.read_text(encoding="utf-8"), encoding="utf-8")
    personal.save(team_project, {"engine": "claude"})
    assert config.load(other).agent.engine == "opencode"
    personal.clear(team_project)
    assert config.load(team_project).agent.engine == "opencode" and not personal.path(team_project).exists()


def test_unknown_keys_and_corrupt_files_never_break_loading(team_project):
    personal.save(team_project, {"engine": "claude", "hack": "x", "extra_args": ["--malo"]})
    assert "hack" not in personal.load(team_project) and "extra_args" not in personal.load(team_project)
    personal.path(team_project).write_text("{no es json", encoding="utf-8")
    assert config.load(team_project).agent.engine == "opencode"                       # se ignora: no tumba el CLI


def test_save_agent_goes_to_the_personal_store_and_leaves_the_project_file_alone(tmp_path):
    store = projects.ProjectStore(tmp_path / "reg.json", tmp_path / "projects")
    info = store.create("Uno", ARCHIMATE, None, projects.AgentSettings(model="base/modelo"))
    before = info.toml.read_bytes()
    store.save_agent(info, projects.AgentSettings(engine="claude", model="sonnet", max_attempts=5))
    assert info.toml.read_bytes() == before
    cfg = store.load(info)
    assert (cfg.agent.engine, cfg.agent.model, cfg.agent.max_attempts) == ("claude", "sonnet", 5)
    store.reset_agent(info)
    assert store.load(info).agent.model == "base/modelo"


def test_install_is_idempotent_and_ensure_refreshes_only_when_the_model_changes(tmp_path):
    agentdefs.ensure(tmp_path, "m/uno")
    f = tmp_path / ".opencode/agents/forge-python.md"
    assert "model: m/uno" in f.read_text(encoding="utf-8") and (tmp_path / ".claude/agents/forge-python.md").exists()
    os.utime(f, (1, 1))
    agentdefs.ensure(tmp_path, "m/uno")
    assert f.stat().st_mtime == 1                                                      # mismo contenido: no se reescribe
    agentdefs.ensure(tmp_path, "m/dos")
    assert "model: m/dos" in f.read_text(encoding="utf-8")


def test_generated_agents_are_ignored_by_git_but_regenerated_on_build():
    import subprocess
    r = subprocess.run(["git", "check-ignore", "archiforge/.opencode/agents/forge-python.md", "archiforge/.claude/agents/forge-python.md"],
                       cwd=TOOL.parent, capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.count("\n") == 2
    tracked = subprocess.run(["git", "ls-files", "archiforge/.opencode", "archiforge/.claude"], cwd=TOOL.parent, capture_output=True, text=True).stdout
    assert tracked.strip() == ""
    import inspect
    from forge import cli
    assert "agentdefs.ensure" in inspect.getsource(cli.build_one)
