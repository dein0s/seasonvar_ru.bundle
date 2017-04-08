[svru]: [http://seasonvar.ru]
[prem]: [http://seasonvar.ru/premium]
[api]: [http://seasonvar.ru/?mod=api]
[marks]: [http://seasonvar.ru/?mod=pause]

___
[![Gitter](https://badges.gitter.im/dein0s/seasonvar_ru.bundle.svg)](https://gitter.im/dein0s/seasonvar_ru.bundle?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
___
# Основная функциональность

#### Легенда:

_\*acc_ - необходимо указать в настройках плагина логин и пароль для [сайта][svru].

_\*acc-prem_ - необходимо иметь [премиум][prem] на [сайте][svru].

_\*api-key_ - необходимо указать в настройках плагина ключ API (доступен обладателям [премиума][prem] на странице [API][api]).

_\*dev_ - в настройках плагина включен режим разработчика.
___
* [x] Последние обновления
    * [x] За 1 день
    * [x] За 3 дня
    * [x] За 1 неделю
    * [x] Указать свой диапазон (в днях)

**ВАЖНО!**: без _\*api-key_ - 7 дней (кол-во блоков на главной странице), с _\*api-key_ максимальный лимит - 14 дней (метод `JSON.ObjectFromString()` имеет ограничение на размер входящих данных).

* [x] Поиск (только через меню плагина)
    * [x] Ввод строки для поиска
    * [x] Фильтровать результаты поиска по жанру (_\*api-key_)
    * [x] Фильтровать результаты поиска по стране (_\*api-key_)


* [ ] Фильтр (еще не реализовано)


* [ ] Закладки (еще не реализовано)
    * [ ] Добавить вручную (по ID сезона)
    * [ ] Из меню сезона
    * [ ] Импортировать с [сайта][marks] (_\*acc_)
    * [ ] Экспортировать в файл
    * [ ] Импортировать из файла
    * [ ] Синхронизация между плагином и [сайтом][marks] (_\*acc_)


* [x] История (отображает последние открытые в плагине сериалы)
    * [x] Очистить историю

**ВАЖНО!**: кол-во сохраняемых в истории сериалов можно указать в настройках плагина (значение по умолчанию: 50).

* [x] Утилиты
    * [x] Дебаг (_\*dev_ )
    * [x] Очистить кэш (_\*dev_ ) - удалит кэш для всех ключей из `__init__.py: CACHE_KEYS`
    * [x] Проверить API ключ (_\*acc_ + _\*acc-prem_) - установит/обновит _\*api-key_ если он доступен на [сайте][api].
    * [x] Проверить IP (_\*acc_ + _\*acc-prem_ + _\*api-key_) - проверит/разрешит доступ для текущий внешнего IP на [сайте][api]


### TODO:
* [ ] Добавить в README секцию с описанием установки
* [ ] Добавить в README секцию с описанием настроек плагина
* [ ] Обновление плагина через Plex
* [ ] Закладки
* [ ] Фильтр
* [ ] Субтитры (пока Plex не разрешает указывать субтитры в рамках плагина)