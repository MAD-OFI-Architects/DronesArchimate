"""ArchiForge Studio: la TUI. Tema, arranque y pantalla de inicio."""
from __future__ import annotations

from textual.app import App
from textual.theme import Theme

from ...config import TOOL_ROOT
from ...credentials import CredentialStore
from ..projects import ProjectStore

THEME = Theme(
    name="archiforge", primary="#7aa2f7", secondary="#bb9af7", accent="#7dcfff", warning="#e0af68", error="#f7768e",
    success="#9ece6a", foreground="#c0caf5", background="#13141c", surface="#1a1b26", panel="#24283b", dark=True,
    variables={"block-cursor-text-style": "bold", "input-selection-background": "#7aa2f7 35%"},
)


class StudioApp(App):
    CSS_PATH = "theme.tcss"
    TITLE = "ArchiForge Studio"
    SUB_TITLE = "del ArchiMate al software, con el arquitecto decidiendo"
    BINDINGS = [("ctrl+q", "quit", "Salir")]

    def __init__(self, store: ProjectStore | None = None, creds: CredentialStore | None = None):
        super().__init__()
        self.store = store or ProjectStore()
        self.creds = creds or CredentialStore()

    def on_mount(self) -> None:
        self.register_theme(THEME)
        self.theme = "archiforge"
        if not self.store.list() and (TOOL_ROOT / "forge.toml").exists():          # primera vez: trae el proyecto que ya existe
            self.store.register(TOOL_ROOT / "forge.toml", "Drones (proyecto actual)")
        from .home import HomeScreen
        self.push_screen(HomeScreen())


def run() -> None:
    StudioApp().run()
