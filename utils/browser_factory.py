# -*- coding: utf-8 -*-
"""Фабрика браузера Chrome и настраиваемые опции запуска.

Опции собираются из трёх источников (в порядке возрастания приоритета):

1. значения по умолчанию класса :class:`BrowserOptions`;
2. переменные окружения (``HEADLESS``, ``WINDOW_SIZE``, ``LANG`` и др.);
3. аргумент командной строки pytest ``--browser-options``.

Примеры использования командной строки::

    python -m pytest --browser-options "headless=false;window-size=1280,800"
    python -m pytest --browser-options "lang=en-US;user-agent=Mozilla/5.0 ..."
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from typing import Any, Mapping

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Пользовательский агент без слова «Headless» — так окно браузера
# выглядит для сайта как обычный Chrome.
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36"
)

# Значения, которые разрешено передавать через переменные окружения
# и аргумент --browser-options.
_BOOL_KEYS = {
    "headless", "no-sandbox", "disable-dev-shm-usage", "disable-gpu",
    "use-automation-extension",
}
_INT_KEYS = {"implicit-wait", "page-load-timeout"}
_STR_KEYS = {"window-size", "window-position", "lang", "user-agent",
              "download-dir", "profile-dir"}

# Соответствие ключей настроек именам полей BrowserOptions
# («window-size» -> «window_size»)
_KEY_TO_FIELD = {
    key: key.replace("-", "_")
    for key in _BOOL_KEYS | _INT_KEYS | _STR_KEYS
}

# Имена переменных окружения -> ключи опций
_ENV_MAP = {
    "HEADLESS": "headless",
    "WINDOW_SIZE": "window-size",
    "WINDOW_POSITION": "window-position",
    "LANG": "lang",
    "USER_AGENT": "user-agent",
    "DOWNLOAD_DIR": "download-dir",
    "PROFILE_DIR": "profile-dir",
    "IMPLICIT_WAIT": "implicit-wait",
    "PAGE_LOAD_TIMEOUT": "page-load-timeout",
    "NO_SANDBOX": "no-sandbox",
    "DISABLE_DEV_SHM_USAGE": "disable-dev-shm-usage",
    "DISABLE_GPU": "disable-gpu",
    "USE_AUTOMATION_EXTENSION": "use-automation-extension",
}


def _as_bool(value: Any) -> bool:
    """Строка/значение -> логическое: '1', 'true', 'yes', 'on' — истина."""
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class BrowserOptions:
    """Набор опций запуска браузера Chrome.

    :param headless: запуск в режиме ``--headless=new``.
    :param window_size: размер окна, например ``"1440,900"``.
    :param window_position: положение окна на экране, например ``"0,0"``.
    :param lang: язык интерфейса браузера (``--lang``).
    :param user_agent: строка User-Agent.
    :param download_dir: каталог для загружаемых файлов.
    :param profile_dir: каталог профиля Chrome (``--user-data-dir``).
    :param no_sandbox: запуск без песочницы (нужно в контейнерах).
    :param disable_dev_shm_usage: не использовать ``/dev/shm``.
    :param disable_gpu: отключить аппаратное ускорение.
    :param use_automation_extension: оставить расширение автоматизации.
    :param exclude_switches: список переключателей, скрывающих Selenium.
    :param implicit_wait: таймаут неявного ожидания, сек.
    :param page_load_timeout: таймаут загрузки страницы, сек.
    :param extra_args: дополнительные аргументы командной строки Chrome.
    """

    headless: bool = True
    window_size: str = "1440,900"
    window_position: str = "0,0"
    lang: str = "ru-RU"
    user_agent: str = DEFAULT_USER_AGENT
    download_dir: str = ""
    profile_dir: str = ""
    no_sandbox: bool = True
    disable_dev_shm_usage: bool = True
    disable_gpu: bool = True
    use_automation_extension: bool = False
    exclude_switches: tuple[str, ...] = ("enable-automation",)
    implicit_wait: float = 5.0
    page_load_timeout: float = 60.0
    extra_args: tuple[str, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "BrowserOptions":
        """Собрать опции из переменных окружения."""
        env = os.environ if env is None else env
        values: dict[str, Any] = {}
        for env_name, key in _ENV_MAP.items():
            raw = env.get(env_name)
            if raw is None or raw == "":
                continue
            field_name = _KEY_TO_FIELD[key]
            if key in _BOOL_KEYS:
                values[field_name] = _as_bool(raw)
            elif key in _INT_KEYS:
                values[field_name] = float(raw)
            else:
                values[field_name] = raw
        options = cls()
        return replace(options, **values) if values else options

    @classmethod
    def parse_cli(cls, spec: str | None) -> dict[str, Any]:
        """Разобрать строку ``key=value;key=value`` в словарь переопределений.

        Поддерживаемые ключи: ``headless``, ``window-size``,
        ``window-position``, ``lang``, ``user-agent``, ``download-dir``,
        ``profile-dir``, ``no-sandbox``, ``disable-dev-shm-usage``,
        ``disable-gpu``, ``use-automation-extension``,
        ``implicit-wait``, ``page-load-timeout``.

        Ключ ``arg`` добавляет произвольный аргумент Chrome, например
        ``arg=--disable-blink-features=AutomationControlled``.
        """
        overrides: dict[str, Any] = {}
        extra: list[str] = []
        if not spec:
            return overrides
        for chunk in spec.split(";"):
            chunk = chunk.strip()
            if not chunk or "=" not in chunk:
                continue
            key, _, raw = chunk.partition("=")
            key = key.strip().lower()
            raw = raw.strip()
            if key == "arg":
                extra.append(raw)
            elif key in _KEY_TO_FIELD:
                field_name = _KEY_TO_FIELD[key]
                if key in _BOOL_KEYS:
                    overrides[field_name] = _as_bool(raw)
                elif key in _INT_KEYS:
                    overrides[field_name] = float(raw)
                else:
                    overrides[field_name] = raw
        if extra:
            overrides["extra_args"] = tuple(extra)
        return overrides

    @classmethod
    def from_cli(cls, spec: str | None) -> "BrowserOptions":
        """Собрать опции только из строки командной строки."""
        overrides = cls.parse_cli(spec)
        return replace(cls(), **overrides) if overrides else cls()

    @classmethod
    def resolve(cls, cli_spec: str | None = None,
                env: Mapping[str, str] | None = None) -> "BrowserOptions":
        """Опции из переменных окружения с наложением аргумента CLI.

        Явно заданные в CLI параметры имеют приоритет над окружением,
        даже если их значение совпадает со значением по умолчанию.
        """
        base = cls.from_env(env)
        overrides = cls.parse_cli(cli_spec)
        return replace(base, **overrides) if overrides else base

    # ------------------------------------------------------------------
    def describe(self) -> str:
        """Краткое текстовое описание опций — попадает в отчёт pytest."""
        parts = [
            f"headless={self.headless}",
            f"window={self.window_size}",
            f"position={self.window_position}",
            f"lang={self.lang}",
            f"implicit_wait={self.implicit_wait}",
        ]
        if self.profile_dir:
            parts.append(f"profile={self.profile_dir}")
        if self.download_dir:
            parts.append(f"downloads={self.download_dir}")
        if self.extra_args:
            parts.append("extra=" + ",".join(self.extra_args))
        return "; ".join(parts)


def build_chrome_options(options: BrowserOptions) -> Options:
    """Собрать объект :class:`Options` Chrome по настройкам."""
    chrome_options = Options()

    if options.headless:
        chrome_options.add_argument("--headless=new")
    if options.window_size:
        chrome_options.add_argument(f"--window-size={options.window_size}")
    if options.window_position:
        chrome_options.add_argument(f"--window-position={options.window_position}")
    if options.lang:
        chrome_options.add_argument(f"--lang={options.lang}")
    if options.user_agent:
        chrome_options.add_argument(f"--user-agent={options.user_agent}")
    if options.no_sandbox:
        chrome_options.add_argument("--no-sandbox")
    if options.disable_dev_shm_usage:
        chrome_options.add_argument("--disable-dev-shm-usage")
    if options.disable_gpu:
        chrome_options.add_argument("--disable-gpu")

    # Снятие признаков автоматизации: скрываем «enable-automation»,
    # отключаем расширение автоматизации и переключатель Blink.
    if options.exclude_switches:
        chrome_options.add_experimental_option("excludeSwitches",
                                               list(options.exclude_switches))
    chrome_options.add_experimental_option("useAutomationExtension",
                                           options.use_automation_extension)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Каталог загрузок и профиль пользователя
    prefs: dict[str, Any] = {}
    if options.download_dir:
        os.makedirs(options.download_dir, exist_ok=True)
        prefs["download.default_directory"] = os.path.abspath(options.download_dir)
        prefs["download.prompt_for_download"] = False
        prefs["download.directory_upgrade"] = True
        prefs["profile.default_content_setting_values.automatic_downloads"] = 1
    if options.profile_dir:
        os.makedirs(options.profile_dir, exist_ok=True)
        chrome_options.add_argument(f"--user-data-dir={os.path.abspath(options.profile_dir)}")
    if prefs:
        chrome_options.add_experimental_option("prefs", prefs)

    for extra in options.extra_args:
        chrome_options.add_argument(extra)

    return chrome_options


def create_driver(options: BrowserOptions,
                  service: Service | None = None) -> webdriver.Chrome:
    """Создать драйвер Chrome с заданными опциями."""
    driver = webdriver.Chrome(options=build_chrome_options(options), service=service)
    driver.implicitly_wait(options.implicit_wait)
    driver.set_page_load_timeout(options.page_load_timeout)
    return driver


class BrowserFactory:
    """Создание и корректное закрытие драйверов Chrome.

    Закрытый браузер убирается из списка, чтобы не обращаться к нему
    повторно: повторный ``quit()`` к уже закрытой сессии заставляет
    Selenium повторять HTTP-запросы и заметно замедляет прогон.
    """

    def __init__(self, options: BrowserOptions):
        self.options = options
        self._browsers: list[webdriver.Chrome] = []

    def create(self) -> webdriver.Chrome:
        """Создать браузер с опциями по умолчанию."""
        return self.create_with(self.options)

    def create_with(self, options: BrowserOptions) -> webdriver.Chrome:
        """Создать браузер с указанными опциями."""
        browser = create_driver(options)
        self._browsers.append(browser)
        return browser

    def release(self, browser: webdriver.Chrome) -> None:
        """Закрыть браузер и убрать его из списка.

        Если обычное закрытие не удалось (например, страница зависла),
        останавливается служба chromedriver — иначе процесс браузера
        остаётся висеть в системе.
        """
        if browser in self._browsers:
            self._browsers.remove(browser)
        try:
            browser.quit()
        except Exception:
            try:
                browser.service.stop()
            except Exception:
                pass

    def close_all(self) -> None:
        """Закрыть все оставшиеся браузеры."""
        for browser in list(self._browsers):
            self.release(browser)
