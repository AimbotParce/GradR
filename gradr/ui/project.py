"""
Projects management screens.
"""

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
    Delivery,
    Grade,
    Project,
    Student,
    Subject,
    Team,
    TeamMembership,
)
from .base import BaseScreen
from .utils import open_native_file_picker, view_delivery


class ProjectDetailsScreen(BaseScreen):
    """Screen for managing projects within a classroom."""

    def __init__(self, project_id: int):
        self.project_id = project_id
        super().__init__()

    def compose(self):
        yield Header()
        yield Container(
            Label(id="classroom-title"),
            Label(id="project-name"),
            Label(id="project-description"),
            Label(""),
            Label("[bold cyan]Deliveries:[/bold cyan]"),
            ScrollableContainer(id="deliveries-list"),
            Button("Add Team", id="add-team", variant="primary"),
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Load projects."""
        await self.load_project_info()
        await self.load_deliveries()

    async def load_project_info(self) -> None:
        """Load project details from database."""

        async with get_async_session() as session:
            project = await session.get(Project, self.project_id)

            classroom_title = self.query_one("#classroom-title", Label)
            name = self.query_one("#project-name", Label)
            desc = self.query_one("#project-description", Label)

            if not project:
                classroom_title.update("[bold red]Project not found[/bold red]")
                return
            name.update(f"[bold cyan]Project Name:[/bold cyan] {project.name}")
            desc.update(f"[bold cyan]Description:[/bold cyan] {project.description or 'No description'}")

            subject_result = await session.execute(
                select(Subject).where(Subject.id == Classroom.subject_id and Classroom.id == project.classroom_id)
            )
            subject = subject_result.scalars().first()
            if not subject:
                classroom_title.update("[bold red]Subject not found[/bold red]")
                return
            classroom_title.update(f"[bold cyan]Subject {subject.name} Classroom #{project.classroom_id}[/bold cyan]")

    async def load_deliveries(self) -> None:
        """Refresh projects list."""

        deliveries_list = self.query_one("#deliveries-list", ScrollableContainer)
        deliveries_list.remove_children()

        async with get_async_session() as session:
            teams_result = await session.execute(select(Team).where(Team.project_id == self.project_id))
            teams = teams_result.scalars().all()

            deliveries_result = await session.execute(
                select(Delivery).where(Delivery.team_id == Team.id and Team.project_id == self.project_id)
            )
            deliveries = deliveries_result.scalars().all()
            team_id_to_deliveries = {delivery.team_id: delivery for delivery in deliveries}

            for team in teams:
                participants_result = await session.execute(
                    select(Student).join(TeamMembership).where(TeamMembership.team_id == team.id)
                )
                participants = participants_result.scalars().all()
                participant_names = " + ".join([p.name for p in participants]) if participants else "(No members)"
                delivery = team_id_to_deliveries.get(team.id)
                parts = []
                if delivery:
                    grade_result = await session.execute(
                        select(func.avg(Grade.grade)).where(Grade.delivery_id == delivery.id)
                    )
                    avg_grade = grade_result.scalars().first()

                    deliveries_list.mount(
                        HorizontalGroup(
                            Button(participant_names, id=f"team-{team.id}"),
                            Button("Add Submission", id=f"add-delivery-{team.id}", variant="primary"),
                            Button(f"View Submission", id=f"delivery-{delivery.id}", variant="warning"),
                            Button(f"Grade", id=f"grade-{delivery.id}", variant="success"),
                            Button("Delete Team", id=f"delete-{team.id}", variant="error"),
                            Button(f"Grade: {avg_grade:.2f}" if avg_grade is not None else "Grade: N/A"),
                        )
                    )
                else:
                    deliveries_list.mount(
                        HorizontalGroup(
                            Button(participant_names, id=f"team-{team.id}"),
                            Button("Add Submission", id=f"add-delivery-{team.id}", variant="primary"),
                            Button(f"View Submission", variant="warning", disabled=True),
                            Button(f"Grade", variant="success", disabled=True),
                            Button("Delete Team", id=f"delete-{team.id}", variant="error"),
                            Button("Grade: N/A"),
                        )
                    )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if not button_id:
            return
        if button_id == "add-team":
            new_team_id = await self._create_team()
            await self.app.push_screen(TeamDetailsScreen(new_team_id))
        elif button_id.startswith("team-"):
            team_id = int(button_id.split("-")[1])
            await self.app.push_screen(TeamDetailsScreen(team_id))
        elif button_id.startswith("delivery-"):
            delivery_id = int(button_id.split("-")[1])
            await view_delivery(delivery_id)
        elif button_id.startswith("add-delivery-"):
            team_id = int(button_id.split("-")[2])
            await self._add_delivery(team_id)
            await self.load_deliveries()
        elif button_id.startswith("grade-"):
            delivery_id = int(button_id.split("-")[1])
            await self.app.push_screen(GradeTeamScreen(delivery_id))
        elif button_id.startswith("delete-"):
            team_id = int(button_id.split("-")[1])
            await self._delete_team(team_id)

    async def _add_delivery(self, team_id: int):
        """Add a delivery file for a team."""
        # Open window to select and upload delivery file
        file_selection = open_native_file_picker()
        if file_selection:
            file_bytes = file_selection["file_bytes"]
            file_name = file_selection["file_name"]
            async with get_async_session() as session:
                delivery = Delivery(team_id=team_id, file_name=file_name, file_bytes=file_bytes)
                session.add(delivery)
                await session.commit()

    async def _create_team(self) -> int:
        """Create a new team for the project."""
        async with get_async_session() as session:
            team = Team(project_id=self.project_id)
            session.add(team)
            await session.commit()
            team_id = team.id
        await self.load_deliveries()
        return team_id

    async def _delete_team(self, team_id: int):
        """Delete a team from the project."""
        async with get_async_session() as session:
            team = await session.get(Team, team_id)
            if team:
                await session.delete(team)
                await session.commit()
        await self.load_deliveries()


from .grade import GradeTeamScreen
from .team import TeamDetailsScreen
