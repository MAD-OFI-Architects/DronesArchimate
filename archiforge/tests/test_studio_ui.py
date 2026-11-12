"""La TUI recorrida de punta a punta con el pilot de Textual (sin terminal)."""
import asyncio
import sys
from pathlib import Path

import pytest

pytest.importorskip("textual")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from textual.widgets import DataTable, Input, RichLog, SelectionList, Select  # noqa: E402

from forge.credentials import CredentialStore  # noqa: E402
from forge.studio import projects  # noqa: E402
from forge.studio.projects import AgentSettings, ProjectStore  # noqa: E402
from forge.studio.ui.app import StudioApp  # noqa: E402
from forge.studio.ui.widgets import Banner  # noqa: E402

TOOL = Path(__file__).resolve().parents[1]
ARCHIMATE = TOOL.parent / "diseno/modelo/drones-mantenimiento.archimate"
DOCS = TOOL.parent / "diseno"
SIZE = (150, 46)


def run(coro):
    return asyncio.run(coro)


async def wait_for(pilot, cond, timeout=20.0):
    for _ in range(int(timeout / 0.2)):
        await pilot.pause(0.2)
        try:
            if cond():
                return
        except Exception:  # noqa: BLE001 — la pantalla puede no estar lista todavía
            pass
    raise AssertionError("la TUI no llegó al estado esperado a tiempo")


@pytest.fixture
def env(tmp_path):
    store = ProjectStore(tmp_path / "reg.json", tmp_path / "projects")
    info = store.create("Proyecto de prueba", ARCHIMATE, DOCS, AgentSettings(engine="custom", custom_argv=("true",), max_attempts=1))
    creds = CredentialStore(tmp_path / "cred.json")
    return store, creds, info


def banner_text(screen, sel="#banner"):
    return str(screen.query_one(sel, Banner).render())


def test_home_lists_projects_and_opens_the_dashboard_with_all_contexts(env):
    store, creds, info = env

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: app.screen.query_one(DataTable).row_count == 1)
            await pilot.press("enter")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "DomainsScreen" and app.screen.query_one(DataTable).row_count == 9)
    run(go())


def test_new_project_flow_analyzes_the_model_and_creates_it(env, tmp_path):
    store, creds, _ = env

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: type(app.screen).__name__ == "HomeScreen")
            await pilot.press("n")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "NewProjectScreen")
            s = app.screen
            s.query_one("#name", Input).value = "Otro modelo"
            s.query_one("#archimate", Input).value = str(ARCHIMATE)
            await wait_for(pilot, lambda: "Este modelo todavía no sirve" in str(s.query_one("#summary").render()))   # sin docs: no apto
            assert s.query_one("#create").disabled
            s.query_one("#docs", Input).value = str(DOCS)
            await wait_for(pilot, lambda: not s.query_one("#create").disabled)                                      # con docs: listo
            assert "9 contextos" in str(s.query_one("#summary").render())
            await pilot.click("#create")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "DomainsScreen")
        assert [p.name for p in store.list()] == ["Proyecto de prueba", "Otro modelo"] and (tmp_path / "projects/otro-modelo/forge.toml").exists()
    run(go())


def test_new_project_rejects_a_file_that_is_not_a_model(env):
    store, creds, _ = env

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: type(app.screen).__name__ == "HomeScreen")
            await pilot.press("n")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "NewProjectScreen")
            app.screen.query_one("#archimate", Input).value = str(TOOL / "README.md")
            await wait_for(pilot, lambda: "no sirve" in str(app.screen.query_one("#summary").render()))
            assert app.screen.query_one("#create").disabled
    run(go())


def _choose(screen, lang="python", arch="hexagonal", style="microservicio", db="postgresql", patterns=()):
    """El arquitecto elige explícitamente cada opción: el formulario no trae ninguna elegida."""
    screen.query_one("#language", Select).value = lang
    screen.query_one("#architecture", Select).value = arch
    screen.query_one("#style", Select).value = style
    screen.query_one("#database", Select).value = db
    sel = screen.query_one("#patterns", SelectionList)
    for p in patterns:
        sel.select(p)


def _open_decision(app, pilot, context):
    async def go():
        await pilot.press("enter")
        await wait_for(pilot, lambda: type(app.screen).__name__ == "DomainsScreen" and app.screen.query_one(DataTable).row_count == 9)
        rows = [r.context for r in app.screen.rows]
        for _ in range(rows.index(context)):
            await pilot.press("down")
        await pilot.press("enter")
        await wait_for(pilot, lambda: type(app.screen).__name__ == "DecisionScreen")
    return go()


def test_decision_form_starts_blank_and_refuses_to_save_until_everything_is_chosen(env):
    store, creds, info = env

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: type(app.screen).__name__ == "HomeScreen")
            await _open_decision(app, pilot, "Intervenciones")
            s = app.screen
            assert all(not isinstance(s.query_one(f"#{i}", Select).value, str) for i in ("language", "architecture", "style", "database"))
            assert list(s.query_one("#patterns", SelectionList).selected) == []                  # ningún patrón preseleccionado
            assert not any(w in str(s.query_one("#advice").render()).lower() for w in ("recomend", "evaluaci", "aconsej"))
            await pilot.press("ctrl+s")
            await pilot.pause(0.3)
            assert "Elige el lenguaje" in banner_text(s) and not (info.root / "decisiones/intervenciones.toml").exists()
            _choose(s, "csharp", "clean-ddd", "microservicio", "mongodb", patterns=("cqrs",))
            s.query_one("#why-lenguaje").text = "C# por tipado fuerte y soporte de DDD en el agregado Orden de trabajo."
            await pilot.press("ctrl+s")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "DomainsScreen")
        saved = (info.root / "decisiones/intervenciones.toml").read_text(encoding="utf-8")
        assert 'contexto = "Intervenciones"' in saved and "tipado fuerte" in saved and "cqrs = true" in saved and "cache = false" in saved
    run(go())


def test_pattern_dependency_is_reported_in_the_form_not_silently_added(env):
    store, creds, info = env

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: type(app.screen).__name__ == "HomeScreen")
            await _open_decision(app, pilot, "Intervenciones")
            s = app.screen
            _choose(s, patterns=("pipeline",))                      # pipeline requiere cqrs
            await pilot.press("ctrl+s")
            await pilot.pause(0.3)
            assert "cqrs" in banner_text(s) and "cqrs" not in s.query_one("#patterns", SelectionList).selected
    run(go())


def test_tokens_are_saved_masked_and_deleted(env):
    store, creds, info = env

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: type(app.screen).__name__ == "HomeScreen")
            await pilot.press("k")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "AgentScreen")
            s = app.screen
            s.query_one("TabbedContent").active = "tab-tokens"
            await pilot.pause(0.3)
            s.query_one("#secret", Input).value = "sk-ant-api03-muy-secreto-1234"
            await pilot.click("#save-token")
            await pilot.pause(0.3)
            assert creds.get("ANTHROPIC_API_KEY") == "sk-ant-api03-muy-secreto-1234"
            table = s.query_one("#tokens", DataTable)
            cells = [str(table.get_cell_at((0, c))) for c in range(2)]
            assert cells[0] == "ANTHROPIC_API_KEY" and "muy-secreto" not in cells[1] and cells[1].endswith("1234")
            assert s.query_one("#secret", Input).value == ""                                  # el campo se limpia
            await pilot.click("#del-token")
            await pilot.pause(0.3)
            assert creds.names() == []
    run(go())


def test_invalid_token_name_is_reported_not_stored(env):
    store, creds, _ = env

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: type(app.screen).__name__ == "HomeScreen")
            await pilot.press("k")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "AgentScreen")
            s = app.screen
            s.query_one("TabbedContent").active = "tab-tokens"
            await pilot.pause(0.3)
            s.query_one("#varname", Input).value = "nombre malo"
            s.query_one("#secret", Input).value = "abc"
            await pilot.click("#save-token")
            await pilot.pause(0.3)
            assert "no es un nombre de variable válido" in banner_text(s, "#tbanner") and creds.names() == []
    run(go())


def test_engine_and_model_are_saved_into_the_project(env):
    store, creds, info = env

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: type(app.screen).__name__ == "HomeScreen")
            await pilot.press("k")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "AgentScreen")
            s = app.screen
            s.query_one("#engine", Select).value = "claude"
            await pilot.pause(0.2)
            s.query_one("#model", Input).value = "sonnet"
            await pilot.click("#save-engine")
            await pilot.pause(0.4)
    before = info.toml.read_bytes()
    run(go())
    cfg = store.load(info)
    assert (cfg.agent.engine, cfg.agent.model) == ("claude", "sonnet")
    assert info.toml.read_bytes() == before                               # lo personal no toca forge.toml (que viaja con git)


def test_reset_button_returns_to_the_team_value(env):
    store, creds, info = env
    store.save_agent(info, projects.AgentSettings(engine="claude", model="sonnet"))

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: type(app.screen).__name__ == "HomeScreen")
            await pilot.press("k")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "AgentScreen")
            await wait_for(pilot, lambda: app.screen.query_one("#model", Input).value == "sonnet")
            await pilot.click("#reset")
            await wait_for(pilot, lambda: app.screen.query_one("#model", Input).value == "")
    run(go())
    assert store.load(info).agent.engine == "custom"


def test_build_screen_streams_the_log_and_reports_failure_without_crashing(env):
    store, creds, info = env

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: type(app.screen).__name__ == "HomeScreen")
            await _open_decision(app, pilot, "Repuestos del Taller")
            _choose(app.screen)
            await pilot.press("ctrl+s")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "DomainsScreen")
            await pilot.press("b")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "BuildScreen")
            s = app.screen
            await pilot.click("#start")
            await wait_for(pilot, lambda: not s.query_one("#start").disabled and s.handle is not None and not s.handle.running, 90)
            await pilot.pause(1.5)
            assert s.handle.results == {"repuestos-del-taller": 1}                 # el agente «true» no escribe nada: las puertas fallan
            assert "Terminó con fallos" in banner_text(s)
            assert s.query_one("#log", RichLog).lines                            # el log llegó a la pantalla
    run(go())


def test_assemble_without_built_domains_explains_instead_of_crashing(env):
    store, creds, info = env

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: type(app.screen).__name__ == "HomeScreen")
            await _open_decision(app, pilot, "Repuestos del Taller")
            _choose(app.screen)
            await pilot.press("ctrl+s")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "DomainsScreen")
            await pilot.press("a")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "AssembleScreen")
            await pilot.click("#run")
            await wait_for(pilot, lambda: not app.screen.running and "fallos" in banner_text(app.screen))
    run(go())


def test_forge_studio_is_a_registered_command_and_does_not_need_forge_toml(tmp_path):
    import subprocess
    r = subprocess.run([sys.executable, "-m", "forge", "-c", str(tmp_path / "no-existe.toml"), "studio", "--help"], cwd=TOOL, capture_output=True, text=True)
    assert r.returncode == 0 and "studio" in r.stdout.lower()
    r = subprocess.run([sys.executable, "-m", "forge", "--help"], cwd=TOOL, capture_output=True, text=True)
    assert "studio" in r.stdout


def test_draft_justifications_show_as_grey_suggestions_and_empty_fields_drop_them(env):
    store, creds, info = env
    (info.root / "decisiones").mkdir(exist_ok=True)
    (info.root / "decisiones/intervenciones.toml").write_text(
        'contexto = "Intervenciones"\nlenguaje = "csharp"\narquitectura = "clean-ddd"\nestilo = "microservicio"\nbase_de_datos = "mongodb"\npuerto = 5101\n'
        '[patrones]\ncache = true\nmemento = true\ncifrado = { usar = true, algoritmo = "aes-256-gcm" }\n[justificacion]\nlenguaje = "Ejemplo: C# por tipado fuerte y soporte de DDD."\n'
        'estilo = "Elegimos microservicio porque publica y consume eventos del ciclo de la OT."\n', encoding="utf-8")

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: type(app.screen).__name__ == "HomeScreen")
            await _open_decision(app, pilot, "Intervenciones")
            s = app.screen
            lang, estilo = s.query_one("#why-lenguaje"), s.query_one("#why-estilo")
            assert lang.text == "" and lang.placeholder.startswith("Ejemplo:")                 # borrador: sugerencia gris
            assert estilo.text.startswith("Elegimos microservicio")                           # argumento real: se conserva
            await pilot.press("ctrl+s")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "DomainsScreen")
    run(go())
    saved = (info.root / "decisiones/intervenciones.toml").read_text(encoding="utf-8")
    assert "Ejemplo:" not in saved and "Elegimos microservicio" in saved


def test_assemble_failure_for_unjustified_decisions_tells_where_to_fix_it(env):
    store, creds, info = env

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: type(app.screen).__name__ == "HomeScreen")
            await _open_decision(app, pilot, "Repuestos del Taller")
            _choose(app.screen)
            await pilot.press("ctrl+s")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "DomainsScreen")
            await pilot.press("a")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "AssembleScreen")
            s = app.screen
            s.lines.append("❌ política: decisiones justificadas:")          # lo que imprime el ensamblado real
            s.done(1)
            assert "justificar cada decisión" in banner_text(s)
    run(go())


def test_a_chosen_pattern_asks_where_it_applies_and_saves_it(env):
    store, creds, info = env

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: type(app.screen).__name__ == "HomeScreen")
            await _open_decision(app, pilot, "Intervenciones")
            s = app.screen
            where = s.query_one("#where-strategy", Input)
            assert not where.display and not s.query_one("#where-title").display                # nada elegido: no se pregunta nada
            _choose(s, "csharp", "clean-ddd", "microservicio", "mongodb", patterns=("strategy",))
            await pilot.pause(0.4)
            assert where.display and s.query_one("#where-title").display                         # elegido: pide dónde se aplica
            assert not s.query_one("#where-decorator", Input).display
            await pilot.press("ctrl+s")
            await pilot.pause(0.3)
            assert "aplicar_en" in banner_text(s) and not (info.root / "decisiones/intervenciones.toml").exists()
            where.value = "el cálculo de horas-hombre de una orden"
            await pilot.press("ctrl+s")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "DomainsScreen")
        saved = (info.root / "decisiones/intervenciones.toml").read_text(encoding="utf-8")
        assert 'strategy = { usar = true, aplicar_en = "el cálculo de horas-hombre de una orden" }' in saved
    run(go())


def test_platform_screen_asks_for_every_platform_decision_without_preselecting_any(env):
    store, creds, info = env

    async def go():
        app = StudioApp(store, creds)
        async with app.run_test(size=SIZE) as pilot:
            await wait_for(pilot, lambda: app.screen.query_one(DataTable).row_count == 1)
            await pilot.press("enter")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "DomainsScreen" and app.screen.query_one(DataTable).row_count == 9)
            await wait_for(pilot, lambda: "sin decidir" in str(app.screen.query_one("#platform-text").render()))
            await pilot.press("p")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "PlatformScreen")
            claves = ("mensajeria", "gateway", "frontend", "despliegue", "simuladores")
            assert all(app.screen.query_one(f"#{c}", Select).value is Select.NULL for c in claves)      # nada viene elegido
            await pilot.press("ctrl+s")
            await wait_for(pilot, lambda: "Elige:" in banner_text(app.screen))                         # no se guarda sin elegir todo
            for c, v in zip(claves, ("rabbitmq", "propio", "ninguno", "propio", "ninguno")):
                app.screen.query_one(f"#{c}", Select).value = v
            app.screen.query_one("#img-mongo", Input).value = "mongo:8"
            await pilot.press("ctrl+s")
            await wait_for(pilot, lambda: type(app.screen).__name__ == "DomainsScreen")
            await wait_for(pilot, lambda: "sin decidir" not in str(app.screen.query_one("#platform-text").render()))
        g = (Path(info.root) / "decisiones/plataforma.toml").read_text(encoding="utf-8")
        for linea in ('mensajeria = "rabbitmq"', 'gateway = "propio"', 'frontend = "ninguno"', 'despliegue = "propio"', 'simuladores = "ninguno"', 'mongo = "mongo:8"'):
            assert linea in g
    run(go())
