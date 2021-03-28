import pandas as pd
import requests as rq
from oresapi import Session

WM_API = 'https://wikimedia.org/api/rest_v1'

EDITOR_ACT_ALL = 'all-activity-levels'
EDITOR_ACT_1_4 = '1..4-edits'
EDITOR_ACT_5_24 = '5..24-edits'
EDITOR_ACT_25_99 = '25..99-edits'
EDITOR_ACT_100 = '100..-edits'
EDITOR_ALL_ACTIVITY_LEVELS = [EDITOR_ACT_ALL, EDITOR_ACT_1_4, EDITOR_ACT_5_24, EDITOR_ACT_25_99, EDITOR_ACT_100]

EDITOR_TYPE_ANON = 'anonymous'
EDITOR_TYPE_USER = 'user'
EDITOR_TYPE_GBOT = 'group-bot'
EDITOR_TYPE_NBOT = 'name-bot'
EDITOR_ALL_TYPES = [EDITOR_TYPE_ANON, EDITOR_TYPE_USER, EDITOR_TYPE_GBOT, EDITOR_TYPE_NBOT]

PV_ACCESS_ALL = 'all-access'
PV_ACCESS_DESKTOP = 'desktop'
PV_ACCESS_MOBAPP = 'mobile-app'
PV_ACCESS_MOBWEB = 'mobile-web'

PV_AGENT_ALL = 'all-agents'
PV_AGENT_USER = 'user'
PV_AGENT_SPIDER = 'spider'
PV_AGENT_AUTOMATED = 'automated'

PV_GRANULARITY_HOUR = 'hourly'
PV_GRANULARITY_DAY = 'daily'
PV_GRANULARITY_MONTH = 'monthly'


def retrieve_pageviews_aggregate(lang, start=20180101, end=20201201, access=PV_ACCESS_ALL,
                                 granularity=PV_GRANULARITY_DAY, agent=PV_AGENT_ALL):
    response = rq.get(f'{WM_API}/metrics/pageviews/aggregate/{lang}.wikipedia.org/{access}/{agent}/{granularity}'
                      f'/{start}/{end}')
    lang_result = {'date': [], 'views': []}
    for res in response.json()['items']:
        lang_result['date'].append(pd.to_datetime(res['timestamp'][:-2], format='%Y%m%d'))
        lang_result['views'].append(res['views'])
    return pd.DataFrame(lang_result)


def retrieve_pageviews_aggregate_all_langs(codes, start=20180101, end=20201201, access=PV_ACCESS_ALL,
                                           granularity=PV_GRANULARITY_DAY, agent=PV_AGENT_ALL):
    df_lang_list = []
    for code in codes:
        df_lang = retrieve_pageviews_aggregate(code, start, end, access, granularity, agent)
        df_lang['code'] = code
        df_lang_list.append(df_lang)
    return pd.concat(df_lang_list)


def retrieve_edit_counts(lang, start=20180101, end=20201201, granularity='daily', editor_type='user',
                         page_type='content'):
    response = rq.get(
        f'{WM_API}/metrics/edits/aggregate/{lang}.wikipedia.org/{editor_type}/{page_type}/{granularity}/{start}/{end}')
    data = response.json()
    df_edits = pd.DataFrame(data['items'][0]['results'])
    df_edits['date'] = pd.to_datetime(df_edits.timestamp).dt.date
    df_edits['edits'] = df_edits.edits
    df_edits['user_kind'] = editor_type
    df_edits['lang'] = lang
    return df_edits[['edits', 'date', 'user_kind', 'lang']]


def retrieve_edit_counts_edit_types_lang(lang, start=20180101, end=20201201, granularity='daily', page_type='content'):
    pd_list = []
    for editor_type in EDITOR_ALL_TYPES:
        pd_list.append(
            retrieve_edit_counts(lang, start, end, granularity, editor_type, page_type).set_index('date', drop=True))
    return pd.concat(pd_list, axis=0)


def retrieve_all_edit_counts(codes, start=20180101, end=20201201, granularity='daily', page_type='content'):
    pd_list = [retrieve_edit_counts_edit_types_lang(code, start, end, granularity, page_type) for code in codes]
    return pd.concat(pd_list, axis=0)


def retrieve_newly_registered(lang, start=20180101, end=20201201, granularity='daily'):
    response = rq.get(f'{WM_API}/metrics/registered-users/new/{lang}.wikipedia.org/{granularity}/{start}/{end}')
    data = response.json()
    df_act = pd.DataFrame(data['items'][0]['results'])
    df_act['date'] = pd.to_datetime(df_act.timestamp).dt.date
    df_act['newly_registered'] = df_act.new_registered_users
    return df_act[['newly_registered', 'date']]


def retrieve_newly_registered_all_langs(codes, start=20180101, end=20201201, granularity='daily'):
    pd_list = []
    for code in codes:
        pd_list.append(retrieve_newly_registered(code, start, end, granularity).set_index('date'))
        pd_list[-1]['lang'] = code
    return pd.concat(pd_list, axis=0)


def retrieve_active_editors(lang, activity_level=EDITOR_ACT_ALL, start=20180101, end=20201201,
                            granularity='daily', editor_type='user', page_type='content'):
    response = rq.get(f'{WM_API}/metrics/editors/aggregate/{lang}.wikipedia.org/{editor_type}/{page_type}/'
                      f'{activity_level}/{granularity}/{start}/{end}')
    data = response.json()
    df_act = pd.DataFrame(data['items'][0]['results'])
    df_act['date'] = pd.to_datetime(df_act.timestamp).dt.date
    df_act[activity_level] = df_act.editors
    return df_act[['date', activity_level]]


def retrieve_all_editor_activity_levels(lang, start=20180101, end=20201201, granularity='daily', editor_type='user',
                                        page_type='content'):
    pd_list = []
    for activity_level in EDITOR_ALL_ACTIVITY_LEVELS:
        pd_list.append(retrieve_active_editors(lang, activity_level, start, end, granularity, editor_type, page_type))

    pd_list = [df.set_index('date', drop=True) for df in pd_list]
    pd_merged = pd.concat(pd_list, axis=1)
    pd_merged['code'] = lang
    return pd_merged


def retrieve_all_editor_activity_levels_for_all_wikis(codes, start=20171201, end=20201201, granularity='daily',
                                                      editor_type='user', page_type='content'):
    pd_list = [
        retrieve_all_editor_activity_levels(code, start, end, granularity, editor_type, page_type) for code in codes]
    return pd.concat(pd_list, axis=0)


def retrieve_name_bots(lang, from_date=20180101, to_date=20200517):
    response = rq.get(
        f'{WM_API}/metrics/edits/aggregate/{lang}.wikipedia.org/name-bot/content/daily/{from_date}/{to_date}')
    data = response.json()
    df_namebots = pd.DataFrame(data['items'][0]['results'])
    df_namebots['date'] = pd.to_datetime(df_namebots.timestamp)
    df_namebots['count'] = df_namebots.edits
    return df_namebots[['date', 'count']]


def load_session(user_agent, host='https://ores.wikimedia.org', retries=5, batch_size=50, parallel_requests=4):
    # e.g. user_agent = 'th.ruprechter@gmail.com'
    return Session(host, user_agent=user_agent, retries=retries, batch_size=batch_size,
                   parallel_requests=parallel_requests)
