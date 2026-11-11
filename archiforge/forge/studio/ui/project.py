"""Nuevo proyecto: elige el .archimate, ve al instante si sirve, y la TUI genera el forge.toml."""
from __future__ import annotations

from pathlib import Path

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static

from ..model import ModelReport, inspect_model
from ..projects import ENGINES, AgentSettings, ProjectError
from .widgets import Banner, PathPicker

ENGINE_LABELS = [("OpenCode (cualquier proveedor)", "opencode"), ("Claude Code", "claude"), ("Comando propio", "custom")]


class NewProjectScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Volver")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with VerticalScroll(classes="card", id="form"):
                yield Static("Nuevo proyecto", classes="card-title")
                yield Label("Nombre", classes="field-label")
                yield Input(placeholder="p. ej. Mantenimiento de drones", id="name")
                yield Label("Archivo ArchiMate (.archimate)", classes="field-label")
                with Horizontal(classes="pathrow"):
                    yield Input(placeholder="/ruta/al/modelo.archimate", id="archimate")
                    yield Button("Examinar…", id="pick-model")
                yield Label("Documentos de fase (opcional, carpeta)", classes="field-label")
                with Horizontal(classes="pathrow"):
                    yield Input(placeholder="carpeta con Fase02/…, Fase05/… (si tu modelo los usa)", id="docs")
                    yield Button("Examinar…", id="pick-docs")
                yield Label("Motor del agente", classes="field-label")
                yield Select(ENGINE_LABELS, value="opencode", allow_blank=False, id="engine")
                yield Label("Modelo (opcional; se puede cambiar luego)", classes="field-label")
                yield Input(placeholder="proveedor/modelo, p. ej. opencode/deepseek-v4.1-flash-free", id="model")
                yield Banner(id="banner")
                with Horizontal(classes="buttons"):
                    yield Button("Crear proyecto", id="create", variant="success", disabled=True)
                    yield Button("Cancelar", id="cancel")
            with VerticalScroll(classes="card", id="report"):
                yield Static("Qué entiende la herramienta de tu modelo", classes="card-title")
                yield Static("Elige un archivo .archimate para analizarlo.", id="summary", classes="muted")
        yield Footer()

    # ---- análisis del modelo (en un hilo: el parser tarda)
    @on(Input.Changed, "#archimate")
    @on(Input.Changed, "#docs")
    def _changed(self) -> None:
        path = self.query_one("#archimate", Input).value.strip()
        docs = self.query_one("#docs", Input).value.strip()
        if not path:
            self.query_one("#create", Button).disabled = True
            self.query_one("#summary", Static).update("Elige un archivo .archimate para analizarlo.")
            return
        self.query_one("#summary", Static).update("[dim]Analizando…[/]")
        self.analyze(Path(path).expanduser(), Path(docs).expanduser() if docs else None)

    @work(thread=True, exclusive=True)
    def analyze(self, path: Path, docs: Path | None) -> None:
        if docs is not None and not docs.is_dir():
            report = ModelReport(path, errors=[f"La carpeta de documentos «{docs}» no existe."])
        else:
            report = inspect_model(path, docs)
        self.app.call_from_thread(self.show_report, report)

    def show_report(self, r: ModelReport) -> None:
        lines = []
        if r.ok:
            t = r.totals
            lines.append(f"[b $success]✓ Modelo listo[/]  {t['contextos']} contextos · {t['agregados']} agregados · {t['comandos']} comandos\n")
            lines += [f"  [b]{c.name}[/]  [dim]{c.classification}[/]\n    {c.aggregates} agregados · {c.commands} comandos · "
                      f"publica {c.published} · consume {c.consumed}" for c in r.contexts]
        else:
            lines.append("[b $error]✗ Este modelo todavía no sirve[/]\n")
        for e in r.errors[:8]:
            lines.append(f"[$error]✗[/] {e}")
        if len(r.errors) > 8:
            lines.append(f"[dim]… y {len(r.errors) - 8} problemas más[/]")
        for w in r.warnings[:5]:
            lines.append(f"[$warning]![/] {w}")
        for h in r.hints:
            lines.append(f"\n[$accent]→ {h}[/]")
        self.query_one("#summary", Static).update("\n".join(lines))
        self.query_one("#create", Button).disabled = not r.ok

    # ---- selectores
    @on(Button.Pressed, "#pick-model")
    def _pick_model(self) -> None:
        self.app.push_screen(PathPicker("Elige tu archivo .archimate", Path.home(), ".archimate"), lambda p: p and self._set("#archimate", p))

    @on(Button.Pressed, "#pick-docs")
    def _pick_docs(self) -> None:
        self.app.push_screen(PathPicker("Elige la carpeta de documentos de fase", Path.home(), None), lambda p: p and self._set("#docs", p))

    def _set(self, sel: str, p: Path) -> None:
        self.query_one(sel, Input).value = str(p)

    # ---- crear
    @on(Button.Pressed, "#cancel")
    def _cancel(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#create")
    def _create(self) -> None:
        b = self.query_one(Banner)
        engine = self.query_one("#engine", Select).value
        try:
            if engine == "custom":
                raise ProjectError("El comando propio se configura después, en «Agente y tokens».")
            docs = self.query_one("#docs", Input).value.strip()
            info = self.app.store.create(self.query_one("#name", Input).value, Path(self.query_one("#archimate", Input).value).expanduser(),
                                         Path(docs).expanduser() if docs else None,
                                         AgentSettings(engine=str(engine), model=self.query_one("#model", Input).value.strip()))
        except ProjectError as e:
            b.show("error", str(e))
            return
        self.app.pop_screen()
        from .domains import DomainsScreen
        self.app.push_screen(DomainsScreen(info))
