# coding=utf-8

# Standard Library
from collections import OrderedDict

# Bundle Library
import constants as cnst
import api_seasonvar_data as api
import web_seasonvar_data as web
from utils import make_title

# TODO: add trailers as extras Framework.bundle/Contents/Resources/Versions/2/Models/Metadata/tv_models.pym

EPISODE_ID_PATTERN = r'^(\d{1,3})'
API_GET_UPDATE_LIST_DAYS_LIMIT = 14  # NB: JSON conversion limit - maximum size 5242880


def get_latest_updates(day_count=1):
    day_count = int(day_count)
    if day_count > API_GET_UPDATE_LIST_DAYS_LIMIT:
        day_count = API_GET_UPDATE_LIST_DAYS_LIMIT
    if Prefs['force_web']:
        return web.get_update_list(day_count)
    if Prefs['api_key']:
        data = api.get_update_list(day_count, season_info=True)
        if data:
            result = format_api_updates_data(data)
            return result
    result = web.get_update_list(day_count)
    if result:
        return result
    else:
        raise Ex.MediaNotAvailable


def get_search_results(query, country=[], genre=[]):
    if query is None:
        raise Ex.MediaNotAvailable
    if Prefs['force_web']:
        return web.get_search_results(query)
    if Prefs['api_key']:
        data = api.search(query, country=country, genre=genre)
        if data:
            result = format_api_search_data(data)
            return result
    result = web.get_search_results(query)
    if result:
        return result
    else:
        raise Ex.MediaNotAvailable


def get_season_data(show_name, season_id):
    if Prefs['force_web']:
        return web.get_season_data(show_name, season_id)
    if Prefs['api_key']:
        data = api.get_season(season_id)
        if data:
            result = format_api_season_data(data)
            return result
    result = web.get_season_data(show_name, season_id)
    if result:
        return result
    else:
        raise Ex.MediaNotAvailable


def get_genre_list():
    data = api.get_genre_list()
    return data


def get_country_list():
    data = api.get_country_list()
    return data


def format_api_season_data(data):
    result = {
        'season_id': data['id'],
        'name': data['name'],
        'summary': data['description'],
        'season_number': data['season_number'],  # NB: can be 0
        'title': make_title(data.get('season_number'), data['name']),
        'thumb_small': data['poster_small'],
        'thumb': data['poster'],
        'rating': average_rating(data.get('rating')),
        'playlist': {}
    }
    if 'other_season' in data:
        result['other_season'] = data['other_season']
    if 'playlist' in data:
        for episode in data['playlist']:
            episode_id = Regex(EPISODE_ID_PATTERN).search(episode['name'])
            episode['episode_id'] = episode_id.group(1) if episode_id else episode['name']
            if 'perevod' not in episode:
                if 'TRANSLATE_DEFAULT' in result['playlist']:
                    result['playlist']['TRANSLATE_DEFAULT'].append(episode)
                else:
                    result['playlist']['TRANSLATE_DEFAULT'] = [episode]
            else:
                if episode['perevod'] not in cnst.UNSUPPORTED_TRANSLATES:
                    if episode['perevod'] in result['playlist']:
                        result['playlist'][episode['perevod']].append(episode)
                    else:
                        result['playlist'][episode['perevod']] = [episode]
    return result


def format_api_updates_data(data):
    result = OrderedDict()
    for item in data:
        if item['id'] not in cnst.BLACKLISTED_SEASONS:
            if item['id'] not in result and item['id']:
                result[item['id']] = {
                    'season_id': item['id'],
                    'name': item['name'],
                    'thumb': item['poster'],
                    'title': make_title(item.get('season'), item['name']),
                    'update_messages': [item['message']]
                }
            else:
                result[item['id']]['update_messages'].append(item['message'])
    return result


def format_api_search_data(data):
    result = OrderedDict()
    for item in data:
        if item['id'] not in cnst.BLACKLISTED_SEASONS:
            result[item['id']] = {
                'season_id': item['id'],
                'name': item['name'],
                'thumb': item['poster'],
                'title': make_title(item.get('season'), item['name']),
            }
    return result


def average_rating(ratings):
    result = 0.0
    if ratings:
        for value in ratings.itervalues():
            result += float(value['ratio'])
        # NB: know why? because FUCK YOU! that's why... FrameworkException: Operator '/=' is not supported
        result = result / len(ratings)
    return result
