from fastapi.security import OAuth2PasswordBearer
import jwt
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, get_db
from fastapi import BackgroundTasks
from parsers.hh_parser import run_hh_parser
from fastapi import UploadFile, File
from fastapi.staticfiles import StaticFiles

import models
import schemas
import security
import os
import shutil
from sqlalchemy.orm import selectinload




@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # Включаем векторное расширение
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)
    yield

# Оставляем ТОЛЬКО ОДИН экземпляр приложения
app = FastAPI(title="Job Parser API", lifespan=lifespan)

# Создаем папку uploads, если её нет
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Настройка CORS должна идти СРАЗУ ПОСЛЕ создания app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ТЕСТОВЫЙ РОУТ ---
@app.get("/test-db")
async def test_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT COUNT(*) FROM users;"))
    return {"users_count": result.scalar()}


# --- РЕГИСТРАЦИЯ ---
@app.post("/auth/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Проверяем, нет ли уже такого email в базе
    query = select(models.User).where(models.User.email == user.email)
    result = await db.execute(query)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    
    # 2. Хэшируем пароль
    hashed_pwd = security.get_password_hash(user.password)
    
    # 3. Создаем пользователя
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pwd,
        full_name=user.full_name,
        role=user.role
    )
    
    # 4. Сохраняем в базу
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user) # Получаем сгенерированный ID
    
    return new_user


# --- ЛОГИН (ПОЛУЧЕНИЕ ТОКЕНА) ---
@app.post("/auth/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # В Swagger форма отправляет поле 'username', мы воспринимаем его как 'email'
    query = select(models.User).where(models.User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalars().first()
    
    # Проверяем, существует ли пользователь и совпадает ли пароль
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Генерируем токен, "зашивая" в него ID пользователя и его роль
    access_token = security.create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Указываем, где FastAPI должен искать токен (в заголовках запроса)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Функция-зависимость для проверки токена
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        # Расшифровываем токен
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Неверный токен")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Токен истек или недействителен")
    
    # Ищем пользователя в БД
    result = await db.execute(select(models.User).where(models.User.id == int(user_id)))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user

async def get_optional_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)), db: AsyncSession = Depends(get_db)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: str = payload.get("sub")
        result = await db.execute(select(models.User).where(models.User.id == int(user_id)))
        return result.scalars().first()
    except:
        return None
    

# Роут для получения данных о себе
@app.get("/auth/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# Обновление текстовых данных профиля
@app.put("/users/me", response_model=schemas.UserResponse)
async def update_profile(user_update: schemas.UserUpdate, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.resume_text is not None:
        current_user.resume_text = user_update.resume_text
    if user_update.company_name is not None:
        current_user.company_name = user_update.company_name # Сохраняем компанию
    
    await db.commit()
    await db.refresh(current_user)
    return current_user

# Загрузка аватарки
@app.post("/users/me/avatar", response_model=schemas.UserResponse)
async def upload_avatar(file: UploadFile = File(...), current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Генерируем уникальное имя файла
    file_location = f"uploads/{current_user.id}_{file.filename}"
    # Сохраняем файл физически
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Сохраняем путь в базу
    current_user.avatar = f"/{file_location}"
    await db.commit()
    await db.refresh(current_user)
    return current_user

def check_admin(user: models.User):
    if user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав. Требуется роль администратора.")

# 1. Получить всех пользователей
@app.get("/admin/users") # Убрали response_model, так как теперь возвращаем словарь
async def get_all_users(
    skip: int = 0, 
    limit: int = 10, 
    current_user: models.User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    check_admin(current_user)
    
    # Считаем общее количество
    total_result = await db.execute(text("SELECT COUNT(*) FROM users"))
    total = total_result.scalar()
    
    # Получаем срез
    result = await db.execute(
        select(models.User).order_by(models.User.id).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    
    return {
        "users": users,
        "total": total
    }

# 2. Изменить роль пользователя
@app.put("/admin/users/{user_id}/role", response_model=schemas.UserResponse)
async def update_user_role(user_id: int, role: str, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    check_admin(current_user)
    
    # Ищем пользователя
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    target_user = result.scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Обновляем роль
    try:
        target_user.role = models.UserRole(role)
        await db.commit()
        await db.refresh(target_user)
        return target_user
    except ValueError:
        raise HTTPException(status_code=400, detail="Недопустимая роль. Используйте: seeker, recruiter, admin")

# 3. Удалить пользователя
@app.delete("/admin/users/{user_id}")
async def delete_user(user_id: int, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    check_admin(current_user)
    
    # Нельзя удалить самого себя
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя удалить свой собственный аккаунт")
        
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    target_user = result.scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
        
    await db.delete(target_user)
    await db.commit()
    return {"status": "success", "message": "Пользователь удален"}

def check_recruiter(user: models.User):
    if user.role != models.UserRole.recruiter:
        raise HTTPException(status_code=403, detail="Только рекрутеры могут управлять вакансиями")
    

# Запуск парсера HH.ru (Фоновая задача)
@app.post("/admin/parse/hh")
async def start_hh_parser(
    background_tasks: BackgroundTasks, # Инструмент FastAPI для фоновых задач
    query: str = "IT", 
    pages: int = 1, 
    current_user: models.User = Depends(get_current_user)
):
    check_admin(current_user) # Только админ может запускать парсер
    
    # Говорим FastAPI: "Отправь пользователю ответ 'ОК', а эту функцию запусти в фоне"
    background_tasks.add_task(run_hh_parser, query, pages)
    
    return {"status": "success", "message": f"Парсер запущен в фоне. Запрос: '{query}', Страниц: {pages}"}

# Создать вакансию
@app.post("/recruiter/vacancies", response_model=schemas.VacancyResponse)
async def create_vacancy(vacancy: schemas.VacancyCreate, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    check_recruiter(current_user)
    
    new_vac = models.Vacancy(
        title=vacancy.title,
        description=vacancy.description,
        company=current_user.company_name or current_user.full_name or "Не указана",
        author_id=current_user.id,
        source="internal",
        is_published=vacancy.is_published
    )
    db.add(new_vac)
    await db.commit()
    await db.refresh(new_vac)
    return new_vac

# Получить свои вакансии (с пагинацией)
@app.get("/recruiter/vacancies")
async def get_my_vacancies(skip: int = 0, limit: int = 10, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    check_recruiter(current_user)
    
    # Считаем общее количество вакансий
    total_result = await db.execute(select(func.count()).select_from(models.Vacancy).where(models.Vacancy.author_id == current_user.id))
    total = total_result.scalar()
    
    # Сложный запрос: получаем вакансии И количество откликов (applications) к каждой
    query = (
        select(models.Vacancy, func.count(models.Application.id).label("app_count"))
        .outerjoin(models.Application, models.Vacancy.id == models.Application.vacancy_id)
        .where(models.Vacancy.author_id == current_user.id)
        .group_by(models.Vacancy.id)
        .order_by(models.Vacancy.id.desc())
        .offset(skip).limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    # Формируем список словарей для фронтенда
    vacancies_with_counts = []
    for vac, count in rows:
        v_dict = {
            "id": vac.id,
            "title": vac.title,
            "company": vac.company,
            "description": vac.description,
            "is_published": vac.is_published,
            "created_at": vac.created_at,
            "applications_count": count # Отправляем реальное число
        }
        vacancies_with_counts.append(v_dict)
    
    return {"vacancies": vacancies_with_counts, "total": total}

# Удалить свою вакансию
@app.delete("/recruiter/vacancies/{vac_id}")
async def delete_my_vacancy(vac_id: int, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    check_recruiter(current_user)
    result = await db.execute(select(models.Vacancy).where(models.Vacancy.id == vac_id, models.Vacancy.author_id == current_user.id))
    vac = result.scalars().first()
    if not vac:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
        
    await db.delete(vac)
    await db.commit()
    return {"status": "success"}

# Получить одну конкретную вакансию
@app.get("/vacancies/{vac_id}", response_model=schemas.VacancyResponse)
async def get_vacancy(vac_id: int, current_user: models.User = Depends(get_optional_current_user), db: AsyncSession = Depends(get_db)):
    vac = (await db.execute(select(models.Vacancy).where(models.Vacancy.id == vac_id))).scalars().first()
    if not vac: raise HTTPException(status_code=404, detail="Не найдено")
    
    response_vac = schemas.VacancyResponse.from_orm(vac)
    if current_user and current_user.role == models.UserRole.seeker:
        ints = (await db.execute(select(models.Interaction).where(models.Interaction.vacancy_id == vac_id, models.Interaction.user_id == current_user.id))).scalars().all()
        types = [i.interaction_type.value for i in ints]
        response_vac.is_viewed = "view" in types
        response_vac.is_liked = "like" in types
        response_vac.is_applied = "apply" in types
            
    return response_vac

# Откликнуться на вакансию (только для соискателей)
@app.post("/vacancies/{vac_id}/apply")
async def apply_to_vacancy(vac_id: int, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != models.UserRole.seeker: raise HTTPException(status_code=403, detail="Только соискатели")
    
    # 1. Записываем отклик (Application)
    existing_app = await db.execute(select(models.Application).where(models.Application.vacancy_id == vac_id, models.Application.applicant_id == current_user.id))
    if existing_app.scalars().first(): raise HTTPException(status_code=400, detail="Уже откликнулись")
    db.add(models.Application(vacancy_id=vac_id, applicant_id=current_user.id))
    
    # 2. Записываем взаимодействие для ML (Interaction = apply)
    db.add(models.Interaction(user_id=current_user.id, vacancy_id=vac_id, interaction_type=models.InteractionType.apply))
    
    await db.commit()
    return {"message": "Отклик отправлен"}

@app.post("/vacancies/{vac_id}/view")
async def record_view(vac_id: int, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role == models.UserRole.seeker:
        existing = await db.execute(select(models.Interaction).where(models.Interaction.vacancy_id == vac_id, models.Interaction.user_id == current_user.id, models.Interaction.interaction_type == models.InteractionType.view))
        if not existing.scalars().first():
            db.add(models.Interaction(user_id=current_user.id, vacancy_id=vac_id, interaction_type=models.InteractionType.view))
            await db.commit()
    return {"status": "ok"}

@app.post("/vacancies/{vac_id}/like")
async def toggle_like(vac_id: int, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != models.UserRole.seeker: raise HTTPException(status_code=403, detail="Только соискатели")
        
    existing = await db.execute(select(models.Interaction).where(models.Interaction.vacancy_id == vac_id, models.Interaction.user_id == current_user.id, models.Interaction.interaction_type == models.InteractionType.like))
    interaction = existing.scalars().first()
    
    if interaction:
        await db.delete(interaction) # Убираем лайк
        await db.commit()
        return {"status": "unliked"}
    else:
        db.add(models.Interaction(user_id=current_user.id, vacancy_id=vac_id, interaction_type=models.InteractionType.like))
        await db.commit()
        return {"status": "liked"}
    

@app.get("/seeker/favorites", response_model=list[schemas.VacancyResponse])
async def get_favorites(current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != models.UserRole.seeker: raise HTTPException(status_code=403)
        
    # Ищем ID всех лайкнутых вакансий
    likes = await db.execute(select(models.Interaction.vacancy_id).where(models.Interaction.user_id == current_user.id, models.Interaction.interaction_type == models.InteractionType.like))
    vac_ids = likes.scalars().all()
    
    if not vac_ids: return []
        
    # Достаем эти вакансии
    vacancies = await db.execute(select(models.Vacancy).where(models.Vacancy.id.in_(vac_ids)))
    res = []
    for v in vacancies.scalars().all():
        v_resp = schemas.VacancyResponse.from_orm(v)
        v_resp.is_liked = True
        res.append(v_resp)
    return res

# Редактировать вакансию (только для автора-рекрутера)
@app.put("/recruiter/vacancies/{vac_id}", response_model=schemas.VacancyResponse)
async def update_my_vacancy(vac_id: int, vac_update: schemas.VacancyUpdate, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    check_recruiter(current_user)
    result = await db.execute(select(models.Vacancy).where(models.Vacancy.id == vac_id, models.Vacancy.author_id == current_user.id))
    vac = result.scalars().first()
    if not vac:
        raise HTTPException(status_code=404, detail="Вакансия не найдена или вы не являетесь автором")
    
    if vac_update.title: vac.title = vac_update.title
    if vac_update.description: vac.description = vac_update.description
    if vac_update.is_published is not None: vac.is_published = vac_update.is_published
    
    await db.commit()
    await db.refresh(vac)
    return vac

@app.get("/vacancies")
async def get_all_vacancies(
    search: str = None, 
    skip: int = 0, 
    limit: int = 12, 
    # Используем опционального пользователя, чтобы лайки видело только авторизованный соискатель
    current_user: models.User = Depends(get_optional_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # 1. Поиск вакансий
    query = select(models.Vacancy).where(models.Vacancy.is_published == True)
    if search:
        query = query.where(
            (models.Vacancy.title.ilike(f"%{search}%")) | 
            (models.Vacancy.description.ilike(f"%{search}%")) |
            (models.Vacancy.company.ilike(f"%{search}%"))
        )
    
    # 2. Считаем общее кол-во
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    
    # 3. Получаем список вакансий
    result = await db.execute(query.order_by(models.Vacancy.created_at.desc()).offset(skip).limit(limit))
    vacancies = result.scalars().all()
    
    # 4. Если юзер — соискатель, ищем все его лайки и просмотры для ЭТИХ вакансий
    user_interactions = []
    if current_user and current_user.role == models.UserRole.seeker and vacancies:
        vac_ids = [v.id for v in vacancies]
        int_query = await db.execute(
            select(models.Interaction).where(
                models.Interaction.user_id == current_user.id,
                models.Interaction.vacancy_id.in_(vac_ids)
            )
        )
        user_interactions = int_query.scalars().all()

    # 5. Собираем итоговый ответ с проставленными флагами is_liked / is_viewed
    res_vacancies = []
    for vac in vacancies:
        # Превращаем модель SQLAlchemy в Pydantic схему
        v_resp = schemas.VacancyResponse.from_orm(vac)
        
        if current_user and current_user.role == models.UserRole.seeker:
            # Ищем, какие типы действий юзер совершал с этой вакансией
            actions = [i.interaction_type.value for i in user_interactions if i.vacancy_id == vac.id]
            v_resp.is_viewed = "view" in actions
            v_resp.is_liked = "like" in actions
            v_resp.is_applied = "apply" in actions
            
        res_vacancies.append(v_resp)
    
    return {"vacancies": res_vacancies, "total": total}

@app.get("/seeker/applications", response_model=list[schemas.ApplicationSeekerResponse])
async def get_my_applications(current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != models.UserRole.seeker:
        raise HTTPException(status_code=403, detail="Только соискатель")
    
    # Загружаем отклики вместе с информацией о вакансии
    query = (
        select(models.Application)
        .options(selectinload(models.Application.vacancy))
        .where(models.Application.applicant_id == current_user.id)
        .order_by(models.Application.created_at.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()

# 2. Для рекрутера: Посмотреть отклики на конкретную вакансию
@app.get("/recruiter/vacancies/{vac_id}/applications", response_model=list[schemas.ApplicationRecruiterResponse])
async def get_vacancy_applications(vac_id: int, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    check_recruiter(current_user)
    
    # Проверяем, принадлежит ли вакансия рекрутеру
    vac = await db.execute(select(models.Vacancy).where(models.Vacancy.id == vac_id, models.Vacancy.author_id == current_user.id))
    if not vac.scalars().first():
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    
    # Загружаем отклики вместе с информацией о кандидате
    query = (
        select(models.Application)
        .options(selectinload(models.Application.applicant))
        .where(models.Application.vacancy_id == vac_id)
        .order_by(models.Application.created_at.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()

# 3. Для рекрутера: Изменить статус отклика
@app.put("/recruiter/applications/{app_id}/status")
async def update_application_status(app_id: int, status: str, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    check_recruiter(current_user)
    
    query = select(models.Application).options(selectinload(models.Application.vacancy)).where(models.Application.id == app_id)
    result = await db.execute(query)
    application = result.scalars().first()
    
    if not application or application.vacancy.author_id != current_user.id:
        raise HTTPException(status_code=404, detail="Отклик не найден")
    
    try:
        # Проверяем, существует ли такой статус в Enum
        application.status = models.ApplicationStatus(status)
        await db.commit()
        return {"status": "success"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный статус")