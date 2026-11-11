"""Piezas reutilizables: banner de estado y selector de archivos/carpetas."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Label, Static


class Banner(Static):
    """Mensaje destacado (ok / warn / error / info). Oculto hasta que se muestra algo."""
    KINDS = ("ok", "warn", "error", "info")

    def show(self, kind: str, text: str) -> None:
        for k in self.KINDS:
            self.remove_class(f"-{k}")
        self.add_class("-visible", f"-{kind}")
        self.update(text)

    def clear(self) -> None:
        self.remove_class("-visible")
        self.update("")


class _FilteredTree(DirectoryTree):
    def __init__(self, path: Path, suffix: str | None, **kw):
        super().__init__(path, **kw)
        self.suffix = suffix            # None = solo carpetas

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        out = []
        for p in paths:
            if p.name.startswith("."):
                continue
            if p.is_dir() or (self.suffix and p.suffix.lower() == self.suffix):
                out.append(p)
        return out


class PathPicker(ModalScreen[Path | None]):
    """Elige un archivo (`suffix=".archimate"`) o una carpeta (`suffix=None`). Devuelve la ruta o None."""
    BINDINGS = [("escape", "cancel", "Cancelar")]

    def __init__(self, title: str, start: Path | None = None, suffix: str | None = None):
        super().__init__()
        self.title_text, self.suffix = title, suffix
        self.start = (start if start and start.exists() else Path.home())
        self.picked: Path | None = None

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self.title_text, classes="title")
            yield Label("↑↓ navegar · Enter abrir/elegir" + (" · «Elegir carpeta» usa la resaltada" if not self.suffix else ""), classes="muted")
            yield _FilteredTree(self.start, self.suffix, id="tree")
            yield Label("", id="picked", classes="accent")
            with Horizontal(classes="buttons"):
                if not self.suffix:
                    yield Button("Elegir carpeta", id="ok", variant="primary")
                yield Button("Cancelar", id="cancel")

    def on_directory_tree_file_selected(self, ev: DirectoryTree.FileSelected) -> None:
        if self.suffix:
            self.dismiss(Path(ev.path))

    def on_directory_tree_directory_selected(self, ev: DirectoryTree.DirectorySelected) -> None:
        self.picked = Path(ev.path)
        self.query_one("#picked", Label).update(f"Carpeta: {self.picked}")

    def on_tree_node_highlighted(self, ev) -> None:
        data = getattr(ev.node, "data", None)
        path = getattr(data, "path", None)
        if path and Path(path).is_dir() and not self.suffix:
            self.picked = Path(path)
            self.query_one("#picked", Label).update(f"Carpeta: {self.picked}")

    def on_button_pressed(self, ev: Button.Pressed) -> None:
        self.dismiss(self.picked if ev.button.id == "ok" else None)

    def action_cancel(self) -> None:
        self.dismiss(None)
