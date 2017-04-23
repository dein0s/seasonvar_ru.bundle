# coding=utf-8

# Standard Library
from functools import wraps

# Bundle Library
import cache
import factory
import history
import messages
import bookmarks
from utils import F, L, get_public_ip, make_fake_url, update_api_key
from updater import Updater
from DumbTools import DumbKeyboard
from web_seasonvar_extra import get_api_key, check_ip_and_allow


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


#############################
###    Init                ##
#############################
def Start():
    Locale.DefaultLocale = Prefs['language'].split('/')[1]  # NB: Language in prefs as 'English/en'
    ObjectContainer.title1 = TITLE
    history.init_history()
    bookmarks.init_marks()


@handler(PREFIX, TITLE, art=ART_SEASONVAR, thumb=ICON_SEASONVAR)
@route(PREFIX)
def MainMenu():
    oc = ObjectContainer()
    Updater(PREFIX + '/update', oc)
    oc.add(DirectoryObject(key=Callback(UpdatesFolder), title=L('MAIN_LATEST_UPDATES'), thumb=R('icon_updates.png')))
    oc.add(DirectoryObject(key=Callback(BookmarksFolder), title=L('MAIN_BOOKMARKS'), thumb=R('icon_bookmarks.png')))
    oc.add(DirectoryObject(key=Callback(SearchFolder), title=L('MAIN_SEARCH'), thumb=R('icon_search.png')))
    oc.add(DirectoryObject(key=Callback(HistoryFolder), title=L('MAIN_HISTORY'), thumb=R('icon_history.png')))
    if Prefs['api_key']:
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
        query = 1
    oc = ObjectContainer(title2=F('LATEST_UPDATES_FOR', query))
    updates_data = factory.get_latest_updates(day_count=query)
    cache.set_updates_cache(updates_data)
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
    if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(PREFIX, oc, GetSearchResultFolder, genre=genre, country=country,
                     dktitle=L('SEARCH_INPUT'))
    else:
        oc.add(InputDirectoryObject(key=Callback(GetSearchResultFolder, genre=genre, country=country),
                                    title=L('SEARCH_INPUT')))
    if Prefs['api_key'] and Prefs['adv_menu']:
        if genre and Client.Product in DumbKeyboard.clients:
            genres_title = L('SEARCH_GENRE') + ': %s' % ''.join('[%s]' % i for i in genre)
            oc.add(DirectoryObject(key=Callback(GetSearchGenreFolder, query=query, genre=genre, country=country),
                                   title=genres_title))
        else:
            oc.add(DirectoryObject(key=Callback(GetSearchGenreFolder, query=query, genre=genre, country=country),
                                   title=L('SEARCH_PICK_GENRE')))
        if country and Client.Product in DumbKeyboard.clients:
            countries_title = L('SEARCH_COUNTRY') + ': %s' % ''.join('[%s]' % i for i in country)
            oc.add(DirectoryObject(key=Callback(GetSearchCountryFolder, query=query, genre=genre, country=country),
                                   title=countries_title))
        else:
            oc.add(DirectoryObject(key=Callback(GetSearchCountryFolder, query=query, genre=genre, country=country),
                                   title=L('SEARCH_PICK_COUNTRY')))
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
    genre_list = cache.get_genre_cache_or_create()
    done_title = L('SEARCH_DONE')
    if Client.Product in DumbKeyboard.clients:
        done_title = done_title + ': %s' % ''.join('[%s]' % g for g in genre)
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(SearchFolder, query=query, country=country, genre=genre), title=done_title))
    if genre:
        oc.add(DirectoryObject(key=Callback(GetSearchGenreFolder, query=query, country=country, genre=genre[:-1]),
                               title=L('SEARCH_REMOVE_LAST')))
        oc.add(DirectoryObject(key=Callback(GetSearchGenreFolder, query=query, country=country, genre=[]),
                               title=L('SEARCH_REMOVE_ALL')))
    for item in genre_list.values():
        if item not in genre:
            oc.add(DirectoryObject(key=Callback(GetSearchGenreFolder, query=query, country=country,
                                                genre=genre+[item]), title=item))
        else:
            oc.add(DirectoryObject(key=Callback(GetSearchGenreFolder, query=query, country=country,
                                                genre=genre), title=u'✓ %s' % item))
    return oc


@route(PREFIX + '/search/{query}/country', genre=list, country=list)
def GetSearchCountryFolder(query=None, genre=[], country=[]):
    country_list = cache.get_country_cache_or_create()
    done_title = L('SEARCH_DONE')
    if Client.Product in DumbKeyboard.clients:
        done_title = done_title + ': %s' % ''.join('[%s]' % c for c in country)
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(SearchFolder, query=query, country=country, genre=genre), title=done_title))
    if country:
        oc.add(DirectoryObject(key=Callback(GetSearchCountryFolder, query=query, country=country[:-1], genre=genre),
                               title=L('SEARCH_REMOVE_LAST')))
        oc.add(DirectoryObject(key=Callback(GetSearchCountryFolder, query=query, country=[], genre=genre),
                               title=L('SEARCH_REMOVE_ALL')))
    for item in country_list.values():
        if item not in country:
            oc.add(DirectoryObject(key=Callback(GetSearchCountryFolder, query=query, country=country+[item],
                                                genre=genre), title=item))
        else:
            oc.add(DirectoryObject(key=Callback(GetSearchCountryFolder, query=query, country=country,
                                                genre=genre), title=u'✓ %s' % item))
    return oc


#############################
###    Season              ##
#############################
@route(PREFIX + '/season/{season_id}', check_updates=bool)
def GetSeasonFolder(show_name, season_id, check_updates=False):
    season = cache.get_season_cache_or_create(show_name, season_id)
    history.push_to_history(season)
    oc = ObjectContainer(title2=season['title'], no_cache=True)

    if season['playlist']:
        oc.add(DirectoryObject(key=Callback(GetTranslatesFolder, show_name=show_name, season_id=season_id,
                                            check_updates=check_updates), title=L('SEASON_TRANSLATES_FOLDER'),
                                            thumb=season['thumb'], art=season['thumb']))

    if 'other_season' in season:
        oc.add(DirectoryObject(key=Callback(GetOtherSeasonsFolder, show_name=show_name, season_id=season_id),
                               title=L('SEASON_OTHER_SEASONS_FOLDER'), thumb=season['thumb'], art=season['thumb']))

    if bookmarks.is_marked(season_id):
        # NB: sadly we can't navigate back to season folder because of https://forums.plex.tv/discussion/comment/1416318
        last_watched = bookmarks.get_mark(season_id)['last_watched']
        if Client.Product in DumbKeyboard.clients:
            DumbKeyboard(PREFIX, oc, BookmarksAdd, show_name=show_name, season_id=season_id,
                         dktitle=F('SEASON_UPDATE_BOOKMARK', last_watched), dknumbersonly=True,
                         dkthumb=R('icon_add.png'))
        else:
            oc.add(InputDirectoryObject(key=Callback(BookmarksAdd, show_name=show_name, season_id=season_id),
                                        title=F('SEASON_UPDATE_BOOKMARK', last_watched), thumb=R('icon_add.png'),
                                        art=season['thumb']))
        oc.add(DirectoryObject(key=Callback(BookmarksDel, season_id=season_id), title=L('SEASON_DEL_BOOKMARK'),
                                         thumb=R('icon_del.png'), art=season['thumb']))

    else:
        if Client.Product in DumbKeyboard.clients:
            DumbKeyboard(PREFIX, oc, BookmarksAdd, show_name=show_name, season_id=season_id,
                         dktitle=L('SEASON_ADD_BOOKMARK'), dknumbersonly=True, dkthumb=R('icon_add.png'))
        else:
            oc.add(InputDirectoryObject(key=Callback(BookmarksAdd, show_name=show_name, season_id=season_id),
                                        title=L('SEASON_ADD_BOOKMARK'), thumb=R('icon_add.png'),
                                        art=season['thumb']))
    return oc


@route(PREFIX + '/season/{season_id}/translates', check_updates=bool)
def GetTranslatesFolder(show_name, season_id, check_updates):
    season = cache.get_season_cache_or_create(show_name, season_id)
    oc = ObjectContainer(title2=season['title'], content=ContainerContent.Seasons)
    for trans_index, translate in enumerate(season['playlist'].keys()):
        fake_url = make_fake_url(show_name=show_name, season_id=season_id, translate=translate)
        title = translate
        if check_updates:
            updates_cache = cache.get_updates_cache()
            if season_id in updates_cache:
                update_messages = updates_cache[season_id]['update_messages']
                # NB: know why? because FUCK YOU! that's why... NameError: global name 'any' is not defined
                if True in [translate in message for message in update_messages]:
                    title = '(*) ' + title
                # NB: because of messed update messages, thx to http://seasonvar.ru team
                else:
                    ep_names = [ep['name'] for ep in season['playlist'][translate]]
                    if True in [ep_name in update_messages for ep_name in ep_names]:
                        title = '(*) ' + translate
        if bookmarks.is_marked(season_id):
            last_watched = bookmarks.get_mark(season_id)['last_watched']
            translate_episodes = [ep['episode_id'] for ep in season['playlist'][translate]]
            if True in [int(ep) > int(last_watched) for ep in translate_episodes]:
                title = '(!) ' + title
        oc.add(SeasonObject(key=Callback(GetEpisodesFolder, show_name=show_name, season_id=season_id,
                                         translate=translate), rating_key=fake_url, index=trans_index + 1,
                            title=L(title), source_title=TITLE, thumb=season['thumb'], summary=season['summary']))
    return oc


@route(PREFIX + '/season/{season_id}/translates/{translate}')
def GetEpisodesFolder(show_name, season_id, translate):
    season = cache.get_season_cache_or_create(show_name, season_id)
    oc = ObjectContainer(title2=translate, content=ContainerContent.Episodes)
    for episode in season['playlist'][translate]:
        fake_url = make_fake_url(show_name=show_name, season_id=season_id, translate=translate,
                                 episode_id=episode['episode_id'])
        oc.add(URLService.MetadataObjectForURL(fake_url))
    return oc


@route(PREFIX + '/season/{season_id}/other_seasons')
def GetOtherSeasonsFolder(show_name, season_id):
    season = cache.get_season_cache_or_create(show_name, season_id)
    if 'other_season' in season:
        oc = ObjectContainer()
        for item_season_number, item_season_id in season['other_season'].items():
            title = u'%s сезон' % item_season_number
            oc.add(DirectoryObject(key=Callback(GetSeasonFolder, show_name=show_name, season_id=item_season_id),
                                   thumb=season['thumb'], title=title, art=season['thumb']))
        return oc
    # NB: If called from outside of season folder and have no other seasons
    raise Ex.MediaNotAvailable


# NB: data for URLService
@route(PREFIX + '/cache/season_cache/{season_id}')
def SeasonCache(show_name, season_id):
    season_cache = cache.get_season_cache_or_create(show_name, season_id)
    return JSON.StringFromObject(season_cache)


#############################
###    Bookmarks           ##
#############################
@route(PREFIX + '/bookmarks')
def BookmarksFolder():
    marks = bookmarks.get_all_marks()
    if not marks and not Prefs['adv_menu']:
        return MessageContainer(header=INFO_HEADER, message=messages.INFO.BOOKMARKS_EMPTY)
    oc = ObjectContainer()
    if Prefs['adv_menu']:
        oc.add(DirectoryObject(key=Callback(BookmarksClear), title=L('BOOKMARKS_CLEAR'), thumb=R('icon_clear.png')))
        oc.add(DirectoryObject(key=Callback(BookmarksImportFile), title=L('BOOKMARKS_IMPORT_FILE'),
                               thumb=R('icon_import.png')))
        oc.add(DirectoryObject(key=Callback(BookmarksExportFile), title=L('BOOKMARKS_EXPORT_FILE'),
                               thumb=R('icon_export.png')))
        if Prefs['password'] and Prefs['username']:
            oc.add(DirectoryObject(key=Callback(BookmarksSyncWeb), title=L('BOOKMARKS_SYNC_SITE'),
                                   thumb=R('icon_sync.png')))
    for season in sorted(marks.values(),key=lambda k: int(k['season_id']), reverse=True):
        oc.add(DirectoryObject(key=Callback(GetSeasonFolder, show_name=season['name'], season_id=season['season_id']),
                               title=season['title'], thumb=season['thumb'], art=season['thumb']))
    return oc


@route(PREFIX + '/bookmarks/add/{season_id}')
def BookmarksAdd(show_name, season_id, query=None):
    bookmarks.add_mark(show_name, season_id, query)
    return MessageContainer(header=INFO_HEADER, message=messages.INFO.BOOKMARK_ADDED)


@route(PREFIX + '/bookmarks/del/{season_id}')
def BookmarksDel(season_id):
    bookmarks.del_mark(season_id)
    return MessageContainer(header=INFO_HEADER, message=messages.INFO.BOOKMARK_DELETED)


@route(PREFIX + '/bookmarks/clear')
def BookmarksClear():
    bookmarks.set_empty_marks()
    return MessageContainer(header=INFO_HEADER, message=messages.INFO.BOOKMARKS_CLEARED)

@route(PREFIX + '/bookmarks/export/file')
def BookmarksExportFile():
    bookmarks.export_marks_to_file()
    return MessageContainer(header=INFO_HEADER, message=messages.INFO.BOOKMARKS_EXPORTED)


@route(PREFIX + '/bookmarks/import/file')
def BookmarksImportFile():
    bookmarks.import_marks_from_file()
    return MessageContainer(header=INFO_HEADER, message=messages.INFO.BOOKMARKS_IMPORTED)


@route(PREFIX + '/bookmarks/sync')
def BookmarksSyncWeb():
    bookmarks.sync_with_seasonvar_site()
    return MessageContainer(header=INFO_HEADER, message=messages.INFO.BOOKMARKS_SYNCED)


#############################
###    History             ##
#############################
@route(PREFIX + '/history')
def HistoryFolder():
    plugin_history = history.get_history()
    if not plugin_history:
        return MessageContainer(header=INFO_HEADER, message=messages.INFO.HISTORY_EMPTY)
    oc = ObjectContainer(title2=F('HISTORY_ITEMS', len(plugin_history) if history else 0, history.HISTORY_MAX_LEN))
    oc.add(DirectoryObject(key=Callback(HistoryClear), title=L('HISTORY_CLEAR'), thumb=R('icon_clear.png')))
    for season in sorted(plugin_history.values(), key=lambda k: k['time_added'], reverse=True):
        oc.add(DirectoryObject(key=Callback(GetSeasonFolder, show_name=season['name'], season_id=season['season_id']),
                               title=season['title'], thumb=season['thumb'], art=season['thumb']))
    return oc


@route(PREFIX + '/history/clean')
def HistoryClear():
    history.set_empty_history()
    return MessageContainer(header=INFO_HEADER, message=messages.INFO.HISTORY_CLEARED)


#############################
###    Tools               ##
#############################
@route(PREFIX + '/tools')
def ToolsFolder():
    # TODO: move here all ip/api cheks and other usefull stuff
    oc = ObjectContainer(title2=L('MAIN_TOOLS'))
    if Prefs['dev_menu']:
        oc.add(DirectoryObject(key=Callback(ToolDebug), title=L('TOOLS_DEBUG'), thumb=R('icon_debug.png')))
        oc.add(DirectoryObject(key=Callback(ToolClearCache), title=L('TOOLS_CLEAR_CACHE'), thumb=R('icon_clear.png')))
        oc.add(DirectoryObject(key=Callback(ToolClearDict), title=L('TOOLS_CLEAR_DICT'), thumb=R('icon_clear.png')))
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
    var = 'THIS IS DEBUG'
    log_debug('!! %s !!' % var)
    log_debug('>>> DEBUG END <<<')
    return MessageContainer(header=INFO_HEADER, message=var)


@route(PREFIX + '/tools/clear_cache')
def ToolClearCache():
    cache.clear_cache()
    return MessageContainer(header=INFO_HEADER, message=messages.INFO.CACHE_CLEARED)

@route(PREFIX + '/tools/clear_dict')
def ToolClearDict():
    keys = []
    for item in Dict:
        keys.append(item)
    for key in keys:
        del Dict[key]
    Dict.Save()
    return MessageContainer(header=INFO_HEADER, message=messages.INFO.DICT_CLEARED)


@route(PREFIX + '/dummy')
@not_implemented
def Dummy():
    return None
