"""Page Object страницы https://practice-automation.com/modals/

Два модальных окна плагина Popup Maker:

    Кнопка #simpleModal  → затемнение #pum-1318 → окно #popmake-1318 «Simple Modal»
    Кнопка #formModal    → затемнение #pum-674  → окно #popmake-674  «Modal Containing A Form»

Внутри окна: заголовок #pum_popup_title_<id>, содержимое .pum-content,
кнопка закрытия .pum-close («×»).
Настройки закрытия (data-popmake): Simple — только «×»; Form — «×» и Esc.
Клик по затемнению не закрывает ни одно окно.

В Form Modal — форма Jetpack: Name (обязательное), Email, Message, Submit.
"""

from typing import Literal

import allure
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage, Locator

ModalKind = Literal["simple", "form"]

# id кнопки-триггера и id попапа в Popup Maker
_MODALS: dict[str, tuple[str, str, str]] = {
    "simple": ("simpleModal", "1318", "Simple Modal"),
    "form": ("formModal", "674", "Form Modal"),
}

FIELD_WRAP = {
    "name": "g1065-name",
    "email": "g1065-email",
    "message": "g1065-message",
}


class ModalsPage(BasePage):
    PATH = "/modals/"

    HEADING = (By.XPATH, "//h1[normalize-space()='Modals']")

    # --- форма внутри Form Modal -----------------------------------------
    NAME = (By.ID, "g1065-name")
    NAME_LABEL = (By.CSS_SELECTOR, "#popmake-674 label[for='g1065-name']")
    EMAIL = (By.ID, "g1065-email")
    MESSAGE = (By.ID, "contact-form-comment-g1065-message")
    SUBMIT = (By.CSS_SELECTOR, "#popmake-674 button[type='submit']")
    SUCCESS = (By.CSS_SELECTOR, "#popmake-674 .contact-form-submission.submission-success")
    FORM_ERROR = (By.CSS_SELECTOR, "#popmake-674 .contact-form__error.show-errors")

    # ========================================================================
    # Локаторы окон
    # ========================================================================
    @staticmethod
    def trigger(kind: ModalKind) -> Locator:
        return By.ID, _MODALS[kind][0]

    @staticmethod
    def overlay(kind: ModalKind) -> Locator:
        return By.ID, f"pum-{_MODALS[kind][1]}"

    @staticmethod
    def container(kind: ModalKind) -> Locator:
        return By.ID, f"popmake-{_MODALS[kind][1]}"

    @staticmethod
    def title(kind: ModalKind) -> Locator:
        return By.ID, f"pum_popup_title_{_MODALS[kind][1]}"

    @staticmethod
    def content(kind: ModalKind) -> Locator:
        return By.CSS_SELECTOR, f"#popmake-{_MODALS[kind][1]} .pum-content"

    @staticmethod
    def close_button(kind: ModalKind) -> Locator:
        return By.CSS_SELECTOR, f"#popmake-{_MODALS[kind][1]} .pum-close"

    @staticmethod
    def name_of(kind: ModalKind) -> str:
        return _MODALS[kind][2]

    # ========================================================================
    # Страница
    # ========================================================================
    def is_heading_visible(self) -> bool:
        return self.is_visible(self.HEADING)

    def get_trigger_text(self, kind: ModalKind) -> str:
        return self.get_text(self.trigger(kind))

    def is_trigger_clickable(self, kind: ModalKind) -> bool:
        try:
            self.wait.until(EC.element_to_be_clickable(self.trigger(kind)))
            return True
        except TimeoutException:
            return False

    # ========================================================================
    # Открытие / закрытие
    # ========================================================================
    def is_modal_open(self, kind: ModalKind, timeout: float = 3) -> bool:
        return self.is_visible(self.container(kind), timeout)

    def is_overlay_visible(self, kind: ModalKind, timeout: float = 3) -> bool:
        return self.is_visible(self.overlay(kind), timeout)

    def wait_modal_closed(self, kind: ModalKind, timeout: float = 5) -> bool:
        """True, если окно и затемнение скрылись за timeout секунд."""
        return self.wait_invisible(self.overlay(kind), timeout)

    def open_modal(self, kind: ModalKind):
        with allure.step(f"Нажать кнопку «{self.name_of(kind)}»"):
            self.click(self.trigger(kind))
            self.find(self.container(kind))
        return self

    def close_by_x(self, kind: ModalKind):
        with allure.step(f"Закрыть окно «{self.name_of(kind)}» кнопкой «×»"):
            self.click(self.close_button(kind))
        return self

    @allure.step("Нажать Esc")
    def press_escape(self):
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        return self

    def click_overlay(self, kind: ModalKind):
        """Клик по затемнению в левом верхнем углу экрана — заведомо вне окна."""
        with allure.step(f"Кликнуть по затемнению вне окна «{self.name_of(kind)}»"):
            overlay = self.find(self.overlay(kind))
            size = overlay.size
            ActionChains(self.driver).move_to_element_with_offset(
                overlay, -size["width"] // 2 + 20, -size["height"] // 2 + 20
            ).click().perform()
        return self

    def get_modal_title(self, kind: ModalKind) -> str:
        return self.get_text(self.title(kind))

    def get_modal_text(self, kind: ModalKind) -> str:
        return self.get_text(self.content(kind))

    def is_close_button_visible(self, kind: ModalKind) -> bool:
        return self.is_visible(self.close_button(kind))

    def get_close_button_label(self, kind: ModalKind) -> str:
        return self.find(self.close_button(kind)).get_attribute("aria-label") or ""

    # ========================================================================
    # Форма в Form Modal
    # ========================================================================
    def get_name_label(self) -> str:
        return self.get_text(self.NAME_LABEL)

    def are_form_fields_visible(self) -> dict[str, bool]:
        return {
            "Name": self.is_visible(self.NAME),
            "Email": self.is_visible(self.EMAIL),
            "Message": self.is_visible(self.MESSAGE),
            "Submit": self.is_visible(self.SUBMIT),
        }

    def fill_form(
        self, name: str | None = None, email: str | None = None, message: str | None = None
    ):
        shown = ", ".join(
            f"{k}=«{v}»"
            for k, v in (("Name", name), ("Email", email), ("Message", message))
            if v is not None
        )
        with allure.step(f"Заполнить форму: {shown or 'ничего'}"):
            for locator, value in ((self.NAME, name), (self.EMAIL, email), (self.MESSAGE, message)):
                if value is not None:
                    self.type(locator, value)
        return self

    @allure.step("Нажать Submit в форме")
    def submit_form(self):
        self.click(self.SUBMIT)
        return self

    def is_success_visible(self, timeout: float = 10) -> bool:
        return self.is_visible(self.SUCCESS, timeout)

    def get_success_text(self) -> str:
        return self.get_text(self.SUCCESS)

    def get_field_error(self, field: str, timeout: float = 5) -> str:
        """Текст ошибки под полем (name / email / message) или '' если ошибки нет."""
        locator = (
            By.CSS_SELECTOR,
            f"[data-jp-field-id='{FIELD_WRAP[field]}'] .contact-form__input-error.has-errors",
        )
        if not self.is_visible(locator, timeout):
            return ""
        return self.find(locator).text.strip()
