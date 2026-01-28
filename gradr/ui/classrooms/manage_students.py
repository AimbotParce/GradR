from sqlalchemy import func, select
from textual.containers import (
    Container,
    Horizontal,
    HorizontalGroup,
    ScrollableContainer,
    Vertical,
    VerticalScroll,
)
from textual.widgets import Button, Footer, Header, Input, Label

from ...database import get_async_session
from ...database.models import Classroom, ClassroomMembership, Student
from ..base import BaseScreen


class ManageClassroomStudentsScreen(BaseScreen):
    """Screen for adding/removing students from a classroom."""

    def __init__(self, classroom_id: int):
        super().__init__()
        self.classroom_id = classroom_id

    def compose(self):
        yield Header()
        yield Container(
            Vertical(
                Label(id="classroom-title"),
                Label("Add students to this classroom:"),
                Horizontal(
                    Container(
                        Label("[bold cyan]Available Students:[/bold cyan]"),
                        VerticalScroll(id="available-students"),
                    ),
                    Container(
                        Label("[bold cyan]Current Members:[/bold cyan]"),
                        VerticalScroll(id="classroom-students"),
                    ),
                ),
            )
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Load students and memberships."""
        await self.load_classroom_info()
        await self.load_students()

    async def load_classroom_info(self) -> None:
        """Load classroom details from database."""
        async with get_async_session() as session:
            classroom = await session.get(Classroom, self.classroom_id)
            if classroom:
                title = self.query_one("#classroom-title", Label)
                title.update(f"[bold cyan]Manage Students for Classroom #{self.classroom_id}[/bold cyan]")

    async def load_students(self) -> None:
        """Refresh students and memberships."""

        async with get_async_session() as session:
            # Get all students
            available_students = await session.execute(select(Student))
            available_students = available_students.scalars().all()

            available_list = self.query_one("#available-students", VerticalScroll)
            available_list.remove_children()
            current_list = self.query_one("#classroom-students", VerticalScroll)
            current_list.remove_children()

            for student in available_students:
                if await session.get(
                    ClassroomMembership,
                    {"student_id": student.id, "classroom_id": self.classroom_id},
                ):
                    # Student is already a member
                    current_list.mount(
                        HorizontalGroup(
                            Button(student.name),  # Only for display, no action
                            Button("Remove", id=f"remove-{student.id}", variant="error"),
                        )
                    )
                else:
                    available_list.mount(
                        HorizontalGroup(
                            Button(student.name),  # Only for display, no action
                            Button("Add", id=f"add-{student.id}", variant="success"),
                        )
                    )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""

        button_id = event.button.id
        if not button_id:
            return

        if button_id.startswith("add-"):
            student_id = int(button_id.split("-")[1])
            async with get_async_session() as session:
                membership = ClassroomMembership(student_id=student_id, classroom_id=self.classroom_id)
                session.add(membership)
                await session.commit()
            await self.load_students()
        elif button_id.startswith("remove-"):
            student_id = int(button_id.split("-")[1])
            async with get_async_session() as session:
                membership = await session.get(
                    ClassroomMembership,
                    {"student_id": student_id, "classroom_id": self.classroom_id},
                )
                if membership:
                    await session.delete(membership)
                    await session.commit()
            await self.load_students()

        for screen in self.app.screen_stack:
            if isinstance(screen, ClassroomMenuScreen) and screen.classroom_id == self.classroom_id:
                await screen.load_students()


from .main import ClassroomMenuScreen
