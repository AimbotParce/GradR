from sqlalchemy.orm import declarative_base, registry

Base = declarative_base()
mapper_registry = registry()

from .classroom import Classroom
from .delivery import Delivery
from .grade import Grade
from .project import Project
from .student import Student
from .subject import Subject
from .teacher import Teacher
from .team import Team
from .team_membership import TeamMembership

__all__ = [
    "Classroom",
    "Delivery",
    "Project",
    "Student",
    "Subject",
    "Team",
    "TeamMembership",
    "Teacher",
    "Grade",
]
