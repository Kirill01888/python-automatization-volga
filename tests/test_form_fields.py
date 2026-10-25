"""Тесты страницы Form Fields: https://practice-automation.com/form-fields/

Включает пункт 5 задания: поле Message заполняется списком элементов
раздела Automation tools, полученным средствами Selenium, через запятую.
"""

import allure
import pytest

from pages.form_fields_page import COLORS, DRINKS, SUCCESS_ALERT, FormFieldsPage

pytestmark = [pytest.mark.forms]

NAME = "Autotest User"
PASSWORD = "Secret#123"
EMAIL = "autotest.user@example.com"
MESSAGE = "Autotest message"
EXPECTED_TOOLS = ["Selenium", "Playwright", "Cypress", "Appium", "Katalon Studio"]
EMPTY_FORM = {
    "name": "",
    "password": "",
    "drinks": [],
    "colors": [],
    "automation": "",
    "email": "",
    "message": "",
}


@pytest.fixture
def page(driver) -> FormFieldsPage:
    return FormFieldsPage(driver).open()


def check_submitted(page: FormFieldsPage) -> None:
    with allure.step(f"Появился alert «{SUCCESS_ALERT}»"):
        assert page.is_alert_present(timeout=5), "Alert об отправке не появился"
        assert page.accept_alert() == SUCCESS_ALERT


def check_not_submitted(page: FormFieldsPage) -> None:
    with allure.step("Alert об отправке не появился — форма не отправлена"):
        submitted = page.is_alert_present(timeout=2)
        if submitted:
            page.accept_alert()
        assert not submitted, "Форма была отправлена"


# ==========================================================================
# Отправка формы
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Форма (Form Fields)")
@allure.story("Отправка формы")
class TestFormSubmit:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Страница открывается: все поля формы на месте, форма пустая")
    def test_page_initial_state(self, page):
        """Цель: убедиться, что форма загружается полностью и в чистом состоянии —
        все поля и варианты выбора на месте, ничего не заполнено заранее.

        Ожидаемый результат: есть заголовок «Form Fields» и пометка «* Required»
        у Name; подписи напитков (Water … Ctrl-Alt-Delight) и цветов (Red …
        #FFC0CB), варианты списка (пусто, Yes, No, Undecided), подсказка «Enter
        message here» и пять пунктов Automation tools; все поля пустые, ничего
        не выбрано.
        """
        with allure.step("Заголовок и пометка «* Required» у Name"):
            assert page.is_heading_visible(), "Заголовок 'Form Fields' не отображается"
            assert page.get_required_note() == "* Required"
        with allure.step("Подписи напитков, цветов и варианты списка"):
            assert page.get_drink_labels() == DRINKS
            assert page.get_color_labels() == COLORS
            assert page.get_automation_options() == ["", "Yes", "No", "Undecided"]
        with allure.step("Подсказка в Message и список Automation tools"):
            assert page.get_message_placeholder() == "Enter message here"
            assert page.get_automation_tools() == EXPECTED_TOOLS
        with allure.step("Все поля пустые, ничего не выбрано"):
            assert page.get_form_state() == {**EMPTY_FORM, "automation": "default"}

    @pytest.mark.positive
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title(
        "Пункт 5 задания: Message = список Automation tools через запятую, форма отправляется"
    )
    def test_message_from_automation_tools(self, page):
        """Цель: выполнить пункт 5 задания — получить средствами Selenium список
        элементов раздела Automation tools, преобразовать его в текст через
        запятую и заполнить им поле Message.

        Ожидаемый результат: в Message ровно «Selenium, Playwright, Cypress,
        Appium, Katalon Studio» — список со страницы в том же порядке; форма
        с этим значением отправляется — alert «Message received!».
        """
        page.fill_name(NAME)
        text = page.fill_message_with_tools()
        with allure.step("В Message ровно список инструментов со страницы через запятую"):
            assert text == ", ".join(EXPECTED_TOOLS), f"Список со страницы: «{text}»"
            assert page.get_message() == "Selenium, Playwright, Cypress, Appium, Katalon Studio"
        page.submit()
        check_submitted(page)

    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Полностью заполненная форма отправляется: alert «Message received!»")
    def test_submit_full_form(self, page):
        """Цель: проверить основной сценарий — отправку формы со всеми заполненными
        полями всех типов (текст, пароль, чекбоксы, радиокнопка, список).

        Ожидаемый результат: перед отправкой все введённые значения на месте;
        после Submit появляется alert «Message received!».
        """
        page.fill_name(NAME).fill_password(PASSWORD)
        page.toggle_drink("Coffee").toggle_drink("Ctrl-Alt-Delight")
        page.choose_color("Blue").choose_automation("Yes")
        page.fill_email(EMAIL).fill_message(MESSAGE)
        with allure.step("Перед отправкой все значения на месте"):
            assert page.get_form_state() == {
                "name": NAME,
                "password": PASSWORD,
                "drinks": ["Coffee", "Ctrl-Alt-Delight"],
                "colors": ["Blue"],
                "automation": "yes",
                "email": EMAIL,
                "message": MESSAGE,
            }
        page.submit()
        check_submitted(page)

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("После отправки все поля формы очищаются")
    def test_form_reset_after_submit(self, page):
        """Цель: проверить, что после успешной отправки форма очищается и готова
        к новому вводу — так устроен обработчик submitForm().

        Ожидаемый результат: после закрытия alert «Message received!» текстовые
        поля пустые, чекбоксы и радиокнопки сняты, в списке ничего не выбрано.
        """
        page.fill_name(NAME).fill_password(PASSWORD).toggle_drink("Milk")
        page.choose_color("Green").choose_automation("Undecided")
        page.fill_email(EMAIL).fill_message(MESSAGE)
        page.submit()
        check_submitted(page)
        with allure.step(
            "Name, Password, Email, Message пустые; чекбоксы, радиокнопки и список сброшены"
        ):
            assert page.get_form_state() == EMPTY_FORM

    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Форма только с обязательным полем Name отправляется")
    def test_submit_only_required(self, page):
        """Цель: убедиться, что для отправки достаточно единственного
        обязательного поля — Name; остальные поля необязательны.

        Ожидаемый результат: форма с заполненным только Name отправляется —
        alert «Message received!».
        """
        page.fill_name(NAME).submit()
        check_submitted(page)


# ==========================================================================
# Элементы формы
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Форма (Form Fields)")
@allure.story("Элементы формы")
class TestFormControls:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Чекбоксы напитков отмечаются независимо, повторный клик снимает отметку")
    def test_drink_checkboxes(self, page):
        """Цель: проверить работу группы чекбоксов напитков — допускается выбор
        нескольких вариантов и снятие отметки.

        Ожидаемый результат: Water, Coffee и Wine отмечаются одновременно;
        повторный клик по Coffee снимает только его отметку.
        """
        for drink in ("Water", "Coffee", "Wine"):
            page.toggle_drink(drink)
        with allure.step("Отмечены Water, Coffee, Wine"):
            assert page.get_checked_drinks() == ["Water", "Coffee", "Wine"]
        page.toggle_drink("Coffee")
        with allure.step("После повторного клика Coffee снят, остальные отмечены"):
            assert page.get_checked_drinks() == ["Water", "Wine"]

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Радиокнопки цвета: выбрана всегда только одна")
    def test_color_radio_single_choice(self, page):
        """Цель: проверить группу радиокнопок цвета — в отличие от чекбоксов,
        выбран может быть только один вариант.

        Ожидаемый результат: при поочерёдном выборе каждого из пяти цветов
        отмечен всегда только последний выбранный.
        """
        for color in COLORS:
            page.choose_color(color)
            with allure.step(f"Выбран только «{color}»"):
                assert page.get_checked_colors() == [color]

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title(
        "Выпадающий список «Do you like automation?»: по умолчанию пусто, выбираются Yes, No, Undecided"
    )
    def test_automation_select(self, page):
        """Цель: проверить выпадающий список «Do you like automation?» —
        значение по умолчанию и выбор каждого варианта.

        Ожидаемый результат: по умолчанию выбран пустой вариант; Yes, No
        и Undecided выбираются и становятся текущим значением списка.
        """
        with allure.step("По умолчанию выбран пустой вариант"):
            assert page.get_automation_value() == "default"
        for text, value in (("Yes", "yes"), ("No", "no"), ("Undecided", "undecided")):
            page.choose_automation(text)
            with allure.step(f"Выбрано «{text}» (value={value})"):
                assert page.get_automation_value() == value

    @pytest.mark.positive
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Поле Password скрывает ввод (type=password) и принимает значение")
    def test_password_masked(self, page):
        """Цель: убедиться, что поле Password скрывает вводимые символы,
        но сохраняет значение.

        Ожидаемый результат: тип поля — password (символы маскируются),
        введённое значение принято полем.
        """
        page.fill_password(PASSWORD)
        with allure.step("Тип поля — password, значение принято"):
            assert page.get_password_type() == "password"
            assert page.get_password() == PASSWORD


# ==========================================================================
# Негативные
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Форма (Form Fields)")
@allure.story("Негативные сценарии")
class TestFormNegative:
    @pytest.mark.negative
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(
        "Без Name форма не отправляется: браузер помечает поле невалидным, данные сохраняются"
    )
    def test_submit_without_name(self, page):
        """Цель: проверить обязательность поля Name — форма без него не должна
        отправляться, а введённые пользователем данные не должны теряться.

        Ожидаемый результат: alert «Message received!» не появляется; поле Name
        помечено браузером как невалидное, есть сообщение встроенной проверки;
        отмеченный напиток, Email и Message сохранены.
        """
        page.toggle_drink("Water").fill_email(EMAIL).fill_message(MESSAGE)
        page.submit()
        check_not_submitted(page)
        valid, message = page.get_name_validity()
        with allure.step(f"Name невалидно, сообщение браузера: «{message}»"):
            assert not valid, "Пустое Name считается валидным"
            assert message, "Нет сообщения встроенной проверки"
        with allure.step("Введённые данные не сброшены"):
            assert page.get_checked_drinks() == ["Water"]
            assert page.get_email() == EMAIL
            assert page.get_message() == MESSAGE

    @pytest.mark.negative
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.xfail(
        reason="Известный дефект: атрибут required считает пробелы заполнением, "
        "Name из одних пробелов принимается",
        strict=False,
    )
    @allure.title("Name из одних пробелов не должно считаться заполненным")
    def test_submit_whitespace_name(self, page):
        """Цель: проверить, что Name из одних пробелов не считается заполненным —
        частый дефект валидации обязательных полей.

        Ожидаемый результат: форма не должна отправляться. Тест помечен xfail —
        атрибут required считает пробелы значением, и форма отправляется
        (известный дефект).
        """
        page.fill_name("     ").submit()
        check_not_submitted(page)

    @pytest.mark.negative
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.xfail(
        reason="Известный дефект: Email — обычное текстовое поле без проверки формата, "
        "некорректный адрес принимается вопреки подсказке «No fake emails!»",
        strict=False,
    )
    @pytest.mark.parametrize("bad_email", ["abc", "user@"], ids=["no_at", "no_domain"])
    @allure.title("Некорректный Email «{bad_email}» не должен приниматься")
    def test_submit_invalid_email(self, page, bad_email):
        """Цель: проверить, что поле Email не принимает адрес неверного формата —
        на странице у поля подсказка «No fake emails!». Тест параметризован
        адресами без «@» и без домена.

        Ожидаемый результат: форма с некорректным Email не должна отправляться.
        Тест помечен xfail — поле обычное текстовое, формат не проверяется,
        и форма отправляется (известный дефект).
        """
        page.fill_name(NAME).fill_email(bad_email).submit()
        check_not_submitted(page)
