"""Базовый Page Object: общие действия и ожидания для всех страниц."""
import allure
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
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
        return WebDriverWait(self.driver, timeout or self.timeout).until(_visible)

    def is_visible(self, locator: Locator, timeout: float = 3) -> bool:
        try:
            self.find_visible(locator, timeout)
            return True
        except TimeoutException:
            return False

    def wait_invisible(self, locator: Locator, timeout: float | None = None) -> bool:
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
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

    def accept_alert(self) -> str:
        alert = self.wait.until(EC.alert_is_present())
        text = alert.text
        alert.accept()
        return text
