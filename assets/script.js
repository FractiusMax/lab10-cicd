/**
 * Клиентская валидация и отправка формы заявки.
 *
 * Форма намеренно сделана без серверной части: задача лабораторной работы —
 * проверить, что CI/CD-конвейер ловит регрессии в интерфейсе. Валидация
 * выполняется в браузере, а результат отправки показывается блоком «Заявка
 * отправлена».
 */
(function () {
  'use strict';

  var EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  var form = document.getElementById('request-form');
  var success = document.getElementById('success');

  /**
   * Показывает или скрывает сообщение об ошибке поля.
   * @param {string} fieldId идентификатор поля
   * @param {string} message текст ошибки; пустая строка — ошибки нет
   */
  function setError(fieldId, message) {
    var node = document.getElementById('error-' + fieldId);
    if (!node) return;
    node.textContent = message;
    node.hidden = !message;
  }

  /**
   * Проверяет одно поле и возвращает текст ошибки (пустая строка — всё в порядке).
   * @param {string} fieldId идентификатор поля
   * @returns {string}
   */
  function validateField(fieldId) {
    var element = document.getElementById(fieldId);
    if (!element) return '';

    var value = (element.value || '').trim();

    if (fieldId === 'name') {
      if (!value) return 'Укажите имя';
      if (value.length < 2) return 'Имя должно содержать не менее 2 символов';
      return '';
    }

    if (fieldId === 'email') {
      if (!value) return 'Укажите электронную почту';
      if (!EMAIL_PATTERN.test(value)) return 'Некорректный адрес электронной почты';
      return '';
    }

    if (fieldId === 'message') {
      if (!value) return 'Укажите текст сообщения';
      if (value.length < 10) return 'Сообщение должно содержать не менее 10 символов';
      return '';
    }

    if (fieldId === 'agree') {
      if (!element.checked) return 'Необходимо согласие на обработку персональных данных';
      return '';
    }

    return '';
  }

  var FIELDS = ['name', 'email', 'message', 'agree'];

  FIELDS.forEach(function (fieldId) {
    var element = document.getElementById(fieldId);
    if (!element) return;

    var eventName = element.type === 'checkbox' ? 'change' : 'blur';
    element.addEventListener(eventName, function () {
      setError(fieldId, validateField(fieldId));
    });

    // Ошибка исчезает, как только поле исправлено
    element.addEventListener('input', function () {
      var node = document.getElementById('error-' + fieldId);
      if (node && !node.hidden && !validateField(fieldId)) {
        setError(fieldId, '');
      }
    });
  });

  form.addEventListener('submit', function (event) {
    event.preventDefault();

    var firstInvalid = null;

    FIELDS.forEach(function (fieldId) {
      var message = validateField(fieldId);
      setError(fieldId, message);
      if (message && !firstInvalid) firstInvalid = fieldId;
    });

    if (firstInvalid) {
      var invalid = document.getElementById(firstInvalid);
      if (invalid && typeof invalid.focus === 'function') invalid.focus();
      return;
    }

    document.getElementById('success-name').textContent =
      document.getElementById('name').value.trim();
    document.getElementById('success-email').textContent =
      document.getElementById('email').value.trim();

    form.hidden = true;
    success.hidden = false;
  });
})();
