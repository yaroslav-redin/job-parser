# Job Parser & Recommender System

Проект представляет собой рекрутинговый портал с функционалом парсинга вакансий и рекомендательной системой на основе ML.

## 🚀 Как запустить проект (для разработчиков)

Для запуска вам понадобится только установленный **Docker Desktop** и **Git**.

### 1. Клонирование репозитория
```bash
git clone https://github.com/yaroslav-redin/job-parser.git
cd job_parser
```

### 2. Запуск через Docker
Находясь в корневой папке проекта (job_parser), выполните команду:
```bash
docker-compose up -d --build
```

### 3. Готово!
Докер автоматически скачает базы данных, установит все зависимости Python и Node.js.
Проект будет доступен по адресам:
* **Frontend (САМ САЙТ):** [http://localhost:5173](http://localhost:5173)
* **Backend API (БЭКЕНД с апи-запросами):** [http://localhost:8000/docs](http://localhost:8000/docs)

*Примечание: При первом запуске скачивание образов (PostgreSQL, Redis, Python, Node) может занять 3-5 минут в зависимости от скорости интернета.*

## 🛠 Архитектура (Стек)
* **Frontend:** Vue 3 (Composition API), Pinia, Vue Router, Tailwind/Чистый CSS.
* **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL (+ pgvector), Redis.
```
