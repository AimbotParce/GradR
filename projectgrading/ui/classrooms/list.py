"""
Subject management screens
"""

from sqlalchemy import func, select
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.widgets import Button, Footer, Header, Input, Label

from ...database import get_async_session
from ...database.models import Classroom, ClassroomMembership
from ...database.models.subject import Subject
from ..base import BaseScreen


class ClassroomsListScreen(BaseScreen):
    """Screen for managing classrooms."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, subject_id: int):
        """
        Initialize ClassroomsScreen.

        Args:
            subject_id: The ID of the subject to which the classrooms belong.
        """
        self.subject_id = subject_id
        super().__init__()

    def compose(self):
        """Compose the screen."""
        yield Header()
        yield Container(
            Vertical(
                Label(id="subject-name"),  # Placeholder for subject name
                ScrollableContainer(id="classrooms-list"),
                Button("Create New Classroom", id="btn-create-classroom", variant="primary"),
            )
        )
        yield Footer()

    async def on_mount(self):
        """Handle screen mount."""
        await self.load_subject_info()
        await self.load_classrooms()

    async def load_subject_info(self):
        """Load subject details from database."""
        async with get_async_session() as session:
            subject = await session.get(Subject, self.subject_id)
            if subject:
                title = self.query_one("#subject-name", Label)
                title.update(f"[bold cyan]Classrooms for Subject {subject.name}[/bold cyan]")

    async def load_classrooms(self):
        """Load classrooms from database."""
        async with get_async_session() as session:
            classrooms = await session.execute(select(Classroom))
            classrooms = classrooms.scalars().all()

            classrooms_list = self.query_one("#classrooms-list", ScrollableContainer)
            classrooms_list.remove_children()

            if not classrooms:
                classrooms_list.mount(Label("[dim]No classrooms yet[/dim]"))
            else:
                for classroom in classrooms:
                    count_result = await session.execute(
                        select(func.count(ClassroomMembership.student_id)).where(
                            ClassroomMembership.classroom_id == classroom.id
                        )
                    )
                    member_count = count_result.scalar_one()
                    item = Horizontal(
                        Button(
                            f"Classroom {classroom.id} ({member_count} members)",
                            id=f"btn-classroom-{classroom.id}",
                        ),
                        Button("Delete", id=f"btn-delete-classroom-{classroom.id}", variant="error"),
                        classes="classroom-item",
                    )
                    classrooms_list.mount(item)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if not button_id:
            return
        if button_id == "btn-create-classroom":
            classroom_id = await self._create_classroom()
            await self.app.push_screen(ClassroomMenuScreen(classroom_id))
        elif button_id.startswith("btn-delete-classroom-"):
            classroom_id = int(button_id.split("-")[-1])
            await self._delete_classroom(classroom_id)
        elif button_id.startswith("btn-classroom-"):
            classroom_id = int(button_id.split("-")[-1])
            await self.app.push_screen(ClassroomMenuScreen(classroom_id))

    async def _delete_classroom(self, classroom_id: int):
        """Delete a classroom."""
        async with get_async_session() as session:
            classroom = await session.get(Classroom, classroom_id)
            if classroom:
                await session.delete(classroom)
                await session.commit()
        await self.load_classrooms()

    async def _create_classroom(self):
        """Create a new classroom."""
        async with get_async_session() as session:
            classroom = Classroom(subject_id=self.subject_id)
            session.add(classroom)
            await session.commit()
            classroom_id = classroom.id
        await self.load_classrooms()
        return classroom_id


from .main import ClassroomMenuScreen
