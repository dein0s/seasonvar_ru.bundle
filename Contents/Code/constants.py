# coding=utf-8

API_GET_UPDATE_LIST_DAYS_LIMIT = 14  # NB: JSON conversion limit - maximum size 5242880
WEB_GET_UPDATE_LIST_DAYS_LIMIT = 7  # NB: Max blocks on main page http://seasonvar
HISTORY_KEY = 'history'
CACHE_INVALID_AFTER_KEY = 'invalid_after'
SEASON_CACHE_KEY = 'season_cache'
SEASON_CACHE_INVALIDATE = 60 * 5
UPDATES_CACHE_KEY = 'updates_cache'

UNSUPPORTED_TRANSLATES = [u'Субтитры', u'Трейлеры', u'Субтитры VP']

BLACKLISTED_SEASONS = ['12678', '14924']


class URL_SV(object):
    MAIN = 'http://seasonvar.ru'
    API = '/?mod=api'
    LOGIN = '/?mod=login'
    PLAYER = '/player.php'
    AUTOCOMPLETE = '/autocomplete.php'
    BOOKMARKS = '/jsonMark.php'
    SEARCH = '/search'


class URL_DATALOCK(object):
    MAIN = 'http://datalock.ru'
    PLAYER = '/player'
    PLAYLIST = '/playlist'


class URL_SV_CDN(object):
    MAIN = 'http://cdn.seasonvar.ru'
    THUMB = '/oblojka'
    THUMB_SMALL = '/oblojka/small'


class URL_COMMON(object):
    UNPACK_SERVICE = 'http://jsunpack.jeek.org/?'


class Re(object):

    class MainPage(object):
        pass


class XP(object):
    """
    General xpath locators.
    """
    LINK = '//a'
    SCRIPT = '//script'
    SPAN = '//span'
    TEXT = '//p'
    H1 = '//h1'
    H2 = '//h2'
    ROW = '//tr'
    COL = '//td'
    WITH_TEXT = '[contains(text(), "%s")]'


class XP_MainP(object):
    """
    Main page (http://seasonvar.ru/) xpath locators.
    """
    DAY = '//div[@class="news"]'
    LOGGED_IN = '//li[@class="headmenu-title"]'
    PREMIUM = '//body[@class="premium"]'
    SEASON_TITLE = '//div[@class="news_n"]'
    SEASON_UPDATE_MSG = '//span[@class="news_s"]'


class XP_SeasonP(object):
    """
    Season page (http://seasonvar.ru/serial-<***>.html) xpath locators.
    """
    INFO = '//div[@class="pgs-sinfo-info"]'
    MAIN = '//div[@class="pgs-sinfo"]'
    PLAYER = '//div[@class="pgs-player"]'
    RATINGS = '//div[@class="pgs-sinfo_list rating"]'
    TITLE = '//h1[@class="pgs-sinfo-title"]'
    BLOCK_PLAYER = '//div[@class="pgs-player-block"]'
    LEGAL_PLAYER = '//div[@class="legal"]'


class XP_ApiP(object):
    """
    API page (http://seasonvar.ru/?mod=api) xpath locators.
    """
    API_KEY = '//div[@class="pgs-msg"]/input'
