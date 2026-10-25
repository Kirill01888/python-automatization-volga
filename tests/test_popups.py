"""Тесты страницы Popups: https://practice-automation.com/popups/

Alert, confirm и prompt — встроенные диалоги браузера: Selenium работает
с ними через driver.switch_to.alert (методы BasePage: accept/dismiss/type).
"""

import allure
import pytest
from selenium.common.exceptions import UnexpectedAlertPresentException

from pages.popups_page import (
    ALERT_TEXT,
    CONFIRM_CANCEL,
    CONFIRM_OK,
    CONFIRM_TEXT,
    PROMPT_EMPTY,
    PROMPT_TEXT,
    TOOLTIP_TEXT,
    PopupsPage,
    prompt_greeting,
)

pytestmark = [pytest.mark.popups]


@pytest.fixture
def page(driver) -> PopupsPage:
    return PopupsPage(driver).open()


def check_no_dialog(page: PopupsPage) -> None:
    with allure.step("Диалог закрыт"):
        assert not page.is_alert_present(timeout=1), "Диалог остался открытым"


# ==========================================================================
# Страница и alert
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Всплывающие окна (Popups)")
@allure.story("Alert")
class TestAlert:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Страница открывается: 3 кнопки диалогов, результаты пустые, подсказка скрыта")
    def test_page_initial_state(self, page):
        """Цель: убедиться, что страница загружается в исходном состоянии — все
        элементы для вызова диалогов на месте и ни один результат ещё не показан.

        Ожидаемый результат: есть заголовок «Popups» и кнопки «Alert Popup»,
        «Confirm Popup», «Prompt Popup»; результаты confirm и prompt пустые;
        текст «<< click me to see a tooltip >>» виден, сама подсказка скрыта.
        """
        with allure.step("Заголовок и кнопки «Alert Popup», «Confirm Popup», «Prompt Popup»"):
            assert page.is_heading_visible(), "Заголовок 'Popups' не отображается"
            assert page.get_button_texts() == {
                "alert": "Alert Popup",
                "confirm": "Confirm Popup",
                "prompt": "Prompt Popup",
            }
        with allure.step("Результаты confirm и prompt пустые"):
            assert page.get_confirm_result() == ""
            assert page.get_prompt_result() == ""
        with allure.step("Текст подсказки виден, сама подсказка скрыта"):
            assert page.get_tooltip_trigger_text() == "<< click me to see a tooltip >>"
            assert not page.is_tooltip_visible(timeout=0.5)

    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(f"Alert: текст «{ALERT_TEXT}», закрывается кнопкой OK")
    def test_alert(self, page):
        """Цель: проверить, что кнопка «Alert Popup» вызывает встроенный alert
        браузера с правильным текстом и что его можно закрыть.

        Ожидаемый результат: появляется alert «Hi there, pal!»; после нажатия OK
        диалог закрыт и страница снова доступна.
        """
        page.click_alert()
        with allure.step(f"Текст alert — «{ALERT_TEXT}»"):
            assert page.get_alert_text() == ALERT_TEXT
        page.accept_alert()
        check_no_dialog(page)


# ==========================================================================
# Confirm
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Всплывающие окна (Popups)")
@allure.story("Confirm")
class TestConfirm:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(f"Confirm → OK: результат «{CONFIRM_OK}»")
    def test_confirm_ok(self, page):
        """Цель: проверить подтверждение в confirm-диалоге и то, что страница
        отображает выбор пользователя.

        Ожидаемый результат: появляется confirm «OK or Cancel, which will it be?»;
        после OK диалог закрыт, под кнопкой выводится «OK it is!».
        """
        page.click_confirm()
        with allure.step(f"Текст confirm — «{CONFIRM_TEXT}»"):
            assert page.get_alert_text() == CONFIRM_TEXT
        page.accept_alert()
        check_no_dialog(page)
        with allure.step(f"Результат «{CONFIRM_OK}»"):
            assert page.get_confirm_result() == CONFIRM_OK

    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(f"Confirm → Cancel: результат «{CONFIRM_CANCEL}»")
    def test_confirm_cancel(self, page):
        """Цель: проверить отказ в confirm-диалоге — страница должна различать
        OK и Cancel.

        Ожидаемый результат: после Cancel диалог закрыт, под кнопкой выводится
        «Cancel it is!».
        """
        page.click_confirm()
        page.dismiss_alert()
        check_no_dialog(page)
        with allure.step(f"Результат «{CONFIRM_CANCEL}»"):
            assert page.get_confirm_result() == CONFIRM_CANCEL

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Confirm повторно: результат меняется с «OK it is!» на «Cancel it is!» и обратно")
    def test_confirm_result_switches(self, page):
        """Цель: убедиться, что результат confirm каждый раз отражает последний
        выбор пользователя, а не первый.

        Ожидаемый результат: при последовательных ответах OK → Cancel → OK
        результат меняется на «OK it is!» → «Cancel it is!» → «OK it is!».
        """
        for action, expected in (
            ("ok", CONFIRM_OK),
            ("cancel", CONFIRM_CANCEL),
            ("ok", CONFIRM_OK),
        ):
            page.click_confirm()
            page.accept_alert() if action == "ok" else page.dismiss_alert()
            with allure.step(f"Результат «{expected}»"):
                assert page.get_confirm_result() == expected


# ==========================================================================
# Prompt
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Всплывающие окна (Popups)")
@allure.story("Prompt")
class TestPrompt:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Prompt с именем «Kirill» → OK: «Nice to meet you, Kirill!»")
    def test_prompt_with_name(self, page):
        """Цель: проверить ввод текста в prompt-диалог и использование введённого
        значения на странице.

        Ожидаемый результат: появляется prompt «Hi there, what's your name?»;
        после ввода «Kirill» и OK выводится «Nice to meet you, Kirill!».
        """
        page.click_prompt()
        with allure.step(f"Текст prompt — «{PROMPT_TEXT}»"):
            assert page.get_alert_text() == PROMPT_TEXT
        page.type_into_prompt("Kirill")
        page.accept_alert()
        check_no_dialog(page)
        with allure.step("Результат «Nice to meet you, Kirill!»"):
            assert page.get_prompt_result() == prompt_greeting("Kirill")

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Prompt принимает кириллицу, пробелы, дефис и апостроф в имени")
    def test_prompt_special_names(self, page):
        """Цель: убедиться, что prompt корректно принимает имена не только из
        латиницы — с кириллицей, пробелом, апострофом и дефисом.

        Ожидаемый результат: для «Кирилл», «Анна Мария», «O'Neil-Smith» выводится
        «Nice to meet you, <имя>!» с именем без искажений.
        """
        for name in ("Кирилл", "Анна Мария", "O'Neil-Smith"):
            with allure.step(f"Имя «{name}»"):
                page.click_prompt()
                page.type_into_prompt(name)
                page.accept_alert()
                assert page.get_prompt_result() == prompt_greeting(name)


# ==========================================================================
# Подсказка
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Всплывающие окна (Popups)")
@allure.story("Подсказка (tooltip)")
class TestTooltip:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title(f"Клик по «click me to see a tooltip» показывает подсказку «{TOOLTIP_TEXT}»")
    def test_tooltip_shows(self, page):
        """Цель: проверить, что подсказка показывается по клику на текст-триггер.

        Ожидаемый результат: после клика по «<< click me to see a tooltip >>»
        появляется подсказка с текстом «Cool text».
        """
        page.click_tooltip()
        with allure.step(f"Подсказка «{TOOLTIP_TEXT}» видна"):
            assert page.is_tooltip_visible(), "Подсказка не появилась"
            assert page.get_tooltip_text() == TOOLTIP_TEXT

    @pytest.mark.positive
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Повторный клик скрывает подсказку, третий — снова показывает")
    def test_tooltip_toggles(self, page):
        """Цель: убедиться, что клик работает как переключатель — подсказку можно
        скрыть и показать снова.

        Ожидаемый результат: первый клик показывает подсказку, второй скрывает,
        третий снова показывает.
        """
        page.click_tooltip()
        assert page.is_tooltip_visible(), "Подсказка не появилась"
        page.click_tooltip()
        with allure.step("После второго клика подсказка скрыта"):
            assert page.wait_tooltip_hidden(), "Подсказка не скрылась"
        page.click_tooltip()
        with allure.step("После третьего клика подсказка снова видна"):
            assert page.is_tooltip_visible()


# ==========================================================================
# Негативные
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Всплывающие окна (Popups)")
@allure.story("Негативные сценарии")
class TestPopupsNegative:
    @pytest.mark.negative
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title(f"Prompt без ввода → OK: «{PROMPT_EMPTY}»")
    def test_prompt_empty(self, page):
        """Цель: проверить реакцию страницы на prompt, подтверждённый без ввода
        имени.

        Ожидаемый результат: пустой ввод не считается именем — выводится
        «Fine, be that way...», а не приветствие.
        """
        page.click_prompt()
        page.accept_alert()
        check_no_dialog(page)
        with allure.step(f"Результат «{PROMPT_EMPTY}»"):
            assert page.get_prompt_result() == PROMPT_EMPTY

    @pytest.mark.negative
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title(f"Prompt с введённым именем → Cancel: имя не принимается, «{PROMPT_EMPTY}»")
    def test_prompt_cancel(self, page):
        """Цель: убедиться, что при отмене prompt введённый текст не используется,
        даже если пользователь успел его набрать.

        Ожидаемый результат: после ввода «Kirill» и Cancel выводится
        «Fine, be that way...», имя на странице не появляется.
        """
        page.click_prompt()
        page.type_into_prompt("Kirill")
        page.dismiss_alert()
        check_no_dialog(page)
        with allure.step(f"Результат «{PROMPT_EMPTY}», введённое имя не показано"):
            assert page.get_prompt_result() == PROMPT_EMPTY

    @pytest.mark.negative
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Пока alert открыт, страница заблокирована: клик по другой кнопке невозможен")
    def test_page_blocked_while_alert_open(self, page):
        """Цель: проверить, что открытый alert блокирует страницу — пока он не
        закрыт, другие элементы недоступны.

        Ожидаемый результат: попытка нажать «Confirm Popup» при открытом alert
        завершается UnexpectedAlertPresentException; confirm не вызывается,
        его результат остаётся пустым.
        """
        page.click_alert()
        assert page.is_alert_present(), "Alert не появился"
        with allure.step(
            "Попытка нажать «Confirm Popup» при открытом alert → UnexpectedAlertPresentException"
        ), pytest.raises(UnexpectedAlertPresentException):
            page.driver.find_element(*page.CONFIRM_BTN).click()
        with allure.step("Confirm не сработал: результат пустой"):
            if page.is_alert_present(timeout=0.5):
                page.accept_alert()
            assert page.get_confirm_result() == ""
