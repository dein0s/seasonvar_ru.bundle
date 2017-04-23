# coding=utf-8

HISTORY_KEY = 'history'
try:
    HISTORY_MAX_LEN = int(Prefs['history_len'])
except:
    HISTORY_MAX_LEN = 50


def set_empty_history():
    Dict[HISTORY_KEY] = {}
    Dict.Save()


def init_history():
    if HISTORY_KEY not in Dict:
        set_empty_history()

def get_history():
    init_history()
    return Dict[HISTORY_KEY]

def push_to_history(data):
    history = get_history()
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
