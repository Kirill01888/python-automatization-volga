"""Page Object страницы https://practice-automation.com/popups/

Кнопки вызывают браузерные диалоги (работа через driver.switch_to.alert):

    #alert   → alert   «Hi there, pal!»
    #confirm → confirm «OK or Cancel, which will it be?»
               OK → #confirmResult «OK it is!», Cancel → «Cancel it is!»
    #prompt  → prompt  «Hi there, what's your name?»
               имя → #promptResult «Nice to meet you, <имя>!»
               пусто / Cancel → «Fine, be that way...»

Подсказка: клик по .tooltip_1 переключает видимость #myTooltip «Cool text».
"""
import allure
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage

ALERT_TEXT = "Hi there, pal!"
CONFIRM_TEXT = "OK or Cancel, which will it be?"
PROMPT_TEXT = "Hi there, what's your name?"
CONFIRM_OK = "OK it is!"
CONFIRM_CANCEL = "Cancel it is!"
PROMPT_EMPTY = "Fine, be that way..."
TOOLTIP_TEXT = "Cool text"


def prompt_greeting(name: str) -> str:
    return f"Nice to meet you, {name}!"


class PopupsPage(BasePage):
    PATH = "/popups/"

    HEADING = (By.XPATH, "//h1[normalize-space()='Popups']")
    ALERT_BTN = (By.ID, "alert")
    CONFIRM_BTN = (By.ID, "confirm")
    PROMPT_BTN = (By.ID, "prompt")
    CONFIRM_RESULT = (By.ID, "confirmResult")
    PROMPT_RESULT = (By.ID, "promptResult")
    TOOLTIP_TRIGGER = (By.CSS_SELECTOR, ".tooltip_1")
    TOOLTIP = (By.ID, "myTooltip")

    # --- чтение ---------------------------------------------------------------
    def is_heading_visible(self) -> bool:
        return self.is_visible(self.HEADING)

    def get_button_texts(self) -> dict[str, str]:
        return {name: self.get_text(loc) for name, loc in
                (("alert", self.ALERT_BTN), ("confirm", self.CONFIRM_BTN), ("prompt", self.PROMPT_BTN))}

    def _text_content(self, locator) -> str:
        return (self.driver.find_element(*locator).get_attribute("textContent") or "").strip()

    def get_confirm_result(self) -> str:
        return self._text_content(self.CONFIRM_RESULT)

    def get_prompt_result(self) -> str:
        return self._text_content(self.PROMPT_RESULT)

    def get_tooltip_trigger_text(self) -> str:
        return self.driver.find_element(*self.TOOLTIP_TRIGGER).text.replace(TOOLTIP_TEXT, "").strip()

    def _tooltip_shown_class(self) -> bool:
        """showTooltip() переключает класс show у #myTooltip — это и есть состояние подсказки."""
        classes = self.driver.find_element(*self.TOOLTIP).get_attribute("class") or ""
        return "show" in classes.split()

    def is_tooltip_visible(self, timeout: float = 5) -> bool:
        """Подсказка показана: у неё есть класс show и браузер считает её видимой.
        Видимость ждём с запасом — появление идёт с анимацией fadeIn (1 с),
        под нагрузкой (-n, несколько браузеров) она запаздывает."""
        try:
            WebDriverWait(self.driver, timeout, poll_frequency=0.5).until(
                lambda _: self._tooltip_shown_class()
                and self.driver.find_element(*self.TOOLTIP).is_displayed())
            return True
        except TimeoutException:
            return False

    def wait_tooltip_hidden(self, timeout: float = 5) -> bool:
        """Подсказка скрыта: класса show нет и элемент невидим (visibility: hidden)."""
        try:
            WebDriverWait(self.driver, timeout, poll_frequency=0.5).until(
                lambda _: not self._tooltip_shown_class()
                and not self.driver.find_element(*self.TOOLTIP).is_displayed())
            return True
        except TimeoutException:
            return False

    def get_tooltip_text(self) -> str:
        return self._text_content(self.TOOLTIP)

    # --- действия --------------------------------------------------------------
    @allure.step("Нажать «Alert Popup»")
    def click_alert(self):
        self.click(self.ALERT_BTN)
        return self

    @allure.step("Нажать «Confirm Popup»")
    def click_confirm(self):
        self.click(self.CONFIRM_BTN)
        return self

    @allure.step("Нажать «Prompt Popup»")
    def click_prompt(self):
        self.click(self.PROMPT_BTN)
        return self

    @allure.step("Кликнуть по «<< click me to see a tooltip >>»")
    def click_tooltip(self):
        self.click(self.TOOLTIP_TRIGGER)
        return self
