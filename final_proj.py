################################
##### Name: Mingzhe (Daniel) Yu
##### Uniqname: dnlyu
################################

from bs4 import BeautifulSoup
import requests
import json
import webbrowser
import time
import sqlite3
from flask import Flask, render_template, request
import sys
import plotly.graph_objs as go

URL = 'https://www.spotcrime.com'
CACHE_FILENAME = 'spot_crime_cache.json'
CACHE_DICT = {}

class SpotCrime:
    '''a spot crime record

    Instance Attributes
    -------------------
    category: string
        the category of a crime (eg. 'Theft', 'Assault', 'Other')

    date: string
        the date and time a crime happened ( 04/13/20/ 01:10 PM.)
    
    address: string
        where the crime happened
    
    link: string
        link to crime details
    '''
    def __init__(self):
        self.category = 'no category'
        self.date = 'no date'
        self.address = 'no address'
        self.link = 'no link'
    
    def info(self):
        return self.category + '    ' + self.date + '    ' + self.address + '    ' + self.link
    
    def __str__(self):
        return self.category + '    ' + self.date + '    ' + self.address + '    ' + self.link

class City:
    def __init__(self):
        self.crime_map = 'no crime map'
        self.most_wanted = 'no most wanted'
        self.daily_crime_reports = 'no daily crime reports'

    # def 

def open_cache():
    '''
    Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME, "w")
    fw.write(dumped_json_cache)
    fw.close()

def build_state_url_dict():
    '''
    Make a dictionary that maps state name to state page url from 'www.spotcrime.com'

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.spotcrime.com/mi', ...}
    '''
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    keyword_search = soup.find(class_ = 'dropdown-menu')
    list_of_state = keyword_search.find_all('li', recursive = False)
    state_url_dict = {}
    base_url = 'https://www.spotcrime.com'
    for element in list_of_state:
        per_state = element.find('a').string.lower()
        per_url = element.find('a').get('href')
        state_url_dict[per_state] = base_url + per_url
    return state_url_dict

def build_state_url_dict_with_cache():
    ''' Make a dictionary that maps state name to state page url from 'www.spotcrime.com' with cache

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    if URL in CACHE_DICT.keys():
        print("Using Cache")
        return CACHE_DICT[URL]
    else:
        print("Fetching")
        CACHE_DICT[URL] = build_state_url_dict()
        save_cache(CACHE_DICT)
        return CACHE_DICT[URL]

def generate_state_id_dict(state_url_dict):
    state_id_dict = {}
    for i, state in enumerate(state_url_dict.keys()):
        state_id_dict[state] = i
    return state_id_dict

def build_city_content_url_dict(state_url):
    response = requests.get(state_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    keyword_search = soup.find(class_ = "table table-condensed table-striped table-hover text-left")
    list_of_city_content = keyword_search.find_all('a')
    base_url = 'https://www.spotcrime.com'
    city_content_url_dict = {}
    for element in list_of_city_content:
        if element.string is not None:
            per_city_content = element.string.lower()
            per_url = element.get('href')
            city_content_url_dict[per_city_content] = base_url + per_url
    return city_content_url_dict
    
def build_city_content_url_dict_with_cache(state_url):
    if state_url in CACHE_DICT.keys():
        print("Using Cache")
        return CACHE_DICT[state_url]
    else:
        print("Fetching")
        CACHE_DICT[state_url] = build_city_content_url_dict(state_url)
        save_cache(CACHE_DICT)
        return CACHE_DICT[state_url]

def get_crime_label_helper(daily_crime_data):
    soup = BeautifulSoup(daily_crime_data, 'html.parser')
    keyword_search = soup.find(class_ = 'row')
    list_of_crime_label_raw = keyword_search.find_all('li', recursive = True)
    list_of_crime_label = []
    for element in list_of_crime_label_raw:
        list_of_crime_label.append(element.find('a').string)
    return list_of_crime_label
    
def get_crime_label(daily_archives_url):
    if daily_archives_url in CACHE_DICT.keys():
        print("Using Cache")
        return get_crime_label_helper(CACHE_DICT[daily_archives_url])
    else:
        print("Fetching")
        response = requests.get(daily_archives_url)
        CACHE_DICT[daily_archives_url] = response.text
        save_cache(CACHE_DICT)
        return get_crime_label_helper(CACHE_DICT[daily_archives_url])

def get_crime_label_link_heler(daily_crime_data):
    soup = BeautifulSoup(daily_crime_data, 'html.parser')
    keyword_search = soup.find(class_ = 'row')
    list_of_crime_label_raw = keyword_search.find_all('li', recursive = True)
    list_of_crime_label_link = []
    for element in list_of_crime_label_raw:
        list_of_crime_label_link.append(element.find('ref').string)
    return list_of_crime_label_link

def get_crime_label_link(daily_archives_url):
    if daily_archives_url in CACHE_DICT.keys():
        print('Using Cache')
        return get_crime_label_link_heler(CACHE_DICT[daily_archives_url])
    else:
        print("Fetching")
        response = requests.get(daily_archives_url)
        CACHE_DICT[daily_archives_url] = response.text
        save_cache(CACHE_DICT)
        return get_crime_label_link_heler(CACHE_DICT[daily_archives_url])

def get_crime_instance_list_helper(crime_data):
    '''Make an instance from a spot crime URL.
    Parameters
    ----------
    sport_crime: text
        text file scraping from website
    
    Returns
    -------
    instance
        a spot crime instance
    '''
    soup = BeautifulSoup(crime_data, 'html.parser')
    base_url = 'https://www.spotcrime.com'
    crime_instance_list = []

    crime_table = soup.find(class_ = 'table table-condensed table-striped table-hover text-left')
    crime_entry_list = crime_table.find_all('tr')
    for each_crime_entry in crime_entry_list:
        crime_content_list = list(each_crime_entry.find_all('td'))
        if len(crime_content_list) != 0:
            crime_instance = SpotCrime()
            crime_instance.order = crime_content_list[0].string
            crime_instance.category = crime_content_list[1].string
            crime_instance.date = crime_content_list[2].string
            crime_instance.address = crime_content_list[3].string
            crime_instance.link = base_url + crime_content_list[4].find('a').get('href')
            # print(crime_instance.info())
            crime_instance_list.append(crime_instance)
    return crime_instance_list

def get_crime_instance_list(crime_url):
    if crime_url in CACHE_DICT.keys():
        print('Using Cache')
        return get_crime_instance_list_helper(CACHE_DICT[crime_url])
    else:
        print("Fetching")
        response = requests.get(crime_url)
        CACHE_DICT[crime_url] = response.text
        save_cache(CACHE_DICT)
        time.sleep(3)
        return get_crime_instance_list_helper(CACHE_DICT[crime_url])

def get_crime_for_city_helper(daily_crime_data, amount):
    daily_crime_list = []
    base_url = 'https://www.spotcrime.com'
    soup = BeautifulSoup(daily_crime_data, 'html.parser')
    keyword_search = soup.find(class_ = 'row')
    list_of_crime_label_raw = keyword_search.find_all('li', recursive = True)
    i = 0
    for crime in list_of_crime_label_raw:
        crime_link_tag = crime.find('a')
        crime_detail_path = crime_link_tag['href']
        crime_detail_url = base_url + crime_detail_path
        daily_crime_list.append(get_crime_instance_list(crime_detail_url))
        i += 1
        if i == amount:
            break

    return daily_crime_list

def get_crime_for_city(daily_archives_url, amount):
    if daily_archives_url in CACHE_DICT.keys():
        print('Using Cache')
        return get_crime_for_city_helper(CACHE_DICT[daily_archives_url], amount)
    else:
        print('Fetching')
        response = requests.get(daily_archives_url)
        CACHE_DICT[daily_archives_url] = response.text
        save_cache(CACHE_DICT)
        return get_crime_for_city_helper(CACHE_DICT[daily_archives_url], amount)

def create_state_list_table(raw_data):
    table_name = "Spotcrime.sqlite"
    conn = sqlite3.connect(table_name)
    cur = conn.cursor()

    drop_sql = '''
        DROP TABLE IF EXISTS "State"
    '''

    create_sql = '''
        CREATE TABLE IF NOT EXISTS "State" (
            "Id"            INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "State"         TEXT NOT NULL
        );
    '''

    cur.execute(drop_sql)
    cur.execute(create_sql)
    
    for entry in raw_data:
        insertion = [entry]
        insert_sql = '''
            INSERT INTO State
            VALUES (NULL, ?)
        '''
        cur.execute(insert_sql, insertion)

    conn.commit()

def create_crime_list_table_with_data(raw_data):
    table_name = "Spotcrime.sqlite"
    conn = sqlite3.connect(table_name)
    cur = conn.cursor()

    drop_sql = '''
        DROP TABLE IF EXISTS "CrimeListByTime"
    '''

    create_sql = '''
        CREATE TABLE IF NOT EXISTS "CrimeListByTime" (
            "Id"            INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "DailyCrime"    TEXT NOT NULL
        );
    '''

    cur.execute(drop_sql)
    cur.execute(create_sql)
    
    for entry in raw_data:
        insertion = [entry]
        insert_sql = '''
            INSERT INTO CrimeListByTime
            VALUES (NULL, ?)
        '''
        cur.execute(insert_sql, insertion)

    conn.commit()

def create_crime_instance_list_table():
    table_name = "Spotcrime.sqlite"
    conn = sqlite3.connect(table_name)
    cur = conn.cursor()

    drop_sql = '''
        DROP TABLE IF EXISTS "CrimeInstanceList"
    '''

    create_sql = '''
        CREATE TABLE IF NOT EXISTS "CrimeInstanceList"(
            "Id"        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Category"  TEXT NOT NULL,
            "Date"      TEXT NOT NULL,
            "Address"   TEXT NOT NULL,
            "Link"      TEXT NOT NULL,
            "StateId"   TEXT NOT NULL
        )
    '''
    
    cur.execute(drop_sql)
    cur.execute(create_sql)
    conn.commit()

def insert_entry_into_crime_instance_list_table(raw_data, stateId):
    table_name = "Spotcrime.sqlite"
    conn = sqlite3.connect(table_name)
    cur = conn.cursor()

    insert_sql = '''
        INSERT INTO "CrimeInstanceList"
        VALUES (NULL, ?, ?, ?, ?, ?)
    '''

    inserted_data = [raw_data.category, raw_data.date, raw_data.address, raw_data.link, stateId]
    cur.execute(insert_sql, inserted_data)
    conn.commit()

###############################################################################################
# CACHE_DICT = open_cache()
# a = len(CACHE_DICT)
# a = build_state_url_dict_with_cache()
# a = build_city_content_url_dict_with_cache(URL + '/mi')
# a = get_crime_label('https://www.spotcrime.com/mi/alaiedon+twp/daily')
# a = get_crime_label('https://www.spotcrime.com/mi/ann+arbor/daily')
# a = get_crime_instance_list('https://spotcrime.com/mi/ann+arbor/daily-blotter/2020-04-14')
# a = get_crime_for_city('https://spotcrime.com/mi/ann+arbor/daily', 15)

# for b in a:
    # print(len(b))
# print(a)
# print(len(a[1]))
# crime_list = ["03", "b", "c"]
# create_crime_list_table(crime_list)
# print(len(crime_list))
###############################################################################################
def handle_the_request(state, city, info_type, amount=None):
    state_url_dict = build_state_url_dict_with_cache()
    create_state_list_table(state_url_dict.keys())
    state_id_dict = generate_state_id_dict(state_url_dict)

    state_url = state_url_dict[state.lower()]
    city_content_url_dict = build_city_content_url_dict_with_cache(state_url)
    user_input = city + ' ' + info_type
    city_content_url = city_content_url_dict[user_input.lower()]
    if info_type.lower() == 'crime map':
        webbrowser.open(city_content_url)
        return 'Succeed!'
    elif info_type.lower() == 'most wanted':
        webbrowser.open(city_content_url)
        return 'Succeed!'
    elif info_type.lower() == 'daily crime reports':
        crime_label_list = get_crime_label(city_content_url)
        create_crime_list_table_with_data(crime_label_list)
        create_crime_instance_list_table()
        crime_on_each_day_list = get_crime_for_city(city_content_url, int(amount))
        # crime_on_each_day_content_list = [[]]
        # for i, crime_on_each_day in enumerate(crime_on_each_day_list):
        #     for entry in crime_on_each_day:
        #         crime_on_each_day_content_list[i].append(entry.info())
        for single_day_instance_list in crime_on_each_day_list:
            for each_crime_entry in single_day_instance_list:
                insert_entry_into_crime_instance_list_table(each_crime_entry, state_id_dict[state.lower()])
        # for i in range(int(amount)):
        #     print('[', i + 1, ']', crime_label_list[i])
        # number = input('Choose a number and see details:\n')
        # for entry in crime_on_each_day_list[int(number) - 1]:
        #     print(entry)

        x_vals = []
        y_vals = []
        # x_vals = crime_label_list[0:int(amount)]
        for label in crime_label_list[0:int(amount)]:
            x_vals.append(str(label))
        for crime in crime_on_each_day_list:
            y_vals.append(len(crime))
        bar_data = go.Bar(x=x_vals, y=y_vals)
        # basic_layout = go.Layout(title="Number of crime vs. date")
        fig = go.Figure(data=bar_data)
        div = fig.to_html(full_html=False)
        return render_template('response.html', 
                            in_crime_label_list= crime_label_list,
                            in_crime_on_each_day_list= crime_on_each_day_list,
                            in_amount = int(amount),
                            plot_div = div)


def operate_on_terminal():
    # pass
    
    state_url_dict = build_state_url_dict_with_cache()
    create_state_list_table(state_url_dict.keys())
    state_id_dict = generate_state_id_dict(state_url_dict)

    exit_flag = False
    while not exit_flag:
        state = input('Enter a state name (eg. Michigan, michigan) or "exit":\n')
        if state.lower() == 'exit':
            exit_flag = True
        elif state.lower() not in state_url_dict.keys():
            print('[Error] Enter proper state name')
        else:
            state_url = state_url_dict[state.lower()]
            city_content_url_dict = build_city_content_url_dict_with_cache(state_url)
            city = input('Enter a city name (eg. Ann Arbor, ann arbor) or "exit":\n')
            if city.lower() == 'exit':
                exit_flag = True
            else:
                while not exit_flag:
                    info_type = input('Enter an info type you want to search (Crime Map/ Most Wanted/ Daily Crime Reports) or "exit":\n')
                    if info_type.lower() == 'exit':
                        exit_flag = True
                    elif (city + ' ' + info_type).lower() not in city_content_url_dict.keys():
                        print('[Error] Enter proper city name or info type')
                    else:
                        user_input = city + ' ' + info_type
                        city_content_url = city_content_url_dict[user_input.lower()]
                        if info_type.lower() == 'crime map':
                            # TODO SHOW OPEN WEBSITE
                            webbrowser.open(city_content_url)
                        elif info_type.lower() == 'most wanted':
                            # TODO SHOW OPEN WEBSITE
                            webbrowser.open(city_content_url)
                        elif info_type.lower() == 'daily crime reports':
                            # dispay recent 3 days of crime
                            # pass
                            crime_label_list = get_crime_label(city_content_url)
                            # SAVE DATA INTO TABLE
                            create_crime_list_table_with_data(crime_label_list)
                            # print(crime_label_list)
                            length = len(crime_label_list)
                            notGetback = True
                            create_crime_instance_list_table()
                            while notGetback:
                                amount = input('How many entries to show (recommend within 20):\n')
                                if not amount.isnumeric() or int(amount) > length:
                                    print(f"[Error] Please enter an integer between 1 to {length - 1}")
                                else:
                                    crime_on_each_day_list = get_crime_for_city(city_content_url, int(amount))
                                    for single_day_instance_list in crime_on_each_day_list:
                                        for each_crime_entry in single_day_instance_list:
                                            insert_entry_into_crime_instance_list_table(each_crime_entry, state_id_dict[state.lower()])
                                    for i in range(int(amount)):
                                        print('[', i + 1, ']', crime_label_list[i])
                                    number = input('Choose a number and see details:\n')
                                    for entry in crime_on_each_day_list[int(number) - 1]:
                                        print(entry)
                                    xvals = []
                                    yvals = []
                                    for label in crime_label_list[0:int(amount)]:
                                        xvals.append(str(label))
                                    # b = ['04/26/2020 Crime Blotter', '04/27/2020 Crime Blotter', '04/28/2020 Crime Blotter', '04/29/2020 Crime Blotter']
                                    # xvals = b[0:int(amount)]
                                    # xvals.append()
                                    # xvals = crime_label_list[0:int(amount)]
                                    for crime in crime_on_each_day_list:
                                        yvals.append(len(crime))
                                    # print(xvals)
                                    # print(yvals)
                                    # xvals.append(1)
                                    # xvals.append(2)
                                    # xvals.append(3)
                                    # yvals.append(1)
                                    # yvals.append(2)
                                    # yvals.append(3)
                                    bar_data = go.Bar(x=xvals, y=yvals)
                                    basic_layout = go.Layout(title="Number of crime vs. date")
                                    fig = go.Figure(data=bar_data, layout=basic_layout)
                                    fig.show()
                                    notGetback = False



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('inputs.html') # just the static html

@app.route('/handle_form', methods=['POST'])
def handle_the_form():
    state = request.form['state']
    city = request.form['city']
    info_type = request.form['info_type']
    amount = request.form['amount']
    
    #TODO: RETURN THE CORRESPONDING RESPONSE
    return handle_the_request(state, city, info_type, amount)


if __name__ == "__main__":
    # app.run(debug=True)
    CACHE_DICT = open_cache()
    while True:
        operation_type = input('User Menu:\nType 1 if you would like to operate on browser.\nType 2 if you would like to operate on terminal.\nType exit if you would like to exit the program.\n')
        if operation_type == '1':
            app.run(debug=True)
        elif operation_type == '2':
            operate_on_terminal()
        elif operation_type == 'exit':
            print("Thank you for using this program. Bye!")
            sys.exit()



    