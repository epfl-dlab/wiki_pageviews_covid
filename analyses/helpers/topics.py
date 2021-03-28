import numpy as np
from dateutil.relativedelta import relativedelta
import statsmodels.formula.api as smf
import datetime
import statsmodels
import pandas as pd
from .diffs_n_diffs import get_standard_error_sum
from .vars import topics, codes

order_topics = [
    # "Persistent Increase"
    'Culture.Media.Video games',
    'Culture.Media.Books',
    'Culture.Internet culture',
    'Culture.Visual arts.Fashion',
    'Culture.Biography.Biography*',
    # "Persistent Decrease"
    'Geography.Regions.Asia.West Asia',
    'Culture.Sports',
    # "Transient Increase"
    'Culture.Media.Entertainment',
    'Culture.Media.Films',
    'Geography.Regions.Americas.South America',
    'Culture.Media.Television',
    'Culture.Literature',
    'STEM.Biology',
    'Geography.Regions.Americas.Central America',
    # "Transient Decrease"
    'Culture.Food and drink',
    'Geography.Regions.Asia.Central Asia',
    'STEM.Libraries & Information',
    'Geography.Regions.Africa.Northern Africa',
    'STEM.Engineering',
    'History and Society.Transportation',
    'Culture.Visual arts.Architecture',
    # "Eventual Increase"
    'STEM.Mathematics',
    'Geography.Regions.Africa.Eastern Africa',
    'Geography.Regions.Africa.Central Africa',
    'Culture.Linguistics',
    'STEM.Space',
    'Culture.Performing arts',
    # Eventual Decrease
    'Geography.Regions.Europe.Eastern Europe',
    'Geography.Regions.Asia.North Asia',
    'Geography.Regions.Africa.Southern Africa',
    'STEM.Medicine & Health',
    # Untouched
    'Culture.Visual arts.Comics and Anime',
    'Geography.Regions.Americas.North America', 'Culture.Media.Radio',
    'Geography.Regions.Africa.Western Africa', 'STEM.Physics',
    'Geography.Regions.Asia.South Asia', 'STEM.Chemistry',
    'History and Society.Military and warfare',
    'Geography.Regions.Asia.Southeast Asia', 'Culture.Media.Music',
    'Geography.Regions.Europe.Northern Europe',
    'History and Society.History', 'Geography.Regions.Oceania',
    'History and Society.Society', 'Geography.Regions.Asia.East Asia',
    'Culture.Philosophy and religion', 'STEM.Technology',
    'STEM.Earth and environment',
    'History and Society.Business and economics',
    'Geography.Geographical',
    'History and Society.Politics and government',
    'Culture.Media.Software', 'STEM.Computing',
    'Geography.Regions.Europe.Western Europe',
    'History and Society.Education',
    'Geography.Regions.Europe.Southern Europe'
]

colors_z = [(5, "white", "Persistent Increase"),
            (2, "tab:gray", "Persistent Decrease"),
            (7, "white", "Transient Increase"),
            (7, "tab:gray", "Transient Decrease"),
            # (6, "white", "Reversed Increase "),
            # (1, "tab:gray", "Reverted Decrease"),
            (6, "white", "Eventual Increase"),
            (4, "tab:gray", "Eventual Decrease"),
            (26, "white", "Unchanged"),
            ]

order_topics = np.array(order_topics)[::-1]


def get_diffs_in_diffs_result_topics(df):
    res_ = smf.ols(formula='value_pct ~  C(topic) * C(pos_dummy) * C(treated_dummy)', data=df).fit()
    res = res_.get_robustcov_results(cov_type='HC0')
    res = statsmodels.regression.linear_model.RegressionResultsWrapper(res)

    print("R2: {}".format(res.rsquared))
    print("params:", len(res.params))
    df_list = []

    for topic in topics:
        str_baseline = 'C(pos_dummy)[T.1]:C(treated_dummy)[T.1]'
        if topic == "Culture.Biography.Biography*":
            val = res.params[str_baseline]
            std = get_standard_error_sum(res, [str_baseline])

        else:
            tmp_str = 'C(topic)[T.{}]:C(pos_dummy)[T.1]:C(treated_dummy)[T.1]'
            val = res.params[str_baseline] + \
                  res.params[tmp_str.format(topic)]
            print(val)

            std = get_standard_error_sum(res, [str_baseline, tmp_str.format(topic)])

        tmp_dict = {
            "topic": topic,
            "low": val - 2 * std,
            "high": val + 2 * std,
            "val": val,
            "pval": (val - 2 * std > 0) or (val + 2 * std < 0),
            "std": std
        }

        df_list.append(tmp_dict)

    return pd.DataFrame(df_list)


def get_df_pageviews_topics(agg, intervention_pre_f, delta_pre, intervention_pos_f, delta_pos, time_int):
    df_list = []

    for lang in codes:
        for key in agg[lang]['topics'].keys():
            y = agg[lang]['topics'][key]['sum'] + agg[lang + ".m"]['topics'][key]['sum']

            norm_desktop = agg[lang]['topics'][key]['sum'].values / y
            norm_mobile = agg[lang + ".m"]['topics'][key]['sum'].values / y

            y_pct = agg[lang]['topics'][key]['percent'] * norm_desktop + agg[lang + ".m"]['topics'][key][
                'percent'] * norm_mobile

            x = agg[lang]["sum"].index

            names = [("pre", "treated"), ("pos", "treated"), ("pre", "control"), ("pos", "control")]
            intervention_pre = intervention_pre_f(lang, delta_pre)
            intervention_pos = intervention_pos_f(lang, delta_pos)

            pre_treated = [intervention_pre - relativedelta(days=time_int), intervention_pre]
            pos_treated = [intervention_pos,
                           min(intervention_pos + relativedelta(days=time_int), pd.to_datetime("31st of July of 2020"))]

            pre_control = [pre_treated[0] - relativedelta(years=1), pre_treated[1] - relativedelta(years=1)]
            pos_control = [pos_treated[0] - relativedelta(years=1), pos_treated[1] - relativedelta(years=1)]
            baseline = (20190101, 20191231)

            start_baseline = datetime.datetime.strptime(str(baseline[0]), "%Y%m%d")
            end_baseline = datetime.datetime.strptime(str(baseline[1]), "%Y%m%d")
            mask_baseline = (x <= end_baseline) & (x >= start_baseline)

            for idx, dates in enumerate([pre_treated, pos_treated, pre_control, pos_control]):

                mask = (x >= pd.to_datetime(dates[0])) & \
                       (x < pd.to_datetime(dates[1]))

                for mean_value, mean_value_pct in zip(y[mask].values, y_pct[mask].values):
                    if mean_value <= 0:
                        return None, y[mask]

                    df_list.append({
                        "lang": lang,
                        "period": names[idx][0],
                        "group": names[idx][1],
                        "value_pct": np.log(mean_value_pct),
                        "value_log": np.log(mean_value),
                        "topic": key
                    })

    df_pageviews = pd.DataFrame(df_list)

    df_pageviews["pos_dummy"] = (df_pageviews.period == "pos").astype(int)
    df_pageviews["treated_dummy"] = (df_pageviews.group == "treated").astype(int)

    #     df_pageviews['value_pct'] = (df_pageviews['value_pct'] - df_pageviews['value_pct'].mean())\
    #                     / df_pageviews['value_pct'].std()

    df_pageviews_results = get_diffs_in_diffs_result_topics(df_pageviews)
    return df_pageviews, df_pageviews_results
