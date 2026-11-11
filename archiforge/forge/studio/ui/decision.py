"""Decisiones de un dominio: la herramienta aconseja (columna derecha), el arquitecto decide (formulario)."""
from __future__ import annotations

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, SelectionList, Static, TextArea
from textual.widgets.selection_list import Selection

from ...config import Domain
from ...gates import PLACEHOLDER
from ..service import Studio
from .widgets import Banner

LANGS = [("C# (.NET)", "csharp"), ("Python (FastAPI)", "python"), ("Java (Spring Boot)", "java")]
ARCHS = [("Clean Architecture + DDD", "clean-ddd"), ("Hexagonal (puertos y adaptadores)", "hexagonal")]
STYLES = [("Microservicio", "microservicio"), ("SOA", "soa"), ("Monolito modular", "monolito-modular")]
DBS = [("MongoDB (NoSQL, documentos)", "mongodb"), ("PostgreSQL (SQL, relacional)", "postgresql")]
WHY = [("lenguaje", "¿Por qué este lenguaje?"), ("arquitectura", "¿Por qué esta arquitectura interna?"),
       ("estilo", "¿Por qué este estilo de servicio?"), ("base_de_datos", "¿Por qué esta base de datos?")]
REC_STYLE = {"recomendado": "bold #9ece6a", "opcional": "#e0af68", "no necesario": "dim"}


class DecisionScreen(Screen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar"), ("ctrl+s", "save", "Guardar")]

    def __init__(self, studio: Studio, context: str):
        super().__init__()
        self.studio, self.context = studio, context
        self.draft: Domain = studio.draft(context)
        self.advice = studio.advice(context)

    def compose(self) -> ComposeResult:
        d = self.draft
        yield Header()
        with Horizontal():
            with VerticalScroll(id="form", classes="card"):
                yield Static(f"Decisiones de «{self.context}»", classes="card-title")
                with Horizontal(classes="pair"):
                    with Vertical():
                        yield Label("Lenguaje", classes="field-label")
                        yield Select(LANGS, value=d.language, allow_blank=False, id="language")
                    with Vertical():
                        yield Label("Arquitectura interna", classes="field-label")
                        yield Select(ARCHS, value=d.architecture, allow_blank=False, id="architecture")
                with Horizontal(classes="pair"):
                    with Vertical():
                        yield Label("Estilo de servicio", classes="field-label")
                        yield Select(STYLES, value=d.style, allow_blank=False, id="style")
                    with Vertical():
                        yield Label("Base de datos", classes="field-label")
                        yield Select(DBS, value=d.database, allow_blank=False, id="database")
                yield Label("Puerto", classes="field-label")
                yield Input(str(d.port), id="port", type="integer")
                yield Label("Patrones  (espacio marca/desmarca)", classes="field-label")
                yield SelectionList(*[Selection(self._label(a), a["id"], bool(d.patterns.get(a["id"], {}).get("usar"))) for a in self.advice], id="patterns")
                for key, q in WHY:
                    yield Label(q, classes="field-label")
                    cur = d.rationale.get(key, "")
                    draft = bool(PLACEHOLDER.match(cur))        # «Ejemplo: …» es una sugerencia, no un argumento: se muestra en gris
                    yield TextArea("" if draft else cur, id=f"why-{key}",
                                   placeholder=cur if draft else "Escribe tu argumento propio (mín. 30 caracteres)")
                yield Banner(id="banner")
                with Horizontal(classes="buttons"):
                    yield Button("Guardar decisiones", id="save", variant="success")
                    yield Button("Cancelar", id="cancel")
            with VerticalScroll(id="why", classes="card"):
                yield Static("Lo que aconseja la herramienta", classes="card-title")
                yield Static(self._advice_text(), id="advice")
        yield Footer()

    @staticmethod
    def _label(a: dict) -> Text:
        t = Text(a["nombre"], style="bold")
        t.append(f" · {a['recomendacion']}", style=REC_STYLE.get(a["recomendacion"], ""))
        if a["evaluacion"]:
            t.append(" · ★ la evaluación lo exige", style="#7dcfff")
        return t

    def _advice_text(self) -> Text:
        f = self.studio.facts(self.context)
        t = Text()
        t.append(f"{f['purpose']}\n\n", style="italic")
        t.append(f"{len(f['aggregates'])} agregados · {len(f['commands'])} comandos · {len(f['rules'])} reglas de negocio · {len(f['queries'])} consultas\n", style="dim")
        t.append("Nunca se impone un patrón sin señal en el modelo: menos clases también es buena arquitectura.\n\n", style="dim")
        for a in self.advice:
            t.append(f"{a['nombre']}", style="bold")
            t.append(f" · {a['recomendacion']}\n", style=REC_STYLE.get(a["recomendacion"], ""))
            t.append(f"  {a['razon']}\n", style="")
            t.append(f"  Evítalo si: {a['cuando_no']}  ·  costo: {a['costo']}\n\n", style="dim")
        return t

    # ---- guardar
    def _collect(self) -> Domain:
        g = lambda i: self.query_one(f"#{i}", Select).value  # noqa: E731
        try:
            port = int(self.query_one("#port", Input).value)
        except ValueError:
            raise ValueError("El puerto debe ser un número.") from None
        chosen = set(self.query_one("#patterns", SelectionList).selected)
        patterns = {a["id"]: {**self.draft.patterns.get(a["id"], {}), "usar": a["id"] in chosen} for a in self.advice}
        why = {k: self.query_one(f"#why-{k}", TextArea).text.strip() for k, _ in WHY}
        keep = {k: v for k, v in self.draft.rationale.items() if k not in why}     # justificaciones de patrones, etc.
        rationale = {**keep, **{k: v for k, v in why.items() if v}}              # un campo vacío elimina el borrador
        return Domain(self.context, str(g("language")), str(g("architecture")), str(g("style")), str(g("database")), port,
                      patterns=patterns, rationale=rationale)

    def action_save(self) -> None:
        b = self.query_one(Banner)
        try:
            d = self._collect()
            errors, warns = self.studio.check(d)
            if errors:
                b.show("error", "\n".join(f"✗ {e}" for e in errors))
                return
            self.studio.save(d)
        except Exception as e:  # noqa: BLE001
            b.show("error", str(e))
            return
        if warns:
            self.app.notify("\n".join(warns[:3]), title="Guardado, con avisos", severity="warning", timeout=8)
        else:
            self.app.notify(f"Decisiones de «{self.context}» guardadas.", title="Guardado")
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)

    @on(Button.Pressed, "#save")
    def _save(self) -> None:
        self.action_save()

    @on(Button.Pressed, "#cancel")
    def _cancel(self) -> None:
        self.action_cancel()
