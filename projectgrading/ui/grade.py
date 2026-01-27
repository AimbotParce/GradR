"""
Projects management screens.
"""

from sqlalchemy import select
from textual.containers import Container, HorizontalGroup
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
from .utils import view_delivery


class GradeTeamScreen(BaseScreen):
    """Screen for grading a project for a team."""

    def __init__(self, delivery_id: int):
        super().__init__()
        self.delivery_id = delivery_id

    def compose(self):
        yield Header()
        yield Container(
            Label(id="classroom-title"),
            Label(id="project-title"),
            Label(id="team-participants"),
            Label(""),
            Label("[bold cyan]Delivery file:[/bold cyan]", id="delivery-file"),
            Label("[bold cyan]Stored at:[/bold cyan]", id="stored-at"),
            Input(placeholder="Enter grade here", id="grade-input"),
            Input(placeholder="Enter comments here", id="comments-input"),
            HorizontalGroup(
                Button("Submit Grade", id="submit-grade", variant="success"),
                Button("View Submission", id="view-submission", variant="warning"),
            ),
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Load grading screen."""
        await self.load_delivery_info()
        await self.load_grade_info()

    async def load_delivery_info(self) -> None:
        """Load grading info from database."""
        async with get_async_session() as session:
            classroom_title = self.query_one("#classroom-title", Label)
            project_title = self.query_one("#project-title", Label)
            team_participants = self.query_one("#team-participants", Label)

            delivery_file = self.query_one("#delivery-file", Label)
            stored_at = self.query_one("#stored-at", Label)

            delivery = await session.get(Delivery, self.delivery_id)
            if not delivery:
                classroom_title.update("[bold red]Delivery not found[/bold red]")
                return

            delivery_file.update(f"[bold cyan]File Name:[/bold cyan] {delivery.file_name}")
            stored_at.update(f"[bold cyan]Stored at:[/bold cyan] {delivery.timestamp}")

            team = await session.get(Team, delivery.team_id)
            if not team:
                classroom_title.update("[bold red]Team not found[/bold red]")
                return

            project = await session.get(Project, team.project_id)
            if not project:
                classroom_title.update("[bold red]Project not found[/bold red]")
                return

            classroom = await session.get(Classroom, project.classroom_id)
            if not classroom:
                classroom_title.update("[bold red]Classroom not found[/bold red]")
                return

            subject = await session.get(Subject, classroom.subject_id)
            if not subject:
                classroom_title.update("[bold red]Subject not found[/bold red]")
                return

            classroom_title.update(f"[bold cyan]Subject {subject.name} Classroom #{classroom.id}[/bold cyan]")
            project_title.update(f"[bold cyan]Project {project.name} Team #{team.id}[/bold cyan]")

            # Load team members
            stmt = select(Student).join(TeamMembership).where(TeamMembership.team_id == team.id)
            result = await session.execute(stmt)
            students = result.scalars().all()
            student_names = " + ".join([s.name for s in students])
            team_participants.update(f"[bold cyan]Team Members:[/bold cyan] {student_names}")

    async def load_grade_info(self) -> None:
        """Load existing grade info if any."""
        async with get_async_session() as session:
            grade_result = await session.execute(select(Grade).where(Grade.delivery_id == self.delivery_id))
            grade = grade_result.scalars().first()
            if not grade:
                return

            grade_input = self.query_one("#grade-input", Input)
            comments_input = self.query_one("#comments-input", Input)

            grade_input.value = str(grade.grade)
            comments_input.value = grade.comments or ""

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if not button_id:
            return
        if button_id == "submit-grade":
            await self._submit_grade()
        elif button_id == "view-submission":
            await view_delivery(self.delivery_id)

    async def _submit_grade(self) -> None:
        """Submit the grade to the database."""
        grade_input = self.query_one("#grade-input", Input)
        comments_input = self.query_one("#comments-input", Input)

        grade_value = grade_input.value
        if not grade_value:
            return
        if not grade_value.replace(".", "", 1).isdigit():
            return
        grade_value = float(grade_value)
        if grade_value < 0 or grade_value > 10:
            return

        comments_value = comments_input.value

        async with get_async_session() as session:
            # Check if grade already exists
            existing_grade_result = await session.execute(
                select(Grade).where(Grade.delivery_id == self.delivery_id and Grade.teacher_id == 1)
            )  # Assuming teacher_id=1 for simplicity
            grade = existing_grade_result.scalars().first()
            if grade:
                # Update existing grade
                grade.grade = grade_value
                grade.comments = comments_value
            else:
                # Create new grade
                grade = Grade(
                    delivery_id=self.delivery_id,
                    grade=grade_value,
                    comments=comments_value,
                    teacher_id=1,  # Assuming teacher_id=1 for simplicity
                )

            session.add(grade)
            await session.commit()
        self.dismiss()

        for screen in self.app.screen_stack:
            if isinstance(screen, ProjectDetailsScreen):
                await screen.load_deliveries()


from .project import ProjectDetailsScreen
