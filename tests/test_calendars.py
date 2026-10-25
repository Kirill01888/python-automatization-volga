"""Тесты страницы Calendars: https://practice-automation.com/calendars/

Виджет — tiny-date-picker (Jetpack). Значение в поле меняется только
после клика по дню, поэтому в каждом сценарии после выбора месяца/года
обязательно выбирается день.
"""

import calendar
from datetime import date

import allure
import pytest

from pages.calendars_page import MONTHS, CalendarsPage, fmt, month_shift

TODAY = date.today()


def last_day(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def title(year: int, month: int) -> str:
    return f"{MONTHS[month - 1]} {year}"


@pytest.fixture
def page(driver) -> CalendarsPage:
    return CalendarsPage(driver).open()


def check_selected(page: CalendarsPage, expected: date) -> None:
    """Общая проверка выбранной даты: поле, шапка календаря и выделение в сетке."""
    with allure.step(f"Проверить, что выбрана дата {fmt(expected)}"):
        assert page.get_date_value() == expected.isoformat(), (
            f"Значение поля {page.get_date_value()!r}, ожидалось {expected.isoformat()!r}"
        )
        page.open_picker()
        assert page.get_picker_title() == title(expected.year, expected.month), (
            f"Календарь показывает {page.get_picker_title()!r}"
        )
        assert page.get_selected_dates() == [expected], (
            f"В сетке выделено {page.get_selected_dates()}, ожидалось [{expected}]"
        )
        page.press_escape()


pytestmark = [pytest.mark.calendars]


# ==========================================================================
# Базовые сценарии
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Календарь")
@allure.story("Базовые сценарии")
class TestCalendarBasics:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title(
        "Страница открывается: заголовок, поле даты с подписью и подсказкой формата, кнопка Submit"
    )
    def test_page_elements(self, page):
        """Базовая проверка формы до любых действий пользователя:
        заголовок «Calendars», поле даты, кнопка Submit видны; подпись поля
        «Select or enter a date», под полем подсказка «YYYY-MM-DD»; поле пустое.
        """
        with allure.step("Заголовок, поле даты и кнопка Submit видны"):
            assert page.is_heading_visible(), "Заголовок 'Calendars' не отображается"
            assert page.is_date_input_visible(), "Поле даты не отображается"
            assert page.is_submit_visible(), "Кнопка Submit не отображается"
        with allure.step("Подпись поля и подсказка формата"):
            assert page.get_label_text() == "Select or enter a date"
            assert page.get_format_hint() == "YYYY-MM-DD", "Нет подсказки формата под полем"
        with allure.step("Поле даты изначально пустое"):
            assert page.get_date_value() == "", "Поле даты не пустое при загрузке"

    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(
        "Календарь открывается на текущем месяце, сегодня отмечено, сетка построена корректно"
    )
    def test_picker_opens_with_correct_grid(self, page):
        """Клик по полю открывает календарь:
        1. В шапке текущий месяц и год, сегодняшний день отмечен.
        2. Сетка — 42 ячейки (6 недель), неделя начинается с понедельника.
        3. Дней текущего месяца ровно столько, сколько в месяце, по порядку с 1-го.
        4. Бледные дни принадлежат соседним месяцам.
        """
        page.open_picker()
        with allure.step(f"В шапке {title(TODAY.year, TODAY.month)}, отмечено {fmt(TODAY)}"):
            assert page.get_picker_title() == title(TODAY.year, TODAY.month)
            assert page.get_today_cell() == TODAY, "Сегодняшний день не отмечен в сетке"
        year, month = page.get_displayed_month()
        grid = page.get_grid()
        with allure.step("Сетка: 42 ячейки, неделя с понедельника"):
            assert len(grid) == 42, f"В сетке {len(grid)} ячеек"
            assert grid[0].date.weekday() == 0, "Неделя начинается не с понедельника"
        with allure.step(f"Дней месяца: {last_day(year, month)}, бледные — соседние месяцы"):
            assert page.get_month_days() == [
                date(year, month, d) for d in range(1, last_day(year, month) + 1)
            ]
            for cell in page.get_edge_days():
                assert (cell.date.year, cell.date.month) != (year, month), (
                    f"Бледный день {cell.date} принадлежит текущему месяцу"
                )

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title(
        "Навигация стрелками: «>» — следующий месяц, «<» — предыдущий, «>» + «<» — исходный"
    )
    def test_arrow_navigation(self, page):
        current = title(TODAY.year, TODAY.month)
        nxt = title(*month_shift(TODAY.year, TODAY.month, 1))
        prv = title(*month_shift(TODAY.year, TODAY.month, -1))
        page.open_picker()
        with allure.step(f"«>»: {current} → {nxt}"):
            page.next_month()
            assert page.get_picker_title() == nxt
        with allure.step(f"«<»: {nxt} → {current} (возврат на исходный месяц)"):
            page.prev_month()
            assert page.get_picker_title() == current
        with allure.step(f"«<»: {current} → {prv}"):
            page.prev_month()
            assert page.get_picker_title() == prv

    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(
        "Выбор даты кликом: в текущем месяце и в других месяцах через пагинацию стрелками"
    )
    def test_select_date_by_click(self, page):
        """1. Клик по 10-му числу текущего месяца: дата в поле в формате
           YYYY-MM-DD, календарь закрылся, в сетке выделен этот день.
        2. Пагинация стрелками на −13, +2 и +14 месяцев и клик по 20-му числу
           (рекомендованная на странице техника «using pagination»).
        """
        target = TODAY.replace(day=10)
        with allure.step(f"1. Текущий месяц: выбрать {fmt(target)}"):
            page.open_picker().select_day(10)
            assert not page.is_picker_open(timeout=0.5), "Календарь не закрылся после выбора"
            check_selected(page, target)

        for offset in (-13, 2, 14):
            target = date(*month_shift(TODAY.year, TODAY.month, offset), 20)
            with allure.step(f"2. Пагинация на {offset:+d} мес.: выбрать {fmt(target)}"):
                page.pick_date_by_pagination(target)
                check_selected(page, target)

    @pytest.mark.positive
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title(
        "Ручной ввод синхронизирует календарь; введённая и выбранная даты успешно отправляются"
    )
    def test_manual_input_and_submit(self, page):
        """1. Ввод 2027-03-18 вручную — календарь переключается на March 2027
           и подсвечивает 18-е; Submit — «Thank you for your response» с датой.
        2. Страница заново, выбор 5-го числа следующего месяца в календаре;
           Submit — «Thank you for your response» с датой.
        """
        typed = date(2027, 3, 18)
        with allure.step(f"1. Ручной ввод {typed.isoformat()} и отправка"):
            page.type_date(typed.isoformat())
            assert page.is_picker_open(), "Календарь не открыт при вводе"
            assert page.get_picker_title() == title(typed.year, typed.month)
            assert page.get_highlighted_date() == typed, "Введённый день не подсвечен"
            page.submit()
            assert page.is_success_visible(), "Нет сообщения «Thank you for your response»"
            assert typed.isoformat() in page.get_page_text()

        picked = date(*month_shift(TODAY.year, TODAY.month, 1), 5)
        with allure.step(f"2. Выбор {fmt(picked)} в календаре и отправка"):
            page.open().select_date(picked)
            check_selected(page, picked)
            page.submit()
            assert page.is_success_visible(), "Нет сообщения «Thank you for your response»"
            assert picked.isoformat() in page.get_page_text()


# ==========================================================================
# 1. Меню месяцев
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Календарь")
@allure.story("Меню месяцев (Month picker)")
class TestMonthPicker:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Меню месяцев: каждый из 12 пунктов даёт правильный номер месяца в поле и шапке")
    def test_month_menu_numbers(self, page):
        page.open_picker().open_month_menu()
        with allure.step("Меню содержит 12 месяцев по порядку (data-month 0–11)"):
            menu = page.get_month_menu()
            assert [i for i, _ in menu] == list(range(12)), f"data-month в меню: {menu}"
        page.press_escape()

        errors = []
        for month, name in enumerate(MONTHS, start=1):
            expected = date(TODAY.year, month, 15)
            try:
                with allure.step(f"Месяц №{month} — {name}"):
                    page.open_picker().open_month_menu()
                    index, label = page.get_month_menu()[month - 1]
                    assert name.startswith(label) or label.startswith(name[:3]), (
                        f"пункт data-month={index} подписан {label!r}"
                    )
                    page.choose_month(month - 1)
                    assert page.get_header_month() == name, f"в шапке {page.get_header_month()!r}"
                    page.select_day(15)
                    check_selected(page, expected)
            except AssertionError as exc:
                errors.append(f"{name}: {exc}")
                page.press_escape()

        assert not errors, "Несоответствия в меню месяцев:\n" + "\n".join(errors)


# ==========================================================================
# 2. Меню годов
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Календарь")
@allure.story("Меню годов (Year picker)")
class TestYearPicker:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(
        "Меню годов: диапазон, граничные годы min/max, годы за пределами меню и 9999-12-31"
    )
    def test_year_picker(self, page):
        """Комплексная проверка выбора года.

        1. Меню годов: список непрерывный, содержит текущий год, границы —
           текущий год ±100 (сейчас 1926–2126). min и max берём из меню.
        2. Граничные годы из меню (min, max): выбрать год в меню, затем месяц
           и день (значение в поле меняется только после клика по дню),
           проверить выбор и отправить форму — ожидается успех.
           Месяц берём подальше от границы диапазона: для min — декабрь,
           для max — январь (граница виджета = сегодня ±100 лет с точностью до дня).
        3. Годы за пределами меню (min−1, max+1): в меню их нет, вводим дату
           в поле вручную и отправляем — форма их принимает, ожидается успех.
        4. Максимальная дата 9999-12-31: вводим вручную и отправляем — успех.

        Перед каждой отправкой страница открывается заново (после успешной
        отправки форма заменяется сообщением). Ошибки собираются по всем
        случаям, итог — общий список.
        """
        errors = []

        # --- 1. Диапазон годов -------------------------------------------
        try:
            with allure.step("1. Меню годов: непрерывный список, текущий год ±100"):
                page.open_picker().open_year_menu()
                years = page.get_year_menu()
                year_min, year_max = min(years), max(years)
                allure.attach(
                    f"min={year_min}, max={year_max}, всего={len(years)}",
                    name="Диапазон годов",
                    attachment_type=allure.attachment_type.TEXT,
                )
                page.press_escape()
                assert sorted(years) == list(range(year_min, year_max + 1)), (
                    "в списке годов пропуски"
                )
                assert TODAY.year in years, "в меню нет текущего года"
                assert (year_min, year_max) == (TODAY.year - 100, TODAY.year + 100), (
                    f"диапазон {year_min}–{year_max}, ожидался {TODAY.year - 100}–{TODAY.year + 100}"
                )
        except AssertionError as exc:
            errors.append(f"Диапазон: {exc}")

        def submit_and_check(target_text: str) -> None:
            page.submit()
            assert page.is_success_visible(), f"{target_text} не отправилась"
            assert target_text in page.get_page_text(), f"в ответе нет {target_text}"

        # --- 2. Граничные годы из меню -------------------------------------
        for edge, target in [("min", date(year_min, 12, 15)), ("max", date(year_max, 1, 15))]:
            try:
                with allure.step(
                    f"2. Граничный год из меню ({edge} = {target.year}): выбрать {fmt(target)} и отправить"
                ):
                    page.open().open_picker().open_year_menu().choose_year(target.year)
                    assert page.get_header_year() == target.year, (
                        f"в шапке {page.get_header_year()}, ожидался {target.year}"
                    )
                    page.open_month_menu().choose_month(target.month - 1)
                    page.select_day(target.day)
                    check_selected(page, target)
                    submit_and_check(target.isoformat())
            except AssertionError as exc:
                errors.append(f"{edge} ({target.year}): {exc}")

        # --- 3. Годы за пределами меню ---------------------------------------
        for edge, target in [
            ("min−1", date(year_min - 1, 6, 15)),
            ("max+1", date(year_max + 1, 6, 15)),
        ]:
            try:
                with allure.step(
                    f"3. Год вне меню ({edge} = {target.year}): ввести {target.isoformat()} и отправить"
                ):
                    page.open().type_date(target.isoformat())
                    submit_and_check(target.isoformat())
            except AssertionError as exc:
                errors.append(f"{edge} ({target.year}): {exc}")

        # --- 4. 9999-12-31 ----------------------------------------------------
        try:
            with allure.step("4. Максимальная дата 9999-12-31: ввести и отправить"):
                page.open().type_date("9999-12-31")
                submit_and_check("9999-12-31")
        except AssertionError as exc:
            errors.append(f"9999-12-31: {exc}")

        assert not errors, "Ошибки в выборе года:\n" + "\n".join(errors)


# ==========================================================================
# 3. Границы месяца
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Календарь")
@allure.story("Границы месяца (±1 день)")
class TestMonthBoundaries:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Границы нечётных месяцев 2026: 1-е − 1 день, последнее + 1 день")
    def test_month_boundaries(self, page):
        """Проверяем месяцы 2026 года через один: 1, 3, 5, 7, 9, 11.

        Через ±1 день каждая проверка задевает и соседние месяцы, поэтому
        покрываются все 12 месяцев (и декабрь 2025 через 01.01.2026 − 1 день):

            Январь:  31.12.2025 ← 01.01 … 31.01 → 01.02
            Март:    28.02      ← 01.03 … 31.03 → 01.04
            Май:     30.04      ← 01.05 … 31.05 → 01.06
            Июль:    30.06      ← 01.07 … 31.07 → 01.08
            Сентябрь:31.08      ← 01.09 … 30.09 → 01.10
            Ноябрь:  31.10      ← 01.11 … 30.11 → 01.12

        Для каждого месяца 4 шага:
        1. Выбрать 1-е число — месяц не меняется              (01.03.2026 → месяц 3)
        2. 1-е число − 1 день — последнее число предыдущего   (01.03 → 28.02)
           Для января это переход в прошлый год: 01.01.2026 → 31.12.2025
        3. Выбрать последнее число — месяц не меняется        (31.03.2026 → месяц 3)
        4. Последнее число + 1 день — 1-е следующего месяца   (31.03 → 01.04)

        «±1 день» = клик по бледному дню соседнего месяца в сетке (с фокусом
        и скриншотом в отчёте). После каждого шага проверяется значение поля,
        месяц/год в шапке и то, что в сетке выделен только этот день.
        Ошибки собираются по всем месяцам, итог — общий список.
        """
        year = 2026
        errors = []

        for month in range(1, 13, 2):
            name = MONTHS[month - 1]
            first = date(year, month, 1)
            last = date(year, month, last_day(year, month))
            py, pm = month_shift(year, month, -1)
            prev_last = date(py, pm, last_day(py, pm))
            next_first = date(*month_shift(year, month, 1), 1)

            try:
                with allure.step(
                    f"{name} {year}: {fmt(prev_last)} ← {fmt(first)} … {fmt(last)} → {fmt(next_first)}"
                ):
                    with allure.step(
                        f"1. Выбрать 1-е число: {fmt(first)} — месяц остаётся №{month}"
                    ):
                        page.select_date(first)
                        check_selected(page, first)

                    with allure.step(f"2. {fmt(first)} − 1 день = {fmt(prev_last)}"):
                        actual = page.shift_selected_date(-1)
                        assert actual == prev_last, f"{fmt(first)} − 1 день дало {fmt(actual)}"
                        check_selected(page, prev_last)

                    with allure.step(
                        f"3. Выбрать последнее число: {fmt(last)} — месяц остаётся №{month}"
                    ):
                        page.select_date(last)
                        check_selected(page, last)

                    with allure.step(f"4. {fmt(last)} + 1 день = {fmt(next_first)}"):
                        actual = page.shift_selected_date(+1)
                        assert actual == next_first, f"{fmt(last)} + 1 день дало {fmt(actual)}"
                        check_selected(page, next_first)

            except AssertionError as exc:
                errors.append(f"{name}: {exc}")
                page.press_escape()

        assert not errors, "Ошибки на границах месяцев:\n" + "\n".join(errors)


# ==========================================================================
# 4. Переход через год
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Календарь")
@allure.story("Переход через год")
class TestYearRollover:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(
        "Переход через год: 31.12 + 1 день = 01.01 следующего, 01.01 − 1 день = 31.12 предыдущего"
    )
    def test_year_rollover(self, page):
        """Проверяем переход через границу года в обе стороны для нескольких лет:

            1999 — смена тысячелетия       31.12.1999 → 01.01.2000, 01.01.1999 → 31.12.1998
            2024 — високосный год          31.12.2024 → 01.01.2025, 01.01.2024 → 31.12.2023
            2026 — пример из задания       31.12.2026 → 01.01.2027, 01.01.2026 → 31.12.2025
            2027                           31.12.2027 → 01.01.2028, 01.01.2027 → 31.12.2026
            2099 — смена века              31.12.2099 → 01.01.2100, 01.01.2099 → 31.12.2098

        Смена тысячелетия проверяется на 1999 → 2000: виджет работает только
        с годами из меню (текущий ±100, сейчас 1926–2126), поэтому 2999 → 3000
        через календарь недоступен.

        Для каждого года 4 шага:
        1. Выбрать 31.12 (через меню года и месяца).
        2. 31.12 + 1 день — клик по бледному 1 января в сетке декабря
           → 01.01 следующего года, в шапке January следующего года.
        3. Выбрать 01.01 того же года.
        4. 01.01 − 1 день — клик по бледному 31 декабря в сетке января
           (если 1 января — понедельник и декабря в сетке нет, переход стрелкой)
           → 31.12 предыдущего года.

        После каждого шага проверяется значение поля, месяц/год в шапке
        и то, что в сетке выделен только этот день.
        Ошибки собираются по всем годам, итог — общий список.
        """
        years = [1999, 2024, 2026, 2027, 2099]
        errors = []

        for year in years:
            dec31, jan1 = date(year, 12, 31), date(year, 1, 1)
            next_jan1, prev_dec31 = date(year + 1, 1, 1), date(year - 1, 12, 31)

            try:
                with allure.step(
                    f"{year}: {fmt(prev_dec31)} ← {fmt(jan1)} … {fmt(dec31)} → {fmt(next_jan1)}"
                ):
                    with allure.step(f"1. Выбрать {fmt(dec31)}"):
                        page.select_date(dec31)
                        check_selected(page, dec31)

                    with allure.step(f"2. {fmt(dec31)} + 1 день = {fmt(next_jan1)}"):
                        actual = page.shift_selected_date(+1)
                        assert actual == next_jan1, f"{fmt(dec31)} + 1 день дало {fmt(actual)}"
                        check_selected(page, next_jan1)

                    with allure.step(f"3. Выбрать {fmt(jan1)}"):
                        page.select_date(jan1)
                        check_selected(page, jan1)

                    with allure.step(f"4. {fmt(jan1)} − 1 день = {fmt(prev_dec31)}"):
                        actual = page.shift_selected_date(-1)
                        assert actual == prev_dec31, f"{fmt(jan1)} − 1 день дало {fmt(actual)}"
                        check_selected(page, prev_dec31)

            except AssertionError as exc:
                errors.append(f"{year}: {exc}")
                page.press_escape()

        assert not errors, "Ошибки при переходе через год:\n" + "\n".join(errors)


# ==========================================================================
# 6. Високосные годы
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Календарь")
@allure.story("Високосные годы")
class TestLeapYears:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Високосные годы: в феврале 29 или 28 дней, последний день февраля + 1 = 01.03")
    def test_leap_years(self, page):
        """Проверяем февраль для високосных и невисокосных лет.

        Правило: год високосный, если делится на 4, кроме кратных 100,
        но кратные 400 — снова високосные. Поэтому:
            2024, 2028 — високосные (делятся на 4)          → 29 дней
            2000       — високосный (делится на 400)         → 29 дней
            2026, 2027 — обычные                             → 28 дней
            2100       — обычный (кратен 100, но не 400)     → 28 дней

        Для каждого года:
        1. Через меню года и месяца открыть февраль.
        2. Посчитать дни февраля в сетке (без бледных дней соседних месяцев).
        3. Выбрать последний день февраля (29.02 или 28.02) — поле, шапка, выделение.
        4. Последний день + 1 (клик по бледному 1 марта) = 01.03 того же года.

        Ожидаемое число дней считаем по правилу выше, а не через модуль
        calendar, чтобы тест проверял виджет независимо.
        Ошибки собираются по всем годам, итог — общий список.
        """
        cases = [2024, 2028, 2000, 2026, 2027, 2100]
        errors = []

        for year in cases:
            is_leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
            days = 29 if is_leap else 28
            kind = "високосный" if is_leap else "обычный"
            feb_last, march_first = date(year, 2, days), date(year, 3, 1)

            try:
                with allure.step(f"{year} — {kind}, ожидается {days} дней в феврале"):
                    with allure.step(f"1. Открыть February {year}"):
                        page.go_to(year, 2)

                    with allure.step(f"2. В сетке ровно {days} дней февраля"):
                        feb = page.get_month_days()
                        assert len(feb) == days, f"в феврале {year} показано {len(feb)} дней"

                    with allure.step(f"3. Выбрать последний день: {fmt(feb_last)}"):
                        page.select_day(days)
                        check_selected(page, feb_last)

                    with allure.step(f"4. {fmt(feb_last)} + 1 день = {fmt(march_first)}"):
                        actual = page.shift_selected_date(+1)
                        assert actual == march_first, f"{fmt(feb_last)} + 1 день дало {fmt(actual)}"
                        check_selected(page, march_first)

            except AssertionError as exc:
                errors.append(f"{year}: {exc}")
                page.press_escape()

        assert not errors, "Ошибки в обработке високосных лет:\n" + "\n".join(errors)


# ==========================================================================
# Негативные
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Календарь")
@allure.story("Негативные сценарии")
class TestCalendarNegative:
    @pytest.mark.negative
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Esc закрывает календарь без выбора даты — поле остаётся пустым")
    def test_escape_closes_without_value(self, page):
        page.open_picker().press_escape()
        assert page.wait_picker_closed(), "Календарь не закрылся по Esc"
        assert page.get_date_value() == ""

    @pytest.mark.negative
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Клик вне календаря закрывает его без выбора даты")
    def test_click_outside_closes_without_value(self, page):
        page.open_picker().click_outside()
        assert page.wait_picker_closed(), "Календарь не закрылся по клику вне него"
        assert page.get_date_value() == ""

    @pytest.mark.negative
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "bad_value",
        ["0001-01-01", "abc", "2026-13-01", "31.12.2026", "2026-02-31"],
        ids=["year_0001", "letters", "month_13", "wrong_format", "feb_31"],
    )
    @allure.title("Некорректная дата «{bad_value}» не отправляется: форма показывает ошибку")
    def test_invalid_date_rejected(self, page, bad_value):
        page.type_date(bad_value).submit()
        assert page.is_error_visible(), "Форма не показала ошибку"
        assert not page.is_success_visible(timeout=2), "Некорректная дата была отправлена"
