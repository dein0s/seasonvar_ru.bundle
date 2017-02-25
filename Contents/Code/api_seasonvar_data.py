# -*- coding: UTF-8 -*-
import constants
from utils import logger
# import requests  # TODO: think about switching to it


API_URL = 'http://api.seasonvar.ru'

class COMMANDS(object):
    GET_COUNTRY_LIST = 'getCountryList'
    GET_GENRE_LIST = 'getGenreList'
    SEARCH = 'search'
    GET_SEASON = 'getSeason'
    GET_SEASON_LIST = 'getSeasonList'
    GET_SERIAL_LIST = 'getSerialList'
    GET_UPDATE_LIST = 'getUpdateList'


@logger
def make_request(command, **kwargs):
    if not Prefs['api_key']:
        Log.Error('>>> MISSING API_KEY IN CHANNEL SETTINGS <<<')
        return None
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0'}
    data = {
        'key': Prefs['api_key'],
        'command': command
        }
    if kwargs:
        for k, v in kwargs.items():
            if v:
                # NB: this is because Plex uses urllib2 instead of requests and we need to pass an array
                if k == 'country':
                    for i_c, c in enumerate(kwargs['country']):
                        data['country[%s]' % i_c] = c
                # NB: this is because Plex uses urllib2 instead of requests and we need to pass an array
                elif k == 'genre':
                    for i_g, g in enumerate(kwargs['genre']):
                        data['genre[%s]' % i_g] = g
                else:
                    data[k] = v
    response = HTTP.Request(url=API_URL, values=data, cacheTime=CACHE_1HOUR)
    result = JSON.ObjectFromString(response.content)
    if result == 'null':
        Log.Error('>>> Received empty response <<<')
        return None
    if isinstance(result, dict) and 'error' in result:
        Log.Error('>>> Received error in API response: %s <<<' % result['error'])
        return None
    return result


def get_update_list(day_count=1, season_info=True):
    response = make_request(COMMANDS.GET_UPDATE_LIST, day_count=day_count, seasonInfo=season_info)
    return response


def get_season(season_id):
    response = make_request(COMMANDS.GET_SEASON, season_id=season_id)
    return response


def get_genre_list():
    response = make_request(COMMANDS.GET_GENRE_LIST)
    return response


def get_country_list():
    response = make_request(COMMANDS.GET_COUNTRY_LIST)
    return response


def search(query, country=[], genre=[]):
    response = make_request(COMMANDS.SEARCH, query=query, country=country, genre=genre)
    return response


def reset_session():
    HTTP.ClearCookies()
    HTTP.ClearCache()
    return None
