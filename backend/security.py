from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt

SECRET_KEY = "super_secret_diplom_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

# Настройка алгоритма хэширования (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Проверяет, совпадает ли введенный пароль с хэшем из БД"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Превращает пароль в нечитаемый хэш"""
    return pwd_context.hash(password)

def create_access_token(data: dict):
    """Создает JWT токен"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Генерируем токен
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt