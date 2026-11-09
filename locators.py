# -*- coding: utf-8 -*-
"""Локаторы элементов страницы формы заявки.

Локаторы собраны в одном месте, чтобы при изменении разметки правился
только этот файл, а не код тестов.
"""

# --- Поля формы -------------------------------------------------------------
NAME_INPUT = "#name"
EMAIL_INPUT = "#email"
TOPIC_SELECT = "#topic"
MESSAGE_TEXTAREA = "#message"
AGREE_CHECKBOX = "#agree"
SUBMIT_BUTTON = "#submit"
FORM = "#request-form"

# --- Сообщения об ошибках ---------------------------------------------------
ERROR_NAME = "#error-name"
ERROR_EMAIL = "#error-email"
ERROR_TOPIC = "#error-topic"
ERROR_MESSAGE = "#error-message"
ERROR_AGREE = "#error-agree"

# --- Блок успешного ответа --------------------------------------------------
SUCCESS_BLOCK = "#success"
SUCCESS_TITLE = ".success__title"
SUCCESS_NAME = "#success-name"
SUCCESS_EMAIL = "#success-email"

# --- Служебные элементы -----------------------------------------------------
PAGE_TITLE = "Заявка на консультацию — Лабораторная работа № 10"
