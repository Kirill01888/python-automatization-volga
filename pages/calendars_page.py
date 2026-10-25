"""Page Object страницы https://practice-automation.com/calendars/

Форма Jetpack с одним полем даты (формат YYYY-MM-DD) и кнопкой Submit.
По клику на поле открывается виджет tiny-date-picker (Jetpack):

    .dp-below > .dp
        .dp-cal-header : .dp-prev | .dp-cal-month | .dp-cal-year | .dp-next
        .dp-days       : 42 кнопки .dp-day (6 недель, неделя с понедельника)
                         .dp-edge-day   — день соседнего месяца (бледный)
                         .dp-selected   — выбранная дата
                         .dp-current    — подсвеченная (фокус виджета)
                         .dp-day-today  — сегодня
        .dp-months     : 12 кнопок .dp-month[data-month=0..11]   (меню месяцев)
        .dp-years      : кнопки .dp-year[data-year]              (меню годов)

Значение в поле меняется только после клика по дню.
"""
import calendar
from dataclasses import dataclass
from datetime import date, timedelta

import allure
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from pages.base_page import BasePage

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def fmt(d: date) -> str:
    """Дата для подписей шагов: 31.12.2026."""
    return d.strftime("%d.%m.%Y")


def month_shift(year: int, month: int, delta: int) -> tuple[int, int]:
    total = year * 12 + (month - 1) + delta
    return total // 12, total % 12 + 1


@dataclass
class DayCell:
    """Кнопка дня в сетке календаря с вычисленной датой."""
    date: date
    element: WebElement
    is_edge: bool
    is_selected: bool
    is_current: bool
    is_today: bool
    is_disabled: bool


class CalendarsPage(BasePage):
    PATH = "/calendars/"

    # --- форма ---------------------------------------------------------------
    HEADING = (By.XPATH, "//h1[normalize-space()='Calendars']")
    DATE_LABEL = (By.XPATH, "//label[normalize-space()='Select or enter a date']")
    FORMAT_HINT = (By.CSS_SELECTOR, ".contact-form__field-format")
    FIELD_ERROR = (By.CSS_SELECTOR, ".contact-form__input-error.has-errors")
    FORM_ERROR = (By.CSS_SELECTOR, ".contact-form__error.show-errors")
    SUCCESS = (By.CSS_SELECTOR, ".contact-form-submission.submission-success")

    # --- виджет --------------------------------------------------------------
    PICKER = (By.CSS_SELECTOR, ".dp-below .dp")
    HEADER_MONTH = (By.CSS_SELECTOR, ".dp-below .dp-cal-header .dp-cal-month")
    HEADER_YEAR = (By.CSS_SELECTOR, ".dp-below .dp-cal-header .dp-cal-year")
    PREV = (By.CSS_SELECTOR, ".dp-below .dp-cal-header .dp-prev")
    NEXT = (By.CSS_SELECTOR, ".dp-below .dp-cal-header .dp-next")
    DAYS_VIEW = (By.CSS_SELECTOR, ".dp-below .dp-days")
    MONTHS_VIEW = (By.CSS_SELECTOR, ".dp-below .dp-months")
    MONTH_ITEMS = (By.CSS_SELECTOR, ".dp-below .dp-months .dp-month")
    YEARS_VIEW = (By.CSS_SELECTOR, ".dp-below .dp-years")
    YEAR_ITEMS = (By.CSS_SELECTOR, ".dp-below .dp-years .dp-year")

    _GRID_JS = """
        return Array.from(document.querySelectorAll('.dp-below .dp-days .dp-day'))
            .map(b => [b, b.textContent.trim(), b.className]);
    """

    # ========================================================================
    # Поле и форма
    # ========================================================================
    @property
    def date_input(self) -> WebElement:
        label = self.find(self.DATE_LABEL)
        return self.driver.find_element(By.ID, label.get_attribute("for"))

    @property
    def submit_button(self) -> WebElement:
        form = self.date_input.find_element(By.XPATH, "./ancestor::form")
        return form.find_element(By.CSS_SELECTOR, "button[type='submit']")

    def get_label_text(self) -> str:
        return self.get_text(self.DATE_LABEL)

    def get_format_hint(self) -> str:
        return self.get_text(self.FORMAT_HINT)

    def is_heading_visible(self) -> bool:
        return self.is_visible(self.HEADING)

    def is_date_input_visible(self) -> bool:
        return self.date_input.is_displayed()

    def is_submit_visible(self) -> bool:
        return self.submit_button.is_displayed()

    def get_date_value(self) -> str:
        return self.date_input.get_attribute("value") or ""

    def type_date(self, text: str):
        with allure.step(f"Ввести в поле даты вручную: «{text}»"):
            field = self.scroll_to(self.date_input)
            field.click()
            field.send_keys(Keys.CONTROL, "a")
            field.send_keys(Keys.DELETE)
            field.send_keys(text)
        return self

    @allure.step("Нажать Esc в поле даты")
    def press_escape(self):
        self.date_input.send_keys(Keys.ESCAPE)
        return self

    @allure.step("Кликнуть по заголовку страницы (вне календаря)")
    def click_outside(self):
        self.click(self.HEADING)
        return self

    @allure.step("Нажать Submit")
    def submit(self):
        if self.is_picker_open(timeout=0.5):
            self.click_outside()
            self.wait_picker_closed()
        self.click_element(self.submit_button)
        return self

    def is_success_visible(self, timeout: float = 10) -> bool:
        return self.is_visible(self.SUCCESS, timeout)

    def is_error_visible(self, timeout: float = 5) -> bool:
        return self.is_visible(self.FIELD_ERROR, timeout) or self.is_visible(self.FORM_ERROR, 0.5)

    def get_page_text(self) -> str:
        return self.driver.find_element(By.TAG_NAME, "body").text

    # ========================================================================
    # Открытие / закрытие виджета
    # ========================================================================
    def is_picker_open(self, timeout: float = 3) -> bool:
        return self.is_visible(self.PICKER, timeout)

    def wait_picker_closed(self) -> bool:
        return self.wait_invisible(self.PICKER, timeout=5)

    @allure.step("Открыть календарь кликом по полю даты")
    def open_picker(self):
        if self.is_picker_open(timeout=0.3):
            return self
        self.click_element(self.date_input)
        if not self.is_picker_open(timeout=2):
            # поле уже было в фокусе — снимаем фокус и кликаем снова
            self.click(self.HEADING)
            self.click_element(self.date_input)
        self.find(self.PICKER)
        return self

    # ========================================================================
    # Шапка: месяц/год, стрелки
    # ========================================================================
    def get_header_month(self) -> str:
        return self.get_text(self.HEADER_MONTH)

    def get_header_year(self) -> int:
        return int(self.get_text(self.HEADER_YEAR))

    def get_picker_title(self) -> str:
        """Например: 'October 2026'."""
        return f"{self.get_header_month()} {self.get_header_year()}"

    def get_displayed_month(self) -> tuple[int, int]:
        return self.get_header_year(), MONTHS.index(self.get_header_month()) + 1

    def _switch_month(self, locator) -> None:
        old = self.get_picker_title()
        self.click(locator)
        self.wait.until(lambda _: self.get_picker_title() != old)

    @allure.step("Стрелка «>»: следующий месяц")
    def next_month(self):
        self._switch_month(self.NEXT)
        return self

    @allure.step("Стрелка «<»: предыдущий месяц")
    def prev_month(self):
        self._switch_month(self.PREV)
        return self

    def paginate_to(self, year: int, month: int):
        with allure.step(f"Перелистать стрелками до {MONTHS[month - 1]} {year}"):
            cur_y, cur_m = self.get_displayed_month()
            diff = (year - cur_y) * 12 + (month - cur_m)
            for _ in range(abs(diff)):
                self.next_month() if diff > 0 else self.prev_month()
        return self

    # ========================================================================
    # Меню месяцев
    # ========================================================================
    @allure.step("Открыть меню месяцев (Month picker)")
    def open_month_menu(self):
        self.click(self.HEADER_MONTH)
        self.find(self.MONTHS_VIEW)
        return self

    def get_month_menu(self) -> list[tuple[int, str]]:
        """[(data-month, подпись), ...] в порядке отображения."""
        return [
            (int(el.get_attribute("data-month")), el.text.strip())
            for el in self.find_all(self.MONTH_ITEMS)
        ]

    def choose_month(self, index: int):
        with allure.step(f"Выбрать в меню месяц {MONTHS[index]} (data-month={index})"):
            self.click((By.CSS_SELECTOR, f".dp-below .dp-month[data-month='{index}']"))
            self.find(self.DAYS_VIEW)
        return self

    # ========================================================================
    # Меню годов
    # ========================================================================
    @allure.step("Открыть меню годов (Year picker)")
    def open_year_menu(self):
        self.click(self.HEADER_YEAR)
        self.find(self.YEARS_VIEW)
        return self

    def get_year_menu(self) -> list[int]:
        return [int(v) for v in self.driver.execute_script(
            "return Array.from(document.querySelectorAll('.dp-below .dp-year'))"
            ".map(b => b.getAttribute('data-year'));"
        )]

    def choose_year(self, year: int):
        with allure.step(f"Выбрать в меню год {year}"):
            self.click((By.CSS_SELECTOR, f".dp-below .dp-year[data-year='{year}']"))
            self.find(self.DAYS_VIEW)
        return self

    @allure.step("Получить диапазон годов виджета из меню")
    def get_year_range(self) -> tuple[int, int]:
        """(min, max) из меню годов; меню закрывается без выбора."""
        self.open_picker().open_year_menu()
        years = self.get_year_menu()
        self.press_escape()
        self.wait_picker_closed()
        return min(years), max(years)

    def go_to(self, year: int, month: int):
        with allure.step(f"Перейти в календаре на {MONTHS[month - 1]} {year} через меню года и месяца"):
            self.open_picker()
            if self.get_header_year() != year:
                self.open_year_menu().choose_year(year)
            if self.get_displayed_month()[1] != month:
                self.open_month_menu().choose_month(month - 1)
        return self

    # ========================================================================
    # Сетка дней
    # ========================================================================
    def get_grid(self) -> list[DayCell]:
        """Все 42 ячейки с вычисленной датой: бледные дни до первого числа —
        предыдущий месяц, после последнего — следующий."""
        year, month = self.get_displayed_month()
        prev_ym, next_ym = month_shift(year, month, -1), month_shift(year, month, 1)
        cells, seen_current = [], False
        for element, text, classes in self.driver.execute_script(self._GRID_JS):
            cls = classes.split()
            is_edge = "dp-edge-day" in cls
            if is_edge:
                y, m = next_ym if seen_current else prev_ym
            else:
                seen_current = True
                y, m = year, month
            cells.append(DayCell(
                date=date(y, m, int(text)), element=element, is_edge=is_edge,
                is_selected="dp-selected" in cls, is_current="dp-current" in cls,
                is_today="dp-day-today" in cls, is_disabled="dp-day-disabled" in cls,
            ))
        return cells

    def get_month_days(self) -> list[date]:
        """Даты текущего (не бледного) месяца в сетке."""
        return [c.date for c in self.get_grid() if not c.is_edge]

    def get_edge_days(self) -> list[DayCell]:
        return [c for c in self.get_grid() if c.is_edge]

    def get_selected_dates(self) -> list[date]:
        return [c.date for c in self.get_grid() if c.is_selected]

    def get_highlighted_date(self) -> date | None:
        cur = [c.date for c in self.get_grid() if c.is_current]
        return cur[0] if cur else None

    def get_today_cell(self) -> date | None:
        today = [c.date for c in self.get_grid() if c.is_today]
        return today[0] if today else None

    def _cell(self, target: date) -> DayCell | None:
        return next((c for c in self.get_grid() if c.date == target), None)

    def select_day(self, day: int):
        year, month = self.get_displayed_month()
        with allure.step(f"Кликнуть в сетке день {day} ({fmt(date(year, month, day))})"):
            cell = self._cell(date(year, month, day))
            assert cell is not None and not cell.is_edge, f"В {month:02d}.{year} нет дня {day}"
            self.click_element(cell.element)
            self.wait_picker_closed()
        return self

    def _focus_and_click(self, cell: DayCell, title: str) -> None:
        """Наводим курсор и фокус на день (виден в отчёте), затем кликаем."""
        self.scroll_to(cell.element)
        ActionChains(self.driver).move_to_element(cell.element).perform()
        self.driver.execute_script("arguments[0].focus();", cell.element)
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name=title, attachment_type=allure.attachment_type.PNG,
        )
        cell.element.click()
        self.wait_picker_closed()

    def select_date(self, target: date):
        with allure.step(f"Выбрать дату {fmt(target)} (меню года/месяца + клик по дню)"):
            self.go_to(target.year, target.month)
            self.select_day(target.day)
        return self

    def pick_date_by_pagination(self, target: date):
        with allure.step(f"Выбрать дату {fmt(target)} перелистыванием стрелками"):
            self.open_picker().paginate_to(target.year, target.month)
            self.select_day(target.day)
        return self

    def selected_value_date(self) -> date:
        return date.fromisoformat(self.get_date_value())

    def shift_selected_date(self, days: int) -> date:
        """Сдвиг выбранной даты на ±1 день кликом по соседнему (бледному) дню.

        Если нужного дня нет в сетке (например, 1-е число — понедельник и
        предыдущий месяц не показан), переходим стрелкой и выбираем день там.
        """
        current = self.selected_value_date()
        target = current + timedelta(days=days)
        sign = "+" if days > 0 else "−"
        with allure.step(f"{fmt(current)} {sign} {abs(days)} д. → выбрать {fmt(target)}"):
            self.open_picker()
            cell = self._cell(target)
            if cell is not None:
                kind = "бледный день соседнего месяца" if cell.is_edge else "день"
                self._focus_and_click(cell, f"Фокус на {fmt(target)} ({kind})")
            else:
                with allure.step("Дня нет в сетке — перейти стрелкой в соседний месяц"):
                    self.next_month() if days > 0 else self.prev_month()
                    self._focus_and_click(self._cell(target), f"Фокус на {fmt(target)}")
        return target
