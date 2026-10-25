"""Фабрика браузеров.

Все браузеры поднимаются через Selenium Manager (встроен в Selenium 4):
драйвер, а при необходимости и сам браузер (Chrome for Testing / Firefox),
скачиваются автоматически. Ручная настройка не требуется.
"""
from collections.abc import Callable

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

from config import WINDOW_HEIGHT, WINDOW_WIDTH


class BrowserUnavailableError(Exception):
    """Браузер не удалось запустить на этой машине."""


def _chrome(headless: bool) -> WebDriver:
    options = webdriver.ChromeOptions()
    options.page_load_strategy = "eager"
    options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-search-engine-choice-screen")
    if headless:
        options.add_argument("--headless=new")
    return webdriver.Chrome(options=options)


def _edge(headless: bool) -> WebDriver:
    options = webdriver.EdgeOptions()
    options.page_load_strategy = "eager"
    options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
    options.add_argument("--disable-notifications")
    if headless:
        options.add_argument("--headless=new")
    return webdriver.Edge(options=options)


def _firefox(headless: bool) -> WebDriver:
    options = webdriver.FirefoxOptions()
    options.page_load_strategy = "eager"
    options.add_argument(f"--width={WINDOW_WIDTH}")
    options.add_argument(f"--height={WINDOW_HEIGHT}")
    options.set_preference("dom.webnotifications.enabled", False)
    if headless:
        options.add_argument("-headless")
    return webdriver.Firefox(options=options)


BROWSERS: dict[str, Callable[[bool], WebDriver]] = {
    "chrome": _chrome,
    "firefox": _firefox,
    "edge": _edge,
}


def parse_browsers(value: str) -> list[str]:
    """'chrome,firefox' -> ['chrome', 'firefox']; 'all' -> все поддерживаемые."""
    names = [n.strip().lower() for n in value.split(",") if n.strip()]
    if "all" in names:
        return list(BROWSERS)
    unknown = [n for n in names if n not in BROWSERS]
    if unknown:
        raise ValueError(
            f"Неизвестный браузер: {', '.join(unknown)}. "
            f"Доступны: {', '.join(BROWSERS)} или all"
        )
    return names


def create_driver(name: str, headless: bool = False) -> WebDriver:
    try:
        driver = BROWSERS[name](headless)
    except WebDriverException as exc:
        raise BrowserUnavailableError(
            f"Браузер '{name}' не удалось запустить: {exc.msg or exc}"
        ) from exc
    driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
    # Запас на медленную загрузку при параллельном запуске (-n auto)
    driver.set_script_timeout(30)
    driver.set_page_load_timeout(60)
    return driver
