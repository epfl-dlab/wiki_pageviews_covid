from sklearn import preprocessing
import pandas as pd

def normalize_time_series(df):
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(df)
    return pd.DataFrame(x_scaled, columns=df.columns, index=df.index)


def get_attention_shift_ts(df, min_date, rolling=5):
    baseline_columns = ['baseline' in f for f in df.columns]
    shift_columns = [not ('baseline' in f) for f in df.columns]

    df = normalize_time_series(df)

    ### EFFECT
    df_effect = df.iloc[:, shift_columns]
    df_baseline = df.iloc[:, baseline_columns]

    mask_effect = df_effect.index >= min_date
    df_effect = df_effect[mask_effect]

    mean_effect = df_effect.mean(axis=1).rolling(rolling).mean()

    ### BASELINE
    mask_baseline = (df_baseline.index >= pd.to_datetime(min_date) - pd.DateOffset(years=1)) & (
                df_baseline.index <= pd.to_datetime('2019-04-20'))
    df_baseline = df_baseline[mask_baseline]
    df_baseline.index = df_baseline.index + pd.DateOffset(years=1)

    mean_baseline = df_baseline.mean(axis=1).rolling(rolling).mean()

    ### Plot
    min_value = min(mean_effect.min(), mean_baseline.min())
    mean_effect = mean_effect - min_value
    mean_baseline = mean_baseline - min_value

    normalization = max(mean_effect.max(), mean_baseline.max())
    mean_effect = mean_effect / normalization
    mean_baseline = mean_baseline / normalization

    return mean_effect, mean_baseline