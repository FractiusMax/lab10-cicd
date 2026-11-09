# -*- coding: utf-8 -*-
"""Автоматизированные тесты пользовательского интерфейса формы заявки.

Четыре сценария из методички к лабораторной работе № 10:

  У1 — страница формы открывается и содержит все элементы;
  У2 — корректно заполненная форма отправляется, показывается подтверждение;
  У3 — пустая форма не отправляется, выводятся ошибки обязательных полей;
  У4 — некорректный адрес электронной почты отклоняется.
"""
from __future__ import annotations

import pytest

import locators


@pytest.mark.ui
def test_01_form_page_contains_all_elements(form_page, capture):
    """У1: страница формы открывается и содержит все элементы."""
    form_page.open()

    assert form_page.driver.title == locators.PAGE_TITLE, "неверный заголовок страницы"

    # Заголовок формы на месте
    assert form_page.is_visible("h1.page__title")
    assert form_page.text_of("h1.page__title") == "Заявка на консультацию"

    # Все поля формы присутствуют и доступны для ввода
    for selector in (
        locators.NAME_INPUT,
        locators.EMAIL_INPUT,
        locators.TOPIC_SELECT,
        locators.MESSAGE_TEXTAREA,
        locators.AGREE_CHECKBOX,
        locators.SUBMIT_BUTTON,
    ):
        assert form_page.is_visible(selector), f"не найден элемент {selector}"

    # Успешного ответа на странице пока нет
    assert not form_page.success_is_visible()

    capture("ui_01_form_page")


@pytest.mark.ui
def test_02_valid_form_is_submitted_successfully(form_page, capture):
    """У2: корректно заполненная форма отправляется."""
    form_page.open()

    form_page.fill_valid_form(
        name="Иванов Иван",
        email="ivanov@example.com",
        message="Прошу связаться со мной по вопросу консультации.",
        topic="support",
    )
    form_page.submit()

    # Появился блок успешного ответа
    assert form_page.success_is_visible(), "блок «Заявка отправлена» не показан"
    assert form_page.text_of(locators.SUCCESS_TITLE) == "Заявка отправлена"

    # В подтверждении указаны имя и адрес из формы
    assert form_page.text_of(locators.SUCCESS_NAME) == "Иванов Иван"
    assert form_page.text_of(locators.SUCCESS_EMAIL) == "ivanov@example.com"

    # Форма скрыта, ошибок нет
    assert not form_page.is_visible(locators.FORM)
    assert form_page.error_message("name") == ""
    assert form_page.error_message("email") == ""

    capture("ui_02_success")


@pytest.mark.ui
def test_03_empty_form_shows_validation_errors(form_page, capture):
    """У3: пустая форма не отправляется, показываются ошибки полей."""
    form_page.open()

    form_page.submit()

    # Заявка не отправлена — блока успеха нет
    assert not form_page.success_is_visible(), "форма отправилась без данных"

    # Ошибки обязательных полей показаны и информативны
    assert form_page.error_message("name") == "Укажите имя"
    assert form_page.error_message("email") == "Укажите электронную почту"
    assert form_page.error_message("message") == "Укажите текст сообщения"
    assert form_page.error_message("agree") == (
        "Необходимо согласие на обработку персональных данных"
    )

    capture("ui_03_empty_form_errors")


@pytest.mark.ui
def test_04_invalid_email_is_rejected(form_page, capture):
    """У4: некорректный адрес электронной почты отклоняется."""
    form_page.open()

    form_page.fill_name("Петрова Анна")
    form_page.fill_email("не-email")
    form_page.fill_message("Текст сообщения достаточной длины.")
    form_page.agree()
    form_page.submit()

    # Форма не отправлена
    assert not form_page.success_is_visible(), "форма отправилась с некорректным e-mail"

    # Ошибка указана именно для поля email
    assert form_page.error_message("email") == "Некорректный адрес электронной почты"

    # Остальные поля заполнены верно — ошибок по ним нет
    assert form_page.error_message("name") == ""
    assert form_page.error_message("message") == ""
    assert form_page.error_message("agree") == ""

    # После исправления адреса форма отправляется
    form_page.fill_email("petrova@example.com")
    form_page.submit()
    assert form_page.success_is_visible(), "форма не отправилась после исправления e-mail"

    capture("ui_04_invalid_email")
