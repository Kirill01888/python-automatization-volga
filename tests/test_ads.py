"""Тесты страницы Ads: https://practice-automation.com/ads/

Реклама — окно Popup Maker, открывается автоматически через 4,5 с после
загрузки, закрывается только кнопкой «×», cookie не используется.
"""

import allure
import pytest

from pages.ads_page import AdsPage

pytestmark = [pytest.mark.ads]

AD_TITLE = "Hi"
AD_TEXT = "I am an ad."
COUNTDOWN = "An ad will appear in 5…4…3…2…1"

# Реклама не должна появиться раньше этого момента (задержка 4,5 с минус запас)
NOT_BEFORE = 3.5
# Сколько ждать, что закрытая реклама не появится повторно, с
NO_REAPPEAR_WAIT = 11


@pytest.fixture
def page(driver) -> AdsPage:
    return AdsPage(driver).open()


@pytest.fixture
def page_with_ad(page) -> AdsPage:
    """Страница, на которой реклама уже появилась."""
    page.wait_for_ad()
    return page


def check_ad_closed(page: AdsPage) -> None:
    with allure.step("Окно и затемнение скрыты, у <html> снят класс pum-open"):
        assert page.wait_ad_hidden(), "Реклама не закрылась"
        assert not page.is_html_marked_open(), "У <html> остался класс pum-open"


# ==========================================================================
# Появление
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Рекламные окна")
@allure.story("Появление")
class TestAdAppearance:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title(
        "Страница открывается: заголовок «Ads», текст с отсчётом, ссылка; рекламы ещё нет"
    )
    def test_page_initial_state(self, page):
        """Цель: убедиться, что страница загружается в исходном состоянии и реклама
        не перекрывает её с первой секунды.

        Ожидаемый результат: в момент загрузки рекламного окна нет; на странице
        есть заголовок «Ads», текст «An ad will appear in 5…4…3…2…1» и ссылка
        «how to handle ads in test automation».
        """
        # Проверяем первым шагом: через 4,5 с реклама появится по расписанию
        with allure.step(
            f"Сразу после загрузки ({page.seconds_since_load():.1f} с) реклама ещё не показана"
        ):
            assert not page.is_ad_visible(timeout=0), "Реклама показана сразу после загрузки"
        with allure.step("Заголовок, текст с отсчётом и ссылка видны"):
            assert page.is_heading_visible(), "Заголовок 'Ads' не отображается"
            assert page.get_countdown_text() == COUNTDOWN
            assert page.is_link_visible(), "Ссылка «how to handle ads» не отображается"

    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Реклама появляется автоматически через ~4,5 с после загрузки страницы")
    def test_ad_appears_automatically(self, page):
        """Цель: проверить, что реклама показывается сама, без действий пользователя,
        и с той задержкой, что задана в настройках попапа (auto_open, 4500 мс).

        Ожидаемый результат: окно рекламы появляется в интервале 3,5–12 с после
        загрузки (на практике около 5 с: задержка плюс анимация); фактическое время
        прикладывается к отчёту.
        """
        elapsed = page.wait_for_ad()
        with allure.step(
            f"Реклама появилась через {elapsed:.1f} с — в интервале {NOT_BEFORE}–{page.AD_WAIT_TIMEOUT} с"
        ):
            assert NOT_BEFORE <= elapsed <= page.AD_WAIT_TIMEOUT, (
                f"Реклама появилась через {elapsed:.1f} с"
            )

    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(
        "Окно рекламы: затемнение, заголовок «Hi», текст «I am an ad.», кнопка «×», role=dialog"
    )
    def test_ad_content(self, page_with_ad):
        """Цель: проверить, что показанное окно — полноценная модальная реклама
        с правильным содержимым и средством закрытия.

        Ожидаемый результат: видно затемнение, у <html> класс pum-open; заголовок
        «Hi», текст «I am an ad.»; кнопка «×» с aria-label «Close»; окно размечено
        как модальный диалог (role="dialog", aria-modal="true").
        """
        page = page_with_ad
        with allure.step("Затемнение видно, у <html> класс pum-open"):
            assert page.is_overlay_visible()
            assert page.is_html_marked_open()
        with allure.step(f"Заголовок «{AD_TITLE}», текст «{AD_TEXT}»"):
            assert page.get_ad_title() == AD_TITLE
            assert page.get_ad_text() == AD_TEXT
        with allure.step("Кнопка «×» с aria-label «Close», окно — модальный диалог"):
            assert page.get_close_label() == "Close"
            assert page.get_dialog_attributes() == {"role": "dialog", "aria-modal": "true"}

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Окно рекламы целиком помещается в видимую область экрана")
    def test_ad_inside_viewport(self, page_with_ad):
        """Цель: убедиться, что окно рекламы не выходит за края экрана на обычном
        десктопном разрешении — иначе часть содержимого или кнопка «×» недоступны.

        Ожидаемый результат: все границы окна (top, left, bottom, right) находятся
        внутри видимой области; координаты прикладываются к отчёту.
        """
        assert page_with_ad.is_ad_inside_viewport(), "Окно рекламы выходит за границы экрана"

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title(
        "Мобильный экран 375×812: реклама появляется, помещается в экран и закрывается «×»"
    )
    def test_ad_on_mobile_viewport(self, driver):
        """Цель: проверить рекламу на экране смартфона (375×812): адаптивное окно
        должно оставаться видимым целиком и закрываемым.

        Ожидаемый результат: реклама появляется, окно целиком помещается в экран,
        кнопка «×» доступна и закрывает окно. В Chrome/Edge экран эмулируется,
        в Firefox меняется размер окна; фактический размер — во вложении.
        """
        page = AdsPage(driver)
        page.set_viewport(375, 812)
        page.open()
        width, height = page.get_viewport()
        allure.attach(
            f"{width}×{height}",
            name="Фактический размер видимой области",
            attachment_type=allure.attachment_type.TEXT,
        )
        page.wait_for_ad()
        with allure.step("Окно рекламы помещается в экран"):
            assert page.is_ad_inside_viewport(), "Окно рекламы выходит за границы экрана"
        page.close_ad()
        check_ad_closed(page)


# ==========================================================================
# Закрытие
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Рекламные окна")
@allure.story("Закрытие")
class TestAdClosing:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Реклама закрывается кнопкой «×»")
    def test_close_by_x(self, page_with_ad):
        """Цель: проверить основной (и единственный разрешённый настройками) способ
        закрыть рекламу — кнопку «×».

        Ожидаемый результат: окно и затемнение скрываются, у <html> снимается
        класс pum-open.
        """
        page_with_ad.close_ad()
        check_ad_closed(page_with_ad)

    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("После закрытия рекламы ссылка на странице снова доступна для клика")
    def test_page_reachable_after_close(self, page_with_ad):
        """Цель: убедиться, что после закрытия рекламы страница полностью доступна —
        не остаётся невидимого затемнения, перехватывающего клики.

        Ожидаемый результат: в точке ссылки «how to handle ads in test automation»
        находится сама ссылка, а не затемнение (проверка через elementFromPoint).
        """
        page = page_with_ad
        page.close_ad()
        check_ad_closed(page)
        with allure.step("В точке ссылки находится сама ссылка, а не затемнение"):
            assert page.is_link_reachable(), "Ссылка перекрыта после закрытия рекламы"


# ==========================================================================
# Повторный показ
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Рекламные окна")
@allure.story("Повторный показ")
class TestAdReappearance:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Закрытая реклама не появляется повторно без перезагрузки страницы")
    def test_no_reappear_without_reload(self, page_with_ad):
        """Цель: проверить, что закрытая реклама не навязывается повторно в рамках
        той же загрузки страницы.

        Ожидаемый результат: после закрытия реклама не появляется в течение 11 с —
        больше чем вдвое дольше задержки автоматического показа (4,5 с).
        """
        page = page_with_ad
        page.close_ad()
        check_ad_closed(page)
        wait = NO_REAPPEAR_WAIT
        with allure.step(f"В течение {wait:.0f} с (больше задержки показа) реклама не появляется"):
            assert not page.is_ad_visible(timeout=wait), "Реклама появилась повторно"

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("После перезагрузки страницы реклама появляется снова (cookie не используется)")
    def test_reappears_after_reload(self, page_with_ad):
        """Цель: проверить, что реклама показывается при каждом посещении страницы —
        в настройках попапа не используется cookie «уже показано».

        Ожидаемый результат: после закрытия рекламы и перезагрузки страницы окно
        появляется снова с тем же заголовком «Hi».
        """
        page = page_with_ad
        page.close_ad()
        check_ad_closed(page)
        page.reload()
        elapsed = page.wait_for_ad()
        with allure.step(f"Реклама снова появилась через {elapsed:.1f} с после перезагрузки"):
            assert page.get_ad_title() == AD_TITLE


# ==========================================================================
# Негативные
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Рекламные окна")
@allure.story("Негативные сценарии")
class TestAdNegative:
    @pytest.mark.negative
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(
        f"Реклама не появляется раньше задержки: первые {NOT_BEFORE} с после загрузки окна нет"
    )
    def test_ad_not_shown_before_delay(self, page):
        """Цель: убедиться, что реклама не показывается раньше заданной задержки —
        пользователь успевает увидеть страницу.

        Ожидаемый результат: в первые 3,5 с после загрузки окна нет; затем реклама
        всё же появляется (тест не проходит «впустую»).
        """
        with allure.step(f"До {NOT_BEFORE} с после загрузки реклама не показана"):
            assert page.is_ad_absent_until(NOT_BEFORE), (
                f"Реклама появилась раньше {NOT_BEFORE} с (через {page.seconds_since_load():.1f} с)"
            )
        with allure.step("Затем реклама всё-таки появляется"):
            page.wait_for_ad()

    @pytest.mark.negative
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Esc не закрывает рекламу (в настройках закрытие только кнопкой «×»)")
    def test_escape_does_not_close(self, page_with_ad):
        """Цель: проверить, что клавиша Esc не закрывает рекламу — в настройках
        попапа она отключена (esc_press: false).

        Ожидаемый результат: после нажатия Esc окно остаётся открытым.
        """
        page_with_ad.press_escape()
        with allure.step("Окно рекламы остаётся открытым"):
            assert not page_with_ad.wait_ad_hidden(timeout=1.5), "Реклама закрылась по Esc"

    @pytest.mark.negative
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Клик по затемнению вне окна не закрывает рекламу")
    def test_overlay_click_does_not_close(self, page_with_ad):
        """Цель: проверить, что клик по затемнению вокруг окна не закрывает рекламу —
        в настройках попапа это отключено (overlay_click: false).

        Ожидаемый результат: после клика по затемнению вне окна реклама остаётся
        открытой.
        """
        page_with_ad.click_overlay()
        with allure.step("Окно рекламы остаётся открытым"):
            assert not page_with_ad.wait_ad_hidden(timeout=1.5), (
                "Реклама закрылась по клику на затемнение"
            )

    @pytest.mark.negative
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Пока реклама открыта, ссылка под затемнением недоступна: клик не проходит")
    def test_link_blocked_while_ad_open(self, page_with_ad):
        """Цель: убедиться, что пока реклама открыта, элементы страницы под ней
        недоступны — случайный клик не уводит пользователя.

        Ожидаемый результат: в точке ссылки находится затемнение; реальный клик
        мышью в эту точку не открывает новую вкладку и не меняет URL; реклама
        остаётся на месте.
        """
        page = page_with_ad
        driver = page.driver
        with allure.step("В точке ссылки находится затемнение, а не ссылка"):
            assert not page.is_link_reachable(), "Ссылка не перекрыта затемнением"
        url, tabs = driver.current_url, len(driver.window_handles)
        page.click_link_by_coordinates()
        with allure.step("Новая вкладка не открылась, URL не изменился, реклама на месте"):
            assert len(driver.window_handles) == tabs, "По ссылке открылась новая вкладка"
            assert driver.current_url == url, "Страница сменилась"
            assert page.is_ad_visible(timeout=1), "Реклама закрылась после клика"

    @pytest.mark.negative
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title(
        "Пока реклама открыта, страница не прокручивается — ни колесом мыши, ни клавишами"
    )
    def test_scroll_blocked_while_ad_open(self, driver):
        """Цель: проверить, что пока реклама открыта, страница под ней не
        прокручивается — Popup Maker блокирует прокрутку
        (html.pum-open.pum-open-overlay { overflow: hidden }).

        Ожидаемый результат: у <html> overflow-y: hidden; прокрутка колесом мыши
        и клавишами PageDown/End не меняет положение страницы, реклама на месте.
        Контроль: после закрытия рекламы та же прокрутка работает. Окно браузера
        уменьшено до 1280×600, чтобы страница была длиннее экрана.
        """
        page = AdsPage(driver).set_window_size(1280, 600)
        page.open().wait_for_ad()
        with allure.step("Страница длиннее окна — прокрутка в принципе возможна"):
            assert page.is_page_scrollable(), "Страница помещается в окно, проверять нечего"
        with allure.step("У <html> вычисленный overflow-y: hidden"):
            assert page.get_html_overflow() == "hidden", f"overflow-y = {page.get_html_overflow()}"

        start = page.get_scroll_y()
        page.scroll_by_wheel(600)
        with allure.step("После прокрутки колесом позиция страницы не изменилась"):
            assert not page.wait_scroll_changed(start, timeout=1.5), (
                f"Страница прокрутилась: scrollY {start} → {page.get_scroll_y()}"
            )
        page.scroll_by_keys()
        with allure.step("После PageDown и End позиция страницы не изменилась"):
            assert not page.wait_scroll_changed(start, timeout=1.5), (
                f"Страница прокрутилась: scrollY {start} → {page.get_scroll_y()}"
            )
        with allure.step("Реклама всё ещё открыта"):
            assert page.is_ad_visible(timeout=1)

        page.close_ad()
        check_ad_closed(page)
        page.scroll_by_wheel(600)
        with allure.step("Контроль: после закрытия рекламы страница прокручивается"):
            assert page.wait_scroll_changed(start, timeout=3), (
                "Страница не прокручивается и после закрытия"
            )
