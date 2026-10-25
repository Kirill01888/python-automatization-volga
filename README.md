#Автоматизация тестирования (Java, Python) Волга-IT 2026

# UI-автотесты practice-automation.com

UI-автотесты для шести страниц с упражнениями https://practice-automation.com/:
Python 3.12+, Selenium 4, Pytest, Allure, паттерн Page Object.

## Быстрый старт
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
pytest --browser=chrome,firefox -n 4
```
Драйверы (и при отсутствии — сам Chrome/Firefox) Selenium Manager скачает автоматически,
ручная настройка не нужна. Если PowerShell не даёт активировать окружение, один раз выполните
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

### Параметры запуска
| Команда | Что делает |
|---|---|
| `pytest` | все тесты в Chrome (браузер по умолчанию) |
| `pytest --browser=firefox` | запуск в Firefox |
| `pytest --browser=chrome,firefox` | в нескольких браузерах; `--browser=all` — Chrome + Firefox + Edge |
| `pytest -n 4` | параллельно в 4 процесса (pytest-xdist) |
| `pytest --headless` | без окна браузера |
| `pytest -v` | построчный вывод с результатом каждого теста |
| `pytest -m ads` | только одна страница: `calendars`, `modals`, `ads`, `click_events`, `popups`, `forms` |
| `pytest -m negative` / `-m positive` | только негативные / позитивные тесты |

Перед каждым тестом в консоль выводится его название: `▶ <название из Allure> [браузер]`
(с `-n` — технический id теста в момент, когда воркер берёт его в работу).

Рекомендации:
- **Число воркеров — 3–4, а не `-n auto`.** Каждый воркер — отдельный браузер; при перегрузке машины
  тесты с ожиданием по времени (реклама через 4,5 с, анимации окон, подсказка) становятся нестабильными.
- Если браузер на машине не запускается, его тесты помечаются как skipped с причиной.
- Тесты Modals и Calendars реально отправляют формы Jetpack на сайт (данные «Autotest User»);
  Form Fields на сервер ничего не отправляет. Полный прогон в двух браузерах занимает ~6–10 минут.

### Allure-отчёт
Результаты пишутся в `allure-results/` (папка очищается при каждом запуске). Для просмотра нужен
Allure CLI и Java 8+ (Windows: `scoop install allure`, macOS: `brew install allure`):
```bash
allure serve allure-results                                  # собрать и открыть отчёт
allure generate allure-results -o allure-report --clean      # или сохранить отчёт в папку
```
Что есть в отчёте:
- **Suites:** страница → Позитивные / Негативные → группа сценариев; **Behaviors:** страница → группа сценариев.
- Названия тестов и шагов на русском, браузер в параметрах; у тестов страниц Modals, Ads, Click Events, Popups и Form Fields — описание цели и ожидаемого результата.
- При падении — скриншот и URL страницы.
- Полезные вложения и при успехе: время появления рекламы, фактический размер экрана и границы окон
  в мобильных тестах, список Automation tools, скриншоты фокуса на дне календаря при переходе «±1 день».
- Известные дефекты помечены `xfail` с описанием — видны в отчёте, но не делают прогон красным.
- Версии браузеров, ОС и Python — на вкладке Environment.

## Структура
```
config.py            базовый URL, таймауты, размер окна
conftest.py          фикстура driver, опции --browser/--headless, вывод «▶ название», группы Allure,
                     скриншот и URL при падении, environment.properties
core/browsers.py     фабрика браузеров (Chrome, Firefox, Edge) через Selenium Manager
pages/               Page Object: base_page.py (ожидания, клики, диалоги, экран) + по классу на страницу
tests/               тесты, по файлу на страницу
pytest.ini           маркеры и параметры Allure
pyproject.toml       настройки Ruff (линтер и форматтер)
requirements.txt     зависимости для запуска тестов
requirements-dev.txt зависимости для разработки (requirements.txt + Ruff)
```

## Линтер и форматтер
Для проверки и форматирования кода используется [Ruff](https://docs.astral.sh/ruff/) — он заменяет
flake8, isort, pyupgrade и black. Настройки — в `pyproject.toml`: длина строки 100, двойные кавычки,
правила `E`, `W`, `F`, `I` (сортировка импортов), `B`, `UP`, `PT`, `SIM`, `N`, `RUF`
(кириллица в строках и комментариях разрешена).

Ruff ставится вместе с зависимостями для разработки:
```bash
pip install -r requirements-dev.txt
```

| Команда | Что делает |
|---|---|
| `ruff check .` | линтер: показать замечания |
| `ruff check . --fix` | исправить то, что исправляется автоматически (например, порядок импортов) |
| `ruff format .` | отформатировать код |
| `ruff format --check .` | проверить форматирование без изменений (для CI) |
| `ruff format --diff .` | показать, что изменит форматтер |

Перед коммитом:
```bash
ruff check . --fix && ruff format .
```

## Покрытие
| Страница | Позитивные | Негативные | Запусков на браузер |
|---|---|---|---|
| Календарь `/calendars/` | 10 | 3 | 17 |
| Модальные окна `/modals/` | 10 | 5 | 18 |
| Рекламные окна `/ads/` | 9 | 5 | 14 |
| События `/click-events/` | 6 (9 запусков) | 3 | 12 |
| Всплывающие окна `/popups/` | 9 | 3 | 12 |
| Форма `/form-fields/` | 9 | 3 | 13 |
| **Итого** | | | **86** |

Параметризованные тесты (несколько значений одной проверки) считаются одним тестом в таблицах
сценариев и отдельными запусками в отчёте.

## Найденные дефекты
Тесты помечены `xfail` — проверяют правильное поведение и ожидаемо падают, пока дефект не исправлен.

| Страница | Тест | Дефект |
|---|---|---|
| Модальные окна | `test_message_resize_stays_inside_modal` | Поле Message растягивается мышью за правую границу окна Form Modal (на ~370–400 px) |
| Форма | `test_submit_whitespace_name` | Name из одних пробелов принимается: атрибут `required` считает пробелы заполнением |
| Форма | `test_submit_invalid_email` | Email не проверяется по формату: `abc`, `user@` принимаются вопреки подсказке «No fake emails!» |

## Тестовые сценарии

### Календарь — https://practice-automation.com/calendars/
Форма Jetpack: поле даты (формат `YYYY-MM-DD`) и кнопка Submit. По клику на поле открывается
виджет tiny-date-picker: шапка с меню месяца и года и стрелками `<` `>`, сетка из 6 недель
(с понедельника; дни соседних месяцев — бледные), меню месяцев и меню годов (текущий год ±100).
Значение в поле меняется только после клика по дню.

«±1 день» выполняется кликом по бледному дню соседнего месяца (перед кликом на день наводится
фокус, скриншот прикладывается к шагу Allure). Если соседнего дня нет в сетке
(1-е число — понедельник), переходим стрелкой и выбираем день там.
После каждого выбора проверяются: значение поля, месяц/год в шапке и единственный выделенный день в сетке.
В тестах C-6…C-10 ошибки собираются по всем случаям и выводятся одним списком —
падение одного месяца/года не скрывает остальные.

**Запуск:**
```bash
pytest -m calendars --browser=chrome,firefox -n 4     # Chrome и Firefox параллельно
pytest -m calendars -v                                # только Chrome, по одному тесту с выводом названий
```

**Позитивные (10)**
| # | Тест | Сценарий | Ожидаемый результат |
|---|---|---|---|
| C-1 | `test_page_elements` | Открыть страницу | Видны заголовок «Calendars», поле и Submit; подпись «Select or enter a date», под полем `YYYY-MM-DD`; поле пустое |
| C-2 | `test_picker_opens_with_correct_grid` | Кликнуть по полю | Открыт текущий месяц, сегодня отмечено; 42 ячейки, неделя с понедельника, дней месяца — сколько в месяце, бледные дни — соседние месяцы |
| C-3 | `test_arrow_navigation` | `>`, затем `<`, затем `<` | Следующий месяц → исходный → предыдущий |
| C-4 | `test_select_date_by_click` | Выбрать 10-е текущего месяца; пагинацией стрелками на −13 / +2 / +14 мес. выбрать 20-е | В поле выбранная дата `YYYY-MM-DD`, календарь закрылся, выделен этот день |
| C-5 | `test_manual_input_and_submit` | Ввести `2027-03-18` → Submit; заново выбрать в календаре 5-е следующего месяца → Submit | Календарь переключился на March 2027 и подсветил 18-е; оба раза «Thank you for your response» с датой |
| C-6 | `test_month_menu_numbers` | Для каждого из 12 месяцев: меню месяцев → месяц N → 15-е | В меню 12 пунктов `data-month` 0–11 по порядку; в шапке месяц N; в поле `YYYY-NN-15` |
| C-7 | `test_year_picker` | Меню годов; min и max из меню → месяц, день → Submit; min−1 и max+1 вручную → Submit; `9999-12-31` → Submit | Диапазон 1926–2126 без пропусков; все даты выбираются и успешно отправляются (форма не ограничивает год диапазоном виджета) |
| C-8 | `test_month_boundaries` | Месяцы 2026 через один (1, 3, 5, 7, 9, 11): выбрать 1-е; 1-е − 1 день; выбрать последнее; последнее + 1 день | 1-е и последнее не меняют месяц; −1 → последнее число предыдущего (01.01.2026 → 31.12.2025); +1 → 1-е следующего. Через соседние дни покрыты все 12 месяцев |
| C-9 | `test_year_rollover` | 1999, 2024, 2026, 2027, 2099: выбрать 31.12; +1 день; выбрать 01.01; −1 день | 01.01 следующего года и 31.12 предыдущего, включая смену тысячелетия 1999 → 2000 и века 2099 → 2100 (2999 → 3000 вне диапазона виджета 1926–2126) |
| C-10 | `test_leap_years` | Февраль 2024, 2028, 2000 / 2026, 2027, 2100: посчитать дни, выбрать последний, +1 день | 29 дней у високосных (включая 2000), 28 — у остальных (включая 2100); последний день + 1 = 01.03 |

**Негативные (3)**
| # | Тест | Сценарий | Ожидаемый результат |
|---|---|---|---|
| C-N1 | `test_escape_closes_without_value` | Открыть календарь, нажать Esc | Календарь закрыт, поле пустое |
| C-N2 | `test_click_outside_closes_without_value` | Открыть календарь, кликнуть вне его | Календарь закрыт, поле пустое |
| C-N3 | `test_invalid_date_rejected` | Ввести `0001-01-01`, `abc`, `2026-13-01`, `31.12.2026`, `2026-02-31` → Submit (5 параметров) | Форма показывает ошибку, сообщения об успехе нет |


### Модальные окна — https://practice-automation.com/modals/
Две кнопки открывают окна плагина Popup Maker: «Simple Modal» (`#simpleModal` → `#popmake-1318`)
и «Form Modal» (`#formModal` → `#popmake-674`). По настройкам плагина Simple Modal закрывается
только кнопкой «×», Form Modal — «×» и Esc; клик по затемнению не закрывает ни одно окно.
В Form Modal — форма Jetpack: Name (обязательное), Email, Message, Submit.
Тестовые данные отправки: Name «Autotest User», Email `autotest.user@example.com`.

**Запуск:**
```bash
pytest -m modals --browser=chrome,firefox -n 4     # Chrome и Firefox параллельно
pytest -m modals -v                                # только Chrome, по одному тесту с выводом названий
```

**Позитивные (10)**
| # | Тест | Сценарий | Ожидаемый результат |
|---|---|---|---|
| M-1 | `test_page_initial_state` | Открыть страницу | Видны «Modals», кнопки «Simple Modal» и «Form Modal»; оба окна скрыты |
| M-2 | `test_simple_modal_opens` | Нажать «Simple Modal» | Затемнение и окно: заголовок «Simple Modal», текст «Hi, I’m a simple modal.», кнопка «×» (aria-label Close); Form Modal не открыто |
| M-3 | `test_simple_modal_closes_by_x` | Simple Modal → «×» | Окно и затемнение скрыты, кнопки страницы доступны |
| M-4 | `test_form_modal_opens` | Нажать «Form Modal» | Заголовок «Modal Containing A Form», «Please enter your contact info below.», поля Name «(required)», Email, Message, Submit |
| M-5 | `test_form_modal_closes_by_x` | Form Modal → «×» | Окно закрыто, кнопки страницы доступны |
| M-6 | `test_form_modal_closes_by_escape` | Form Modal → Esc | Окно закрыто, кнопки страницы доступны |
| M-7 | `test_modals_reopen_cycle` | 3 раза поочерёдно открыть/закрыть оба окна | Каждый раз открывается нужное окно с правильным заголовком, второе скрыто |
| M-8 | `test_submit_all_fields` | Заполнить Name, Email, Message → Submit | «Thank you for your response», в ответе введённые данные |
| M-9 | `test_submit_only_required` | Заполнить только Name → Submit | Успех — Email и Message необязательны |
| M-10 | `test_modals_on_mobile_viewport` | Экран 375×812 (Chrome/Edge — эмуляция, Firefox — размер окна, минимум ~500 px): открыть и закрыть Simple Modal, затем Form Modal | Simple Modal целиком в экране, содержимое и «×» видны; Form Modal по ширине в экране без горизонтальной прокрутки, «×» видна, поля видны, Submit доступна после прокрутки; оба закрываются «×» |

**Негативные (5)**
| # | Тест | Сценарий | Ожидаемый результат |
|---|---|---|---|
| M-N1 | `test_overlay_click_does_not_close` | Открыть каждое окно, кликнуть по затемнению вне окна | Окна не закрываются |
| M-N2 | `test_submit_without_name` | Email и Message заполнены, Name пустой → Submit | Под Name «This field is required.», успеха нет |
| M-N3 | `test_submit_invalid_email` | Name заполнен, Email `abc`, `user@`, `@mail.ru`, `user mail@example.com` → Submit (4 параметра) | Под Email «Please enter a valid email address», успеха нет |
| M-N4 | `test_submit_whitespace_name` | Name из одних пробелов → Submit | Под Name «This field is required.», успеха нет |
| M-N5 | `test_message_resize_stays_inside_modal` | Открыть Form Modal, потянуть мышью уголок поля Message на 600 px вправо | Поле не должно выходить за правую границу окна. ⚠ **xfail — известный дефект:** поле растягивается за пределы окна |

### Рекламные окна — https://practice-automation.com/ads/
Реклама — окно плагина Popup Maker (`#pum-1272` → `#popmake-1272`): заголовок «Hi», текст «I am an ad.»,
кнопка «×». По настройкам окно открывается **автоматически через 4,5 с** после загрузки, cookie не
используется (после перезагрузки показывается снова), закрывается **только кнопкой «×»** (Esc и клик
по затемнению выключены). Пока окно открыто, у `<html>` есть класс `pum-open`.
Время появления рекламы замеряется и прикладывается к шагу Allure. Доступность ссылки под окном
проверяется через `document.elementFromPoint` — без реального перехода по ссылке.

**Запуск:**
```bash
pytest -m ads --browser=chrome,firefox -n 4     # Chrome и Firefox параллельно
pytest -m ads -v                                # только Chrome, по одному тесту с выводом названий
```

**Позитивные (9)**
| # | Тест | Сценарий | Ожидаемый результат |
|---|---|---|---|
| A-1 | `test_page_initial_state` | Открыть страницу | Заголовок «Ads», текст «An ad will appear in 5…4…3…2…1», ссылка видны; рекламы ещё нет |
| A-2 | `test_ad_appears_automatically` | Ждать после загрузки | Реклама появляется автоматически через 3,5–12 с (по настройкам 4,5 с) |
| A-3 | `test_ad_content` | Проверить окно рекламы | Затемнение, `pum-open` у `<html>`, заголовок «Hi», текст «I am an ad.», «×» (aria-label Close), `role="dialog"`, `aria-modal="true"` |
| A-4 | `test_ad_inside_viewport` | Проверить положение окна | Окно целиком в видимой области экрана |
| A-5 | `test_ad_on_mobile_viewport` | Экран 375×812 (Chrome/Edge — эмуляция устройства, Firefox — размер окна, минимум ~500 px) | Реклама появляется, помещается в экран, закрывается «×» |
| A-6 | `test_close_by_x` | Нажать «×» | Окно и затемнение скрыты, класс `pum-open` снят |
| A-7 | `test_page_reachable_after_close` | Закрыть рекламу, проверить ссылку | В точке ссылки — сама ссылка, перекрытия нет |
| A-8 | `test_no_reappear_without_reload` | Закрыть рекламу и ждать 11 с | Реклама не появляется повторно |
| A-9 | `test_reappears_after_reload` | Закрыть рекламу и перезагрузить страницу | Реклама появляется снова |

**Негативные (5)**
| # | Тест | Сценарий | Ожидаемый результат |
|---|---|---|---|
| A-N1 | `test_ad_not_shown_before_delay` | Наблюдать первые 3,5 с после загрузки | Рекламы нет; затем она появляется |
| A-N2 | `test_escape_does_not_close` | Реклама открыта → Esc | Окно не закрывается |
| A-N3 | `test_overlay_click_does_not_close` | Реклама открыта → клик по затемнению вне окна | Окно не закрывается |
| A-N4 | `test_link_blocked_while_ad_open` | Реклама открыта → клик мышью в точку ссылки | В точке ссылки — затемнение; новая вкладка не открылась, URL не изменился, реклама на месте |
| A-N5 | `test_scroll_blocked_while_ad_open` | Окно 1280×600, реклама открыта → колесо мыши, PageDown, End; затем закрыть рекламу и прокрутить | У `<html>` `overflow-y: hidden`, `scrollY` не меняется, реклама на месте; после закрытия прокрутка работает |

### События — https://practice-automation.com/click-events/
Четыре кнопки с животными; обработчик `onclick` записывает звук в заголовок `h2#demo`:
Cat → «Meow!», Dog → «Woof!», Pig → «Oink!», Cow → «Moo!». У кнопок нет id — локатор по тексту.

**Запуск:**
```bash
pytest -m click_events --browser=chrome,firefox -n 4     # Chrome и Firefox параллельно
pytest -m click_events -v                                # только Chrome, по одному тесту с выводом названий
```

**Позитивные (9 запусков)**
| # | Тест | Сценарий | Ожидаемый результат |
|---|---|---|---|
| E-1 | `test_page_initial_state` | Открыть страницу | Заголовок и описание видны; кнопки Cat, Dog, Pig, Cow по порядку; поле результата пустое |
| E-2…E-5 | `test_click_shows_sound` | Клик по Cat / Dog / Pig / Cow (4 параметра) | «Meow!» / «Woof!» / «Oink!» / «Moo!» |
| E-6 | `test_sequence_overwrites_result` | Клики Cow → Cat → Pig → Dog → Cat | После каждого клика текст заменяется на звук нажатой кнопки, а не дописывается |
| E-7 | `test_repeated_clicks_same_result` | 3 клика по Dog; двойной клик по Pig | «Woof!» и «Oink!» без дублей |
| E-8 | `test_keyboard_activation` | Фокус на Cow + Enter; фокус на Cat + Space | «Moo!», затем «Meow!» |
| E-9 | `test_result_reset_after_reload` | Клик Pig, перезагрузка | После перезагрузки поле результата пустое |

**Негативные (3)**
| # | Тест | Сценарий | Ожидаемый результат |
|---|---|---|---|
| E-N1 | `test_hover_does_not_trigger` | Навести курсор на каждую кнопку без клика | Поле результата пустое |
| E-N2 | `test_click_outside_buttons` | Клик по заголовку и описанию; затем Cat и снова клики вне кнопок | Результат не меняется: пустой, затем «Meow!» |
| E-N3 | `test_press_and_release_outside` | Зажать мышь на Dog, увести и отпустить на заголовке | Клик не засчитан, поле результата пустое |

### Всплывающие окна — https://practice-automation.com/popups/
Кнопки `#alert`, `#confirm`, `#prompt` вызывают встроенные диалоги браузера (Selenium: `driver.switch_to.alert`):
alert «Hi there, pal!»; confirm «OK or Cancel, which will it be?» → `#confirmResult` «OK it is!» / «Cancel it is!»;
prompt «Hi there, what's your name?» → `#promptResult` «Nice to meet you, <имя>!» или «Fine, be that way...».
Клик по «<< click me to see a tooltip >>» переключает подсказку `#myTooltip` «Cool text».

**Запуск:**
```bash
pytest -m popups --browser=chrome,firefox -n 4     # Chrome и Firefox параллельно
pytest -m popups -v                                # только Chrome, по одному тесту с выводом названий
```

**Позитивные (9)**
| # | Тест | Сценарий | Ожидаемый результат |
|---|---|---|---|
| P-1 | `test_page_initial_state` | Открыть страницу | Кнопки «Alert Popup», «Confirm Popup», «Prompt Popup»; результаты пустые; подсказка скрыта |
| P-2 | `test_alert` | Alert → OK | Текст «Hi there, pal!»; диалог закрыт |
| P-3 | `test_confirm_ok` | Confirm → OK | Текст «OK or Cancel, which will it be?»; результат «OK it is!» |
| P-4 | `test_confirm_cancel` | Confirm → Cancel | «Cancel it is!» |
| P-5 | `test_confirm_result_switches` | Confirm: OK → Cancel → OK | Результат меняется соответственно |
| P-6 | `test_prompt_with_name` | Prompt → «Kirill» → OK | Текст «Hi there, what's your name?»; «Nice to meet you, Kirill!» |
| P-7 | `test_prompt_special_names` | Prompt с «Кирилл», «Анна Мария», «O'Neil-Smith» | Каждое имя выводится без искажений |
| P-8 | `test_tooltip_shows` | Клик по «click me to see a tooltip» | Видна подсказка «Cool text» |
| P-9 | `test_tooltip_toggles` | Три клика по подсказке | Показана → скрыта → снова показана |

**Негативные (3)**
| # | Тест | Сценарий | Ожидаемый результат |
|---|---|---|---|
| P-N1 | `test_prompt_empty` | Prompt без ввода → OK | «Fine, be that way...» |
| P-N2 | `test_prompt_cancel` | Prompt, ввести «Kirill» → Cancel | Имя не принято: «Fine, be that way...» |
| P-N3 | `test_page_blocked_while_alert_open` | Alert открыт → клик по «Confirm Popup» | `UnexpectedAlertPresentException`, confirm не сработал, результат пустой |

### Форма — https://practice-automation.com/form-fields/
HTML-форма `#feedbackForm`: Name (`#name-input`, required), Password, чекбоксы напитков `#drink1…5`,
радиокнопки цвета `#color1…5`, список `#automation`, раздел **Automation tools** (`<ul><li>`), Email, Message, Submit.
Отправка (`submitForm()`) показывает alert «Message received!» и очищает все поля; пустое Name блокирует
встроенная проверка браузера (`required`).

**Пункт 5 задания** — тест `test_message_from_automation_tools`: список элементов раздела Automation tools
получается средствами Selenium (`find_elements` по `li`), преобразуется в текст через запятую и вводится в Message:
`Selenium, Playwright, Cypress, Appium, Katalon Studio`.

**Запуск:**
```bash
pytest -m forms --browser=chrome,firefox -n 4     # Chrome и Firefox параллельно
pytest -m forms -v                                # только Chrome, по одному тесту с выводом названий
```

**Позитивные (9)**
| # | Тест | Сценарий | Ожидаемый результат |
|---|---|---|---|
| F-1 | `test_page_initial_state` | Открыть страницу | Заголовок, «* Required», подписи напитков и цветов, варианты списка, подсказка Message, 5 инструментов; форма пустая |
| F-2 | `test_message_from_automation_tools` | Name + Message = список Automation tools через запятую → Submit | Message = `Selenium, Playwright, Cypress, Appium, Katalon Studio`; alert «Message received!» |
| F-3 | `test_submit_full_form` | Заполнить все поля (2 напитка, цвет, Yes, Email, Message) → Submit | Значения на месте; alert «Message received!» |
| F-4 | `test_form_reset_after_submit` | Заполнить форму → Submit → OK | Все поля пустые, чекбоксы, радиокнопки и список сброшены |
| F-5 | `test_submit_only_required` | Только Name → Submit | alert «Message received!» |
| F-6 | `test_drink_checkboxes` | Отметить Water, Coffee, Wine; снять Coffee | Отмечаются независимо, повторный клик снимает отметку |
| F-7 | `test_color_radio_single_choice` | Поочерёдно выбрать все 5 цветов | Выбран всегда только один |
| F-8 | `test_automation_select` | Выбрать Yes, No, Undecided | По умолчанию пустой вариант; выбор применяется |
| F-9 | `test_password_masked` | Ввести пароль | Поле `type="password"`, значение принято |

**Негативные (3)**
| # | Тест | Сценарий | Ожидаемый результат |
|---|---|---|---|
| F-N1 | `test_submit_without_name` | Name пустой, остальное заполнено → Submit | alert нет; Name невалидно (`validity.valid = false`, есть `validationMessage`); данные не сброшены |
| F-N2 | `test_submit_whitespace_name` | Name из пробелов → Submit | Форма не должна отправляться. ⚠ **xfail — известный дефект:** `required` считает пробелы заполнением |
| F-N3 | `test_submit_invalid_email` | Email `abc`, `user@` → Submit (2 параметра) | Форма не должна отправляться. ⚠ **xfail — известный дефект:** формат Email не проверяется вопреки подсказке «No fake emails!» |
