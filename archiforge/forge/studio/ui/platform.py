"""Decisiones de la plataforma: lo que no sale del modelo ArchiMate. El arquitecto elige; la columna derecha solo informa."""
from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static, TextArea

from ... import decisions
from ..service import Studio, StudioError
from .widgets import Banner

OPCIONES = {
    "mensajeria": [("RabbitMQ (broker con colas durables)", "rabbitmq"), ("Relé HTTP en memoria (sin broker)", "memoria")],
    "gateway": [("nginx (sirve el frontend y enruta hacia los servicios)", "nginx"), ("Propio (sin gateway generado; se documentan las rutas)", "propio")],
    "frontend": [("Microfrontends (React + Vite, Web Components)", "microfrontends"), ("Ninguno (solo las APIs)", "ninguno")],
    "despliegue": [("Docker Compose", "docker-compose"), ("Propio (sin artefactos de despliegue)", "propio")],
    "simuladores": [("Generar simuladores de los contextos no construidos", "generar"), ("Ninguno (el equipo configura los proveedores)", "ninguno")],
}


class PlatformScreen(Screen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar"), ("ctrl+s", "save", "Guardar")]

    def __init__(self, studio: Studio):
        super().__init__()
        self.studio = studio

    def compose(self) -> ComposeResult:
        actual = self.studio.cfg.platform
        razones = actual.get("justificacion") or {}
        yield Header()
        with Horizontal():
            with VerticalScroll(id="form", classes="card"):
                yield Static("Decisiones de la plataforma", classes="card-title")
                for clave, (titulo, _) in decisions.ELECCIONES_DE_PLATAFORMA.items():
                    yield Label(titulo, classes="field-label")
                    yield Select(OPCIONES[clave], value=actual.get(clave) or Select.NULL, prompt="Elige…", allow_blank=True, id=clave)
                    yield TextArea(razones.get(clave, ""), id=f"why-{clave}", placeholder="¿Por qué? Escribe tu argumento propio")
                yield Label("Imágenes de contenedor  (vacío = la versión que trae la herramienta)", classes="field-label")
                fijadas = actual.get("imagenes") or {}
                for nombre, defecto in decisions.IMAGENES.items():
                    yield Input(fijadas.get(nombre, ""), id=f"img-{nombre}", placeholder=f"{nombre}: {defecto}")
                yield Banner(id="banner")
                with Horizontal(classes="buttons"):
                    yield Button("Guardar", id="save", variant="success")
                    yield Button("Cancelar", id="cancel")
            with VerticalScroll(id="why", classes="card"):
                yield Static("Referencia", classes="card-title")
                yield Static("\n\n".join(f"[b $primary]{titulo}[/]\n" + "\n".join(f"[b]{k}[/b]: {v}" for k, v in opciones.items())
                                         for titulo, opciones in decisions.ELECCIONES_DE_PLATAFORMA.values()), id="reference")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Plataforma"

    @on(Button.Pressed, "#save")
    def action_save(self) -> None:
        valores = {c: self.query_one(f"#{c}", Select).value for c in decisions.ELECCIONES_DE_PLATAFORMA}
        faltan = [decisions.ELECCIONES_DE_PLATAFORMA[c][0].lower() for c, v in valores.items() if v is Select.NULL]
        if faltan:
            self.query_one(Banner).show("error", f"Elige: {', '.join(faltan)}.")
            return
        why = {c: self.query_one(f"#why-{c}", TextArea).text for c in valores}
        imagenes = {n: self.query_one(f"#img-{n}", Input).value for n in decisions.IMAGENES}
        try:
            self.studio.save_platform({c: str(v) for c, v in valores.items()}, why, imagenes)
        except StudioError as e:
            self.query_one(Banner).show("error", str(e))
            return
        self.dismiss(True)

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        self.dismiss(False)
