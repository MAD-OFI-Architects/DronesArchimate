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

MENSAJERIA = [("RabbitMQ (broker con colas durables)", "rabbitmq"), ("Relé HTTP en memoria (sin broker)", "memoria")]
GATEWAY = [("nginx (sirve el frontend y enruta hacia los servicios)", "nginx"), ("Propio (sin gateway generado; se documentan las rutas)", "propio")]


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
                yield Select(MENSAJERIA, value=actual.get("mensajeria") or Select.NULL, prompt="Elige…", allow_blank=True, id="mensajeria")
                yield Label("¿Por qué este canal?", classes="field-label")
                yield TextArea((actual.get("justificacion") or {}).get("mensajeria", ""), id="why-mensajeria",
                               placeholder="Escribe tu argumento propio")
                yield Label("Gateway", classes="field-label")
                yield Select(GATEWAY, value=actual.get("gateway") or Select.NULL, prompt="Elige…", allow_blank=True, id="gateway")
                yield Label("¿Por qué este gateway?", classes="field-label")
                yield TextArea((actual.get("justificacion") or {}).get("gateway", ""), id="why-gateway",
                               placeholder="Escribe tu argumento propio")
                yield Banner(id="banner")
                with Horizontal(classes="buttons"):
                    yield Button("Guardar", id="save", variant="success")
                    yield Button("Cancelar", id="cancel")
            with VerticalScroll(id="why", classes="card"):
                yield Static("Referencia", classes="card-title")
                yield Static("[b $primary]Canal de eventos[/]\n\n" + "\n\n".join(f"[b]{k}[/b]\n{v}" for k, v in decisions.MENSAJERIAS.items()) +
                             "\n\n[b $primary]Gateway[/]\n\n" + "\n\n".join(f"[b]{k}[/b]\n{v}" for k, v in decisions.GATEWAYS.items()), id="reference")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Plataforma"

    @on(Button.Pressed, "#save")
    def action_save(self) -> None:
        canal, gateway = self.query_one("#mensajeria", Select).value, self.query_one("#gateway", Select).value
        faltan = [n for n, v in (("el canal de eventos", canal), ("el gateway", gateway)) if v is Select.NULL]
        if faltan:
            self.query_one(Banner).show("error", f"Elige {' y '.join(faltan)}.")
            return
        try:
            self.studio.save_platform(str(canal), str(gateway), {"mensajeria": self.query_one("#why-mensajeria", TextArea).text,
                                                                  "gateway": self.query_one("#why-gateway", TextArea).text})
        except StudioError as e:
            self.query_one(Banner).show("error", str(e))
            return
        self.dismiss(True)

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        self.dismiss(False)
