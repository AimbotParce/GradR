"""
Classroom management screens.
"""

from sqlalchemy import delete, select
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.widgets import Button, Footer, Header, Input, Label

from ...database import get_async_session
from ...database.models import Classroom, ClassroomMembership, Project, Student, Subject
from ..base import BaseScreen


class ClassroomMenuScreen(BaseScreen):
    """Screen for managing a specific classroom."""

    def __init__(self, classroom_id: int):
        super().__init__()
        self.classroom_id = classroom_id

    def compose(self):
        yield Header()
        yield Container(
            Vertical(
                Label(f"[bold cyan]Classroom Management[/bold cyan]", id="classroom-title"),
                Horizontal(
                    Vertical(
                        Label("[bold cyan]Students:[/bold cyan]"),
                        ScrollableContainer(id="classroom-students"),
                        Button("Manage Students", id="manage-students", variant="primary"),
                    ),
                    Vertical(
                        Label("[bold cyan]Projects:[/bold cyan]"),
                        ScrollableContainer(id="classroom-projects"),
                        Input(id="project-name-input", placeholder="Enter project name"),
                        Input(id="project-description-input", placeholder="Enter project description (optional)"),
                        Button("Create Project", id="create-project", variant="primary"),
                    ),
                ),
            )
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Load classroom info."""
        await self.load_classroom_info()
        await self.load_students()
        await self.load_projects()

    async def load_classroom_info(self):
        async with get_async_session() as session:
            classroom = await session.get(Classroom, self.classroom_id)
            title = self.query_one("#classroom-title", Label)
            if not classroom:
                title.update(f"[bold red]Classroom not found[/bold red]")
                return

            subject = await session.get(Subject, classroom.subject_id)
            if not subject:
                title.update(f"[bold red]Subject not found[/bold red]")
                return

            classroom_name = f"Subject {subject.name} Classroom #{classroom.id}"
            title.update(f"[bold cyan]{classroom_name}[/bold cyan]")

    async def load_students(self):
        """Load students in the classroom."""

        students_list = self.query_one("#classroom-students", ScrollableContainer)
        students_list.remove_children()

        async with get_async_session() as session:
            result = await session.execute(
                select(Student)
                .join(ClassroomMembership, Student.id == ClassroomMembership.student_id)
                .where(ClassroomMembership.classroom_id == self.classroom_id)
            )
            students = result.scalars().all()

            for student in students:
                students_list.mount(
                    Horizontal(
                        Button(f"👤 {student.name}"),  # Just for display, no action
                        Button("Remove", id=f"remove-student-{student.id}", variant="error", classes="action-button"),
                    )
                )

    async def load_projects(self):
        """Load projects in the classroom."""

        projects_list = self.query_one("#classroom-projects", ScrollableContainer)
        projects_list.remove_children()

        async with get_async_session() as session:
            result = await session.execute(select(Project).where(Project.classroom_id == self.classroom_id))
            projects = result.scalars().all()

            for project in projects:
                description_text = project.description if project.description else ""
                if len(description_text) > 30:
                    description_text = description_text[:27] + "..."

                projects_list.mount(
                    Horizontal(
                        Button(
                            f"📋 {project.name}" + (f" ({description_text})" if description_text else ""),
                            id=f"view-project-{project.id}",
                        ),
                        Button("Delete", id=f"delete-project-{project.id}", variant="error", classes="action-button"),
                    )
                )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if not button_id:
            return
        if button_id == "manage-students":
            self.app.push_screen(ManageClassroomStudentsScreen(self.classroom_id))
        elif button_id == "create-project":
            await self._create_project()
        elif button_id.startswith("delete-project-"):
            project_id = int(button_id.split("-")[-1])
            await self._delete_project(project_id)
        elif button_id.startswith("remove-student-"):
            student_id = int(button_id.split("-")[-1])
            await self._remove_student(student_id)
        elif button_id.startswith("view-project-"):
            project_id = int(button_id.split("-")[-1])
            self.app.push_screen(ProjectDetailsScreen(project_id))

    async def _remove_student(self, student_id: int):
        """Remove a student from the classroom."""

        async with get_async_session() as session:
            await session.execute(
                delete(ClassroomMembership).where(
                    ClassroomMembership.classroom_id == self.classroom_id,
                    ClassroomMembership.student_id == student_id,
                )
            )
            await session.commit()
        await self.load_students()

    async def _delete_project(self, project_id: int):
        """Delete a project."""
        async with get_async_session() as session:
            project = await session.get(Project, project_id)
            if project:
                await session.delete(project)
                await session.commit()
        await self.load_projects()

    async def _create_project(self):
        """Create a new project."""
        name_input = self.query_one("#project-name-input", Input)
        description_input = self.query_one("#project-description-input", Input)

        name = name_input.value.strip()
        description = description_input.value.strip() or None

        if not name:
            name_input.focus()
            return

        async with get_async_session() as session:
            project = Project(name=name, description=description, classroom_id=self.classroom_id)
            session.add(project)
            await session.commit()
        name_input.value = ""
        description_input.value = ""
        await self.load_projects()


from ..project import ProjectDetailsScreen
from .manage_students import ManageClassroomStudentsScreen
