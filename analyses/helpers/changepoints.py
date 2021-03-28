import pandas as pd
from sklearn import preprocessing


apple_features = ['driving', 'walking', 'transit']
google_features = ['residential_percent_change_from_baseline', 'workplaces_percent_change_from_baseline',
                   'transit_stations_percent_change_from_baseline',
                   'retail_and_recreation_percent_change_from_baseline']
combined_features = apple_features + google_features

change_points = {
    'it': pd.to_datetime('2020-03-11 00:00:00'),
    'fra': pd.to_datetime('2020-03-16 00:00:00'),
    'ger': pd.to_datetime('2020-03-16 00:00:00'),
    'da': pd.to_datetime('2020-03-11 00:00:00'),
    'us': pd.to_datetime('2020-03-16 00:00:00'),
    'fi': pd.to_datetime('2020-03-16 00:00:00'),
    'ja': pd.to_datetime('2020-03-31 00:00:00'),
    'ko': pd.to_datetime('2020-02-25 00:00:00'),
    'nl': pd.to_datetime('2020-03-16 00:00:00'),
    'no': pd.to_datetime('2020-03-11 00:00:00'),
    'sr': pd.to_datetime('2020-03-16 00:00:00'),
    'sv': pd.to_datetime('2020-03-11 00:00:00'),
    'can': pd.to_datetime('2020-03-16 00:00:00'),
    'sw': pd.to_datetime('2020-03-16 00:00:00'),
    'aus': pd.to_datetime('2020-03-21 00:00:00'),
    'nz': pd.to_datetime('2020-03-21 00:00:00'),
    'uk': pd.to_datetime('2020-03-21 00:00:00'),
    'at': pd.to_datetime('2020-03-16 00:00:00'),
    'za': pd.to_datetime('2020-03-26 00:00:00'),
    'ie': pd.to_datetime('2020-03-16 00:00:00'),
    'cm': pd.to_datetime('2020-03-21 00:00:00'),
    'be': pd.to_datetime('2020-03-16 00:00:00'),
    'ci': pd.to_datetime('2020-03-21 00:00:00'),
    'sn': pd.to_datetime('2020-03-21 00:00:00'),
    'bj': pd.to_datetime('2020-03-21 00:00:00'),
    'en': pd.to_datetime('2020-03-16 00:00:00'),
    'fr': pd.to_datetime('2020-03-16 00:00:00'),
    'de': pd.to_datetime('2020-03-16 00:00:00'),
}

codes = {
    'it': {'google': 'IT', 'apple': 'Italy'},
    'fra': {'google': 'FR', 'apple': 'France'},
    'ger': {'google': 'DE', 'apple': 'Germany'},
    'da': {'google': 'DK', 'apple': 'Denmark'},
    'us': {'google': 'US', 'apple': 'United States'},
    'fi': {'google': 'FI', 'apple': 'Finland'},
    'ja': {'google': 'JP', 'apple': 'Japan'},
    'ko': {'google': None, 'apple': 'Seoul'},
    'nl': {'google': 'NL', 'apple': 'Netherlands'},
    'no': {'google': 'NO', 'apple': 'Norway'},
    'sr': {'google': None, 'apple': 'Serbia'},
    'sv': {'google': 'SE', 'apple': 'Sweden'},
    'can': {'google': 'CA', 'apple': 'Montreal'},
    'sw': {'google': 'CH', 'apple': 'Switzerland'},
    'aus': {'google': 'AU', 'apple': 'Australia'},
    'nz': {'google': 'NZ', 'apple': 'New Zealand'},
    'uk': {'google': 'GB', 'apple': 'UK'},
    'at': {'google': 'AT', 'apple': 'Austria'},  # Austria
    'za': {'google': 'ZA', 'apple': 'South Africa'},  # South Africa
    'ie': {'google': 'IE', 'apple': 'Ireland'},  # Ireland
    'cm': {'google': 'CM', 'apple': None},  # Cameroon
    'be': {'google': 'BE', 'apple': 'Belgium'},  # Belgium
    'ci': {'google': 'CI', 'apple': None},  # Cote d'Ivoire
    'sn': {'google': 'SN', 'apple': None},  # Senegal
    'bj': {'google': 'BJ', 'apple': None}  # Benin
}

title_codes = {
    'it': 'Italy',
    'da': 'Denmark',
    'fi': 'Finland',
    'ja': 'Japan',
    'ko': 'Korea',
    'nl': 'Netherlands',
    'no': 'Norway',
    'sr': 'Serbia',
    'sv': 'Sweden',
    'en': 'English',
    'fr': 'French',
    'de': 'German',
    'us': 'U.S.',
    'fra': 'France',
    'ger': 'Germany',
    'can': 'Canada',
    'sw': 'Switzerland',
    'aus': 'Australia',
    'nz': 'New Zealand',
    'uk': 'U.K.',
    'at': 'Austria',
    'za': 'South Africa',
    'ie': 'Ireland',
    'cm': 'Cameroon',
    'be': 'Belgium',
    'ci': "Côte d'Ivoire",
    'sn': 'Senegal',
    'bj': 'Benin',
}

en_pop = {
    'us': 234171556,
    'uk': 54472000,
    'can': 19686175,
    'aus': 18356132,
    'za': 4930510,
    'ie': 4112100,
    'nz': 3673623
}

fr_pop = {
    'fra': 65342000,
    'sw': 1827000,
    'can': 10523000,
    'cm': 9546000,
    'be': 8224000,
    'sn': 4521000,
    'bj': 3950000
}

de_pop = {
    'ger': 69701200,
    'at': 7115780,
    'sw': 5161647
}

other_languages_studied = ['it', 'da', 'fi', 'ja', 'ko', 'nl', 'no', 'sr', 'sv']


def preprocess_google_mobility(google_mobility, code):
    df = google_mobility[google_mobility['country_region_code'] == code]
    #    df = df[['date', 'residential_percent_change_from_baseline', 'workplaces_percent_change_from_baseline', 'transit_stations_percent_change_from_baseline']]
    df = df[google_features + ['date']]
    df = df.groupby('date').mean()
    df['residential_percent_change_from_baseline'] = -df['residential_percent_change_from_baseline']
    df.index = pd.to_datetime(df.index)
    return df


def preprocess_apple_mobility(apple_mobility, code):
    df = apple_mobility[apple_mobility['region'] == code]
    df = df.drop(['geo_type', 'region'],
                 axis=1).set_index('transportation_type')
    try:
        df = df.drop(['alternative_name', 'subregion', 'country'], axis=0)
    except:
        pass
    try:
        df = df.drop(['alternative_name', 'subregion', 'country'], axis=0)
    except:
        pass
    return df.T


def normalize_time_series(df):
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(df)
    return pd.DataFrame(x_scaled, columns=df.columns, index=df.index)


def pop_to_weights(pop):
    tot = float(sum(pop.values()))
    return dict((k, v / tot) for k, v in pop.items())


def add_weighted_mobility(mobility_data, weights, name):
    new_df = sum(mobility_data[k] * weight for k, weight in weights.items())
    print(new_df)
    new_df = new_df.dropna(axis='columns')
    print(new_df)
    mobility_data[name] = new_df
    return mobility_data
