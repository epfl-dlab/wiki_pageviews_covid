import pandas as pd

codes = ["de", "fr", "it", "sr", "no", "ko", "da", "sv", "ja", "nl", "fi", "en"]

helper_langs = {
    "sv": "Swedish",
    "de": "German",
    "fr": "French",
    "it": "Italian",
    "sr": "Serbian",
    "no": "Norwegian",
    "ko": "Korean",
    "da": "Danish",
    "ja": "Japanese",
    "nl": "Dutch",
    "fi": "Finnish",
    "en": "English",
    "ca": "Catalan",
    "tr": "Turkey"
}

topics = ['Culture.Biography.Biography*',
          'Culture.Food and drink',
          'Culture.Internet culture',
          'Culture.Linguistics',
          'Culture.Literature',
          'Culture.Media.Books',
          'Culture.Media.Entertainment',
          'Culture.Media.Films',
          'Culture.Media.Music',
          'Culture.Media.Radio',
          'Culture.Media.Software',
          'Culture.Media.Television',
          'Culture.Media.Video games',
          'Culture.Performing arts',
          'Culture.Philosophy and religion',
          'Culture.Sports',
          'Culture.Visual arts.Architecture',
          'Culture.Visual arts.Comics and Anime',
          'Culture.Visual arts.Fashion',
          'Geography.Geographical',
          'Geography.Regions.Africa.Central Africa',
          'Geography.Regions.Africa.Eastern Africa',
          'Geography.Regions.Africa.Northern Africa',
          'Geography.Regions.Africa.Southern Africa',
          'Geography.Regions.Africa.Western Africa',
          'Geography.Regions.Americas.Central America',
          'Geography.Regions.Americas.North America',
          'Geography.Regions.Americas.South America',
          'Geography.Regions.Asia.Central Asia',
          'Geography.Regions.Asia.East Asia',
          'Geography.Regions.Asia.North Asia',
          'Geography.Regions.Asia.South Asia',
          'Geography.Regions.Asia.Southeast Asia',
          'Geography.Regions.Asia.West Asia',
          'Geography.Regions.Europe.Eastern Europe',
          'Geography.Regions.Europe.Northern Europe',
          'Geography.Regions.Europe.Southern Europe',
          'Geography.Regions.Europe.Western Europe',
          'Geography.Regions.Oceania',
          'History and Society.Business and economics',
          'History and Society.Education',
          'History and Society.History',
          'History and Society.Military and warfare',
          'History and Society.Politics and government',
          'History and Society.Society',
          'History and Society.Transportation',
          'STEM.Biology',
          'STEM.Chemistry',
          'STEM.Computing',
          'STEM.Earth and environment',
          'STEM.Engineering',
          'STEM.Libraries & Information',
          'STEM.Mathematics',
          'STEM.Medicine & Health',
          'STEM.Physics',
          'STEM.Space',
          'STEM.Technology']

interventions_helper = {
    '1st case': '1',
    '1st death': '2',
    'Public events banned': '3',
    'School closure': '4',
    'Lockdown': '5',
    "Mobility": '6',
    "Normalcy": '7'
}

int_c = {
    '1st case': '#e6ab02',
    '1st death': '#66a61e',
    'Public events banned': '#e7298a',
    'School closure': '#d95f02',
    'Lockdown': '#1b9e77',
    "Mobility": '#000000',
    "Normalcy": '#000000'
}

int_ls = {
    '1st case': '-',
    '1st death': '-',
    'Public events banned': '-',
    'School closure': '-',
    'Lockdown': '-',
    "Mobility": '--',
    "Normalcy": '-'
}

ARTICLE_CATEGORIES = {'fr': ['e', 'bd', 'b', 'a', 'ba', 'adq'], 'en': ['Start', 'Stub', 'B', 'C', 'GA', 'FA', None]}

CATEGORY_LABELS = {'fr': ['Ébauche', 'bon début', 'bien construit', 'avancé', 'bon article', 'article de qualité'],
                   'en': ['Start', 'Stub', 'B', 'C', 'GA', 'FA', 'No Label']}

CATEGORY_SCORE = {
    'fr': {'e': 0, 'bd': 1, 'b': 2, 'a': 3, 'ba': 4, 'adq': 5},
    'en': {'Start': 0, 'Stub': 1, 'B': 2, 'C': 3, 'GA': 4, 'FA': 5, None: None}}

wiki_code = ['da', 'fi', 'de', 'it', 'ja',
             'nl', 'no', 'ko', 'sv', 'en',
             'fr', 'sr']

mobility_changepoints = ['2020-03-11', '2020-03-16', '2020-03-16', '2020-03-11', '2020-03-31',
                         '2020-03-16', '2020-03-11', '2020-02-25', '2020-03-11', '2020-03-16',
                         '2020-03-16', '2020-03-16']
mobility_changepoints = pd.to_datetime(mobility_changepoints)

mobility_reverted = ['2020-06-05', '2020-05-21', '2020-07-10', '2020-06-26', '2020-06-14',
                     '2020-05-29', '2020-06-04', '2020-04-15', '2020-06-05', '2020-05-21',
                     '2020-07-02', '2020-05-02']

mobility_reverted = pd.to_datetime(mobility_reverted)

mobility_changepoint_dict = dict(zip(wiki_code, list(mobility_changepoints)))
mobility_reverted_dict = dict(zip(wiki_code, list(mobility_reverted)))

# from: https://wikimediafoundation.org/covid19/data/
changepoints_wiki = {'First known death in China reported': '2020-01-11',
                     'COVID-19 name applied to disease caused by virus': '2020-02-11',
                     'Italy begins nationwide lockdown': '2020-03-09',
                     'World Health Organization declares COVID-19 a pandemic': '2020-03-11',
                     'The United States declares a national emergency': '2020-03-13',
                     'India announces 21-day lockdown, Tokyo Olympics are postponed': '2020-03-24',
                     'Global confirmed cases of COVID-19 tops 1 million': '2020-04-02',
                     'British Prime Minister Boris Johnson moves into intensive care': '2020-04-06',
                     'Known global death toll surpasses 200,000': '2020-04-26',
                     'WHO extends its declaration of a global public health emergency': '2020-05-01',
                     'Global confirmed cases of COVID-19 tops 5 million': '2020-05-21',
                     'Global confirmed cases of COVID-19 tops 16 million': '2020-07-26',
                     'COVID-19 deaths worldwide surpass one million': '2020-09-28'}

changepoints_wiki_mod = {
    '1st Death in China': '2020-01-11',
    'Disease Named "COVID-19"': '2020-02-11',
    'Lockdown in Italy': '2020-03-09',
    #'National Emergency in USA': '2020-03-13',
    #'Lockdown in India': '2020-03-24',
    '1 Million Cases': '2020-04-02',
    '200,000 Deaths': '2020-04-26',
    #'WHO extends its declaration of a global public health emergency': '2020-05-01',
    '5 Million Cases': '2020-05-21',
    '16 Million Cases': '2020-07-26',
    '1 Million Deaths': '2020-09-28'}
