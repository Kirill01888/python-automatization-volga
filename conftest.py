import platform
from pathlib import Path

import allure
import pytest

from config import BASE_URL
from core.browsers import BrowserUnavailableError, create_driver, parse_browsers

_browser_versions: dict[str, str] = {}


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        default="chrome",
        help="Браузер(ы) для запуска: chrome, firefox, edge — через запятую, или all",
    )
    parser.addoption(
        "--headless", action="store_true", help="Запуск браузера без окна"
    )


def pytest_generate_tests(metafunc):
    """Каждый тест, использующий driver, запускается в каждом выбранном браузере."""
    if "browser_name" in metafunc.fixturenames:
        try:
            browsers = parse_browsers(metafunc.config.getoption("--browser"))
        except ValueError as exc:
            raise pytest.UsageError(str(exc))
        metafunc.parametrize("browser_name", browsers)


@pytest.fixture
def driver(request, browser_name):
    headless = request.config.getoption("--headless")
    try:
        drv = create_driver(browser_name, headless)
    except BrowserUnavailableError as exc:
        pytest.skip(str(exc))

    _browser_versions[browser_name] = drv.capabilities.get("browserVersion", "?")
    allure.dynamic.tag(browser_name)
    yield drv
    drv.quit()


# Название страницы в отчёте по pytest-маркеру
PAGE_SUITES = {
    "calendars": "Календарь",
    "modals": "Модальные окна",
    "ads": "Рекламные окна",
    "forms": "Форма (Form Fields)",
    "click_events": "События (Click Events)",
    "popups": "Всплывающие окна (Popups)",
}


def _story(item) -> str | None:
    """Значение @allure.story у теста или его класса."""
    for mark in item.iter_markers("allure_label"):
        if mark.kwargs.get("label_type") == "story":
            return mark.args[0]
    return None


@pytest.fixture(autouse=True)
def _allure_suites(request):
    """Дерево вкладки Suites в Allure:

        Календарь
        ├── Позитивные
        │   ├── Меню месяцев (Month picker)
        │   └── ...
        └── Негативные
            └── Негативные сценарии
    """
    item = request.node
    page = next((name for mark, name in PAGE_SUITES.items() if item.get_closest_marker(mark)), None)
    if page:
        allure.dynamic.parent_suite(page)
    if item.get_closest_marker("negative"):
        allure.dynamic.suite("Негативные")
    elif item.get_closest_marker("positive"):
        allure.dynamic.suite("Позитивные")
    story = _story(item)
    if story:
        allure.dynamic.sub_suite(story)


# --------------------------------------------------------------------------
# Вывод в консоль названия теста перед его запуском
# --------------------------------------------------------------------------
_config: pytest.Config | None = None
_titles: dict[str, str] = {}


def pytest_configure(config):
    global _config
    _config = config


def _display_title(item) -> str:
    """Название из @allure.title с подставленными параметрами + браузер."""
    func = getattr(item, "function", None)
    title = getattr(func, "__allure_display_name__", None) or item.name
    params = getattr(getattr(item, "callspec", None), "params", {})
    try:
        title = title.format(**params)
    except (KeyError, IndexError, ValueError):
        pass
    browser = params.get("browser_name")
    return f"{title} [{browser}]" if browser else title


def pytest_collection_modifyitems(items):
    for item in items:
        _titles[item.nodeid] = _display_title(item)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logstart(nodeid, location):
    """Перед каждым тестом печатает «▶ <название>».

    Без -n — русское название из Allure. С -n (xdist) хук срабатывает в главном
    процессе, когда воркер берёт тест: названий там нет, печатается id теста.
    """
    if _config is None or hasattr(_config, "workerinput"):
        return
    reporter = _config.pluginmanager.get_plugin("terminalreporter")
    if reporter is None:
        return
    reporter.ensure_newline()
    reporter.write_line(f"▶ {_titles.get(nodeid, nodeid)}", cyan=True, bold=True)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """При падении теста прикладываем к Allure скриншот и URL страницы."""
    report = yield
    if report.when in ("setup", "call") and report.failed:
        drv = item.funcargs.get("driver")
        if drv is not None:
            try:
                allure.attach(
                    drv.get_screenshot_as_png(),
                    name="Скриншот при падении",
                    attachment_type=allure.attachment_type.PNG,
                )
                allure.attach(
                    drv.current_url,
                    name="URL при падении",
                    attachment_type=allure.attachment_type.URI_LIST,
                )
            except Exception:  # браузер мог уже упасть — отчёт важнее
                pass
    return report


def pytest_sessionfinish(session):
    """Записываем окружение в Allure (вкладка Environment)."""
    alluredir = session.config.getoption("--alluredir", None)
    if not alluredir:
        return
    path = Path(alluredir)
    path.mkdir(parents=True, exist_ok=True)
    env_file = path / "environment.properties"

    # При -n auto этот хук выполняется в каждом процессе xdist: дописываем
    # свои значения к уже записанным, чтобы версии браузеров не потерялись.
    env: dict[str, str] = {}
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition("=")
            if key:
                env[key] = value
    env.update({
        "Base.URL": BASE_URL,
        "Headless": str(session.config.getoption("--headless")),
        "OS": f"{platform.system()} {platform.release()}",
        "Python": platform.python_version(),
    })
    env.update({f"Browser.{n}": v for n, v in _browser_versions.items()})
    env_file.write_text("\n".join(f"{k}={v}" for k, v in sorted(env.items())), encoding="utf-8")
