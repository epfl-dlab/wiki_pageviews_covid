from dateutil.relativedelta import relativedelta
import statsmodels.formula.api as smf
import pandas as pd
import statsmodels
import numpy as np
import datetime


def get_standard_error_sum(results, covariates):
    '''
    #95CI is approximated with +- 2 sum_variance_standard_error
    '''
    # get the variance covariance matrix
    # print(covariates)
    vcov = results.cov_params() \
        .loc[covariates, covariates].values

    # calculate the sum of all pair wise covariances by summing up off-diagonal entries
    off_dia_sum = np.sum(vcov)
    # variance of a sum of variables is the square root
    return np.sqrt(off_dia_sum)


def get_diffs_in_diffs_result(df, codes):
    res_ = smf.ols(formula='value_log ~  pos_dummy * treated_dummy * lang ', data=df).fit()

    res = res_.get_robustcov_results(cov_type='HC0')
    res = statsmodels.regression.linear_model.RegressionResultsWrapper(res)

    print("R2: {}".format(res.rsquared))
    df_list = []

    for lang in codes:
        if lang == "da":
            val = res.params['pos_dummy:treated_dummy']
            std = get_standard_error_sum(res, ['pos_dummy:treated_dummy'])

        else:

            val = res.params['pos_dummy:treated_dummy'] + \
                  res.params['pos_dummy:treated_dummy:lang[T.{}]'.format(lang)]

            std = get_standard_error_sum(res, ['pos_dummy:treated_dummy',
                                               'pos_dummy:treated_dummy:lang[T.{}]'.format(lang)])

        tmp_dict = {
            "lang": lang,
            "low": val - 2 * std,
            "high": val + 2 * std,
            "val": val,
            "pval": (val - 2 * std > 0) or (val + 2 * std < 0),
            "std": std
        }

        df_list.append(tmp_dict)

    return pd.DataFrame(df_list)


def get_df_pageviews(agg, codes, intervention_pre_f, delta_pre, intervention_pos_f, delta_pos, time_int):
    df_list = []

    for lang in codes:  # + [code +".m" for code in codes]:

        y = agg[lang]["sum"] + agg[lang]["covid"]["sum"] + agg[lang + ".m"]["sum"] + agg[lang + ".m"]["covid"]["sum"]
        x = agg[lang]["sum"].index

        names = [("pre", "treated"), ("pos", "treated"), ("pre", "control"), ("pos", "control")]

        intervention_pre = intervention_pre_f(lang, delta_pre)
        intervention_pos = intervention_pos_f(lang, delta_pos)

        pre_treated = [intervention_pre - relativedelta(days=time_int), intervention_pre]
        pos_treated = [intervention_pos,
                       min(intervention_pos + relativedelta(days=time_int), pd.to_datetime("31st of July of 2020"))]

        if lang == "en":
            print(pre_treated)
            print(pos_treated)

        pre_control = [pre_treated[0] - relativedelta(years=1), pre_treated[1] - relativedelta(years=1)]
        pos_control = [pos_treated[0] - relativedelta(years=1), pos_treated[1] - relativedelta(years=1)]
        baseline = (20190101, 20191231)

        start_baseline = datetime.datetime.strptime(str(baseline[0]), "%Y%m%d")
        end_baseline = datetime.datetime.strptime(str(baseline[1]), "%Y%m%d")
        mask_baseline = (x <= end_baseline) & (x >= start_baseline)

        for idx, dates in enumerate([pre_treated, pos_treated, pre_control, pos_control]):

            mask = (x >= pd.to_datetime(dates[0])) & \
                   (x < pd.to_datetime(dates[1]))

            for mean_value in y[mask].values:
                if mean_value <= 0:
                    return None, y[mask]

                df_list.append({
                    "lang": lang,
                    "period": names[idx][0],
                    "group": names[idx][1],
                    "value_log": np.log(mean_value),
                    "value": mean_value
                })

    df_pageviews = pd.DataFrame(df_list)

    df_pageviews["pos_dummy"] = (df_pageviews.period == "pos").astype(int)
    df_pageviews["treated_dummy"] = (df_pageviews.group == "treated").astype(int)
    df_pageviews_results = get_diffs_in_diffs_result(df_pageviews, codes)
    return df_pageviews, df_pageviews_results


def get_df_pca(dfs_pca_shift, codes, interventions, intervention_pre_f, delta_pre, intervention_pos_f, delta_pos,
               time_int):
    df_list = []
    rolling = 5

    for lang in codes:
        names = [("pre", "treated"), ("pos", "treated"), ("pre", "control"), ("pos", "control")]

        lang_name = lang.split('.')[0]

        intervention_pre = intervention_pre_f(lang, delta_pre)
        intervention_pos = intervention_pos_f(lang, delta_pos)

        df_lang = dfs_pca_shift[lang_name]
        x = df_lang.index

        mobility = interventions[lang.replace(".m", "")]["Mobility"]

        baseline_columns = ['baseline' in f for f in df_lang.columns]
        df_control = df_lang.iloc[:, baseline_columns]

        shift_columns = [not ('baseline' in f) for f in df_lang.columns]
        df_treated = df_lang.iloc[:, shift_columns]

        print("{} {}".format(lang, mobility))
        pre_treated = [intervention_pre - relativedelta(days=time_int), intervention_pre]
        pos_treated = [intervention_pos,
                       min(intervention_pos + relativedelta(days=time_int), pd.to_datetime("31st of July of 2020"))]

        pre_control = [pre_treated[0] - relativedelta(years=1), pre_treated[1] - relativedelta(years=1)]
        pos_control = [pos_treated[0] - relativedelta(years=1), pos_treated[1] - relativedelta(years=1)]

        for idx, dates in enumerate([pre_treated, pos_treated, pre_control, pos_control]):

            mask = (x >= pd.to_datetime(dates[0])) & \
                   (x <= pd.to_datetime(dates[1]))

            group = names[idx][1]

            if group == 'treated':
                y = df_treated.mean(axis=1)
            else:
                y = df_control.mean(axis=1)

            for mean_value in y[mask].values:
                df_list.append({
                    "lang": lang,
                    "period": names[idx][0],
                    "group": names[idx][1],
                    "value_log": np.log(mean_value),
                    "value": mean_value
                })

    df_pca = pd.DataFrame(df_list)
    df_pca["pos_dummy"] = (df_pca.period == "pos").astype(int)
    df_pca["treated_dummy"] = (df_pca.group == "treated").astype(int)
    df_pca_results = get_diffs_in_diffs_result(df_pca, codes)
    return df_pca, df_pca_results


def interventions_df_pageviews(agg, codes, interventions, time_int):
    df_list = []

    for intervention in interventions["fr"].keys():

        for lang in codes:

            y = agg[lang]["sum"] + agg[lang]["covid"]["sum"] + agg[lang + ".m"]["sum"] + agg[lang + ".m"]["covid"][
                "sum"]
            x = agg[lang]["sum"].index
            names = [("pre", "treated"), ("pos", "treated"), ("pre", "control"), ("pos", "control")]

            try:
                mobility = interventions[lang.replace(".m", "")][intervention]
            except:
                continue

            pre_treated = [mobility - relativedelta(days=time_int), mobility]
            pos_treated = [mobility, min(mobility + relativedelta(days=time_int), pd.to_datetime("2020-07-31"))]
            pre_control = [pre_treated[0] - relativedelta(years=1),
                           pre_treated[1] - relativedelta(years=1)]
            pos_control = [pos_treated[0] - relativedelta(years=1),
                           pos_treated[1] - relativedelta(years=1)]
            baseline = (20190102, 20191231)

            start_baseline = datetime.datetime.strptime(str(baseline[0]), "%Y%m%d")
            end_baseline = datetime.datetime.strptime(str(baseline[1]), "%Y%m%d")
            mask_baseline = (x <= end_baseline) & (x >= start_baseline)
            baseline = np.mean(y[mask_baseline])

            for idx, dates in enumerate([pre_treated, pos_treated, pre_control, pos_control]):

                mask = (x >= pd.to_datetime(dates[0])) & \
                       (x < pd.to_datetime(dates[1]))

                for mean_value in y[mask].values:
                    df_list.append({
                        "lang": lang,
                        "period": names[idx][0],
                        "group": names[idx][1],
                        "value_log": np.log(mean_value),
                        "intervention": intervention,
                    })

    df_interv_pv = pd.DataFrame(df_list)

    df_interv_pv["pos_dummy"] = (df_interv_pv.period == "pos").astype(int)
    df_interv_pv["treated_dummy"] = (df_interv_pv.group == "treated").astype(int)

    df_list = []

    for intervention in interventions["fr"].keys():
        res_ = smf.ols(formula='value_log ~ lang + pos_dummy * treated_dummy',
                       data=df_interv_pv[(df_interv_pv.intervention == intervention)]).fit()
        res = res_.get_robustcov_results(cov_type='HC0')
        res = statsmodels.regression.linear_model.RegressionResultsWrapper(res)
        conf_int = res.conf_int().loc["pos_dummy:treated_dummy"].values

        val = res.params['pos_dummy:treated_dummy']

        tmp_dict = {
            "intervention": intervention,
            "low": conf_int[0],
            "high": conf_int[1],
            "val": val,
            "pval": res.pvalues.loc["pos_dummy:treated_dummy"],
            "res": res.rsquared
        }

        df_list.append(tmp_dict)

    df_interv_pv_results = pd.DataFrame(df_list)
    return df_interv_pv_results


def interventions_df_pca(dfs_pca_shift, codes, interventions, time_int):
    df_list = []

    for intervention in interventions["fr"].keys():

        for lang in codes:

            lang_name = lang.split('.')[0]

            df_lang = dfs_pca_shift[lang_name]

            x = df_lang.index

            ## PRE-Period
            baseline_columns = ['baseline' in f for f in df_lang.columns]
            df_pre = df_lang.iloc[:, baseline_columns]
            ## POST-Period
            shift_columns = [not ('baseline' in f) for f in df_lang.columns]
            df_post = df_lang.iloc[:, shift_columns]

            names = [("pre", "treated"), ("pos", "treated"), ("pre", "control"), ("pos", "control")]

            try:
                mobility = interventions[lang.replace(".m", "")][intervention]
            except:
                continue

            pre_treated = [mobility - relativedelta(days=time_int), mobility]
            pos_treated = [mobility, min(mobility + relativedelta(days=time_int), pd.to_datetime("2020-07-31"))]
            pre_control = [pre_treated[0] - relativedelta(years=1),
                           pre_treated[1] - relativedelta(years=1)]
            pos_control = [pos_treated[0] - relativedelta(years=1),
                           pos_treated[1] - relativedelta(years=1)]
            baseline = (20190101, 20191231)

            start_baseline = datetime.datetime.strptime(str(baseline[0]), "%Y%m%d")
            end_baseline = datetime.datetime.strptime(str(baseline[1]), "%Y%m%d")
            mask_baseline = (x <= end_baseline) & (x >= start_baseline)

            for idx, dates in enumerate([pre_treated, pos_treated, pre_control, pos_control]):

                period = names[idx][0]

                mask = (x >= pd.to_datetime(dates[0])) & \
                       (x < pd.to_datetime(dates[1]))

                if period == 'pre':
                    y = df_pre.mean(axis=1).rolling(10).mean()
                else:
                    y = df_post.mean(axis=1).rolling(10).mean()

                for mean_value in y[mask].values:
                    df_list.append({
                        "lang": lang,
                        "period": period,
                        "group": names[idx][1],
                        "value_log": np.log(mean_value),
                        "intervention": intervention,
                    })

    df_interv_pca = pd.DataFrame(df_list)

    df_interv_pca["pos_dummy"] = (df_interv_pca.period == "pos").astype(int)
    df_interv_pca["treated_dummy"] = (df_interv_pca.group == "treated").astype(int)

    df_list = []

    for intervention in interventions["fr"].keys():
        print(intervention)

        res_ = smf.ols(formula='value_log ~ lang + pos_dummy * treated_dummy',
                       data=df_interv_pca[(df_interv_pca.intervention == intervention)]).fit()
        res = res_.get_robustcov_results(cov_type='HC0')
        res = statsmodels.regression.linear_model.RegressionResultsWrapper(res)
        conf_int = res.conf_int().loc["pos_dummy:treated_dummy"].values

        val = res.params['pos_dummy:treated_dummy']

        tmp_dict = {
            "intervention": intervention,
            "low": conf_int[0],
            "high": conf_int[1],
            "val": val,
            "pval": res.pvalues.loc["pos_dummy:treated_dummy"],
            "res": res.rsquared
        }

        df_list.append(tmp_dict)

    df_interv_pca_results = pd.DataFrame(df_list)
    return df_interv_pca_results
