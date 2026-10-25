"""Тесты страницы Modals: https://practice-automation.com/modals/"""

import allure
import pytest

from pages.modals_page import ModalsPage

pytestmark = [pytest.mark.modals]

SIMPLE_TITLE = "Simple Modal"
SIMPLE_TEXT = "Hi, I’m a simple modal."
FORM_TITLE = "Modal Containing A Form"
FORM_INTRO = "Please enter your contact info below."

NAME = "Autotest User"
EMAIL = "autotest.user@example.com"
MESSAGE = "Autotest message: проверка отправки формы из модального окна."

REQUIRED_ERROR = "This field is required."
EMAIL_ERROR = "Please enter a valid email address"


@pytest.fixture
def page(driver) -> ModalsPage:
    return ModalsPage(driver).open()


def check_closed(page: ModalsPage, kind: str) -> None:
    with allure.step(f"Окно «{page.name_of(kind)}» и затемнение скрыты, кнопки страницы доступны"):
        assert page.wait_modal_closed(kind), f"Окно «{page.name_of(kind)}» не закрылось"
        assert page.is_trigger_clickable("simple") and page.is_trigger_clickable("form"), (
            "Кнопки страницы недоступны после закрытия окна"
        )


# ==========================================================================
# Simple Modal
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Модальные окна")
@allure.story("Simple Modal")
class TestSimpleModal:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title(
        "Страница открывается: заголовок и кнопки «Simple Modal», «Form Modal»; окна скрыты"
    )
    def test_page_initial_state(self, page):
        """Цель: убедиться, что страница загружается в исходном состоянии — кнопки
        вызова окон на месте и ни одно окно не открыто само.

        Ожидаемый результат: есть заголовок «Modals» и кнопки «Simple Modal»
        и «Form Modal»; оба модальных окна скрыты.
        """
        with allure.step("Заголовок «Modals» и обе кнопки видны"):
            assert page.is_heading_visible(), "Заголовок 'Modals' не отображается"
            assert page.get_trigger_text("simple") == "Simple Modal"
            assert page.get_trigger_text("form") == "Form Modal"
        with allure.step("Оба модальных окна скрыты"):
            assert not page.is_modal_open("simple", timeout=1), "Simple Modal открыто при загрузке"
            assert not page.is_modal_open("form", timeout=1), "Form Modal открыто при загрузке"

    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(
        "Кнопка «Simple Modal» открывает окно с затемнением, заголовком, текстом и кнопкой «×»"
    )
    def test_simple_modal_opens(self, page):
        """Цель: проверить, что кнопка «Simple Modal» открывает именно своё окно
        с правильным содержимым и средством закрытия.

        Ожидаемый результат: видны затемнение и окно с заголовком «Simple Modal»,
        текстом «Hi, I’m a simple modal.» и кнопкой «×» (aria-label «Close»);
        второе окно (Form Modal) при этом не открывается.
        """
        page.open_modal("simple")
        with allure.step("Затемнение и окно видны"):
            assert page.is_overlay_visible("simple")
            assert page.is_modal_open("simple")
        with allure.step(f"Заголовок «{SIMPLE_TITLE}», текст «{SIMPLE_TEXT}»"):
            assert page.get_modal_title("simple") == SIMPLE_TITLE
            assert page.get_modal_text("simple") == SIMPLE_TEXT
        with allure.step("Кнопка закрытия «×» видна"):
            assert page.is_close_button_visible("simple")
            assert page.get_close_button_label("simple") == "Close"
        with allure.step("Form Modal при этом не открылось"):
            assert not page.is_modal_open("form", timeout=0.5)

    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Simple Modal закрывается кнопкой «×»")
    def test_simple_modal_closes_by_x(self, page):
        """Цель: проверить единственный разрешённый настройками способ закрыть
        Simple Modal — кнопку «×».

        Ожидаемый результат: окно и затемнение скрываются, обе кнопки страницы
        снова доступны для клика (затемнение их не перекрывает).
        """
        page.open_modal("simple").close_by_x("simple")
        check_closed(page, "simple")


# ==========================================================================
# Form Modal
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Модальные окна")
@allure.story("Form Modal")
class TestFormModal:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(
        "Кнопка «Form Modal» открывает окно с формой: Name (required), Email, Message, Submit"
    )
    def test_form_modal_opens(self, page):
        """Цель: проверить, что кнопка «Form Modal» открывает окно с формой
        обратной связи и всеми её полями.

        Ожидаемый результат: окно с заголовком «Modal Containing A Form» и текстом
        «Please enter your contact info below.»; видны поля Name (с пометкой
        «(required)»), Email, Message и кнопка Submit; Simple Modal не открывается.
        """
        page.open_modal("form")
        with allure.step(f"Заголовок «{FORM_TITLE}», вводный текст"):
            assert page.get_modal_title("form") == FORM_TITLE
            assert FORM_INTRO in page.get_modal_text("form")
        with allure.step("Поля Name, Email, Message и кнопка Submit видны"):
            visible = page.are_form_fields_visible()
            assert all(visible.values()), f"Не видны: {[k for k, v in visible.items() if not v]}"
        with allure.step("Поле Name помечено как обязательное"):
            assert "(required)" in page.get_name_label()
        with allure.step("Simple Modal при этом не открылось"):
            assert not page.is_modal_open("simple", timeout=0.5)

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Form Modal закрывается кнопкой «×»")
    def test_form_modal_closes_by_x(self, page):
        """Цель: проверить закрытие Form Modal кнопкой «×».

        Ожидаемый результат: окно и затемнение скрываются, кнопки страницы снова
        доступны для клика.
        """
        page.open_modal("form").close_by_x("form")
        check_closed(page, "form")

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Form Modal закрывается клавишей Esc")
    def test_form_modal_closes_by_escape(self, page):
        """Цель: проверить закрытие Form Modal клавишей Esc — для этого окна
        она включена в настройках (esc_press), в отличие от Simple Modal.

        Ожидаемый результат: после нажатия Esc окно и затемнение скрываются,
        кнопки страницы снова доступны.
        """
        page.open_modal("form").press_escape()
        check_closed(page, "form")

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Окна открываются и закрываются поочерёдно 3 раза подряд с правильным содержимым")
    def test_modals_reopen_cycle(self, page):
        """Цель: убедиться, что окна можно открывать и закрывать многократно и они
        не мешают друг другу — состояние после закрытия не «залипает».

        Ожидаемый результат: в каждом из трёх циклов открывается нужное окно
        с правильным заголовком, второе окно остаётся скрытым, после «×» окно
        закрывается.
        """
        for i in range(1, 4):
            with allure.step(f"Цикл {i}: Simple Modal"):
                page.open_modal("simple")
                assert page.get_modal_title("simple") == SIMPLE_TITLE
                assert not page.is_modal_open("form", timeout=0.3)
                page.close_by_x("simple")
                assert page.wait_modal_closed("simple")
            with allure.step(f"Цикл {i}: Form Modal"):
                page.open_modal("form")
                assert page.get_modal_title("form") == FORM_TITLE
                assert not page.is_modal_open("simple", timeout=0.3)
                page.close_by_x("form")
                assert page.wait_modal_closed("form")


# ==========================================================================
# Мобильный экран
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Модальные окна")
@allure.story("Мобильный экран")
class TestModalsMobile:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title(
        "Мобильный экран 375×812: оба окна помещаются по ширине, всё содержимое доступно, закрываются «×»"
    )
    def test_modals_on_mobile_viewport(self, driver):
        """Цель: проверить, что модальные окна пригодны для использования на
        экране смартфона — адаптивная вёрстка Popup Maker растягивает окна
        почти на всю ширину экрана.

        Ожидаемый результат: Simple Modal целиком помещается в экран, его
        содержимое и «×» видны, окно закрывается. Form Modal помещается по
        ширине без горизонтальной прокрутки страницы, «×» в видимой области,
        поля формы видны, а кнопка Submit становится видимой после прокрутки
        к ней (форма выше экрана — по высоте окно прокручивается); окно
        закрывается «×». В Chrome/Edge экран эмулируется, в Firefox меняется
        размер окна; фактический размер и границы окон — во вложениях.
        """
        page = ModalsPage(driver)
        page.set_viewport(375, 812)
        page.open()
        width, height = page.get_viewport()
        allure.attach(
            f"{width}×{height}",
            name="Фактический размер видимой области",
            attachment_type=allure.attachment_type.TEXT,
        )
        errors = []

        try:
            with allure.step("Simple Modal на мобильном экране"):
                page.open_modal("simple")
                allure.attach(
                    str(page.get_rect(page.container("simple"))),
                    name="Границы Simple Modal",
                    attachment_type=allure.attachment_type.TEXT,
                )
                assert page.is_inside_viewport(page.container("simple")), (
                    "Simple Modal не помещается в экран"
                )
                assert page.get_modal_title("simple") == SIMPLE_TITLE
                assert page.get_modal_text("simple") == SIMPLE_TEXT
                assert page.is_inside_viewport(page.close_button("simple")), "Кнопка «×» вне экрана"
                page.close_by_x("simple")
                assert page.wait_modal_closed("simple"), "Simple Modal не закрылось"
        except AssertionError as exc:
            errors.append(f"Simple Modal: {exc}")

        try:
            with allure.step("Form Modal на мобильном экране"):
                page.open_modal("form")
                allure.attach(
                    str(page.get_rect(page.container("form"))),
                    name="Границы Form Modal",
                    attachment_type=allure.attachment_type.TEXT,
                )
                with allure.step("Окно помещается по ширине, горизонтальной прокрутки нет"):
                    assert page.is_inside_viewport(page.container("form"), horizontal_only=True), (
                        "Form Modal шире экрана"
                    )
                    assert not page.has_horizontal_scroll(), (
                        "У страницы появилась горизонтальная прокрутка"
                    )
                with allure.step("Кнопка «×» в видимой области"):
                    assert page.is_inside_viewport(page.close_button("form")), (
                        "Кнопка «×» вне экрана"
                    )
                with allure.step("Поля Name, Email, Message видны"):
                    visible = page.are_form_fields_visible()
                    assert all(visible[k] for k in ("Name", "Email", "Message")), (
                        f"Не видны: {[k for k, v in visible.items() if not v]}"
                    )
                with allure.step("После прокрутки к Submit кнопка в видимой области"):
                    page.scroll_into_view(page.SUBMIT)
                    assert page.is_inside_viewport(page.SUBMIT), "Кнопка Submit недоступна"
                page.close_by_x("form")
                assert page.wait_modal_closed("form"), "Form Modal не закрылось"
        except AssertionError as exc:
            errors.append(f"Form Modal: {exc}")

        assert not errors, "Проблемы на мобильном экране:\n" + "\n".join(errors)


# ==========================================================================
# Отправка формы
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Модальные окна")
@allure.story("Отправка формы")
class TestFormSubmit:
    @pytest.mark.positive
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title(
        "Форма со всеми заполненными полями отправляется: «Thank you for your response» с данными"
    )
    def test_submit_all_fields(self, page):
        """Цель: проверить основной сценарий формы — отправку полностью
        заполненных данных из модального окна.

        Ожидаемый результат: в окне появляется «Thank you for your response»,
        в подтверждении есть введённые Name, Email и Message.
        """
        page.open_modal("form").fill_form(NAME, EMAIL, MESSAGE).submit_form()
        with allure.step("В окне сообщение об успехе с введёнными данными"):
            assert page.is_success_visible(), "Нет сообщения «Thank you for your response»"
            text = page.get_success_text()
            assert "Thank you for your response" in text
            for value in (NAME, EMAIL, MESSAGE):
                assert value in text, f"В ответе нет «{value}»"

    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(
        "Форма только с обязательным полем Name отправляется (Email и Message необязательны)"
    )
    def test_submit_only_required(self, page):
        """Цель: убедиться, что для отправки достаточно единственного
        обязательного поля — Email и Message необязательны.

        Ожидаемый результат: форма с заполненным только Name отправляется,
        в подтверждении есть введённое имя.
        """
        page.open_modal("form").fill_form(name=NAME).submit_form()
        with allure.step("Сообщение об успехе с именем"):
            assert page.is_success_visible(), "Нет сообщения «Thank you for your response»"
            assert NAME in page.get_success_text()


# ==========================================================================
# Негативные
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("Модальные окна")
@allure.story("Негативные сценарии")
class TestModalsNegative:
    @pytest.mark.negative
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Клик по затемнению вне окна не закрывает ни Simple Modal, ни Form Modal")
    def test_overlay_click_does_not_close(self, page):
        """Цель: проверить, что клик по затемнению вокруг окна не закрывает
        ни одно из окон — в настройках обоих окон это отключено (overlay_click).

        Ожидаемый результат: после клика по затемнению вне окна и Simple Modal,
        и Form Modal остаются открытыми.
        """
        for kind in ("simple", "form"):
            with allure.step(
                f"«{page.name_of(kind)}»: клик по затемнению — окно остаётся открытым"
            ):
                page.open_modal(kind).click_overlay(kind)
                assert not page.wait_modal_closed(kind, timeout=1.5), (
                    f"Окно «{page.name_of(kind)}» закрылось по клику на затемнение"
                )
                page.close_by_x(kind)
                assert page.wait_modal_closed(kind)

    @pytest.mark.negative
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Форма без Name не отправляется: «This field is required.»")
    def test_submit_without_name(self, page):
        """Цель: проверить обязательность поля Name — форма без него не должна
        отправляться, даже если остальные поля заполнены.

        Ожидаемый результат: под полем Name ошибка «This field is required.»,
        сообщения об успешной отправке нет.
        """
        page.open_modal("form").fill_form(email=EMAIL, message=MESSAGE).submit_form()
        with allure.step(f"Под полем Name ошибка «{REQUIRED_ERROR}», успеха нет"):
            assert page.get_field_error("name") == REQUIRED_ERROR
            assert not page.is_success_visible(timeout=2), "Форма без Name отправилась"

    @pytest.mark.negative
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "bad_email",
        ["abc", "user@", "@mail.ru", "user mail@example.com"],
        ids=["no_at", "no_domain", "no_local_part", "space_inside"],
    )
    @allure.title(
        "Некорректный Email «{bad_email}» не отправляется: «Please enter a valid email address»"
    )
    def test_submit_invalid_email(self, page, bad_email):
        """Цель: проверить валидацию формата Email. Тест параметризован
        некорректными адресами: без «@», без домена, без имени, с пробелом.

        Ожидаемый результат: под полем Email ошибка «Please enter a valid email
        address», сообщения об успешной отправке нет.
        """
        page.open_modal("form").fill_form(name=NAME, email=bad_email).submit_form()
        with allure.step(f"Под полем Email ошибка «{EMAIL_ERROR}», успеха нет"):
            assert page.get_field_error("email") == EMAIL_ERROR
            assert not page.is_success_visible(timeout=2), (
                f"Форма с Email «{bad_email}» отправилась"
            )

    @pytest.mark.negative
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Name из одних пробелов не считается заполненным: форма не отправляется")
    def test_submit_whitespace_name(self, page):
        """Цель: убедиться, что Name из одних пробелов не считается заполненным —
        частый дефект валидации обязательных полей.

        Ожидаемый результат: под полем Name ошибка «This field is required.»,
        сообщения об успешной отправке нет.
        """
        page.open_modal("form").fill_form(name="     ", email=EMAIL).submit_form()
        with allure.step("Под полем Name ошибка обязательного поля, успеха нет"):
            assert page.get_field_error("name") == REQUIRED_ERROR
            assert not page.is_success_visible(timeout=2), "Форма с Name из пробелов отправилась"

    @pytest.mark.negative
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.xfail(
        reason="Известный дефект: поле Message растягивается мышью за правую границу "
        "модального окна (размер textarea не ограничен шириной окна)",
        strict=False,
    )
    @allure.title("Поле Message нельзя растянуть за пределы окна Form Modal")
    def test_message_resize_stays_inside_modal(self, page):
        """Цель: проверить, что поле Message, которое пользователь может растягивать
        мышью за уголок, не выходит за границы модального окна — иначе вёрстка
        окна ломается, часть поля оказывается поверх затемнения.

        Ожидаемый результат: после попытки растянуть поле на 600 px вправо его
        правая граница не выходит за правую границу окна Form Modal.
        Тест помечен xfail — дефект воспроизводится вручную на десктопе.
        """
        page.open_modal("form")
        resize = page.get_message_resize_style()
        before = page.get_rect(page.MESSAGE)
        page.drag_message_resize_handle(600)
        after = page.get_rect(page.MESSAGE)
        modal = page.get_rect(page.container("form"))
        allure.attach(
            f"resize: {resize}\nMessage до: {before}\nMessage после: {after}\nОкно Form Modal: {modal}",
            name="Размеры поля и окна",
            attachment_type=allure.attachment_type.TEXT,
        )
        with allure.step(
            f"Растяжка сработала — ширина поля изменилась ({before['width']} → {after['width']})"
        ):
            assert after["width"] > before["width"], (
                f"Уголок не потянулся: ширина {before['width']} → {after['width']} "
                f"(resize: {resize}) — проверка невозможна"
            )
        with allure.step(
            f"Правая граница поля ({after['right']}) не дальше правой границы окна ({modal['right']})"
        ):
            assert after["right"] <= modal["right"], (
                f"Поле Message вышло за окно на {after['right'] - modal['right']:.0f} px"
            )
