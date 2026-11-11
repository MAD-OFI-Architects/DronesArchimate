"""Inicio: tus proyectos (cada uno = un .archimate + sus decisiones y su producto generado)."""
from __future__ import annotations

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static

from ... import config
from ..projects import ProjectInfo
from .widgets import Banner, PathPicker

LOGO = Text.from_markup("[b #7aa2f7]◆  A R C H I F O R G E[/]  [#7dcfff]Studio[/]")
STEPS = (
    "[b]1  Proyecto[/] · elige tu .archimate\n"
    "[b]2  Decisiones[/] · lenguaje, arquitectura, BD y patrones por dominio; la herramienta aconseja, tú decides\n"
    "[b]3  Agente[/] · motor, modelo y tokens de API\n"
    "[b]4  Construir[/] · etapas con puertas de calidad en vivo\n"
    "[b]5  Ensamblar[/] · compose, gateway y microfrontends\n\n"
    "[dim]Los tokens se guardan fuera del proyecto (permisos 600) y solo viajan al agente por entorno.[/]"
)


class HomeScreen(Screen):
    BINDINGS = [("n", "new", "Nuevo"), ("i", "import_", "Importar forge.toml"), ("k", "tokens", "Agente y tokens"),
                ("d", "forget", "Olvidar"), ("q", "app.quit", "Salir")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(LOGO, id="logo")
        yield Static("Genera servicios y microfrontends desde un modelo ArchiMate, verificados con puertas automáticas.", id="tagline")
        with Horizontal(id="body"):
            with Vertical(id="projects", classes="card"):
                yield Static("Tus proyectos", classes="card-title")
                yield DataTable(id="table", cursor_type="row", zebra_stripes=True)
                yield Banner(id="banner")
                with Horizontal(classes="buttons"):
                    yield Button("Abrir", id="open", variant="primary")
                    yield Button("Nuevo", id="new", variant="success")
                    yield Button("Agente y tokens", id="tokens")
            with Vertical(id="about", classes="card"):
                yield Static("Cómo funciona", classes="card-title")
                yield Static(STEPS)
        yield Footer()

    def on_mount(self) -> None:
        t = self.query_one(DataTable)
        t.add_columns("Proyecto", "Modelo", "Motor", "Ubicación")
        self.refresh_table()
        t.focus()

    def on_screen_resume(self) -> None:
        self.refresh_table()

    def refresh_table(self) -> None:
        t = self.query_one(DataTable)
        t.clear()
        self.projects = self.app.store.list()
        for p in self.projects:
            try:
                cfg = config.load(p.toml)
                row = (p.name, cfg.archimate.name, f"{cfg.agent.engine}" + (f" · {cfg.agent.model}" if cfg.agent.model else ""), str(p.root))
            except Exception as e:  # noqa: BLE001
                row = (p.name, "⚠ no se pudo leer", str(e)[:40], str(p.root))
            t.add_row(*row, key=str(p.toml))
        if not self.projects:
            self.query_one(Banner).show("info", "Aún no tienes proyectos. Pulsa [b]n[/b] para crear uno desde un archivo .archimate.")
        else:
            self.query_one(Banner).clear()

    def selected(self) -> ProjectInfo | None:
        t = self.query_one(DataTable)
        if not self.projects or t.row_count == 0:
            return None
        try:
            return self.projects[t.cursor_row]
        except IndexError:
            return None

    # ---- acciones
    def action_new(self) -> None:
        from .project import NewProjectScreen
        self.app.push_screen(NewProjectScreen())

    def action_tokens(self) -> None:
        from .agent import AgentScreen
        self.app.push_screen(AgentScreen(self.selected()))

    def action_import_(self) -> None:
        from pathlib import Path
        self.app.push_screen(PathPicker("Elige la carpeta del proyecto (la que contiene forge.toml)", Path.home(), None), self._imported)

    def _imported(self, folder) -> None:
        if folder is None:
            return
        toml = folder / "forge.toml"
        if not toml.exists():
            self.query_one(Banner).show("error", f"No hay forge.toml en {folder}.")
            return
        self.app.store.register(toml)
        self.refresh_table()

    def action_forget(self) -> None:
        p = self.selected()
        if p:
            self.app.store.forget(p)
            self.refresh_table()
            self.query_one(Banner).show("info", f"«{p.name}» ya no aparece aquí. No se borró ningún archivo.")

    def action_open(self) -> None:
        p = self.selected()
        if p:
            from .domains import DomainsScreen
            self.app.push_screen(DomainsScreen(p))

    @on(DataTable.RowSelected)
    def _row(self) -> None:
        self.action_open()

    @on(Button.Pressed, "#open")
    def _open(self) -> None:
        self.action_open()

    @on(Button.Pressed, "#new")
    def _new(self) -> None:
        self.action_new()

    @on(Button.Pressed, "#tokens")
    def _tokens(self) -> None:
        self.action_tokens()
