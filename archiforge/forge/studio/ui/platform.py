"""Decisiones de la plataforma: el canal de eventos entre contextos. El arquitecto elige; la lista de la derecha solo informa."""
from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Select, Static, TextArea

from ... import decisions
from ..service import Studio, StudioError
from .widgets import Banner

OPCIONES = [("RabbitMQ (broker con colas durables)", "rabbitmq"), ("Relé HTTP en memoria (sin broker)", "memoria")]


class PlatformScreen(Screen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar"), ("ctrl+s", "save", "Guardar")]

    def __init__(self, studio: Studio):
        super().__init__()
        self.studio = studio

    def compose(self) -> ComposeResult:
        actual = self.studio.cfg.platform
        yield Header()
        with Horizontal():
            with VerticalScroll(id="form", classes="card"):
                yield Static("Decisiones de la plataforma", classes="card-title")
                yield Label("Canal de eventos entre contextos", classes="field-label")
                yield Select(OPCIONES, value=actual.get("mensajeria") or Select.NULL, prompt="Elige…", allow_blank=True, id="mensajeria")
                yield Label("¿Por qué este canal?", classes="field-label")
                yield TextArea((actual.get("justificacion") or {}).get("mensajeria", ""), id="why-mensajeria",
                               placeholder="Escribe tu argumento propio")
                yield Banner(id="banner")
                with Horizontal(classes="buttons"):
                    yield Button("Guardar", id="save", variant="success")
                    yield Button("Cancelar", id="cancel")
            with VerticalScroll(id="why", classes="card"):
                yield Static("Referencia", classes="card-title")
                yield Static("\n\n".join(f"[b]{k}[/b]\n{v}" for k, v in decisions.MENSAJERIAS.items()), id="reference")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Plataforma"

    @on(Button.Pressed, "#save")
    def action_save(self) -> None:
        valor = self.query_one("#mensajeria", Select).value
        if valor is Select.NULL:
            self.query_one(Banner).show("error", "Elige el canal de eventos.")
            return
        try:
            self.studio.save_platform(str(valor), self.query_one("#why-mensajeria", TextArea).text)
        except StudioError as e:
            self.query_one(Banner).show("error", str(e))
            return
        self.dismiss(True)

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        self.dismiss(False)
