# coding=utf-8

# Standart Library
from collections import OrderedDict

# Bundle Library
import api_seasonvar_data as api
import constants as cnst
from utils import logger, make_title

MAIN_PAGE_CACHE_TIME = 60 * 5  # 5 mins
SEASON_PAGE_CACHE_TIME = 60 * 5  # 5 mins
GET_UPDATE_LIST_DAYS_LIMIT = 7  # NB: max blocks on main page http://seasonvar


class Re(object):
    SEASON_TITLE_NUMBER = Regex(u'(\d+)\sсезон')
    SEASON_TITLE_NAME = Regex('\s(.*?)\/')
    SEASON_TITLE_NAME_ALT = Regex(u'Сериал\s(.*?)\sонлайн')
    SEASON_PLAYER_SECURE_MARK = Regex('\'secureMark\':\s\'(.*?)\',')
    SEASON_PLAYER_TIME = Regex('\'time\':\s(\d+)')
    PLAYER_PLAYLIST = Regex('pl\[\d+\]\s=\s"(.*?)";')
    PLAYER_DEFAULT_PLAYLIST = Regex('{\'0\':\s\"(.*?)\"};')
    TRANSLATE_NAME = Regex('/trans(.*?)/')
    EPISODE_COMMENT_NAME = Regex('^(.*?)\<')
    EPISODE_COMMENT_ID = Regex('^(\d{1,3})')
    EPISODE_COMMENT_TRANSLATE = Regex('\<br\>(.*?)$')
    SEASON_URL_ID = Regex('\-(\d+)\-')
    SEARCH_SUGGESTION_NAME = Regex('^(.*?)\s\/')
    SEARCH_SUGGESTION_NAME_ALT = Regex('^(.*?)\s\(')


def get_request(url, **kwargs):
    url = url if cnst.URL_SV.MAIN in url else cnst.URL_SV.MAIN + url
    headers = {
        'Host': 'seasonvar.ru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Cookie': 'playerHtml=true; uppodhtml5_volume=1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Origin': 'http://seasonvar.ru',
    }
    cacheTime = CACHE_1HOUR
    if 'cache' in kwargs.keys():
        cacheTime = kwargs.pop('cache')
    if 'headers' in kwargs.keys():
        headers.update(kwargs.pop('headers'))
    if 'cookies' in kwargs.keys():
        headers.update({'Cookie' : '; '.join('%s=%s' % (k, v) for k, v in kwargs.pop('cookies').items())})
    response = HTTP.Request(url=url, headers=headers, cacheTime=cacheTime, **kwargs)
    return response


def post_request(url, data, **kwargs):
    return get_request(url, values=data, **kwargs)


def get_update_list(day_count=1):
    """
    Accept numbers (int|str).
    Returns <OrderedDict> with parsed updates data.
    """
    day_count = int(day_count)
    if day_count > GET_UPDATE_LIST_DAYS_LIMIT:
        day_count = GET_UPDATE_LIST_DAYS_LIMIT
    result = OrderedDict()
    page_html = HTML.ElementFromString(get_request('/', cache=MAIN_PAGE_CACHE_TIME).content)
    day_blocks = page_html.findall('.' + cnst.XP_MainP.DAY)
    for d_block in day_blocks[:1 + day_count]:
        season_blocks = d_block.findall('.' + cnst.XP.LINK)
        for s_block in season_blocks:
            season_id = unicode(s_block.get('data-id'))
            title_element = s_block.find('.' + cnst.XP_MainP.SEASON_TITLE)
            update_message = s_block.find('.' + cnst.XP_MainP.SEASON_UPDATE_MSG).text_content().strip()
            number_text = title_element.tail.strip()
            name = title_element.text_content().strip()
            season_number = 0 if number_text == '' else Re.SEASON_TITLE_NUMBER.search(number_text).group(1)
            if season_id not in cnst.BLACKLISTED_SEASONS:
                if season_id not in result:
                    result[season_id] = {
                        'season_id': season_id,
                        'name': name,
                        'update_messages': [update_message],
                        'title': make_title(season_number, name),
                        # NB: otherwise need to request every season page and parse it
                        'thumb': cnst.URL_SV_CDN.MAIN + cnst.URL_SV_CDN.THUMB + '/%s.jpg' % season_id
                    }
                else:
                    result[season_id]['update_messages'].append(update_message)
    return result


def get_season_data_by_link(url):
    """
    Accept url or uri (string).
    Returns dict with parsed season data.
    """
    result = {}
    page_html = HTML.ElementFromString(get_request(url, cache=SEASON_PAGE_CACHE_TIME).content)
    season_id = unicode(page_html.find('.' + cnst.XP_SeasonP.MAIN).get('data-id-season'))
    if season_id not in cnst.BLACKLISTED_SEASONS:
        title_element = page_html.find('.' + cnst.XP_SeasonP.TITLE)
        title_text = title_element.text_content().strip()
        get_season_number = Re.SEASON_TITLE_NUMBER.search(title_text)
        if get_season_number:
            season_number = get_season_number.group(1)
        else:
            season_number = 0
        get_name = Re.SEASON_TITLE_NAME.search(title_text)
        if get_name:
            name = get_name.group(1)
        else:
            name = Re.SEASON_TITLE_NAME_ALT.search(title_text).group(1)
        ratings_block = page_html.findall('.' + cnst.XP_SeasonP.RATINGS + cnst.XP.SPAN)
        summary = page_html.find('.' + cnst.XP_SeasonP.INFO + cnst.XP.TEXT).text_content().strip()
        result = {
            'season_id': season_id,
            'name': name,
            'summary': summary,
            'season_number': int(season_number),
            'title': make_title(season_number, name),
            'thumb': make_thumb_url(season_id),
            'rating': average_rating(ratings_block),
            'playlist': get_season_playlist(page_html)
        }
        season_list = page_html.findall('.' + cnst.XP.H2 + cnst.XP.LINK)
        if len(season_list) > 1:
            other_season = OrderedDict()
            for item in season_list:
                item_title_text = item.text_content().strip()
                item_season_id = Re.SEASON_URL_ID.search(item.get('href')).group(1)
                item_season_number = Re.SEASON_TITLE_NUMBER.search(item_title_text).group(1)
                if item_season_id != season_id:
                    other_season[item_season_number] = item_season_id
            result['other_season'] = other_season
    return result


def get_season_playlist(page_html):
    """
    Accept <HtmlElement> object (http://lxml.de/api/lxml.html.HtmlElement-class.html).
    Returns <OrderedDict> with parsed playlist data.
    """
    result = OrderedDict()
    get_legal_player = page_html.find('.' + cnst.XP_SeasonP.LEGAL_PLAYER)
    get_block_player = page_html.find('.' + cnst.XP_SeasonP.BLOCK_PLAYER)
    season_id = page_html.find('.' + cnst.XP_SeasonP.MAIN).get('data-id-season')
    if get_legal_player or get_block_player:
        playlist_links = get_playlist_from_alt_player(season_id)
    else:
        playlist_links = get_playlist_from_player(page_html)
    for link in playlist_links:
        if cnst.URL_DATALOCK.MAIN in link:
            link_data = HTTP.Request(link, cacheTime=SEASON_PAGE_CACHE_TIME)
        else:
            link = String.Unquote(link.encode('utf-8'), usePlus=True).decode('utf-8')
            link_data = get_request(link, cache=SEASON_PAGE_CACHE_TIME)
        if True in [unsupported_translate in link for unsupported_translate in cnst.UNSUPPORTED_TRANSLATES]:
            continue
        playlist = JSON.ObjectFromString(link_data.content)['playlist']
        additional_id = len(playlist) + 100
        for episode in playlist:
            get_translate = Re.EPISODE_COMMENT_TRANSLATE.search(episode['comment'])
            translate = get_translate.group(1) if get_translate else ''
            if translate == '':
                translate = u'TRANSLATE_DEFAULT'
            if translate not in cnst.UNSUPPORTED_TRANSLATES:
                if translate not in result:
                    result[translate] = []
                if ' SD' in episode['comment']:
                    name = episode['comment'][:episode['comment'].find(' SD')]
                else:
                    name = Re.EPISODE_COMMENT_NAME.search(episode['comment']).group(1)
                get_episode_id = Re.EPISODE_COMMENT_ID.search(episode['comment'])
                if get_episode_id:
                    episode_id = get_episode_id.group(1)
                else:
                    episode_id = str(additional_id)
                    additional_id = additional_id + 1
                fmt_episode = {
                    'link': episode['file'],
                    'name': name,
                    'perevod': translate,
                    'episode_id': episode_id
                }
                result[translate].append(fmt_episode)
    return result


def get_playlist_from_player(page_html):
    """
    Accept <HtmlElement> object (http://lxml.de/api/lxml.html.HtmlElement-class.html).
    Returns list with parsed links.
    """
    # NB: xpath() because find() and findall() doesn't support entire XPath
    # ref. to http://lxml.de/FAQ.html#what-are-the-findall-and-xpath-methods-on-element-tree
    get_player = page_html.xpath('.' + cnst.XP_SeasonP.PLAYER + cnst.XP.SCRIPT + cnst.XP.WITH_TEXT % 'data4play')[0]
    get_player_text = get_player.text_content()
    season_id = page_html.find('.' + cnst.XP_SeasonP.MAIN).get('data-id-season')
    player_secure_mark = Re.SEASON_PLAYER_SECURE_MARK.search(get_player_text).group(1)
    player_time = Re.SEASON_PLAYER_TIME.search(get_player_text).group(1)
    player_data = {
        'id': season_id,
        'secure': player_secure_mark,
        'time': player_time,
        'type': 'html5',
    }
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    player_page = get_request(cnst.URL_SV.PLAYER, cache=SEASON_PAGE_CACHE_TIME, headers=headers, values=player_data)
    playlist_links = Re.PLAYER_PLAYLIST.findall(player_page.content)
    default_playlist = Re.PLAYER_DEFAULT_PLAYLIST.search(player_page.content).group(1)
    playlist_links.append(default_playlist)
    return playlist_links


def get_playlist_from_alt_player(season_id):
    """
    Accept season id (number).
    Returns list with parsed link.
    """
    url = cnst.URL_DATALOCK.MAIN + cnst.URL_DATALOCK.PLAYER + '/%s' % season_id
    page_html = HTML.ElementFromString(HTTP.Request(url, cacheTime=0).content)
    packed_script = page_html.xpath('.' + cnst.XP.SCRIPT + cnst.XP.WITH_TEXT % ';eval')[0]
    packed_script_text = packed_script.text_content()
    unpack_data = {'urlin': packed_script_text}
    unpack_response = HTTP.Request(url=cnst.URL_COMMON.UNPACK_SERVICE, cacheTime=0, values=unpack_data)
    re_pattern = Regex('\/\/datalock.ru/playlist(.*?)\"')
    link_part = re_pattern.search(unpack_response.content).group(1)
    link = cnst.URL_DATALOCK.MAIN + cnst.URL_DATALOCK.PLAYLIST + link_part
    return [link]


def get_search_results(query):
    """
    Accept query text (string).
    Returns <OrderedDict> with parsed search results data.
    """
    url = cnst.URL_SV.AUTOCOMPLETE + '?query=%s' % query
    response_json = JSON.ObjectFromString(get_request(url, cache=MAIN_PAGE_CACHE_TIME).content)
    result = {}
    for index, item in enumerate(response_json['data']):
        if 'serial-' in item:
            season_id = response_json['id'][index]
            suggestion = response_json['suggestions'][index]
            get_name = Re.SEARCH_SUGGESTION_NAME.search(suggestion) or Re.SEARCH_SUGGESTION_NAME_ALT.search(suggestion)
            if get_name:
                name = get_name.group(1)
            else:
                name = suggestion
            get_season_number = Re.SEASON_TITLE_NUMBER.search(suggestion)
            if get_season_number:
                season_number = get_season_number.group(1)
            else:
                season_number = 0
            result[season_id] = {
                'season_id': season_id,
                'name': name,
                'season': int(season_number),
                'title': make_title(season_number, name),
                'thumb': make_thumb_url(season_id),
            }
    sorted_result = OrderedDict(sorted(result.items(), key=lambda k: (k[1]['name'], k[1]['season']), reverse=False))
    return sorted_result


def get_season_link_by_id(show_name, season_id):
    """
    Accept season id (number) and show name (string).
    Returns URI if link found or None.
    """
    # NB: http://seasonvar.ru/autocomplete.php cannot proceed '-'
    if '-' in show_name:
        show_name = show_name.split('-')[0]
    url = cnst.URL_SV.AUTOCOMPLETE + '?query=%s' % show_name
    response_json = JSON.ObjectFromString(get_request(url, cache=0).content)
    for link in response_json['data']:
        if season_id in link:
            return '/' + link
    return None


def get_season_data(show_name, season_id):
    link = get_season_link_by_id(show_name, season_id)
    result = get_season_data_by_link(link)
    return result


def make_thumb_url(season_id):
    url = cnst.URL_SV_CDN.MAIN + cnst.URL_SV_CDN.THUMB + '/%s.jpg' % season_id
    return url


def average_rating(elements):
    """
    Accept list of <HtmlElement> objects (http://lxml.de/api/lxml.html.HtmlElement-class.html).
    Returns float averate rating.
    """
    result = 0.0
    if elements:
        for element in elements:
            result += float(element.text_content())
        # NB: know why? because FUCK YOU! that's why... FrameworkException: Operator '/=' is not supported
        result = result / len(elements)
    return result
