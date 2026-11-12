"""Panel del proyecto: los dominios del modelo, su estado y las políticas del equipo (si el proyecto declara alguna)."""
from __future__ import annotations

from rich.text import Text
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll, Horizontal
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from ..projects import ProjectInfo
from ..service import DomainRow, Studio
from .widgets import Banner

LANG = {"csharp": "C#", "python": "Python", "java": "Java"}
ARCH = {"clean-ddd": "Clean + DDD", "hexagonal": "Hexagonal"}
DB = {"mongodb": "MongoDB", "postgresql": "PostgreSQL"}


class DomainsScreen(Screen):
    BINDINGS = [("enter", "decide", "Decidir"), ("b", "build", "Construir"), ("a", "assemble", "Ensamblar"),
                ("p", "platform", "Plataforma"), ("g", "agent", "Agente y tokens"), ("r", "reload", "Recargar"), ("escape", "app.pop_screen", "Proyectos")]

    def __init__(self, info: ProjectInfo):
        super().__init__()
        self.info = info
        self.studio: Studio | None = None
        self.rows: list[DomainRow] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="left"):
                with Vertical(classes="card", id="domains"):
                    yield Static("Dominios del modelo", classes="card-title")
                    yield DataTable(id="table", cursor_type="row", zebra_stripes=True)
                    yield Banner(id="banner")
                with Vertical(classes="card", id="platform"):
                    yield Static("Plataforma", classes="card-title")
                    yield Static("…", id="platform-text")
                with Vertical(classes="card", id="portfolio"):
                    yield Static("Políticas del proyecto", classes="card-title")
                    yield Static("…", id="rules")
            with Vertical(id="right", classes="card"):
                yield Static("Detalle", classes="card-title")
                with VerticalScroll(id="detail"):
                    yield Static("Cargando el modelo…", id="detail-text", classes="muted")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = self.info.name
        t = self.query_one(DataTable)
        t.add_columns("Dominio", "Agr/Cmd", "Lenguaje", "Arquitectura", "BD", "Estado")
        t.focus()
        self.load()

    def on_screen_resume(self) -> None:
        if self.studio:
            self.action_reload()

    @work(thread=True, exclusive=True)
    def load(self) -> None:
        try:
            if self.studio is None:
                self.studio = Studio(self.app.store.load(self.info), self.app.creds)
            else:
                self.studio.reload()
            rows, rules = self.studio.rows(), self.studio.policy_findings()
        except Exception as e:  # noqa: BLE001 — se muestra, no se cae la TUI
            self.app.call_from_thread(self.query_one(Banner).show, "error", f"No se pudo cargar el proyecto: {e}")
            return
        self.app.call_from_thread(self.fill, rows, rules)

    def fill(self, rows: list[DomainRow], rules: list[str]) -> None:
        self.rows = rows
        cfg = self.studio.cfg
        self.sub_title = f"{self.info.name}  ·  agente: {cfg.agent.engine}" + (f" · {cfg.agent.model}" if cfg.agent.model else "")
        t = self.query_one(DataTable)
        keep = t.cursor_row
        t.clear()
        for r in rows:
            d = r.domain
            if d:
                st = Text(r.status, style="bold #9ece6a" if "completo" in r.status else "#e0af68")
                t.add_row(Text(r.context, style="bold"), f"{r.aggregates} / {r.commands}", LANG.get(d.language, d.language),
                          ARCH.get(d.architecture, d.architecture), DB.get(d.database, d.database), st)
            else:
                t.add_row(Text(r.context, style="dim"), f"{r.aggregates} / {r.commands}", Text("—", style="dim"), Text("—", style="dim"),
                          Text("—", style="dim"), Text("se simula", style="dim italic"))
        if rows:
            t.move_cursor(row=min(keep, len(rows) - 1))
            self.show_detail(min(keep, len(rows) - 1))
        txt = Text()
        for line in rules:
            ok = line.startswith("✓")
            txt.append(line + "\n", style="#9ece6a" if ok else "#f7768e")
        self.query_one("#rules", Static).update(txt)
        canal, gateway = cfg.platform.get("mensajeria"), cfg.platform.get("gateway")
        self.query_one("#platform-text", Static).update(
            f"Canal de eventos: [b]{canal or '[b $warning]sin decidir[/]'}[/]\nGateway: [b]{gateway or '[b $warning]sin decidir[/]'}[/]"
            + ("" if canal and gateway else "\n[dim]pulsa [b]p[/b] para decidirlos[/]"))
        self.query_one("#portfolio").display = bool(rules)         # sin políticas declaradas, el panel no existe
        self.query_one(Banner).clear()
        if not any(r.decided for r in rows):
            self.query_one(Banner).show("info", "Elige un dominio y pulsa [b]Enter[/b] para tomar sus decisiones. Los demás se simulan.")

    @on(DataTable.RowHighlighted)
    def _hl(self, ev: DataTable.RowHighlighted) -> None:
        if self.rows:
            self.show_detail(ev.cursor_row)

    def show_detail(self, i: int) -> None:
        if not self.studio or i >= len(self.rows):
            return
        r = self.rows[i]
        f = self.studio.facts(r.context)
        L = [f"[b $primary]{r.context}[/]  [dim]{f['classification']}[/]", f"{f['purpose']}", "",
             f"[b]Agregados:[/] {', '.join(f['aggregates']) or '—'}",
             f"[b]Publica:[/] {', '.join(f['published']) or '—'}", f"[b]Consume:[/] {', '.join(f['consumed']) or '—'}", ""]
        if r.domain:
            d = r.domain
            L += ["[b $success]Decidido[/]", f"  {LANG.get(d.language, d.language)} · {ARCH.get(d.architecture, d.architecture)} · {d.style} · {DB.get(d.database, d.database)}",
                  f"  Patrones: {', '.join(k for k, v in d.patterns.items() if v.get('usar')) or '—'}", ""]
            L.append("[dim]Enter para editar sus decisiones[/]")
        else:
            L += ["[b $warning]Sin decidir (se simula)[/]", "", "[dim]Enter para decidir y construir este dominio[/]"]
        self.query_one("#detail-text", Static).update("\n".join(L))

    # ---- acciones
    def _current(self) -> DomainRow | None:
        t = self.query_one(DataTable)
        return self.rows[t.cursor_row] if self.rows and t.row_count else None

    @on(DataTable.RowSelected)
    def action_decide(self) -> None:
        r = self._current()
        if r and self.studio:
            from .decision import DecisionScreen
            self.app.push_screen(DecisionScreen(self.studio, r.context), lambda saved: saved and self.action_reload())

    def action_platform(self) -> None:
        if self.studio:
            from .platform import PlatformScreen
            self.app.push_screen(PlatformScreen(self.studio), lambda saved: saved and self.action_reload())

    def action_reload(self) -> None:
        self.load()

    def action_build(self) -> None:
        if not self.studio or not self.studio.cfg.domains:
            self.query_one(Banner).show("warn", "Primero decide al menos un dominio (Enter sobre una fila).")
            return
        from .build import BuildScreen
        self.app.push_screen(BuildScreen(self.studio))

    def action_assemble(self) -> None:
        if not self.studio:
            return
        from .build import AssembleScreen
        self.app.push_screen(AssembleScreen(self.studio))

    def action_agent(self) -> None:
        from .agent import AgentScreen
        self.app.push_screen(AgentScreen(self.info), lambda _=None: self.action_reload())
