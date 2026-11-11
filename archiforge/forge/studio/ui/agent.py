"""Agente: motor, modelo y tokens de API. Los tokens viven fuera del proyecto y solo viajan por entorno."""
from __future__ import annotations

import shlex

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Select, Static, TabbedContent, TabPane

from ... import cli
from ...credentials import KNOWN, CredentialError, CredentialStore, default_path, mask
from ..projects import ENGINES, AgentSettings, ProjectError, ProjectInfo
from .widgets import Banner

ENGINE_LABELS = [("OpenCode (cualquier proveedor)", "opencode"), ("Claude Code", "claude"), ("Comando propio", "custom")]
MODEL_HINT = {"opencode": "proveedor/modelo, p. ej. opencode/deepseek-v4.1-flash-free o github-copilot/auto",
              "claude": "alias o id, p. ej. sonnet, opus o claude-sonnet-5-5", "custom": "no aplica"}
OTHER = "__otro__"


class AgentScreen(Screen):
    BINDINGS = [("escape", "back", "Volver")]

    def __init__(self, info: ProjectInfo | None):
        super().__init__()
        self.info = info
        self.settings = AgentSettings()

    @property
    def creds(self) -> CredentialStore:
        return self.app.creds

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="tab-engine" if self.info else "tab-tokens"):
            with TabPane("Motor y modelo", id="tab-engine"):
                with VerticalScroll(classes="card"):
                    yield Static(f"Agente de «{self.info.name}»" if self.info else "Abre un proyecto para elegir su motor y modelo.", classes="card-title")
                    yield Label("Motor", classes="field-label")
                    yield Select(ENGINE_LABELS, value="opencode", allow_blank=False, id="engine")
                    yield Label("Modelo", classes="field-label")
                    yield Input(id="model")
                    yield Label("Agente de OpenCode (opcional)", classes="field-label")
                    yield Input(placeholder="forge-orchestrator", id="oc-agent")
                    yield Label("Comando propio  (usa {prompt_file} donde va la orden de trabajo)", classes="field-label")
                    yield Input(placeholder="mi-agente --archivo {prompt_file}", id="custom")
                    with Horizontal():
                        with VerticalScroll():
                            yield Label("Intentos por etapa", classes="field-label")
                            yield Input("3", id="attempts", type="integer")
                        with VerticalScroll():
                            yield Label("Tiempo máximo por intento (min)", classes="field-label")
                            yield Input("90", id="timeout", type="integer")
                    yield Static("", id="engine-status")
                    yield Banner(id="banner")
                    with Horizontal(classes="buttons"):
                        yield Button("Guardar motor y modelo", id="save-engine", variant="success", disabled=not self.info)
                        yield Button("Comprobar que está instalado", id="check")
            with TabPane("Tokens de API", id="tab-tokens"):
                with VerticalScroll(classes="card"):
                    yield Static("Tokens de API", classes="card-title")
                    yield Static(f"[dim]Se guardan en {default_path()} (permisos 600), nunca en el proyecto ni en git. "
                                 "Se pasan al agente solo como variables de entorno y jamás se imprimen.[/]")
                    yield DataTable(id="tokens", cursor_type="row", zebra_stripes=True)
                    yield Label("Proveedor", classes="field-label")
                    yield Select([(n, v) for n, v in KNOWN.items()] + [("Otro…", OTHER)], value=KNOWN["Anthropic"], allow_blank=False, id="provider")
                    yield Label("Variable de entorno", classes="field-label")
                    yield Input(KNOWN["Anthropic"], id="varname")
                    yield Label("Token", classes="field-label")
                    yield Input(password=True, placeholder="pega aquí tu token", id="secret")
                    yield Banner(id="tbanner")
                    with Horizontal(classes="buttons"):
                        yield Button("Guardar token", id="save-token", variant="success")
                        yield Button("Eliminar el seleccionado", id="del-token", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        t = self.query_one("#tokens", DataTable)
        t.add_columns("Variable", "Valor")
        self.refresh_tokens()
        if self.info:
            try:
                self.settings = AgentSettings.from_cfg(self.app.store.load(self.info).agent)
            except Exception as e:  # noqa: BLE001
                self.query_one("#banner", Banner).show("error", f"No se pudo leer el proyecto: {e}")
            s = self.settings
            self.query_one("#engine", Select).value = s.engine
            self.query_one("#model", Input).value = s.model
            self.query_one("#oc-agent", Input).value = s.opencode_agent
            self.query_one("#custom", Input).value = " ".join(shlex.quote(x) for x in s.custom_argv)
            self.query_one("#attempts", Input).value = str(s.max_attempts)
            self.query_one("#timeout", Input).value = str(s.timeout_minutes)
        self.hint()

    def hint(self) -> None:
        eng = str(self.query_one("#engine", Select).value)
        self.query_one("#model", Input).placeholder = MODEL_HINT.get(eng, "")
        self.query_one("#custom", Input).disabled = eng != "custom"
        self.query_one("#oc-agent", Input).disabled = eng != "opencode"

    @on(Select.Changed, "#engine")
    def _engine(self) -> None:
        self.hint()

    # ---- motor
    @on(Button.Pressed, "#check")
    def _check(self) -> None:
        eng = str(self.query_one("#engine", Select).value)
        out = self.query_one("#engine-status", Static)
        if eng == "custom":
            out.update("[dim]Comando propio: no hay nada que comprobar aquí.[/]")
            return
        v = cli._ver([eng, "--version"])
        out.update(f"[b $success]✓ {eng} instalado[/]  [dim]{v}[/]" if v else f"[b $error]✗ No encuentro «{eng}» en el PATH.[/]  Instálalo o elige otro motor.")

    @on(Button.Pressed, "#save-engine")
    def _save_engine(self) -> None:
        b = self.query_one("#banner", Banner)
        try:
            argv = tuple(shlex.split(self.query_one("#custom", Input).value))
            s = AgentSettings(engine=str(self.query_one("#engine", Select).value), model=self.query_one("#model", Input).value.strip(),
                              opencode_agent=self.query_one("#oc-agent", Input).value.strip(),
                              max_attempts=int(self.query_one("#attempts", Input).value or 0),
                              timeout_minutes=int(self.query_one("#timeout", Input).value or 0), custom_argv=argv)
            self.app.store.save_agent(self.info, s)
        except (ProjectError, ValueError) as e:
            b.show("error", str(e))
            return
        b.show("ok", "Guardado. Los agentes del proyecto se regeneraron con este modelo.")

    # ---- tokens
    def refresh_tokens(self) -> None:
        t = self.query_one("#tokens", DataTable)
        t.clear()
        try:
            for name in self.creds.names():
                t.add_row(name, mask(self.creds.get(name)), key=name)
        except CredentialError as e:
            self.query_one("#tbanner", Banner).show("error", str(e))

    @on(Select.Changed, "#provider")
    def _provider(self, ev: Select.Changed) -> None:
        if ev.value and ev.value != OTHER:
            self.query_one("#varname", Input).value = str(ev.value)
        elif ev.value == OTHER:
            self.query_one("#varname", Input).value = ""
            self.query_one("#varname", Input).focus()

    @on(Button.Pressed, "#save-token")
    def _save_token(self) -> None:
        b = self.query_one("#tbanner", Banner)
        sec = self.query_one("#secret", Input)
        try:
            self.creds.set(self.query_one("#varname", Input).value.strip(), sec.value)
        except (ValueError, CredentialError) as e:
            b.show("error", str(e))
            return
        sec.value = ""
        self.refresh_tokens()
        b.show("ok", "Token guardado.")

    @on(Button.Pressed, "#del-token")
    def _del_token(self) -> None:
        t = self.query_one("#tokens", DataTable)
        if not t.row_count:
            return
        name = str(t.coordinate_to_cell_key(t.cursor_coordinate).row_key.value)
        self.creds.delete(name)
        self.refresh_tokens()
        self.query_one("#tbanner", Banner).show("info", f"«{name}» eliminado.")

    def action_back(self) -> None:
        self.dismiss(None)
