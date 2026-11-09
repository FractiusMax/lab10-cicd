# -*- coding: utf-8 -*-
"""Page Object страницы формы заявки.

Паттерн Page Object Model (использован в лабораторных работах № 6 и № 7):
тесты работают с методами объекта страницы, а не с «сырыми» селекторами.
"""
from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import locators


class FormPage:
    """Страница с формой заявки на консультацию."""

    def __init__(self, driver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Открытие страницы
    # ------------------------------------------------------------------
    def open(self) -> "FormPage":
        """Открыть страницу с формой."""
        self.driver.get(f"{self.base_url}/index.html")
        self.wait_visible(locators.FORM)
        return self

    # ------------------------------------------------------------------
    # Вспомогательные методы
    # ------------------------------------------------------------------
    def wait_visible(self, selector: str, timeout: int | None = None):
        """Дождаться появления элемента на странице."""
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
        )

    def is_visible(self, selector: str) -> bool:
        """Виден ли элемент на странице."""
        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
        return bool(elements) and elements[0].is_displayed()

    def text_of(self, selector: str) -> str:
        """Текст элемента (пустая строка, если элемента нет)."""
        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
        return elements[0].text.strip() if elements else ""

    # ------------------------------------------------------------------
    # Действия с формой
    # ------------------------------------------------------------------
    def fill_name(self, value: str) -> "FormPage":
        self.driver.find_element(By.CSS_SELECTOR, locators.NAME_INPUT).send_keys(value)
        return self

    def fill_email(self, value: str) -> "FormPage":
        self.driver.find_element(By.CSS_SELECTOR, locators.EMAIL_INPUT).send_keys(value)
        return self

    def fill_message(self, value: str) -> "FormPage":
        self.driver.find_element(By.CSS_SELECTOR, locators.MESSAGE_TEXTAREA).send_keys(value)
        return self

    def select_topic(self, value: str) -> "FormPage":
        from selenium.webdriver.support.ui import Select

        Select(self.driver.find_element(By.CSS_SELECTOR, locators.TOPIC_SELECT)).select_by_value(value)
        return self

    def agree(self) -> "FormPage":
        checkbox = self.driver.find_element(By.CSS_SELECTOR, locators.AGREE_CHECKBOX)
        if not checkbox.is_selected():
            checkbox.click()
        return self

    def submit(self) -> "FormPage":
        self.driver.find_element(By.CSS_SELECTOR, locators.SUBMIT_BUTTON).click()
        return self

    def fill_valid_form(self, name: str = "Иванов Иван",
                        email: str = "ivanov@example.com",
                        message: str = "Прошу связаться со мной по вопросу консультации.",
                        topic: str = "consult") -> "FormPage":
        """Заполнить форму корректными данными (флажок согласия включён)."""
        self.fill_name(name)
        self.fill_email(email)
        self.select_topic(topic)
        self.fill_message(message)
        self.agree()
        return self

    # ------------------------------------------------------------------
    # Проверки
    # ------------------------------------------------------------------
    def error_message(self, field: str) -> str:
        """Текст ошибки поля ('' — ошибки нет)."""
        selector = getattr(locators, f"ERROR_{field.upper()}")
        if not self.is_visible(selector):
            return ""
        return self.text_of(selector)

    def success_is_visible(self) -> bool:
        return self.is_visible(locators.SUCCESS_BLOCK)
