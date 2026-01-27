"""
Students management screen.
"""

from sqlalchemy import select
from textual.containers import Container, ScrollableContainer, Vertical
from textual.widgets import Button, Footer, Header, Input, Label

from ..database import get_async_session
from ..database.models import Student
from .base import BaseScreen


class StudentsScreen(BaseScreen):
    """Screen for creating and managing standalone students."""

    def compose(self):
        yield Header()
        yield Container(
            Vertical(
                Label("[bold cyan]Create Students[/bold cyan]"),
                Input(placeholder="Student name", id="student-name"),
                Button("Add Student", id="add-student", variant="primary"),
                Label(""),
                Label("[bold cyan]Existing Students:[/bold cyan]"),
                ScrollableContainer(
                    id="students-list",
                ),
            )
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Load existing students."""
        await self.load_students()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add-student":
            name_input = self.query_one("#student-name", Input)
            if name_input.value.strip():
                await self.add_student(name_input.value)
                name_input.value = ""
                await self.load_students()

    async def add_student(self, name: str) -> None:
        """Add a new student to the database."""

        async with get_async_session() as session:
            student = Student(name=name)
            session.add(student)
            await session.commit()

    async def load_students(self) -> None:
        """Refresh the list of students."""
        students_list = self.query_one("#students-list", ScrollableContainer)
        students_list.remove_children()

        async with get_async_session() as session:
            result = await session.execute(select(Student))
            students = result.scalars().all()

            for student in students:
                students_list.mount(Label(f"• {student.name} (ID: {student.id})"))
