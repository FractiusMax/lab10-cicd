# Лабораторная работа № 10 — Организация CI/CD и автоматизированного тестирования

Демонстрационный проект: веб-форма «Заявка на консультацию» + автотесты
пользовательского интерфейса на Selenium + конвейер CI/CD на GitHub Actions.

Репозиторий: **https://github.com/FractiusMax/lab10-cicd** (приватный).

Состояние публикации (09.11.2026):

* три ветки `main`, `dev`, `fix` отправлены в удалённый репозиторий;
* pull request № 1 (`fix` → `dev`) и pull request № 2 (`dev` → `main`) созданы
  и слиты после успешного прогона CI;
* выполнено 9 прогонов конвейера: 7 прогонов CI — успешные, 2 прогона CD —
  неуспешные на шаге `configure-pages`: GitHub Pages не включается для
  приватного репозитория на бесплатном тарифе. Чтобы публикация заработала,
  достаточно перевести репозиторий в публичный режим — workflow менять не нужно.

## Состав проекта

| Путь | Назначение |
|---|---|
| `index.html` | Веб-страница с формой заявки |
| `assets/styles.css` | Оформление страницы |
| `assets/script.js` | Клиентская валидация и отправка формы |
| `pages/form_page.py` | Page Object Model для страницы формы |
| `locators.py` | Локаторы элементов страницы |
| `utils/browser_factory.py` | Фабрика браузера Chrome и настройки запуска |
| `conftest.py` | Фикстуры pytest: локальный сервер, браузер, скриншоты |
| `tests/test_01_form.py` | Автотесты пользовательского интерфейса |
| `.github/workflows/ci.yml` | CI: запуск автотестов при каждом push и pull request |
| `.github/workflows/pages.yml` | CD: публикация на GitHub Pages после успешных тестов в `main` |

## Запуск тестов локально

```powershell
cd D:\bbgg\tpo\ЛР10
pip install -r requirements.txt
python -m pytest
```

Полезные варианты запуска:

```powershell
# Отчёт в HTML
python -m pytest --html=artifacts/report.html --self-contained-html

# Видимый браузер вместо headless
python -m pytest --browser-options "headless=false;window-size=1280,800"

# Проверка опубликованной версии на GitHub Pages
python -m pytest --base-url https://<user>.github.io/<repo>
```

## Схема работы конвейера

```
push в любую ветку / pull request
            │
            ▼
    ┌───────────────────┐
    │  CI (ci.yml)      │  установка зависимостей → Chrome → pytest
    └─────────┬─────────┘
              │ все тесты прошли?
              │ нет → красный статус, слияние запрещено
              ▼ да
   pull request  fix → dev  →  слияние
              │
              ▼
   pull request  dev → main  →  слияние
              │
              ▼
    ┌───────────────────┐
    │  CD (pages.yml)    │  тесты в main → публикация на GitHub Pages
    └───────────────────┘
```

## Правила работы с ветками

* `main` — стабильная версия, попадает на GitHub Pages; изменения только
  через pull request;
* `dev` — основная ветка разработки;
* `fix/<задача>` — отдельная ветка под каждую задачу (исправление или
  новая функциональность), создаётся от `dev`.

Порядок работы: `fix/*` → pull request в `dev` → после зелёных тестов
слияние в `dev` → pull request из `dev` в `main` → после зелёных тестов
слияние в `main` → автоматическая публикация.
