"""Page Object страницы https://practice-automation.com/form-fields/

Обычная HTML-форма #feedbackForm:
    Name           #name-input (required, подпись «* Required»)
    Password       input[type=password] (без id)
    Напитки        чекбоксы #drink1…#drink5: Water, Milk, Coffee, Wine, Ctrl-Alt-Delight
    Цвет           радиокнопки #color1…#color5: Red, Blue, Yellow, Green, #FFC0CB
    Automation?    select #automation: '' (по умолчанию), Yes, No, Undecided
    Automation tools  список <ul><li>: Selenium, Playwright, Cypress, Appium, Katalon Studio
    Email          #email (type="text", title «No fake emails!», формат не проверяется)
    Message        textarea #message
    Submit         #submit-btn

submitForm(): alert «Message received!», затем очищает все поля; отправка
на сервер отменяется. Пустое Name блокирует встроенная проверка браузера (required).
"""
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage

DRINKS = ["Water", "Milk", "Coffee", "Wine", "Ctrl-Alt-Delight"]
COLORS = ["Red", "Blue", "Yellow", "Green", "#FFC0CB"]
AUTOMATION_OPTIONS = {"": "default", "Yes": "yes", "No": "no", "Undecided": "undecided"}
SUCCESS_ALERT = "Message received!"


class FormFieldsPage(BasePage):
    PATH = "/form-fields/"

    HEADING = (By.XPATH, "//h1[normalize-space()='Form Fields']")
    FORM = (By.ID, "feedbackForm")
    NAME = (By.ID, "name-input")
    REQUIRED_NOTE = (By.CSS_SELECTOR, "#feedbackForm .red_txt")
    PASSWORD = (By.CSS_SELECTOR, "#feedbackForm input[type='password']")
    AUTOMATION = (By.ID, "automation")
    TOOLS = (By.XPATH, "//label[normalize-space()='Automation tools']/following-sibling::ul[1]/li")
    EMAIL = (By.ID, "email")
    MESSAGE = (By.ID, "message")
    SUBMIT = (By.ID, "submit-btn")

    @staticmethod
    def drink(name: str):
        return By.ID, f"drink{DRINKS.index(name) + 1}"

    @staticmethod
    def color(name: str):
        return By.ID, f"color{COLORS.index(name) + 1}"

    # ========================================================================
    # Чтение состояния
    # ========================================================================
    def is_heading_visible(self) -> bool:
        return self.is_visible(self.HEADING)

    def get_required_note(self) -> str:
        return self.get_text(self.REQUIRED_NOTE)

    def _value(self, locator) -> str:
        return self.driver.find_element(*locator).get_attribute("value") or ""

    def get_name(self) -> str:
        return self._value(self.NAME)

    def get_password(self) -> str:
        return self._value(self.PASSWORD)

    def get_password_type(self) -> str:
        return self.driver.find_element(*self.PASSWORD).get_attribute("type")

    def get_email(self) -> str:
        return self._value(self.EMAIL)

    def get_message(self) -> str:
        return self._value(self.MESSAGE)

    def get_message_placeholder(self) -> str:
        return self.driver.find_element(*self.MESSAGE).get_attribute("placeholder") or ""

    def get_drink_labels(self) -> list[str]:
        return [self.driver.find_element(By.CSS_SELECTOR, f"label[for='drink{i}']").text.strip()
                for i in range(1, len(DRINKS) + 1)]

    def get_color_labels(self) -> list[str]:
        return [self.driver.find_element(By.CSS_SELECTOR, f"label[for='color{i}']").text.strip()
                for i in range(1, len(COLORS) + 1)]

    def get_checked_drinks(self) -> list[str]:
        return [d for d in DRINKS if self.driver.find_element(*self.drink(d)).is_selected()]

    def get_checked_colors(self) -> list[str]:
        return [c for c in COLORS if self.driver.find_element(*self.color(c)).is_selected()]

    def get_automation_value(self) -> str:
        """value выбранного варианта; '' если ничего не выбрано (после сброса формы)."""
        return self._value(self.AUTOMATION)

    def get_automation_options(self) -> list[str]:
        return [o.text.strip() for o in Select(self.find(self.AUTOMATION)).options]

    def get_automation_tools(self) -> list[str]:
        """Пункты раздела Automation tools — средствами Selenium (find_elements)."""
        with allure.step("Получить список элементов раздела «Automation tools»"):
            tools = [li.text.strip() for li in self.find_all(self.TOOLS)]
            allure.attach("\n".join(tools), name="Automation tools",
                          attachment_type=allure.attachment_type.TEXT)
        return tools

    def get_name_validity(self) -> tuple[bool, str]:
        """(valid, validationMessage) встроенной проверки браузера для поля Name."""
        valid, message = self.driver.execute_script(
            "const el = arguments[0]; return [el.validity.valid, el.validationMessage];",
            self.driver.find_element(*self.NAME),
        )
        return bool(valid), message or ""

    def get_form_state(self) -> dict:
        """Снимок всех значений формы — для проверки сброса."""
        return {
            "name": self.get_name(),
            "password": self.get_password(),
            "drinks": self.get_checked_drinks(),
            "colors": self.get_checked_colors(),
            "automation": self.get_automation_value(),
            "email": self.get_email(),
            "message": self.get_message(),
        }

    # ========================================================================
    # Заполнение
    # ========================================================================
    def fill_name(self, name: str):
        with allure.step(f"Ввести Name: «{name}»"):
            self.type(self.NAME, name)
        return self

    def fill_password(self, password: str):
        with allure.step("Ввести Password"):
            self.type(self.PASSWORD, password)
        return self

    def toggle_drink(self, name: str):
        with allure.step(f"Кликнуть чекбокс «{name}»"):
            self.click(self.drink(name))
        return self

    def choose_color(self, name: str):
        with allure.step(f"Выбрать цвет «{name}»"):
            self.click(self.color(name))
        return self

    def choose_automation(self, text: str):
        with allure.step(f"Выбрать в «Do you like automation?»: «{text}»"):
            Select(self.find(self.AUTOMATION)).select_by_visible_text(text)
        return self

    def fill_email(self, email: str):
        with allure.step(f"Ввести Email: «{email}»"):
            self.type(self.EMAIL, email)
        return self

    def fill_message(self, message: str):
        with allure.step(f"Ввести Message: «{message}»"):
            self.type(self.MESSAGE, message)
        return self

    def fill_message_with_tools(self) -> str:
        """Пункт 5 задания: Message = список Automation tools через запятую."""
        tools = self.get_automation_tools()
        text = ", ".join(tools)
        with allure.step(f"Заполнить Message списком через запятую: «{text}»"):
            self.type(self.MESSAGE, text)
        return text

    @allure.step("Нажать Submit")
    def submit(self):
        self.click(self.SUBMIT)
        return self
