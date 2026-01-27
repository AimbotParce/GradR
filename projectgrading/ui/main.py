"""
Main Textual app for ProjectGrading
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Container, Middle
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    Markdown,
    Sparkline,
    Static,
    Welcome,
)

from .students import StudentsScreen
from .subjects import SubjectsListScreen


class MainScreen(Static):
    """Interactive sidebar for navigating subjects and classrooms."""

    def compose(self) -> ComposeResult:
        """Create sidebar content."""
        with Middle():
            with Center():
                yield Label("[bold magenta]ProjectGrading[/bold magenta]", id="app-title")
                yield Label("")
                yield Label("Navigate to:", id="nav-label")
                yield Button("📚 Subjects", id="btn-subjects")
                yield Button("👥 Students", id="btn-students")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events in sidebar."""
        button_id = event.button.id

        if button_id == "btn-subjects":
            self.app.push_screen(SubjectsListScreen())
        elif button_id == "btn-students":
            self.app.push_screen(StudentsScreen())


class GradingApp(App):
    """Main application for grading students."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("h", "home", "Home"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Center():
            yield MainScreen(id="main-screen")
        yield Footer()

    def on_mount(self) -> None:
        """Handle mount event."""
        self.title = "ProjectGrading"

    def action_home(self) -> None:
        """Go back to home screen."""
        while len(self.screen_stack) > 1:
            self.pop_screen()


if __name__ == "__main__":
    app = GradingApp()
    app.run()

    def action_home(self) -> None:
        """Go back to home screen."""
        while len(self.screen_stack) > 1:
            self.pop_screen()


if __name__ == "__main__":
    app = GradingApp()
    app.run()
