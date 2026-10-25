"""Page Object страницы https://practice-automation.com/click-events/

Четыре кнопки .custom_btn с животными. Обработчики onclick записывают
звук в заголовок h2#demo:

    Cat → «Meow!»   Dog → «Woof!»   Pig → «Oink!»   Cow → «Moo!»
"""

import allure
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from pages.base_page import BasePage, Locator

ANIMAL_SOUNDS = {
    "Cat": "Meow!",
    "Dog": "Woof!",
    "Pig": "Oink!",
    "Cow": "Moo!",
}


class ClickEventsPage(BasePage):
    PATH = "/click-events/"

    HEADING = (By.XPATH, "//h1[normalize-space()='Click Events']")
    DESCRIPTION = (By.XPATH, "//p[contains(normalize-space(.), 'Click any of the buttons below')]")
    BUTTONS = (By.CSS_SELECTOR, ".entry-content button.custom_btn")
    RESULT = (By.ID, "demo")

    @staticmethod
    def button(animal: str) -> Locator:
        """У кнопок нет id — ищем по тексту."""
        return By.XPATH, f"//button[contains(@class,'custom_btn')][normalize-space()='{animal}']"

    # --- чтение ---------------------------------------------------------------
    def get_button_texts(self) -> list[str]:
        return [b.text.strip() for b in self.find_all(self.BUTTONS)]

    def get_result(self) -> str:
        """Текст результата; '' если он пуст (элемент может быть нулевой высоты)."""
        element = self.driver.find_element(*self.RESULT)
        return (element.get_attribute("textContent") or "").strip()

    def wait_result(self, expected: str) -> bool:
        try:
            self.wait.until(lambda _: self.get_result() == expected)
            return True
        except TimeoutException:
            return False

    def is_heading_visible(self) -> bool:
        return self.is_visible(self.HEADING)

    def is_description_visible(self) -> bool:
        return self.is_visible(self.DESCRIPTION)

    def _button(self, animal: str) -> WebElement:
        return self.scroll_to(self.find(self.button(animal)))

    # --- действия --------------------------------------------------------------
    def click_animal(self, animal: str):
        with allure.step(f"Нажать кнопку «{animal}»"):
            self.click(self.button(animal))
        return self

    def double_click_animal(self, animal: str):
        with allure.step(f"Двойной клик по кнопке «{animal}»"):
            ActionChains(self.driver).double_click(self._button(animal)).perform()
        return self

    def press_key_on_animal(self, animal: str, key: str):
        names = {Keys.ENTER: "Enter", Keys.SPACE: "Space"}
        with allure.step(f"Фокус на кнопке «{animal}» и нажатие {names.get(key, key)}"):
            self._button(animal).send_keys(key)
        return self

    def hover_animal(self, animal: str):
        with allure.step(f"Навести курсор на кнопку «{animal}» без клика"):
            ActionChains(self.driver).move_to_element(self._button(animal)).pause(0.5).perform()
        return self

    def press_and_release_outside(self, animal: str):
        """Зажать кнопку мыши на кнопке и отпустить на заголовке страницы."""
        with allure.step(f"Зажать мышь на «{animal}», увести курсор и отпустить на заголовке"):
            (
                ActionChains(self.driver)
                .click_and_hold(self._button(animal))
                .move_to_element(self.find(self.HEADING))
                .release()
                .perform()
            )
        return self

    def click_non_buttons(self):
        with allure.step("Кликнуть по заголовку и описанию страницы (не по кнопкам)"):
            for locator in (self.HEADING, self.DESCRIPTION):
                self.click(locator)
        return self

    @allure.step("Перезагрузить страницу")
    def reload(self):
        self.driver.refresh()
        self.find(self.HEADING)
        return self
