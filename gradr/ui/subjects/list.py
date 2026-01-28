"""
Subject management screens
"""

from sqlalchemy import select
from textual.containers import (
    Container,
    Horizontal,
    HorizontalGroup,
    ScrollableContainer,
    Vertical,
)
from textual.widgets import Button, Footer, Header, Input, Label

from ...database import get_async_session
from ...database.models import Subject
from ..base import BaseScreen


class SubjectsListScreen(BaseScreen):
    """Screen for managing subjects."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    def compose(self):
        """Compose the screen."""
        yield Header()
        yield Container(
            Vertical(
                Label("[bold cyan]Existing Subjects:[/bold cyan]"),
                ScrollableContainer(id="subjects-list"),
                Label("[bold cyan]Create Subject[/bold cyan]"),
                Input(id="subject-name-input", placeholder="Enter subject name"),
                Input(id="subject-description-input", placeholder="Enter subject description (optional)"),
                Button("Create", id="btn-create-subject", variant="primary"),
            )
        )
        yield Footer()

    async def on_mount(self):
        """Handle screen mount."""
        await self.load_subjects()

    async def load_subjects(self):
        """Load subjects from database."""
        async with get_async_session() as session:
            subjects = await session.execute(select(Subject))
            subjects = subjects.scalars().all()

            subjects_list = self.query_one("#subjects-list", ScrollableContainer)
            subjects_list.remove_children()

            if not subjects:
                subjects_list.mount(Label("[dim]No subjects yet[/dim]"))
            else:
                for subject in subjects:
                    desc_text = subject.description or ""
                    if desc_text and len(desc_text) > 50:
                        desc_text = desc_text[:47] + "..."
                    item = HorizontalGroup(
                        Button(
                            subject.name + (f": {desc_text}" if desc_text else ""),
                            id=f"btn-subject-{subject.id}",
                        ),
                        Button("Edit", id=f"btn-edit-subject-{subject.id}", variant="warning"),
                        Button("Delete", id=f"btn-delete-subject-{subject.id}", variant="error"),
                        classes="subject-item",
                    )
                    subjects_list.mount(item)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if not button_id:
            return
        if button_id == "btn-create-subject":
            await self._create_subject()
        elif button_id.startswith("btn-delete-subject-"):
            subject_id = int(button_id.split("-")[-1])
            await self._delete_subject(subject_id)
        elif button_id.startswith("btn-edit-subject-"):
            subject_id = int(button_id.split("-")[-1])
            await self.app.push_screen(EditSubjectScreen(subject_id))
        elif button_id.startswith("btn-subject-"):
            subject_id = int(button_id.split("-")[-1])
            await self.app.push_screen(ClassroomsListScreen(subject_id))

    async def _delete_subject(self, subject_id: int):
        """Delete a subject."""
        async with get_async_session() as session:
            subject = await session.get(Subject, subject_id)
            if subject:
                await session.delete(subject)
                await session.commit()
        await self.load_subjects()

    async def _create_subject(self):
        """Create a new subject."""
        name_input = self.query_one("#subject-name-input", Input)
        description_input = self.query_one("#subject-description-input", Input)

        name = name_input.value.strip()
        description = description_input.value.strip() or None

        if not name:
            name_input.focus()
            return

        async with get_async_session() as session:
            subject = Subject(name=name, description=description)
            session.add(subject)
            await session.commit()
        name_input.value = ""
        description_input.value = ""
        await self.load_subjects()


from ..classrooms import ClassroomsListScreen
from .edit import EditSubjectScreen
