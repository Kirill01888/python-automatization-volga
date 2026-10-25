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
EMPTY_FORM = {"name": "", "password": "", "drinks": [], "colors": [],
              "automation": "", "email": "", "message": ""}


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
    @allure.title("Пункт 5 задания: Message = список Automation tools через запятую, форма отправляется")
    def test_message_from_automation_tools(self, page):
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
        page.fill_name(NAME).fill_password(PASSWORD)
        page.toggle_drink("Coffee").toggle_drink("Ctrl-Alt-Delight")
        page.choose_color("Blue").choose_automation("Yes")
        page.fill_email(EMAIL).fill_message(MESSAGE)
        with allure.step("Перед отправкой все значения на месте"):
            assert page.get_form_state() == {
                "name": NAME, "password": PASSWORD, "drinks": ["Coffee", "Ctrl-Alt-Delight"],
                "colors": ["Blue"], "automation": "yes", "email": EMAIL, "message": MESSAGE}
        page.submit()
        check_submitted(page)

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("После отправки все поля формы очищаются")
    def test_form_reset_after_submit(self, page):
        page.fill_name(NAME).fill_password(PASSWORD).toggle_drink("Milk")
        page.choose_color("Green").choose_automation("Undecided")
        page.fill_email(EMAIL).fill_message(MESSAGE)
        page.submit()
        check_submitted(page)
        with allure.step("Name, Password, Email, Message пустые; чекбоксы, радиокнопки и список сброшены"):
            assert page.get_form_state() == EMPTY_FORM

    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Форма только с обязательным полем Name отправляется")
    def test_submit_only_required(self, page):
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
        for color in COLORS:
            page.choose_color(color)
            with allure.step(f"Выбран только «{color}»"):
                assert page.get_checked_colors() == [color]

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Выпадающий список «Do you like automation?»: по умолчанию пусто, выбираются Yes, No, Undecided")
    def test_automation_select(self, page):
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
    @allure.title("Без Name форма не отправляется: браузер помечает поле невалидным, данные сохраняются")
    def test_submit_without_name(self, page):
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
    @pytest.mark.xfail(reason="Известный дефект: атрибут required считает пробелы заполнением, "
                              "Name из одних пробелов принимается", strict=False)
    @allure.title("Name из одних пробелов не должно считаться заполненным")
    def test_submit_whitespace_name(self, page):
        page.fill_name("     ").submit()
        check_not_submitted(page)

    @pytest.mark.negative
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.xfail(reason="Известный дефект: Email — обычное текстовое поле без проверки формата, "
                              "некорректный адрес принимается вопреки подсказке «No fake emails!»", strict=False)
    @pytest.mark.parametrize("bad_email", ["abc", "user@"], ids=["no_at", "no_domain"])
    @allure.title("Некорректный Email «{bad_email}» не должен приниматься")
    def test_submit_invalid_email(self, page, bad_email):
        page.fill_name(NAME).fill_email(bad_email).submit()
        check_not_submitted(page)
