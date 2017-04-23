# coding=utf-8

# Bundle Library
from cache import get_season_cache_or_create
from web_seasonvar_extra import add_account_bookmarks, del_account_bookmarks, get_account_bookmarks

BOOKMARKS_KEY = 'bookmarks'
BOOKMARKS_SYNC_KEY = 'bookmarks_sync'
BOOKMARKS_FILE = 'Bookmarks.json'
BOOKMARKS_BACKUP_FILE = 'Bookmarks_sync_backup.json'
BOOKMARKS_FILE_PATH = Core.storage.abs_path(Core.storage.join_path(Core.bundle_path, BOOKMARKS_FILE))
BOOKMARKS_BACKUP_FILE_PATH = Core.storage.abs_path(Core.storage.join_path(Core.bundle_path, BOOKMARKS_BACKUP_FILE))


def set_empty_marks():
    Dict[BOOKMARKS_KEY] = {}
    Dict.Save()


def set_empty_sync():
    Dict[BOOKMARKS_SYNC_KEY] = []
    Dict.Save()


def init_marks():
    if BOOKMARKS_KEY not in Dict:
        set_empty_marks()
    if BOOKMARKS_SYNC_KEY not in Dict:
        set_empty_sync()


def get_all_marks():
    init_marks()
    return Dict[BOOKMARKS_KEY]


def get_mark(season_id):
    return get_all_marks()[season_id]


def get_sync():
    init_marks()
    return Dict[BOOKMARKS_SYNC_KEY]


def is_marked(season_id):
    marks = get_all_marks()
    if season_id in marks:
        return True
    return False


def add_mark(show_name, season_id, episode_id):
    marks = get_all_marks()
    season = get_season_cache_or_create(show_name, season_id)
    total_episodes = set([0])
    for translate in season['playlist']:
        for episode in season['playlist'][translate]:
            total_episodes.add(int(episode['episode_id']))
    try:
        episode_id = int(episode_id)
    except:
        episode_id = 0
    if episode_id not in total_episodes:
        episode_id = 0
    marks[season_id] = {
        'season_id': season['season_id'],
        'name': season['name'],
        'title': season['title'],
        'thumb': season['thumb'],
        'last_watched': episode_id
    }
    Dict.Save()


def del_mark(season_id):
    if is_marked(season_id):
        del get_all_marks()[season_id]
        Dict.Save()
        Log.Debug('> BOOKMARK %s DELETED <' % season_id)


def export_marks_to_file(file_path=BOOKMARKS_FILE_PATH):
    marks = JSON.StringFromObject(get_all_marks())
    Core.storage.save(file_path, marks)
    Log.Debug('> BOOKMARKS EXPORTED TO FILE %s <' % file_path)


def import_marks_from_file(file_path=BOOKMARKS_FILE_PATH):
    imported_marks = JSON.ObjectFromString(Core.storage.load(file_path))
    marks = get_all_marks()
    if imported_marks:
        for item in imported_marks.values():
            marks[item['season_id']] = item
        Dict.Save()
        Log.Debug('> BOOKMARKS IMPORTED FROM FILE %s <' % file_path)


def sync_with_seasonvar_site():
    web_marks = get_account_bookmarks()
    if web_marks is not None:
        sync = get_sync()
        plugin_marks = get_all_marks()
        web_add = []
        web_del = []
        plugin_add = []
        plugin_del = []
        sync_add = []
        sync_del = []
        for season_id in set(web_marks.keys() + plugin_marks.keys()):
            if season_id in web_marks and season_id not in plugin_marks and season_id not in sync:
                plugin_add.append(web_marks[season_id])
                sync_add.append(season_id)
            elif season_id in plugin_marks and season_id not in web_marks and season_id not in sync:
                web_add.append(plugin_marks[season_id])
                sync_add.append(season_id)
            elif season_id in web_marks and season_id in sync and season_id not in plugin_marks:
                web_del.append(season_id)
                sync_del.append(season_id)
            elif season_id in plugin_marks and season_id in sync and season_id not in web_marks:
                plugin_del.append(season_id)
                sync_del.append(season_id)
            elif season_id in web_marks and season_id in plugin_marks:
                if season_id not in sync:
                    sync_add.append(season_id)
                if plugin_marks[season_id]['last_watched'] > web_marks[season_id]['last_watched']:
                    web_add.append(plugin_marks[season_id])
                elif plugin_marks[season_id]['last_watched'] < web_marks[season_id]['last_watched']:
                    plugin_add.append(web_marks[season_id])
        for season_id in sync:
            if season_id not in web_marks and season_id not in plugin_marks:
                sync_del.append(season_id)
        if plugin_add or plugin_del:
            export_marks_to_file(BOOKMARKS_BACKUP_FILE_PATH)
        if web_add:
            add_account_bookmarks(web_add)
        if web_del:
            del_account_bookmarks(web_del)
        if plugin_add:
            for item in plugin_add:
                get_all_marks()[item['season_id']] = item
        if plugin_del:
            for item in plugin_del:
                del get_all_marks()[item]
        if sync_add:
            for item in sync_add:
                get_sync().append(item)
        if sync_del:
            for item in sync_del:
                get_sync().remove(item)
        Dict.Save()
        Log.Debug('> BOOKMARKS SYNCED <')
