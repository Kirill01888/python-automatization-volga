"""Базовый Page Object: общие действия и ожидания для всех страниц."""
import allure
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import BASE_URL, TIMEOUT

Locator = tuple[str, str]


class BasePage:
    PATH = "/"

    def __init__(self, driver: WebDriver, timeout: int = TIMEOUT):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    @property
    def url(self) -> str:
        return BASE_URL + self.PATH

    def open(self):
        with allure.step(f"Открыть страницу {self.url}"):
            self.driver.get(self.url)
        return self

    # --- поиск и ожидания -------------------------------------------------
    def find(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator: Locator) -> list[WebElement]:
        return self.driver.find_elements(*locator)

    def find_visible(self, locator: Locator, timeout: float | None = None) -> WebElement:
        """Первый ВИДИМЫЙ элемент из всех совпадений (на странице бывают скрытые дубли)."""
        def _visible(drv):
            for el in drv.find_elements(*locator):
                if el.is_displayed():
                    return el
            return False
        return WebDriverWait(self.driver, self.timeout if timeout is None else timeout).until(_visible)

    def is_visible(self, locator: Locator, timeout: float = 3) -> bool:
        try:
            self.find_visible(locator, timeout)
            return True
        except TimeoutException:
            return False

    def wait_invisible(self, locator: Locator, timeout: float | None = None) -> bool:
        try:
            WebDriverWait(self.driver, self.timeout if timeout is None else timeout).until(
                EC.invisibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    # --- действия ---------------------------------------------------------
    def scroll_to(self, element: WebElement) -> WebElement:
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        return element

    def click_element(self, element: WebElement) -> None:
        self.scroll_to(element)
        self.wait.until(EC.element_to_be_clickable(element)).click()

    def click(self, locator: Locator, attempts: int = 3) -> None:
        """Клик по локатору. Если элемент перерисовался между поиском и кликом
        (StaleElementReferenceException) — ищем его заново и повторяем."""
        for attempt in range(1, attempts + 1):
            try:
                self.click_element(self.find(locator))
                return
            except StaleElementReferenceException:
                if attempt == attempts:
                    raise

    def type(self, locator: Locator, text: str, clear: bool = True) -> None:
        element = self.scroll_to(self.find(locator))
        if clear:
            element.clear()
        element.send_keys(text)

    def get_text(self, locator: Locator) -> str:
        return self.find(locator).text.strip()

    # --- браузерные диалоги (alert / confirm / prompt) ---------------------
    def wait_alert(self, timeout: float | None = None) -> Alert:
        return WebDriverWait(self.driver, self.timeout if timeout is None else timeout).until(EC.alert_is_present())

    def is_alert_present(self, timeout: float = 1) -> bool:
        try:
            self.wait_alert(timeout)
            return True
        except TimeoutException:
            return False

    def get_alert_text(self) -> str:
        return self.wait_alert().text

    def accept_alert(self) -> str:
        """Нажать OK в диалоге; возвращает его текст."""
        alert = self.wait_alert()
        text = alert.text
        with allure.step(f"Нажать OK в диалоге «{text}»"):
            alert.accept()
        return text

    def dismiss_alert(self) -> str:
        """Нажать Cancel в диалоге; возвращает его текст."""
        alert = self.wait_alert()
        text = alert.text
        with allure.step(f"Нажать Cancel в диалоге «{text}»"):
            alert.dismiss()
        return text

    def type_into_prompt(self, text: str) -> None:
        with allure.step(f"Ввести в prompt «{text}»"):
            self.wait_alert().send_keys(text)
