# -*- coding: utf-8 -*-
"""Фикстуры pytest для лабораторной работы № 10 (CI/CD).

Здесь описано всё, что нужно автотестам пользовательского интерфейса:

* локальный HTTP-сервер с раздачей статики проекта (в CI проверка идёт
  против опубликованной версии, локально — против файлов проекта);
* браузер Chrome в headless-режиме;
* объект страницы (Page Object Model);
* снимки экрана в каталоге ``screenshots``.
"""
from __future__ import annotations

import functools
import http.server
import os
import threading

import pytest

from pages.form_page import FormPage
from utils.browser_factory import BrowserFactory, BrowserOptions

# Корень проекта — каталог, в котором лежит index.html
ROOT = os.path.dirname(os.path.abspath(__file__))

SCREENSHOTS_DIR = os.path.join(ROOT, "screenshots")
ARTIFACTS_DIR = os.path.join(ROOT, "artifacts")

#: Адрес опубликованной версии. Если переменная не задана, тесты работают
#: против локального сервера, который поднимает фикстура ``local_server``.
BASE_URL_ENV = "BASE_URL"


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    """Обработчик запросов без вывода в консоль."""

    def log_message(self, fmt, *args):  # noqa: A002 - сигнатура базового класса
        pass


# ---------------------------------------------------------------------------
# Настройки
# ---------------------------------------------------------------------------
def pytest_addoption(parser):
    """Добавить пользовательские параметры командной строки."""
    parser.addoption(
        "--browser-options",
        action="store",
        default=None,
        help=(
            "Опции браузера через точку с запятой: "
            "headless=false;window-size=1280,800;lang=ru-RU"
        ),
    )
    parser.addoption(
        "--base-url",
        action="store",
        default=None,
        help="Адрес проверяемой версии приложения (по умолчанию — локальный сервер)",
    )


def pytest_configure(config):
    """Подготовить каталоги артефактов."""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Запомнить результат шага — нужен для снимка экрана при ошибке."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


# ---------------------------------------------------------------------------
# Локальный сервер
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def local_server():
    """Поднять локальный HTTP-сервер с файлами проекта.

    Нужен, чтобы тесты проверяли страницу по HTTP, а не через ``file://`` —
    так поведение совпадает с публикацией на GitHub Pages.
    """
    handler = functools.partial(_QuietHandler, directory=ROOT)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


@pytest.fixture(scope="session")
def base_url(request, local_server) -> str:
    """Адрес проверяемой версии приложения."""
    cli_value = request.config.getoption("--base-url")
    if cli_value:
        return cli_value
    env_value = os.environ.get(BASE_URL_ENV)
    if env_value:
        return env_value
    return local_server


# ---------------------------------------------------------------------------
# Браузер
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def browser_options(request) -> BrowserOptions:
    """Итоговые опции браузера: по умолчанию + переменные окружения + CLI."""
    options = BrowserOptions.resolve(cli_spec=request.config.getoption("--browser-options"))
    print(f"\n[опции браузера] {options.describe()}")
    return options


@pytest.fixture(scope="session")
def browser_factory(browser_options) -> BrowserFactory:
    """Фабрика браузеров Chrome."""
    factory = BrowserFactory(browser_options)
    yield factory
    factory.close_all()


@pytest.fixture
def driver(browser_factory):
    """Браузер Chrome на один тест."""
    browser = browser_factory.create()
    yield browser
    browser_factory.release(browser)


# ---------------------------------------------------------------------------
# Объекты страниц
# ---------------------------------------------------------------------------
@pytest.fixture
def form_page(driver, base_url) -> FormPage:
    """Страница формы заявки."""
    return FormPage(driver, base_url)


# ---------------------------------------------------------------------------
# Снимки экрана
# ---------------------------------------------------------------------------
@pytest.fixture
def capture(driver, request):
    """Снимок экрана: ``capture("имя_снимка")``."""

    def _capture(name: str) -> str:
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)
        path = os.path.join(SCREENSHOTS_DIR, f"{safe}.png")
        with open(path, "wb") as file:
            file.write(driver.get_screenshot_as_png())
        print(f"[снимок] {path}")
        return path

    yield _capture

    report = getattr(request.node, "rep_call", None)
    if report is not None and report.failed:
        _capture(f"FAIL_{request.node.name}")
