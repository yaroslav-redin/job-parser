from pydantic import BaseModel, EmailStr
from typing import Optional
from models import UserRole
from datetime import datetime

# Схема для регистрации (то, что мы ждем от пользователя)
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.seeker

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    resume_text: Optional[str] = None
    company_name: Optional[str] = None

# Схема ответа (то, что мы возвращаем, БЕЗ ПАРОЛЯ!)
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: UserRole
    resume_text: Optional[str] # Добавили
    company_name: Optional[str]
    avatar: Optional[str] 

    class Config:
        from_attributes = True

# Схема для JWT токена
class Token(BaseModel):
    access_token: str
    token_type: str

class VacancyCreate(BaseModel):
    title: str
    description: str
    is_published: bool = True

class VacancyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_published: Optional[bool] = None

class VacancyResponse(BaseModel):
    id: int
    title: str
    company: Optional[str]
    description: str
    source: str
    is_published: bool
    author_id: Optional[int]
    is_applied: bool = False
    is_liked: bool = False   
    is_viewed: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class AppVacancyInfo(BaseModel):
    id: int
    title: str
    company: Optional[str]
    class Config: from_attributes = True

class AppUserInfo(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    resume_text: Optional[str]
    avatar: Optional[str]
    class Config: from_attributes = True

# Схема для соискателя (видит вакансию и статус)
class ApplicationSeekerResponse(BaseModel):
    id: int
    status: str
    created_at: datetime
    vacancy: AppVacancyInfo
    class Config: from_attributes = True

# Схема для рекрутера (видит кандидата и статус)
class ApplicationRecruiterResponse(BaseModel):
    id: int
    status: str
    created_at: datetime
    applicant: AppUserInfo
    class Config: from_attributes = True