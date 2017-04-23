# coding=utf-8

# Standard Library
from time import time
from functools import wraps

# Bundle Library
import messages as msgs
from DumbTools import DumbPrefs


def get_public_ip(external=True):
    if external:
        response = HTTP.Request(url='http://myexternalip.com/raw')
        return response.content
    else:
        return Network.PublicAddress


def make_title(season_number, name):
    if isinstance(season_number, list):
        season_number = season_number[0]
    if season_number == 0 or season_number == '0' or season_number is None:
        title = u'%s' % name
    else:
        title = u'%s сезон - %s' % (season_number, name)
    return title


def logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args and kwargs:
            Log.Debug('*** CALLED %s(%s, %s) ***' % (func.__name__, args, kwargs))
        elif args:
            Log.Debug('*** CALLED %s(%s) ***' % (func.__name__, args))
        elif kwargs:
            Log.Debug('*** CALLED %s(%s) ***' % (func.__name__, kwargs))
        else:
            Log.Debug('*** CALLED %s() ***' % func.__name__)
        return func(*args, **kwargs)
    return wrapper


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        Log.Debug('*** EXECUTION TOOK: %2.2f sec ***' % (end-start))
        return result
    return wrapper


def L(string):
    local_string = Locale.LocalString(string)
    return str(local_string).decode()


def F(string, *args):
    local_string = Locale.LocalStringWithFormat(string, *args)
    return str(local_string).decode()


def check_api_key_valid(api_key):
    if api_key == Prefs['api_key']:
        Log.Debug('>>> API_KEY IS VALID <<<')
        return True
    Log.Debug('>>> API_KEY IS NOT VALID <<<')
    return False


def update_api_key(api_key):
    return DumbPrefs('DumbPrefs', ObjectContainer()).Set(key='api_key', value=api_key)


def make_fake_url(**kwargs):
    fake_url = ''
    if kwargs:
        for k, v in kwargs.items():
            fake_url = fake_url + '#%s=%s' % (k, v)
        if 'X-Plex-Token' not in Request.Headers:
            # NB: if user not authorized on PMS
            raise Ex.MediaNotAuthorized
        fake_url = fake_url + '#%s=%s' % ('token', Request.Headers['X-Plex-Token'])
        fake_url = String.Encode(fake_url)
        return 'http://plex/seasonvar_ru/' + fake_url
    return None

# internal stuff

# def timer_with_logger(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         start = time()
#         result = func(*args, **kwargs)
#         end = time()
#         if args and kwargs:
#             Log.Debug('*** EXECUTED: %s(%s, %s) TIME: %2.2f sec ***' % (func.__name__, args, kwargs, end-start))
#         elif args:
#             Log.Debug('*** EXECUTED: %s(%s) TIME: %2.2f sec ***' % (func.__name__, args, end-start))
#         elif kwargs:
#             Log.Debug('*** EXECUTED: %s(%s) TIME: %2.2f sec ***' % (func.__name__, kwargs, end-start))
#         else:
#             Log.Debug('*** EXECUTED: %s() TIME: %2.2f sec ***' % (func.__name__, end-start))
#         return result
#     return wrapper
#
#
# remove duplicates from list of dicts by dict key
# def remove_duplicates(data, key):
#     seen_values = set()
#     without_duplicates = []
#     for item in data:
#         value = item[key]
#         if value not in seen_values:
#             without_duplicates.append(item)
#             seen_values.add(value)
#     return without_duplicates
