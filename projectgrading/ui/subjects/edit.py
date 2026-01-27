from sqlalchemy import select
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.widgets import Button, Footer, Header, Input, Label

from ...database import get_async_session
from ...database.models import Subject
from ..base import BaseScreen
from .list import SubjectsListScreen


class EditSubjectScreen(BaseScreen):
    """Screen for editing an existing subject."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, subject_id: int):
        super().__init__()
        self.subject_id = subject_id

    def compose(self):
        yield Header()
        yield Container(
            Vertical(
                Label("[bold cyan]Edit Subject[/bold cyan]"),
                Input(id="subject-name-input", placeholder="Enter subject name"),
                Input(id="subject-description-input", placeholder="Enter subject description (optional)"),
                Horizontal(
                    Button("Save Changes", id="btn-save-subject", variant="primary"),
                    Button("Cancel", id="btn-cancel-edit", variant="error"),
                ),
            )
        )
        yield Footer()

    async def on_mount(self):
        """Handle screen mount."""
        await self.load_subject()

    async def load_subject(self):
        """Load subject details from database."""
        async with get_async_session() as session:
            subject = await session.get(Subject, self.subject_id)
            if subject:
                name_input = self.query_one("#subject-name-input", Input)
                description_input = self.query_one("#subject-description-input", Input)
                name_input.value = subject.name
                description_input.value = subject.description or ""

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-save-subject":
            await self._save_subject()
        elif event.button.id == "btn-cancel-edit":
            self.app.pop_screen()

    async def _save_subject(self):
        """Save the edited subject."""
        name_input = self.query_one("#subject-name-input", Input)
        description_input = self.query_one("#subject-description-input", Input)

        name = name_input.value.strip()
        description = description_input.value.strip() or None

        if not name:
            name_input.focus()
            return

        async with get_async_session() as session:
            subject = await session.get(Subject, self.subject_id)
            if subject:
                subject.name = name
                subject.description = description or ""
                await session.commit()
        self.app.pop_screen()
        # Refresh the subjects list in the previous screens
        for screen in self.app.screen_stack:
            if isinstance(screen, SubjectsListScreen):
                await screen.load_subjects()
