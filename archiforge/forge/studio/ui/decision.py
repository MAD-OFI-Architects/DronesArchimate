"""Decisiones de un dominio: el arquitecto elige todo (formulario); la columna derecha es solo referencia."""
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


class DecisionScreen(Screen[bool]):
    BINDINGS = [("escape", "cancel", "Cancelar"), ("ctrl+s", "save", "Guardar")]

    def __init__(self, studio: Studio, context: str):
        super().__init__()
        self.studio, self.context = studio, context
        self.draft: Domain = studio.draft(context)
        self.ref = studio.reference()

    def compose(self) -> ComposeResult:
        d = self.draft
        yield Header()
        with Horizontal():
            with VerticalScroll(id="form", classes="card"):
                yield Static(f"Decisiones de «{self.context}»", classes="card-title")
                with Horizontal(classes="pair"):
                    with Vertical():
                        yield Label("Lenguaje", classes="field-label")
                        yield Select(LANGS, value=d.language or Select.NULL, prompt="Elige…", allow_blank=True, id="language")
                    with Vertical():
                        yield Label("Arquitectura interna", classes="field-label")
                        yield Select(ARCHS, value=d.architecture or Select.NULL, prompt="Elige…", allow_blank=True, id="architecture")
                with Horizontal(classes="pair"):
                    with Vertical():
                        yield Label("Estilo de servicio", classes="field-label")
                        yield Select(STYLES, value=d.style or Select.NULL, prompt="Elige…", allow_blank=True, id="style")
                    with Vertical():
                        yield Label("Base de datos", classes="field-label")
                        yield Select(DBS, value=d.database or Select.NULL, prompt="Elige…", allow_blank=True, id="database")
                yield Label("Puerto", classes="field-label")
                yield Input(str(d.port), id="port", type="integer")
                yield Label("Patrones  (espacio marca/desmarca)", classes="field-label")
                yield SelectionList(*[Selection(self._label(a), a["id"], bool(d.patterns.get(a["id"], {}).get("usar"))) for a in self.ref], id="patterns")
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
                yield Static("Referencia", classes="card-title")
                yield Static(self._advice_text(), id="advice")
        yield Footer()

    @staticmethod
    def _label(a: dict) -> Text:
        t = Text(a["nombre"], style="bold")
        if a.get("categoria"):
            t.append(f" · {a['categoria']}", style="dim")
        return t

    def _advice_text(self) -> Text:
        """Información del contexto y fichas de los patrones. Describe; no valora ni recomienda."""
        f = self.studio.facts(self.context)
        t = Text()
        t.append(f"{f['purpose']}\n\n", style="italic")
        t.append(f"{len(f['aggregates'])} agregados · {len(f['commands'])} comandos · {len(f['rules'])} reglas de negocio · {len(f['queries'])} consultas\n", style="dim")
        t.append(f"Publica: {', '.join(f['published']) or '—'}\nConsume: {', '.join(f['consumed']) or '—'}\n\n", style="dim")
        for a in self.ref:
            t.append(f"{a['nombre']}", style="bold")
            t.append(f" · {a.get('categoria', '')}\n", style="dim")
            t.append(f"  {a['que_es']}\n")
            t.append(f"  Se usa cuando: {a['cuando_si']}\n  No se usa cuando: {a['cuando_no']}\n  Costo: {a['costo']}\n", style="dim")
            if a.get("requiere"):
                t.append(f"  Requiere: {', '.join(a['requiere'])}\n", style="dim")
            t.append("\n")
        return t

    # ---- guardar
    def _collect(self) -> Domain:
        g = lambda i: (lambda v: v if isinstance(v, str) else "")(self.query_one(f"#{i}", Select).value)  # noqa: E731   (sin elegir = "")
        try:
            port = int(self.query_one("#port", Input).value)
        except ValueError:
            raise ValueError("El puerto debe ser un número.") from None
        chosen = set(self.query_one("#patterns", SelectionList).selected)
        patterns = {a["id"]: {**self.draft.patterns.get(a["id"], {}), "usar": a["id"] in chosen} for a in self.ref}
        why = {k: self.query_one(f"#why-{k}", TextArea).text.strip() for k, _ in WHY}
        keep = {k: v for k, v in self.draft.rationale.items() if k not in why}     # justificaciones de patrones, etc.
        rationale = {**keep, **{k: v for k, v in why.items() if v}}              # un campo vacío elimina el borrador
        return Domain(self.context, g("language"), g("architecture"), g("style"), g("database"), port,
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
