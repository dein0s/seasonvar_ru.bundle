# coding=utf-8

# Standart Library
from functools import wraps
from time import time

# Bundle Library
import messages as msgs


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
    try:
        return str(local_string).decode()
    except:
        return local_string


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
    # NB: Avoid ImportError
    from DumbTools import DumbPrefs
    return DumbPrefs('DumbPrefs', ObjectContainer()).Set(key='api_key', value=api_key)


def make_fake_url(**kwargs):
    fake_url = ''
    if kwargs:
        for k, v in kwargs.items():
            fake_url = fake_url + '#%s=%s' % (k, v)
        if 'X-Plex-Token' not in Request.Headers:
            # NB: User not authorized on PMS
            raise Ex.MediaNotAuthorized
        fake_url = fake_url + '#%s=%s' % ('token', Request.Headers['X-Plex-Token'])
        fake_url = String.Encode(fake_url)
        return 'http://plex/seasonvar_ru/' + fake_url
    return None
