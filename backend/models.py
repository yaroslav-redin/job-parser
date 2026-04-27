import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from database import Base # Теперь этот импорт будет работать правильно

class UserRole(enum.Enum):
    seeker = "seeker"
    recruiter = "recruiter"
    admin = "admin"

class ApplicationStatus(enum.Enum):
    pending = "pending"
    reviewed = "reviewed"
    invited = "invited"
    rejected = "rejected"

class InteractionType(enum.Enum):
    view = "view"
    like = "like"
    apply = "apply"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.seeker, nullable=False)
    resume_text = Column(Text, nullable=True)
    company_name = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    vacancies = relationship("Vacancy", back_populates="author")
    applications = relationship("Application", back_populates="applicant")
    interactions = relationship("Interaction", back_populates="user")

class Vacancy(Base):
    __tablename__ = "vacancies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    company = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    source = Column(String, default="internal", nullable=False)
    url = Column(String, unique=True, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_published = Column(Boolean, default=True)
    embedding = Column(Vector(312), nullable=True) 
    created_at = Column(DateTime, server_default=func.now())

    author = relationship("User", back_populates="vacancies")
    applications = relationship("Application", back_populates="vacancy")
    interactions = relationship("Interaction", back_populates="vacancy")

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.pending, nullable=False)
    cover_letter = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    vacancy = relationship("Vacancy", back_populates="applications")
    applicant = relationship("User", back_populates="applications")

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False)
    interaction_type = Column(Enum(InteractionType), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="interactions")
    vacancy = relationship("Vacancy", back_populates="interactions")