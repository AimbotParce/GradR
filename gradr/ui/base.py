"""
Base screen class for all application screens.
"""

from textual.binding import Binding
from textual.screen import Screen


class BaseScreen(Screen):
    """Base screen for all application screens."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]
