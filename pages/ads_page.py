"""Page Object страницы https://practice-automation.com/ads/

Рекламное окно плагина Popup Maker:

    затемнение #pum-1272 → окно #popmake-1272
        заголовок #pum_popup_title_1272  «Hi»
        содержимое .pum-content          «I am an ad.»
        кнопка .pum-close                «×» (aria-label="Close")

Настройки (data-popmake):
    auto_open, delay 4500 мс — окно открывается само после загрузки страницы;
    cookie нет              — после перезагрузки окно показывается снова;
    закрытие только «×»     — esc_press: false, overlay_click: false;
    анимация fade 650 мс.
Пока окно открыто, у <html> есть классы pum-open / pum-open-overlay.
"""
import time

import allure
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class AdsPage(BasePage):
    PATH = "/ads/"

    AD_DELAY = 4.5          # задержка auto_open из настроек попапа, с
    AD_WAIT_TIMEOUT = 12    # с запасом на загрузку страницы и анимацию

    HEADING = (By.XPATH, "//h1[normalize-space()='Ads']")
    COUNTDOWN = (By.XPATH, "//p[contains(normalize-space(.), 'An ad will appear in')]")
    LINK = (By.PARTIAL_LINK_TEXT, "how to handle ads")

    OVERLAY = (By.ID, "pum-1272")
    AD = (By.ID, "popmake-1272")
    AD_TITLE = (By.ID, "pum_popup_title_1272")
    AD_CONTENT = (By.CSS_SELECTOR, "#popmake-1272 .pum-content")
    AD_CLOSE = (By.CSS_SELECTOR, "#popmake-1272 .pum-close")

    loaded_at: float = 0.0

    # ========================================================================
    # Загрузка и окно браузера
    # ========================================================================
    def open(self):
        super().open()
        self.loaded_at = time.monotonic()
        return self

    @allure.step("Перезагрузить страницу")
    def reload(self):
        self.driver.refresh()
        self.loaded_at = time.monotonic()
        return self

    def seconds_since_load(self) -> float:
        return time.monotonic() - self.loaded_at

    def set_viewport(self, width: int, height: int) -> tuple[int, int]:
        """Размер видимой области. Chrome/Edge — эмуляция устройства через CDP
        (окно браузера уже ~500 px сделать нельзя), Firefox — размер окна.
        Возвращает фактические window.innerWidth / innerHeight."""
        with allure.step(f"Установить размер экрана {width}×{height}"):
            if hasattr(self.driver, "execute_cdp_cmd"):
                self.driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": width, "height": height, "deviceScaleFactor": 1, "mobile": True,
                })
            else:
                self.driver.set_window_size(width, height)
        return self.get_viewport()

    def get_viewport(self) -> tuple[int, int]:
        w, h = self.driver.execute_script("return [window.innerWidth, window.innerHeight];")
        return int(w), int(h)

    # ========================================================================
    # Содержимое страницы
    # ========================================================================
    def is_heading_visible(self) -> bool:
        return self.is_visible(self.HEADING)

    def get_countdown_text(self) -> str:
        return self.get_text(self.COUNTDOWN)

    def is_link_visible(self) -> bool:
        return self.is_visible(self.LINK)

    def is_link_reachable(self) -> bool:
        """Находится ли в точке центра ссылки сама ссылка (а не затемнение)."""
        link = self.driver.find_element(*self.LINK)
        return self.driver.execute_script(
            """
            const link = arguments[0];
            link.scrollIntoView({block: 'center'});
            const r = link.getBoundingClientRect();
            const el = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
            return el === link || link.contains(el);
            """,
            link,
        )

    def click_link_by_coordinates(self) -> None:
        """Реальный клик мышью в точку ссылки (без проверок Selenium на перекрытие)."""
        with allure.step("Кликнуть мышью в точку ссылки «how to handle ads in test automation»"):
            link = self.driver.find_element(*self.LINK)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
            ActionChains(self.driver).move_to_element(link).click().perform()

    # ========================================================================
    # Рекламное окно
    # ========================================================================
    def is_ad_visible(self, timeout: float = 3) -> bool:
        return self.is_visible(self.AD, timeout)

    def wait_for_ad(self, timeout: float | None = None) -> float:
        """Ждёт появления рекламы; возвращает время с момента загрузки страницы, с."""
        with allure.step("Дождаться автоматического появления рекламы"):
            self.find_visible(self.AD, self.AD_WAIT_TIMEOUT if timeout is None else timeout)
            elapsed = self.seconds_since_load()
            allure.attach(f"{elapsed:.2f} с после загрузки страницы (задержка в настройках {self.AD_DELAY} с)",
                          name="Время появления рекламы", attachment_type=allure.attachment_type.TEXT)
        return elapsed

    def is_ad_absent_until(self, seconds_after_load: float) -> bool:
        """True, если реклама НЕ появилась до указанной секунды после загрузки."""
        remaining = seconds_after_load - self.seconds_since_load()
        if remaining <= 0:
            return not self.is_ad_visible(timeout=0)
        return not self.is_ad_visible(timeout=remaining)

    def wait_ad_hidden(self, timeout: float = 5) -> bool:
        return self.wait_invisible(self.OVERLAY, timeout)

    def is_overlay_visible(self) -> bool:
        return self.is_visible(self.OVERLAY, timeout=1)

    def get_ad_title(self) -> str:
        return self.get_text(self.AD_TITLE)

    def get_ad_text(self) -> str:
        return self.get_text(self.AD_CONTENT)

    def get_close_label(self) -> str:
        return self.find(self.AD_CLOSE).get_attribute("aria-label") or ""

    def get_dialog_attributes(self, timeout: float = 3) -> dict[str, str]:
        """role и aria-modal окна. Popup Maker выставляет aria-modal="true" после
        завершения анимации открытия, поэтому сначала ждём это значение."""
        overlay = self.driver.find_element(*self.OVERLAY)
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda _: overlay.get_attribute("aria-modal") == "true")
        except TimeoutException:
            pass  # вернём фактическое значение — тест покажет расхождение
        return {"role": overlay.get_attribute("role"), "aria-modal": overlay.get_attribute("aria-modal")}

    def is_html_marked_open(self) -> bool:
        classes = self.driver.find_element(By.TAG_NAME, "html").get_attribute("class") or ""
        return "pum-open" in classes.split()

    def is_ad_inside_viewport(self) -> bool:
        ad = self.find(self.AD)
        rect = self.driver.execute_script(
            """
            const r = arguments[0].getBoundingClientRect();
            return {top: r.top, left: r.left, bottom: r.bottom, right: r.right,
                    vw: window.innerWidth, vh: window.innerHeight};
            """,
            ad,
        )
        allure.attach(str({k: round(v) for k, v in rect.items()}), name="Положение окна рекламы",
                      attachment_type=allure.attachment_type.TEXT)
        return (rect["top"] >= 0 and rect["left"] >= 0
                and rect["bottom"] <= rect["vh"] and rect["right"] <= rect["vw"])

    # ========================================================================
    # Прокрутка страницы
    # ========================================================================
    def set_window_size(self, width: int, height: int):
        with allure.step(f"Установить размер окна браузера {width}×{height}"):
            self.driver.set_window_size(width, height)
        return self

    def get_scroll_y(self) -> float:
        return float(self.driver.execute_script("return window.scrollY;"))

    def get_html_overflow(self) -> str:
        """Вычисленный overflow-y у <html>: Popup Maker ставит hidden, пока окно открыто."""
        return self.driver.execute_script(
            "return getComputedStyle(document.documentElement).overflowY;")

    def is_page_scrollable(self) -> bool:
        return bool(self.driver.execute_script(
            "return document.documentElement.scrollHeight > window.innerHeight;"))

    def scroll_by_wheel(self, pixels: int = 600):
        with allure.step(f"Прокрутить колесом мыши на {pixels} px"):
            ActionChains(self.driver).scroll_by_amount(0, pixels).perform()
        return self

    def scroll_by_keys(self):
        with allure.step("Нажать PageDown и End"):
            ActionChains(self.driver).send_keys(Keys.PAGE_DOWN).pause(0.3).send_keys(Keys.END).perform()
        return self

    def wait_scroll_changed(self, from_y: float, timeout: float = 2) -> bool:
        """True, если позиция прокрутки страницы ушла с from_y за timeout секунд."""
        try:
            WebDriverWait(self.driver, timeout, poll_frequency=0.2).until(
                lambda _: abs(self.get_scroll_y() - from_y) > 1)
            return True
        except TimeoutException:
            return False

    @allure.step("Закрыть рекламу кнопкой «×»")
    def close_ad(self):
        self.click(self.AD_CLOSE)
        return self

    @allure.step("Нажать Esc")
    def press_escape(self):
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        return self

    @allure.step("Кликнуть по затемнению вне окна рекламы (левый верхний угол экрана)")
    def click_overlay(self):
        overlay = self.find(self.OVERLAY)
        size = overlay.size
        ActionChains(self.driver).move_to_element_with_offset(
            overlay, -size["width"] // 2 + 20, -size["height"] // 2 + 20
        ).click().perform()
        return self
