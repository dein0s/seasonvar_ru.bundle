# coding=utf-8

# Bundle Library
import constants as cnst
from api_seasonvar_data import get_genre_list
from utils import make_title
from web_seasonvar_data import get_request, post_request


def reset_session():
    HTTP.ClearCookies()
    HTTP.ClearCache()
    return None


def login():
    login_retries = int(Prefs['login_retries'])
    cookies = None
    while login_retries > 0:
        if cookies is None:
            data = {
            'login': Prefs['username'],
            'password': Prefs['password']
            }
            post_request(cnst.URL_SV.LOGIN, data, cache=0)
            get_cookies = HTTP.CookiesForURL(cnst.URL_SV.MAIN)
            if get_cookies:
                cookies = {}
                if isinstance(get_cookies, str):
                    k, v = get_cookies.split('=')
                    cookies[k] = v
            # NB: know why? because FUCK YOU! that's why... FrameworkException: Operator '-=' is not supported
            login_retries = login_retries - 1
            continue
        else:
            return cookies
    Log.Error('>>> NOT LOGGED IN AFTER %s RETRIES <<<' % Prefs['login_retries'])
    return None


def is_premium(session_cookies):
    if session_cookies is not None:
        response = get_request(cnst.URL_SV.MAIN, cache=0, cookies=session_cookies)
        page_html = HTML.ElementFromString(response.content)
        premium = page_html.find('.' + cnst.XP_MainP.PREMIUM)
        if premium is not None:
            Log.Debug('> PREMIUM ACTIVE <')
            return True
    Log.Error('>>> PREMIUM NOT ACTIVE <<<')
    return False


def is_logged_in(session_cookies):
    if session_cookies is not None:
        response = get_request(cnst.URL_SV.MAIN, cache=0, cookies=session_cookies)
        page_html = HTML.ElementFromString(response.content)
        logged_in = page_html.find('.' + cnst.XP_MainP.LOGGED_IN)
        if logged_in is not None:
            Log.Debug('> LOGGED IN <')
            return True
    Log.Error('>>> NOT LOGGED IN <<<')
    return False


def get_account_bookmarks():
    cookies = login()
    if is_logged_in(cookies):
        bookmarks = {}
        response = get_request(cnst.URL_SV.BOOKMARKS, cache=0, cookies=cookies)
        response_json = JSON.ObjectFromString(response.content)
        for k, v, in response_json['data'].items():
            if v:
                for item in v:
                    last_watched = int(item['series']) if item['series'] != '-1' else 0
                    bookmarks[item['seasonId']] = {
                        'season_id': item['seasonId'],
                        'name': item['name'],
                        'last_watched': last_watched,
                        'title': make_title(item['season'], item['name']),
                        'thumb': item['imgUrl']
                    }
        return bookmarks
    Log.Error('>>> YOU MUST BE LOGGED IN TO GET BOOKMARKS <<<')
    return None


def add_account_bookmarks(bookmarks):
    """
    Accept list of dicts with bookmarks
    """
    cookies = login()
    if is_logged_in(cookies):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        for item in bookmarks:
            data = {
                'id': item['season_id'],
                'minute': 0,
                'pauseadd': True,
                'second': 0,
                'seria': item['last_watched'],
                'tran': 0
            }
            response = post_request(cnst.URL_SV.BOOKMARKS, data, cache=0, cookies=cookies, headers=headers)
            response_json = JSON.ObjectFromString(response.content)
        return True
    Log.Debug('>>> YOU MUST BE LOGGED IN TO ADD BOOKMARK <<<')
    return False


def del_account_bookmarks(bookmarks):
    """
    Accept list of season ids
    """
    cookies = login()
    if is_logged_in(cookies):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        for item in bookmarks:
            data = {
                'delId': item
            }
            response = post_request(cnst.URL_SV.BOOKMARKS, data, cache=0, cookies=cookies, headers=headers)
            response_json = JSON.ObjectFromString(response.content)
            return True
    Log.Debug('>>> YOU MUST BE LOGGED IN TO DEL BOOKMARK <<<')
    return False


def get_api_key():
    cookies = login()
    if is_logged_in(cookies):
        if is_premium(cookies):
            page = get_request(cnst.URL_SV.API, cache=0, cookies=cookies)
            page_html = HTML.ElementFromString(page.content)
            api_key = page_html.find('.' + cnst.XP_ApiP.API_KEY).get('value')
            Log.Debug('> SUCCESSFULLY RETRIEVED API_KEY FROM WEB <')
            return api_key
    Log.Error('>>> YOU MUST HAVE PREMIUM ACCOUNT TO GET AN API_KEY <<<')
    return None


def check_ip_and_allow(ip):
    cookies = login()
    if is_logged_in(cookies):
        if is_premium(cookies):
            get_genre_list()  # NB: api_request to add ip to the table
            page = get_request(cnst.URL_SV.API, cache=0, cookies=cookies)
            page_html = HTML.ElementFromString(page.content)
            rows = page_html.findall('.' + cnst.XP.ROW)
            for row in rows:
                for col in row.getchildren():
                    if ip in col.text_content().strip():
                        allowed = row.find('.' + cnst.XP.COL + cnst.XP.LINK)
                        if allowed is not None:
                            Log.Debug('> IP %s IS NOT ALLOWED, REQUESTING "ALLOW" LINK <' % ip)
                            allowed_link = allowed.get('href')
                            headers = {'Referer': cnst.URL_SV.MAIN + cnst.URL_SV.API}
                            get_request(allowed_link, cache=0, headers=headers, cookies=cookies)
                            return True
                        Log.Debug('> IP %s ALLOWED <' % ip)
                        return True
    Log.Error('>>> YOU MUST HAVE PREMIUM ACCOUNT TO ALLOW IP %s <<<' % ip)
    return False
