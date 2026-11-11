"""Construir y ensamblar: progreso por etapa y log en vivo, con las puertas de calidad en verde o rojo."""
from __future__ import annotations

from rich.text import Text
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, RichLog, Select, SelectionList, Static, Switch
from textual.widgets.selection_list import Selection

from ...credentials import mask
from ..service import BuildHandle, StageRow, Studio, StudioError
from .widgets import Banner

SCOPES = [("Pipeline completo", None), ("Solo microfrontends (S40)", "S40-microfrontend"), ("Solo humo con docker (S30)", "S30-smoke"),
          ("Solo revisión independiente (S50)", "S50-verify")]
GLYPH = {"passed": ("■", "#9ece6a"), "running": ("▶", "#e0af68"), "failed": ("✗", "#f7768e"), "skipped": ("–", "dim"), "pending": ("□", "dim")}


def log_line(line: str) -> Text:
    style = "#9ece6a" if "✅" in line else "#f7768e" if ("❌" in line or "FALLÓ" in line) else "#e0af68" if ("⚠" in line or "OMITIDA" in line) else ""
    return Text(line, style=style)


def ribbon(rows: list[StageRow]) -> Text:
    t = Text()
    for r in rows:
        g, style = GLYPH.get(r.status, GLYPH["pending"])
        t.append(g + " ", style=style)
    return t


class BuildScreen(Screen):
    BINDINGS = [("escape", "back", "Volver"), ("ctrl+b", "start", "Construir")]

    def __init__(self, studio: Studio):
        super().__init__()
        self.studio = studio
        self.handle: BuildHandle | None = None

    def compose(self) -> ComposeResult:
        s = self.studio
        yield Header()
        with Horizontal():
            with VerticalScroll(id="opts", classes="card"):
                yield Static("Qué construir", classes="card-title")
                yield SelectionList(*[Selection(f"{d.context}  [dim]{d.language} · {d.architecture}[/]", d.slug, "completo" not in s.status_of(d))
                                      for d in s.cfg.domains], id="domains")
                yield Label("Alcance", classes="field-label")
                yield Select(SCOPES, value=None, allow_blank=False, id="scope")
                yield Label("Vueltas (reintenta etapas fallidas)", classes="field-label")
                yield Input("1", id="laps", type="integer")
                with Horizontal(classes="switch-row"):
                    yield Switch(False, id="force")
                    yield Label("Repetir etapas ya completadas")
                yield Static("", id="agentline")
                yield Static("", id="tools")
                yield Banner(id="banner")
                with Horizontal(classes="buttons"):
                    yield Button("Construir", id="start", variant="success")
                    yield Button("Cancelar", id="stop", variant="error", disabled=True)
            with Vertical(id="run", classes="card"):
                yield Static("Progreso", classes="card-title")
                yield DataTable(id="progress", cursor_type="none")
                yield RichLog(id="log", markup=False, wrap=True, highlight=False)
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Construir"
        t = self.query_one("#progress", DataTable)
        t.add_columns("Dominio", "Etapas", "Ahora", "Estado")
        self.refresh_progress()
        c = self.studio.cfg.agent
        names = self.studio.creds.names()
        tokens = ", ".join(f"{n} ({mask(self.studio.creds.get(n))})" for n in names) or "ninguno guardado (el agente usará su propia sesión)"
        self.query_one("#agentline", Static).update(f"[b]Agente:[/] {c.engine}" + (f" · {c.model}" if c.model else "") + f"\n[b]Tokens:[/] {tokens}")
        self.check_tools()
        self.set_interval(1.0, self.refresh_progress)

    @work(thread=True, exclusive=True, group="tools")
    def check_tools(self) -> None:
        checks = self.studio.tool_checks(self.studio.cfg.domains)
        txt = Text()
        for name, ok, ver in checks:
            txt.append("✓ " if ok else "✗ ", style="#9ece6a" if ok else "#f7768e")
            txt.append(name, style="" if ok else "#f7768e")
            txt.append(f" · {ver[:34]}\n" if ok else " · falta o versión insuficiente\n", style="dim")
        self.app.call_from_thread(self.query_one("#tools", Static).update, txt)

    def refresh_progress(self) -> None:
        t = self.query_one("#progress", DataTable)
        t.clear()
        for d in self.studio.cfg.domains:
            rows = self.studio.progress(d)
            cur = next((r for r in rows if r.status == "running"), None) or next((r for r in rows if r.status in ("failed", "pending")), None)
            done = sum(1 for r in rows if r.status in ("passed", "skipped"))
            state = Text(f"{done}/{len(rows)}", style="bold #9ece6a" if done == len(rows) else "bold")
            t.add_row(Text(d.context, style="bold"), ribbon(rows), (cur.id if cur else "—"), state)
        if self.handle and not self.handle.running and self.query_one("#stop", Button).disabled is False:
            self.finish()

    def selected_domains(self):
        slugs = set(self.query_one("#domains", SelectionList).selected)
        return [d for d in self.studio.cfg.domains if d.slug in slugs]

    # ---- ejecutar
    def action_start(self) -> None:
        if self.handle and self.handle.running:
            return
        b = self.query_one(Banner)
        log = self.query_one("#log", RichLog)
        scope = self.query_one("#scope", Select).value
        try:
            laps = max(1, int(self.query_one("#laps", Input).value or 1))
            sink = lambda line: self.app.call_from_thread(log.write, log_line(line))  # noqa: E731
            self.handle = self.studio.start_build(self.selected_domains(), sink, laps=laps, only=scope or None,
                                                  force=self.query_one("#force", Switch).value or bool(scope))
        except StudioError as e:
            b.show("error", str(e))
            return
        b.show("info", "Construyendo… puedes cancelar: se detiene al terminar la etapa en curso.")
        self.query_one("#start", Button).disabled = True
        self.query_one("#stop", Button).disabled = False
        log.clear()

    def finish(self) -> None:
        self.query_one("#start", Button).disabled = False
        self.query_one("#stop", Button).disabled = True
        bad = [s for s, c in (self.handle.results if self.handle else {}).items() if c]
        b = self.query_one(Banner)
        if bad:
            b.show("error", f"Terminó con fallos en: {', '.join(bad)}. Revisa el log; las etapas hechas quedan guardadas.")
        else:
            b.show("ok", "Todo construido y verificado. Siguiente paso: ensamblar.")
        self.app.bell()

    @on(Button.Pressed, "#start")
    def _start(self) -> None:
        self.action_start()

    @on(Button.Pressed, "#stop")
    def _stop(self) -> None:
        if self.handle:
            self.handle.cancel()
            self.query_one(Banner).show("warn", "Cancelando al terminar la etapa en curso…")

    def action_back(self) -> None:
        if self.handle and self.handle.running:
            self.query_one(Banner).show("warn", "Hay una construcción en curso: cancélala primero.")
            return
        self.app.pop_screen()


class AssembleScreen(Screen):
    BINDINGS = [("escape", "back", "Volver")]

    def __init__(self, studio: Studio):
        super().__init__()
        self.studio = studio
        self.running = False
        self.lines: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="card"):
            yield Static("Ensamblado: compose, gateway, shell de microfrontends y humo completo", classes="card-title")
            yield Banner(id="banner")
            yield RichLog(id="log", markup=False, wrap=True, highlight=False)
            with Horizontal(classes="buttons"):
                yield Button("Ensamblar", id="run", variant="success")
                yield Button("Volver", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Ensamblar"

    @on(Button.Pressed, "#run")
    def _run(self) -> None:
        if self.running:
            return
        self.running = True
        self.query_one("#run", Button).disabled = True
        self.query_one("#log", RichLog).clear()
        self.lines.clear()
        self.query_one(Banner).show("info", "Ensamblando… (npm y docker pueden tardar varios minutos)")
        self.go()

    @work(thread=True)
    def go(self) -> None:
        log = self.query_one("#log", RichLog)
        def sink(line: str) -> None:
            self.lines.append(line)
            self.app.call_from_thread(log.write, log_line(line))
        code = self.studio.assemble(sink)
        self.app.call_from_thread(self.done, code)

    def done(self, code: int) -> None:
        self.running = False
        self.query_one("#run", Button).disabled = False
        hint = ("La política del proyecto pide justificar cada decisión y hay borradores o textos muy cortos. Vuelve a Dominios, pulsa Enter sobre el dominio "
                "y responde los «¿Por qué…?»; luego ensambla otra vez." if any("decisiones justificadas" in l for l in self.lines) else "")
        self.query_one(Banner).show("ok" if code == 0 else "error",
                                    "Ensamblado y verificado. Levanta todo con: docker compose up --build" if code == 0
                                    else "El ensamblado tiene fallos; revisa el log." + (f"\n{hint}" if hint else ""))

    @on(Button.Pressed, "#back")
    def _back(self) -> None:
        self.action_back()

    def action_back(self) -> None:
        if not self.running:
            self.app.pop_screen()
