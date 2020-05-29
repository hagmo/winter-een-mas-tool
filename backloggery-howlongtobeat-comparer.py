import io
import json
import os.path
import pickle
import re
from _collections import OrderedDict

import requests
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
WEEMAS_SPREADSHEET_ID = '1JU7BwpP47sE62wFO79B7ZXhG56h0Mj393eYqRmUZH2s'
WEEMAS_RANGE_NAME = '2006-2020!A2:A'
AEAENMAS_SPREADSHEET_ID = '1Rwk8jlc8icpJo7ciFoKfZmC_ZIIU1GKBLadJQyQ8fcc'
AEAENMAS_RANGE_NAME = 'Blad1!A2:A'


def get_backloggery_data():
    query_params = {
        'user': 'dasharoldja',
        'temp_sys': 'ZZZ',
        'total': 0,
        'aid': 1,
        'ajid': '0'
    }
    r = requests.get('https://www.backloggery.com/ajax_moregames.php', params=query_params)
    blsoup = BeautifulSoup(r.text, 'html.parser')

    games = []

    sections = blsoup.find_all('section')

    for section in sections:
        if 'gamebox' in section['class'] and 'systemend' not in section['class']:
            game_title = str(section.h2.b.string).strip()
            game_title = trim_title(game_title)
            games.append(game_title)

    print('Found {} Backloggery entries'.format(len(games)))
    return games


def trim_title(t):
    t = re.sub('[^A-Za-zÅÄÖåäö0-9]', ' ', t)
    t = re.sub('[\\s]+', ' ', t)
    return t.lower().strip()


def find_game_duration(search_list_details_block):
    """Try to find a valid game duration in the table from HLTB.

    Look through the descendants. If we find a "Solo" value, accept that value because the others are "Co-Op" and "Vs.".

    If we find "Main Story", see if it has a value. If it doesn't, look at "Main + Extra" and "Completionist", some
    games only have values there.

    Return a tuple of duration and duration type (i.e. heading).
    """
    next_div = False
    target_heading = 'Main Story'

    for element in search_list_details_block.descendants:
        if element.string == target_heading or element.string == 'Solo':
            next_div = True
            target_heading = str(element.string)
        elif next_div and element.name == 'div' and element.string:
            if str(element.string) == '--':
                next_div = False
                if target_heading == 'Main Story':
                    target_heading = 'Main + Extra'
                elif target_heading == 'Main + Extra':
                    target_heading = 'Completionist'
            else:
                return str(element.string).strip(), target_heading

    return None


def parse_game_duration(duration_string):
    """Try to convert game duration to hours.

    Replace "½" with ".5". Jeez.

    Convert minutes to hours.

    :param duration_string: string from HLTB
    :return: the number of hours
    """
    split = duration_string.split(' ')
    if len(split) != 2:
        print('Unknown duration! ' + duration_string)
        return -1

    value = split[0]
    unit = split[1]

    if value.endswith('½'):
        value = value[0:-1] + '.5'
    float_value = float(value)

    if unit == 'Hours':
        return float_value
    elif unit == 'Mins':
        return float_value / 60
    else:
        print('Unknown unit! ' + unit)
        return -1


def match_hltb_data(game_titles):
    try:
        with io.open('custom_names.json', mode='r', encoding='utf-8') as f:
            custom_names = json.loads(f.read())
    except OSError:
        print('No custom name dictionary specified.')
        custom_names = {}

    matched_games = {}
    unmatched_games = []
    not_found_games = []

    backloggery_games_count = len(game_titles)
    for i, backloggery_game in enumerate(game_titles):
        if backloggery_game in custom_names:
            backloggery_game = custom_names[backloggery_game]
        if backloggery_game == 'skip':
            # The special custom name "skip" indicates that we shouldn't consider this game.
            continue

        form_params = {
            'queryString': backloggery_game,
            't': 'games'
        }
        r = requests.post('https://howlongtobeat.com/search_results', data=form_params)
        soup = BeautifulSoup(r.text, 'html.parser')

        print('\rProcessing {} ({:.0f}%)'.format(backloggery_game, i * 100 / backloggery_games_count), end='')
        with open('./req/{}.html'.format(re.sub('[^A-Za-z0-9]', '_', backloggery_game)), 'w', encoding='utf-8') as f:
            f.write(r.text)

        # gamefilename = re.sub('[^A-Za-z0-9]', '_', game)
        # with open('./req/{}.html'.format(gamefilename), encoding='utf-8') as f:
        #     soup = BeautifulSoup(f.read(), 'html.parser')

        game_stripped = trim_title(backloggery_game)
        game_stripped = re.sub('[\\s]', '', game_stripped)

        search_results = soup.find_all('li')

        if len(search_results) == 1 and str(search_results[0].text).strip().startswith('No results'):
            not_found_games.append(backloggery_game)
            continue

        found = False
        for result in search_results:
            data = result.find(class_='search_list_details')
            game_title = str(data.h3.a['title'])
            game_title = trim_title(game_title)
            game_title_stripped = re.sub('[\\s]', '', game_title)

            title_match = game_stripped.lower() == game_title_stripped.lower()
            single_match = len(search_results) == 1

            if title_match or single_match:
                if single_match and not title_match:
                    print('\rWarning: Matching "{}" and "{}" since it was the only match'
                          .format(backloggery_game, game_title))
                found = True

                playtime_block = data.div
                game_duration_info = find_game_duration(playtime_block)
                game_duration_hours = -1
                if game_duration_info is not None:
                    game_duration = game_duration_info[0]
                    game_duration_hours = parse_game_duration(game_duration)
                    if game_duration_info[1] != 'Main Story' and game_duration_info[1] != 'Solo':
                        print('\rWarning: Using {} time for {}'
                              .format(game_duration_info[1], backloggery_game))

                matched_games[backloggery_game] = game_duration_hours

        if not found:
            unmatched_games.append(backloggery_game)

    print()
    return matched_games, unmatched_games, not_found_games


def google_auth():
    """Login a Google user.

    Ask for permission to read Google Sheets.
    :return: the credentials to use when connecting.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def minify_title(game_title):
    """Trim and remove all whitespace from title to ease matching (?)."""
    return trim_title(game_title).replace(' ', '')


def match_google_sheets_data(creds, games):
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=WEEMAS_SPREADSHEET_ID,
                                range=WEEMAS_RANGE_NAME).execute()
    finished_games = [minify_title(value[0]) for value in result.get('values', [])]

    result = sheet.values().get(spreadsheetId=AEAENMAS_SPREADSHEET_ID,
                                range=AEAENMAS_RANGE_NAME).execute()
    finished_aeaenmas_games = [minify_title(value[0]) for value in result.get('values', [])]
    finished_games.extend(finished_aeaenmas_games)

    not_finished_games = []
    matched_finished_games = []

    for game in games:
        minified_game = minify_title(game)
        if minified_game not in finished_games:
            not_finished_games.append(game)
        else:
            matched_finished_games.append(game)

    return not_finished_games, matched_finished_games


def load_mocked_list():
    with io.open('testgames.json', mode='r', encoding='utf-8') as f:
        return json.loads(f.read())


google_creds = google_auth()
backloggery_games = get_backloggery_data()
hltb_results = match_hltb_data(backloggery_games)
hltb_matched_games = hltb_results[0]
hltb_unmatched_games = hltb_results[1]
hltb_not_found_games = hltb_results[2]
# hltb_matched_games = load_mocked_list()

google_results = match_google_sheets_data(google_creds, hltb_matched_games.keys())
eligible_games = google_results[0]
already_finished = google_results[1]

final_result = {}
for eligible_game in eligible_games:
    final_result[eligible_game] = hltb_matched_games[eligible_game]

print()
print('Results:')
for title, duration in OrderedDict(sorted(final_result.items(), key=lambda x: x[1])).items():
    print('{} ({})'.format(title, duration))
print()

print('{} of your games are already finished:'.format(len(already_finished)))
for entry in sorted(already_finished):
    print(entry)
print()

print('{} unmatched games:'.format(len(hltb_unmatched_games)))
for entry in hltb_unmatched_games:
    print(entry)
print()

print('{} games not found:'.format(len(hltb_not_found_games)))
for entry in hltb_not_found_games:
    print(entry)
print()
