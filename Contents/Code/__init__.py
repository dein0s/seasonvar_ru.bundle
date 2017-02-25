# coding=utf-8

# TODO: check, change and localize all strings (titles, prefixes, names, etc.)

import constants as const
import factory
import messages
from utils import get_public_ip, logger, L, F, make_fake_url, update_api_key
from web_seasonvar_extra import check_ip_and_allow, get_api_key
from DumbTools import DumbKeyboard
from functools import wraps


#############################
###    Utils               ##
#############################
def not_implemented(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return MessageContainer(header='ERROR', message=messages.ERROR.NOT_IMPLEMENTED)
    return wrapper

log_debug = Log.Debug


#############################
###    Constants           ##
#############################
PREFIX = '/video/seasonvar_ru'
TITLE = 'Seasonvar.ru'
ART_SEASONVAR = 'art_main.png'
ICON_SEASONVAR = 'logo_main.png'

ERROR_HEADER = messages.ERROR.HEADER
INFO_HEADER = messages.INFO.HEADER

HISTORY_KEY = 'history'
try:
    HISTORY_MAX_LEN = int(Prefs['history_len'])
except:
    HISTORY_MAX_LEN = 50

CACHE_INVALID_AFTER_KEY = 'invalid_after'

SEASON_CACHE_KEY = 'season_cache'
SEASON_CACHE_INVALIDATE = 60 * 5  # 5 mins

UPDATES_CACHE_KEY = 'update_cache'

GENRE_CACHE_KEY = 'genre_cache'
GENRE_CACHE_INVALIDATE = 60 * 60 * 3  # 3 hrs

COUNTRY_CACHE_KEY = 'country_cache'
COUNTRY_CACHE_INVALIDATE = 60 * 60 * 3  # 3 hrs

CACHE_KEYS = [UPDATES_CACHE_KEY, SEASON_CACHE_KEY, GENRE_CACHE_KEY, COUNTRY_CACHE_KEY]


#############################
###    Init                ##
#############################
def Start():
    Locale.DefaultLocale = Prefs['language'].split('/')[1]  # NB: Language in prefs as 'English/en'
    ObjectContainer.title1 = TITLE


@handler(PREFIX, TITLE, art=ART_SEASONVAR, thumb=ICON_SEASONVAR)
@route(PREFIX)
def MainMenu():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(UpdatesFolder), title=L('MAIN_LATEST_UPDATES'), thumb=R('icon_updates.png')))
    oc.add(DirectoryObject(key=Callback(Dummy), title=L('MAIN_BOOKMARKS'), thumb=R('icon_bookmarks.png')))
    oc.add(DirectoryObject(key=Callback(SearchFolder), title=L('MAIN_SEARCH'), thumb=R('icon_search.png')))
    oc.add(DirectoryObject(key=Callback(HistoryFolder), title=L('MAIN_HISTORY'), thumb=R('icon_history.png')))
    oc.add(DirectoryObject(key=Callback(Dummy), title=L('MAIN_FILTER'), thumb=R('icon_filter.png')))
    oc.add(DirectoryObject(key=Callback(ToolsFolder), title=L('MAIN_TOOLS'), thumb=R('icon_tools.png')))
    return oc


#############################
###    Updates             ##
#############################
@route(PREFIX + '/updates')
def UpdatesFolder():
    oc = ObjectContainer(title2=L('MAIN_LATEST_UPDATES'))
    oc.add(DirectoryObject(key=Callback(GetUpdatesFolder, query=1), title=L('LATEST_UPDATES_1D')))
    oc.add(DirectoryObject(key=Callback(GetUpdatesFolder, query=3), title=L('LATEST_UPDATES_3D')))
    oc.add(DirectoryObject(key=Callback(GetUpdatesFolder, query=7), title=L('LATEST_UPDATES_1W')))
    if Client.Product in DumbKeyboard.clients:
        # NB: For clients, that cannot display InputDirectoryObject
        DumbKeyboard(PREFIX + '/updates', oc, GetUpdatesFolder, dktitle=L('LATEST_UPDATES_INPUT_PROMPT'),
                     dknumbersonly=True)
    else:
        oc.add(InputDirectoryObject(key=Callback(GetUpdatesFolder), title=L('LATEST_UPDATES_INPUT'),
                                    prompt=L('LATEST_UPDATES_INPUT_PROMPT')))
    return oc


@route(PREFIX + '/updates/get_{query}d')
def GetUpdatesFolder(query=1):
    try:
        query = int(query)
    except:
        return MessageContainer(header=ERROR_HEADER, message=messages.ERROR.ONLY_NUMBERS_ALLOWED)
    oc = ObjectContainer(title2=F('LATEST_UPDATES_FOR', query))
    updates_data = factory.get_latest_updates(day_count=query)
    if not updates_data:
        pass  # TODO: api > web > error
    SetCache(UPDATES_CACHE_KEY, updates_data)
    for season in updates_data.values():
        oc.add(DirectoryObject(key=Callback(GetSeasonFolder, show_name=season['name'], season_id=season['season_id'],
                                            check_updates=True), thumb=season['thumb'], title=season['title'],
                                            art=season['thumb']))
    return oc


#############################
###    Search              ##
#############################
@route(PREFIX + '/search', genre=list, country=list)
def SearchFolder(query=None, genre=[], country=[]):
    oc = ObjectContainer(title2=L('MAIN_SEARCH'))
    genres_title = 'GENRE'  # TODO: localize
    countries_title = 'COUNTRY'  # TODO: localize
    if Client.Product in DumbKeyboard.clients:
        genres_title = genres_title + ': %s' % ''.join('[%s]' % i for i in genre)
        countries_title = countries_title + ': %s' % ''.join('[%s]' % i for i in country)
        DumbKeyboard(PREFIX + '/search', oc, GetSearchResultFolder, genre=genre, country=country,
                     dktitle=L('SEARCH_INPUT'))
    else:
        oc.add(InputDirectoryObject(key=Callback(GetSearchResultFolder, genre=genre, country=country),
                                    title=L('SEARCH_INPUT')))
    if Prefs['api_key']:
        oc.add(DirectoryObject(key=Callback(GetSearchGenreFolder, query=query, genre=genre, country=country),
                               title=L('SEARCH_PICK_GENRE')))  # TODO: localize
        oc.add(DirectoryObject(key=Callback(GetSearchCountryFolder, query=query, genre=genre, country=country),
                               title=L('SEARCH_PICK_COUNTRY')))  # TODO: localize
    return oc


@route(PREFIX + '/search/{query}', genre=list, country=list)
def GetSearchResultFolder(query=None, genre=[], country=[]):
    search_results = factory.get_search_results(query, country=country, genre=genre)
    oc = ObjectContainer()
    for item in search_results.values():
        oc.add(DirectoryObject(key=Callback(GetSeasonFolder, show_name=item['name'], season_id=item['season_id']),
                               title=item['title'], thumb=item['thumb'], art=item['thumb']))
    return oc


@route(PREFIX + '/search/{query}/genre', genre=list, country=list)
def GetSearchGenreFolder(query=None, genre=[], country=[]):
    genre_list = GetGenreCacheOrCreate()
    done_title = L('DONE')  # TODO: localize
    if Client.Product in DumbKeyboard.clients:
        done_title = done_title + ': %s' % ''.join('[%s]' % g for g in genre)
    oc = ObjectContainer()  # TODO: think about how to deal with web player back navigation
    oc.add(DirectoryObject(key=Callback(SearchFolder, query=query, country=country, genre=genre), title=done_title))
    if genre:
        oc.add(DirectoryObject(key=Callback(GetSearchGenreFolder, query=query, country=country, genre=genre[:-1]), title=L('DELETE_LAST')))  # TODO: localize
        oc.add(DirectoryObject(key=Callback(GetSearchGenreFolder, query=query, country=country, genre=[]), title=L('DELETE_ALL')))  # TODO: localize
    for item in genre_list.values():
        if item not in genre:
            oc.add(DirectoryObject(key=Callback(GetSearchGenreFolder, query=query, country=country, genre=genre+[item]), title=item))
        else:
            oc.add(DirectoryObject(key=Callback(GetSearchGenreFolder, query=query, country=country, genre=genre), title=u'✓ %s' % item))
    return oc


@route(PREFIX + '/search/{query}/country', genre=list, country=list)
def GetSearchCountryFolder(query=None, genre=[], country=[]):
    country_list = GetCountryCacheOrCreate()
    done_title = L('DONE')  # TODO: localize
    if Client.Product in DumbKeyboard.clients:
        done_title = done_title + ': %s' % ''.join('[%s]' % c for c in country)
    oc = ObjectContainer()  # TODO: think about how to deal with web player back navigation
    oc.add(DirectoryObject(key=Callback(SearchFolder, query=query, country=country, genre=genre), title=done_title))
    if country:
        oc.add(DirectoryObject(key=Callback(GetSearchCountryFolder, query=query, country=country[:-1], genre=genre), title=L('DELETE_LAST')))  # TODO: localize
        oc.add(DirectoryObject(key=Callback(GetSearchCountryFolder, query=query, country=[], genre=genre), title=L('DELETE_ALL')))  # TODO: localize
    for item in country_list.values():
        if item not in genre:
            oc.add(DirectoryObject(key=Callback(GetSearchCountryFolder, query=query, country=country+[item], genre=genre), title=item))
        else:
            oc.add(DirectoryObject(key=Callback(GetSearchCountryFolder, query=query, country=country, genre=genre), title=u'✓ %s' % item))
    return oc


#############################
###    Season              ##
#############################
@route(PREFIX + '/season/{season_id}', check_updates=bool)
def GetSeasonFolder(show_name, season_id, check_updates=False):
    season = GetSeasonCacheOrCreate(show_name, season_id, as_string=False)
    PushToHistory(season)
    oc = ObjectContainer(title2=season['title'])
    if season['playlist']:
        oc.add(DirectoryObject(key=Callback(GetTranslatesFolder, show_name=show_name, season_id=season_id,
                                            check_updates=check_updates), title=L('SEASON_TRANSLATES_FOLDER'),
                                            thumb=season['thumb'], art=season['thumb']))
    if 'other_season' in season:
        oc.add(DirectoryObject(key=Callback(GetOtherSeasonsFolder, show_name=show_name, season_id=season_id),
                               title=L('SEASON_OTHER_SEASONS_FOLDER'), thumb=season['thumb'], art=season['thumb']))
    # TODO: add check if exists in bookmarks and related stuff
    oc.add(DirectoryObject(key=Callback(Dummy), title=L('SEASON_ADD_BOOKMARK'), thumb=R('icon_add.png'),
                           art=season['thumb']))
    oc.add(DirectoryObject(key=Callback(Dummy), title=L('SEASON_DEL_BOOKMARK'), thumb=R('icon_del.png'),
                           art=season['thumb']))
    return oc


@route(PREFIX + '/season/{season_id}/translates', check_updates=bool)
def GetTranslatesFolder(show_name, season_id, check_updates):
    season = GetSeasonCacheOrCreate(show_name, season_id, as_string=False)
    oc = ObjectContainer(title2=season['title'], content=ContainerContent.Seasons)
    for trans_index, translate in enumerate(season['playlist'].keys()):
        fake_url = make_fake_url(show_name=show_name, season_id=season_id, translate=translate)
        title = translate
        if check_updates:
            if season_id in Dict[UPDATES_CACHE_KEY]:
                update_messages = Dict[UPDATES_CACHE_KEY][season_id]['update_messages']
                # NB: know why? because FUCK YOU! that's why... NameError: global name 'any' is not defined
                if True in [translate in message for message in update_messages]:
                    title = '(*) ' + translate
        oc.add(SeasonObject(key=Callback(GetEpisodesFolder, show_name=show_name, season_id=season_id,
                                         translate=translate), rating_key=fake_url, index=trans_index + 1,
                            title=L(title), source_title=TITLE, thumb=season['thumb'], summary=season['summary']))
    return oc


@route(PREFIX + '/season/{season_id}/translates/{translate}')
def GetEpisodesFolder(show_name, season_id, translate):
    season = GetSeasonCacheOrCreate(show_name, season_id, as_string=False)
    oc = ObjectContainer(title2=translate, content=ContainerContent.Episodes)
    for episode in season['playlist'][translate]:
        fake_url = make_fake_url(show_name=show_name, season_id=season_id, translate=translate,
                                 episode_id=episode['episode_id'])
        oc.add(URLService.MetadataObjectForURL(fake_url))
    return oc


@route(PREFIX + '/season/{season_id}/other_seasons')
def GetOtherSeasonsFolder(show_name, season_id):
    season = GetSeasonCacheOrCreate(show_name, season_id, as_string=False)
    if 'other_season' in season:
        oc = ObjectContainer()
        for item_season_number, item_season_id in season['other_season'].items():
            title = u'%s сезон' % item_season_number
            oc.add(DirectoryObject(key=Callback(GetSeasonFolder, show_name=show_name, season_id=item_season_id),
                                   thumb=season['thumb'], title=title, art=season['thumb']))
        return oc
    # NB: If called from outside of season folder and have no other seasons
    raise Ex.MediaNotAvailable


#############################
###    History             ##
#############################
@route(PREFIX + '/history')
def HistoryFolder():
    history = Dict[HISTORY_KEY]
    oc = ObjectContainer(title2=F('HISTORY_ITEMS', len(history) if history else 0, HISTORY_MAX_LEN))
    if not history:
        return MessageContainer(header=INFO_HEADER, message=messages.INFO.HISTORY_EMPTY)
    oc.add(DirectoryObject(key=Callback(HistoryClear), title=L('HISTORY_CLEAN'), thumb=R('icon_clear.png')))
    for season in sorted(history.values(),key=lambda k: k['time_added'], reverse=True):
        oc.add(DirectoryObject(key=Callback(GetSeasonFolder, show_name=season['name'], season_id=season['season_id']),
                               title=season['title'], thumb=season['thumb'], art=season['thumb']))
    return oc


@route(PREFIX + '/history/clean')
def HistoryClear():
    if Dict[HISTORY_KEY]:
        del Dict[HISTORY_KEY]
        Dict.Save()
    return MessageContainer(header=INFO_HEADER, message=messages.INFO.HISTORY_CLEARED)


@route (PREFIX + '/history/push')
def PushToHistory(data):
    history = Dict[HISTORY_KEY]
    if not history:
        history = {}
    history[data['season_id']] = {
        'season_id': data['season_id'],
        'name': data['name'],
        'title': data['title'],
        'thumb': data['thumb'],
        'time_added': Datetime.TimestampFromDatetime(Datetime.UTCNow())
    }
    # NB: trim history
    if len(history) > HISTORY_MAX_LEN:
        trimmed_history = sorted(history.values(), key=lambda k: k['time_added'], reverse=True)[:HISTORY_MAX_LEN]
        history = {}
        for item in trimmed_history:
            history[item['season_id']] = item
    Dict[HISTORY_KEY] = history
    Dict.Save()


#############################
###    Tools               ##
#############################
@route(PREFIX + '/tools')
def ToolsFolder():
    # TODO: move here all ip/api cheks and other usefull stuff
    oc = ObjectContainer(title2=L('MAIN_TOOLS'))
    if Prefs['dev_mode']:
        oc.add(DirectoryObject(key=Callback(ToolDebug), title=L('TOOLS_DEBUG'), thumb=R('icon_debug.png')))
        oc.add(DirectoryObject(key=Callback(ToolClearCache), title=L('TOOLS_CLEAR_CACHE'), thumb=R('icon_clear.png')))
    if Prefs['username'] and Prefs['password']:
        oc.add(DirectoryObject(key=Callback(ToolCheckApiKey), title=L('TOOLS_CHECK_API_KEY'), thumb=R('icon_key.png')))
    if Prefs['api_key'] and (Prefs['username'] and Prefs['password']):
        oc.add(DirectoryObject(key=Callback(ToolCheckIp), title=L('TOOLS_CHECK_IP'), thumb=R('icon_ip.png')))
    return oc


@route(PREFIX + '/tools/check_api_key')
def ToolCheckApiKey():
    api_key = get_api_key()
    if api_key is not None:
        if api_key != Prefs['api_key']:
            update_api_key(api_key)
        return MessageContainer(header=INFO_HEADER, message=messages.INFO.API_KEY_VALID)
    return MessageContainer(header=ERROR_HEADER, message=messages.ERROR.API_KEY_NO_PREMIUM)


@route(PREFIX + '/tools/check_ip')
def ToolCheckIp():
    public_ip = get_public_ip(external=False).strip('\n')
    if check_ip_and_allow(public_ip):
        return MessageContainer(header=INFO_HEADER, message=F(messages.INFO.IP_ALLOWED, public_ip))
    return MessageContainer(header=ERROR_HEADER, message=F(messages.ERROR.IP_NO_PREMIUM, public_ip))


@route(PREFIX + '/tools/debug')
def ToolDebug():
    log_debug('>>> DEBUG START <<<')
    from web_seasonvar_extra import get_api_key
    var = get_api_key()
    log_debug('>>> %s <<<' % var)
    log_debug('>>> DEBUG END <<<')
    return MessageContainer(header=INFO_HEADER, message='TEST')


@route(PREFIX + '/tools/clear_cache')
def ToolClearCache():
    for key in CACHE_KEYS:
        if Dict[key]:
            del Dict[key]
    Dict.Save()
    return MessageContainer(header=INFO_HEADER, message=messages.INFO.CACHE_CLEARED)

@route(PREFIX + '/dummy')
@not_implemented
def Dummy():
    return None


#############################
###    Cache               ##
#############################
def GetCacheOrInvalidate(key):
    from copy import deepcopy
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


@route(PREFIX + '/cache/{key}')
def SetCache(key, data):
    if Dict[key]:
        del Dict[key]
    Dict[key] = data
    Dict.Save()


def SetSeasonCache(data):
    cache = GetCacheOrInvalidate(SEASON_CACHE_KEY)
    if not cache or cache != data:
        data[CACHE_INVALID_AFTER_KEY] = Datetime.TimestampFromDatetime(
            Datetime.UTCNow() + Datetime.Delta(seconds=SEASON_CACHE_INVALIDATE))
        SetCache(SEASON_CACHE_KEY, data)


def SetGenreCache(data):
    cache = GetCacheOrInvalidate(GENRE_CACHE_KEY)
    if not cache or cache != data:
        data[CACHE_INVALID_AFTER_KEY] = Datetime.TimestampFromDatetime(
            Datetime.UTCNow() + Datetime.Delta(seconds=GENRE_CACHE_INVALIDATE))
        SetCache(GENRE_CACHE_KEY, data)


def SetCountryCache(data):
    cache = GetCacheOrInvalidate(COUNTRY_CACHE_KEY)
    if not cache or cache != data:
        data[CACHE_INVALID_AFTER_KEY] = Datetime.TimestampFromDatetime(
            Datetime.UTCNow() + Datetime.Delta(seconds=COUNTRY_CACHE_INVALIDATE))
        SetCache(COUNTRY_CACHE_KEY, data)


@route(PREFIX + '/cache/season_cache/{season_id}', as_string=bool)
def GetSeasonCacheOrCreate(show_name, season_id, as_string=True):
    cache = GetCacheOrInvalidate(SEASON_CACHE_KEY)
    if not cache or season_id != cache['season_id']:
        SetSeasonCache(factory.get_season_data(show_name, season_id))
        cache = GetCacheOrInvalidate(SEASON_CACHE_KEY)
    if as_string:
        return JSON.StringFromObject(cache)
    return cache


@route(PREFIX + '/cache/genre_cache')
def GetGenreCacheOrCreate():
    cache = GetCacheOrInvalidate(GENRE_CACHE_KEY)
    if not cache:
        SetGenreCache(factory.get_genre_list())
        cache = GetCacheOrInvalidate(GENRE_CACHE_KEY)
    return cache


@route(PREFIX + '/cache/country_cache')
def GetCountryCacheOrCreate():
    cache = GetCacheOrInvalidate(COUNTRY_CACHE_KEY)
    if not cache:
        SetCountryCache(factory.get_country_list())
        cache = GetCacheOrInvalidate(COUNTRY_CACHE_KEY)
    return cache
