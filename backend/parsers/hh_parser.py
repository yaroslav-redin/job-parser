import httpx
import asyncio
import re
from sqlalchemy import select
from database import AsyncSessionLocal
import models


class HHParser:
    def __init__(self):
        self.base_url = "https://api.hh.ru/vacancies"

        # Более "реалистичные" заголовки
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
        }

    def clean_html(self, raw_html: str) -> str:
        if not raw_html:
            return ""

        cleanr = re.compile("<.*?>")
        cleantext = re.sub(cleanr, "", raw_html)

        return (
            cleantext.replace("&quot;", '"')
            .replace("&nbsp;", " ")
            .replace("&laquo;", '"')
            .replace("&raquo;", '"')
        )

    async def safe_request(self, client: httpx.AsyncClient, url: str, params=None):
        """Retry + backoff для защиты от 403"""
        for attempt in range(3):
            try:
                response = await client.get(
                    url,
                    params=params,
                    headers=self.headers,
                )

                if response.status_code == 200:
                    return response

                if response.status_code == 403:
                    wait_time = 3 * (attempt + 1)
                    print(f"[HH Parser] 403, ждём {wait_time}s...")
                    await asyncio.sleep(wait_time)

                else:
                    response.raise_for_status()

            except Exception as e:
                print(f"[HH Parser] Ошибка запроса: {e}")
                await asyncio.sleep(2)

        return None

    async def fetch_vacancies(self, query: str = "IT", pages: int = 1):
        print(f"\n[HH Parser] Старт парсинга: '{query}'")

        async with httpx.AsyncClient(timeout=15.0) as client:
            async with AsyncSessionLocal() as db:
                added_count = 0

                for page in range(pages):
                    print(f"[HH Parser] Страница {page + 1}/{pages}")

                    params = {
                        "text": query,
                        "per_page": 10,
                        "page": page,
                        # можно убрать area, чтобы не ловить фильтры
                        # "area": 113
                    }

                    response = await self.safe_request(
                        client, self.base_url, params
                    )

                    if not response:
                        print("[HH Parser] Не удалось получить данные")
                        break

                    data = response.json()
                    items = data.get("items", [])

                    if not items:
                        print("[HH Parser] Нет вакансий")
                        break

                    for item in items:
                        vac_url = item.get("alternate_url")

                        # проверка дублей
                        existing = await db.execute(
                            select(models.Vacancy).where(
                                models.Vacancy.url == vac_url
                            )
                        )

                        if existing.scalars().first():
                            continue

                        # используем snippet вместо запроса деталей
                        snippet = item.get("snippet", {})

                        description = self.clean_html(
                            (snippet.get("responsibility") or "")
                            + "\n"
                            + (snippet.get("requirement") or "")
                        )

                        # fallback если пусто
                        if not description:
                            description = "Описание не указано"

                        new_vac = models.Vacancy(
                            title=item.get("name", "Без названия"),
                            company=item.get("employer", {}).get(
                                "name", "Компания не указана"
                            ),
                            description=description,
                            source="hh",
                            url=vac_url,
                            is_published=True,
                        )

                        db.add(new_vac)
                        added_count += 1

                        # маленькая пауза между вакансиями
                        await asyncio.sleep(0.3)

                    await db.commit()
                    print(f"[HH Parser] Страница {page + 1} готова")

                    # пауза между страницами (ВАЖНО)
                    await asyncio.sleep(2)

                print(
                    f"[HH Parser] Готово! Добавлено вакансий: {added_count}\n"
                )

                return {"status": "success", "added": added_count}


async def run_hh_parser(query: str = "IT", pages: int = 1):
    parser = HHParser()
    return await parser.fetch_vacancies(query, pages)