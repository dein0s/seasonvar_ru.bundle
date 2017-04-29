# coding=utf-8

# Standart Library
from copy import deepcopy

# Bundle Library
import factory

CACHE_INVALID_AFTER_KEY = 'invalid_after'

SEASON_CACHE_KEY = 'season_cache'
SEASON_CACHE_INVALIDATE = 60 * 5  # 5 mins

UPDATES_CACHE_KEY = 'update_cache'

GENRE_CACHE_KEY = 'genre_cache'
GENRE_CACHE_INVALIDATE = 60 * 60 * 3  # 3 hrs

COUNTRY_CACHE_KEY = 'country_cache'
COUNTRY_CACHE_INVALIDATE = 60 * 60 * 3  # 3 hrs

CACHE_KEYS = [UPDATES_CACHE_KEY, SEASON_CACHE_KEY, GENRE_CACHE_KEY, COUNTRY_CACHE_KEY]

def set_cache(key, data):
    if Dict[key]:
        del Dict[key]
    Dict[key] = data
    Dict.Save()


def clear_cache():
    for key in CACHE_KEYS:
        if Dict[key]:
            del Dict[key]
    Dict.Save()


def get_cache_or_invalidate(key):
    cache = deepcopy(Dict[key])
    if cache:
        if CACHE_INVALID_AFTER_KEY in cache:
            if Datetime.FromTimestamp(cache[CACHE_INVALID_AFTER_KEY]) > Datetime.UTCNow():
                cache.pop(CACHE_INVALID_AFTER_KEY)
            else:
                del Dict[key]
                Dict.Save()
                cache = None
    return cache

def set_season_cache(data):
    cache = get_cache_or_invalidate(SEASON_CACHE_KEY)
    if not cache or cache != data:
        data[CACHE_INVALID_AFTER_KEY] = Datetime.TimestampFromDatetime(
            Datetime.UTCNow() + Datetime.Delta(seconds=SEASON_CACHE_INVALIDATE))
        set_cache(SEASON_CACHE_KEY, data)

def set_genre_cache(data):
    cache = get_cache_or_invalidate(GENRE_CACHE_KEY)
    if not cache or cache != data:
        data[CACHE_INVALID_AFTER_KEY] = Datetime.TimestampFromDatetime(
            Datetime.UTCNow() + Datetime.Delta(seconds=GENRE_CACHE_INVALIDATE))
        set_cache(GENRE_CACHE_KEY, data)


def set_country_cache(data):
    cache = get_cache_or_invalidate(COUNTRY_CACHE_KEY)
    if not cache or cache != data:
        data[CACHE_INVALID_AFTER_KEY] = Datetime.TimestampFromDatetime(
            Datetime.UTCNow() + Datetime.Delta(seconds=COUNTRY_CACHE_INVALIDATE))
        set_cache(COUNTRY_CACHE_KEY, data)


def set_updates_cache(data):
    set_cache(UPDATES_CACHE_KEY, data)


def get_updates_cache():
    return get_cache_or_invalidate(UPDATES_CACHE_KEY)

def get_country_cache_or_create():
    cache = get_cache_or_invalidate(COUNTRY_CACHE_KEY)
    if not cache:
        set_country_cache(factory.get_country_list())
        cache = get_cache_or_invalidate(COUNTRY_CACHE_KEY)
    return cache


def get_genre_cache_or_create():
    cache = get_cache_or_invalidate(GENRE_CACHE_KEY)
    if not cache:
        set_genre_cache(factory.get_genre_list())
        cache = get_cache_or_invalidate(GENRE_CACHE_KEY)
    return cache


def get_season_cache_or_create(show_name, season_id):
    cache = get_cache_or_invalidate(SEASON_CACHE_KEY)
    if not cache or season_id != cache['season_id']:
        set_season_cache(factory.get_season_data(show_name, season_id))
        cache = get_cache_or_invalidate(SEASON_CACHE_KEY)
    return cache
