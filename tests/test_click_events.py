"""Тесты страницы Click Events: https://practice-automation.com/click-events/"""
import allure
import pytest
from selenium.webdriver.common.keys import Keys

from pages.click_events_page import ANIMAL_SOUNDS, ClickEventsPage

pytestmark = [pytest.mark.click_events]

ANIMALS = list(ANIMAL_SOUNDS)


@pytest.fixture
def page(driver) -> ClickEventsPage:
    return ClickEventsPage(driver).open()


def check_result(page: ClickEventsPage, expected: str) -> None:
    with allure.step(f"В поле результата «{expected}»" if expected else "Поле результата пустое"):
        assert page.wait_result(expected), f"В поле результата «{page.get_result()}», ожидалось «{expected}»"


# ==========================================================================
# Позитивные
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("События (Click Events)")
@allure.story("Клики по кнопкам")
class TestClickEvents:

    @pytest.mark.positive
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Страница открывается: 4 кнопки Cat, Dog, Pig, Cow; поле результата пустое")
    def test_page_initial_state(self, page):
        """Цель: убедиться, что страница загружается в исходном состоянии — все
        кнопки на месте и никакой звук ещё не выведен.

        Ожидаемый результат: есть заголовок «Click Events» и описание; кнопки
        Cat, Dog, Pig, Cow расположены в этом порядке; поле результата пустое.
        """
        with allure.step("Заголовок и описание видны"):
            assert page.is_heading_visible(), "Заголовок 'Click Events' не отображается"
            assert page.is_description_visible()
        with allure.step(f"Кнопки по порядку: {', '.join(ANIMALS)}"):
            assert page.get_button_texts() == ANIMALS
        check_result(page, "")

    @pytest.mark.positive
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("animal", ANIMALS, ids=[a.lower() for a in ANIMALS])
    @allure.title("Клик по «{animal}» показывает звук животного")
    def test_click_shows_sound(self, page, animal):
        """Цель: проверить, что каждая кнопка-животное выводит свой звук —
        основная функция страницы. Тест параметризован по всем четырём кнопкам.

        Ожидаемый результат: после клика в поле результата текст, соответствующий
        кнопке: Cat — «Meow!», Dog — «Woof!», Pig — «Oink!», Cow — «Moo!».
        """
        page.click_animal(animal)
        check_result(page, ANIMAL_SOUNDS[animal])

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Клики подряд в разном порядке: текст каждый раз заменяется, а не дописывается")
    def test_sequence_overwrites_result(self, page):
        """Цель: убедиться, что при кликах по разным кнопкам подряд результат
        каждый раз заменяется, а не накапливается.

        Ожидаемый результат: после каждого клика в поле ровно один звук — звук
        последней нажатой кнопки, без остатков предыдущих.
        """
        for animal in ["Cow", "Cat", "Pig", "Dog", "Cat"]:
            page.click_animal(animal)
            check_result(page, ANIMAL_SOUNDS[animal])

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Повторный и двойной клик по той же кнопке: тот же текст без дублей")
    def test_repeated_clicks_same_result(self, page):
        """Цель: проверить, что многократное нажатие одной и той же кнопки
        (в том числе двойной клик) не дублирует и не искажает результат.

        Ожидаемый результат: после трёх кликов по Dog — ровно «Woof!»; после
        двойного клика по Pig — ровно «Oink!».
        """
        with allure.step("Три одиночных клика по «Dog»"):
            for _ in range(3):
                page.click_animal("Dog")
            check_result(page, "Woof!")
        page.double_click_animal("Pig")
        check_result(page, "Oink!")

    @pytest.mark.positive
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Кнопки срабатывают с клавиатуры: Enter и Space")
    def test_keyboard_activation(self, page):
        """Цель: убедиться, что кнопками можно пользоваться с клавиатуры —
        важно для доступности (пользователи без мыши).

        Ожидаемый результат: Enter при фокусе на Cow выводит «Moo!», Space при
        фокусе на Cat выводит «Meow!».
        """
        page.press_key_on_animal("Cow", Keys.ENTER)
        check_result(page, "Moo!")
        page.press_key_on_animal("Cat", Keys.SPACE)
        check_result(page, "Meow!")

    @pytest.mark.positive
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("После перезагрузки страницы поле результата снова пустое")
    def test_result_reset_after_reload(self, page):
        """Цель: проверить, что результат не сохраняется между загрузками
        страницы — это состояние только текущего просмотра.

        Ожидаемый результат: после клика по Pig выводится «Oink!»; после
        перезагрузки страницы поле результата снова пустое.
        """
        page.click_animal("Pig")
        check_result(page, "Oink!")
        page.reload()
        check_result(page, "")


# ==========================================================================
# Негативные
# ==========================================================================
@allure.epic("practice-automation.com")
@allure.feature("События (Click Events)")
@allure.story("Негативные сценарии")
class TestClickEventsNegative:

    @pytest.mark.negative
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Наведение курсора без клика не показывает звук")
    def test_hover_does_not_trigger(self, page):
        """Цель: убедиться, что звук выводится только по клику, а не при простом
        наведении курсора на кнопку.

        Ожидаемый результат: после наведения курсора поочерёдно на все четыре
        кнопки поле результата остаётся пустым.
        """
        for animal in ANIMALS:
            page.hover_animal(animal)
        check_result(page, "")

    @pytest.mark.negative
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Клик по заголовку и описанию (не по кнопкам) не меняет результат")
    def test_click_outside_buttons(self, page):
        """Цель: проверить, что клики по другим элементам страницы (заголовок,
        описание) не влияют на результат — реагируют только кнопки.

        Ожидаемый результат: без выбранного животного поле остаётся пустым; после
        выбора Cat клики вне кнопок не меняют «Meow!».
        """
        with allure.step("Без выбранного животного результат остаётся пустым"):
            page.click_non_buttons()
            check_result(page, "")
        with allure.step("После «Cat» клики вне кнопок не меняют «Meow!»"):
            page.click_animal("Cat")
            page.click_non_buttons()
            check_result(page, "Meow!")

    @pytest.mark.negative
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Нажатие мыши на кнопке и отпускание вне её не засчитывается как клик")
    def test_press_and_release_outside(self, page):
        """Цель: проверить, что незавершённое нажатие не засчитывается как клик:
        пользователь зажал кнопку мыши на кнопке, но передумал и отпустил её
        в другом месте.

        Ожидаемый результат: при нажатии на Dog и отпускании на заголовке звук
        не выводится, поле результата остаётся пустым.
        """
        page.press_and_release_outside("Dog")
        check_result(page, "")
