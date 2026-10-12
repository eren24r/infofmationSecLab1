# Secure REST API

Защищенное REST API с JWT аутентификацией и интеграцией CI/CD
Рахматов Неъматджон. Р3432
Лабораторная работа №1

## Описание проекта

Защищенное REST API, разработанное с использованием FastAPI. API включает аутентификацию пользователей, управление данными и систему постов с интеграцией CI/CD для автоматического сканирования безопасности.

### API Endpoints

#### 1. **POST /auth/login** - Аутентификация пользователя
- **Описание**: Вход в систему с получением JWT токена
- **Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```
- **Response**:
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

#### 2. **GET /api/data** - Получение списка пользователей (защищено)
- **Описание**: Получение списка всех пользователей системы
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
```json
[
  {
    "id": 1,
    "username": "string",
    "email": "string",
    "created_at": "2025-11-25T00:00:00"
  }
]
```

#### 3. **POST /auth/register** - Регистрация нового пользователя
- **Описание**: Создание нового пользователя в системе
- **Request Body**:
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

#### Дополнительные endpoints:
- **POST /api/posts/** - Создание поста (защищено)
- **GET /api/posts/** - Получение всех постов (защищено)
- **GET /api/posts/{post_id}** - Получение конкретного поста (защищено)
- **DELETE /api/posts/{post_id}** - Удаление поста (защищено, только автор)

## Реализованные меры безопасности

### 1. Защита от SQL-инъекций (SQLi)
- SQLAlchemy ORM с параметризованными запросами
- Реализация:
  - Все запросы к БД используют ORM методы SQLAlchemy
  - Автоматическое экранирование параметров
  - Отсутствие конкатенации строк в SQL запросах

**Примеры в коде**:
```python
# app/routers/auth.py:13
user = db.query(User).filter(User.username == user_credentials.username).first()

# app/routers/posts.py:42
post = db.query(Post).filter(Post.id == post_id).first()
```

### 2. Защита от XSS
- HTML экранирование через встроенную библиотеку `html`
- Реализация:
  - Автоматическая санитизация всех пользовательских входных данных
  - Валидаторы Pydantic для очистки данных перед сохранением

**Примеры в коде**:
```python
# app/schemas.py:14-16
@field_validator('username', 'password')
def sanitize_string(cls, v):
    return html.escape(v) if isinstance(v, str) else v
```

### 3. Защита от Broken Authentication
- JWT токены: Безопасная аутентификация с временными токенами
- Хеширование паролей: Использование bcrypt для хеширования
- Middleware: Автоматическая проверка токенов на защищенных endpoints

Реализация:
```python
# app/security.py:11-12 - Хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# app/security.py:20-29 - Создание JWT токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# app/security.py:31-47 - Верификация токена
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    username: str = payload.get("sub")
    return username
```

### 4. Дополнительно
- Валидация входных данных: Pydantic модели с строгой типизацией
- HTTPS: Поддержка безопасных соединений
- CORS: Настройка разрешенных источников
- Пользователи могут удалять только свои посты

## Установка и запуск

1.
```bash
python -m venv venv
source venv/bin/activate
```

2.
```bash
pip install -r requirements.txt
```

3.
```bash
cp .env.example .env
```

4.
```bash
python run.py
```

5.
```bash
curl http://localhost:8000/health
```

Документация Swagger: `http://localhost:8000/docs`

## Автор

eren24r
