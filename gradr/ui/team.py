from sqlalchemy import func, select
from textual.containers import (
    Container,
    Horizontal,
    HorizontalGroup,
    ScrollableContainer,
    Vertical,
)
from textual.widgets import Button, Footer, Header, Input, Label

from ..database import get_async_session
from ..database.models import (
    Classroom,
    ClassroomMembership,
    Project,
    Student,
    Subject,
    Team,
    TeamMembership,
)
from .base import BaseScreen


class TeamDetailsScreen(BaseScreen):
    """Screen for adding/removing students from a team."""

    def __init__(self, team_id: int):
        super().__init__()
        self.team_id = team_id
        self.project_id = None  # Will be set when loading team info

    def compose(self):
        yield Header()
        yield Container(
            Vertical(
                Label(id="team-title"),
                Label(""),
                Label("Add students to this team:"),
                Horizontal(
                    Container(
                        Label("[bold cyan]Available Students:[/bold cyan]"),
                        ScrollableContainer(id="available-students"),
                    ),
                    Container(
                        Label("[bold cyan]Current Members:[/bold cyan]"),
                        ScrollableContainer(id="current-members"),
                    ),
                ),
            )
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Load students and memberships."""
        await self.load_team_info()
        await self.load_students()

    async def load_team_info(self) -> None:
        """Load team details from database."""

        async with get_async_session() as session:
            title = self.query_one("#team-title", Label)

            team = await session.get(Team, self.team_id)
            if not team:
                title.update(f"[bold red]Team not found[/bold red]")
                return

            project = await session.get(Project, team.project_id)

            if not project:
                title.update("[bold red]Project not found[/bold red]")
                return

            self.project_id = project.id

            subject_result = await session.execute(
                select(Subject).where(Subject.id == Classroom.subject_id and Classroom.id == project.classroom_id)
            )
            subject = subject_result.scalars().first()
            if not subject:
                title.update("[bold red]Subject not found[/bold red]")
                return

            title.update(
                f"[bold cyan]Subject {subject.name} Classroom #{project.classroom_id} > Project {project.name} Team #{team.id}[/bold cyan]"
            )

    async def load_students(self) -> None:
        """Refresh students and memberships."""

        async with get_async_session() as session:
            # Get all students
            available_students = await session.execute(
                select(Student)
                .join(ClassroomMembership)
                .join(Classroom)
                .join(Project)
                .join(Team)
                .where(Team.id == self.team_id)
                .where(
                    ~select(TeamMembership)
                    .filter(TeamMembership.student_id == Student.id, TeamMembership.team_id != self.team_id)
                    .exists()
                )
            )
            available_students = available_students.scalars().all()

            available_list = self.query_one("#available-students", ScrollableContainer)
            available_list.remove_children()
            current_list = self.query_one("#current-members", ScrollableContainer)
            current_list.remove_children()

            for student in available_students:
                if await session.get(TeamMembership, {"student_id": student.id, "team_id": self.team_id}):
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
                membership = TeamMembership(student_id=student_id, team_id=self.team_id)
                session.add(membership)
                await session.commit()
            await self.load_students()
        elif button_id.startswith("remove-"):
            student_id = int(button_id.split("-")[1])
            async with get_async_session() as session:
                membership = await session.get(
                    TeamMembership,
                    {"student_id": student_id, "team_id": self.team_id},
                )
                if membership:
                    await session.delete(membership)
                    await session.commit()
            await self.load_students()

        for screen in self.app.screen_stack:
            if isinstance(screen, ProjectDetailsScreen) and screen.project_id == self.project_id:
                await screen.load_deliveries()


from .project import ProjectDetailsScreen
