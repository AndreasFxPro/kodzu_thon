import os
import datetime
import requests
import urllib
import json
import uuid
import random

from googletrans import Translator
from googlesearch import search
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import python_weather
from telethon import events

city_name = os.environ.get('TELETHON_CITY', 'Odessa')

# create folders
if not os.path.exists('img'):
    os.makedirs('img')
    print(f"Created dir /img")

symbols = '😂👍😉😭🧐🤷‍♂️😡💦💩😎🤯🤬🤡👨‍👨‍👦👨‍👨‍👦‍👦'


def influx_query(query_str: str):
    try:
        url = 'http://localhost:8086/write?db=bots'
        headers = {'Content-Type': 'application/Text'}

        x = requests.post(url, data=query_str.encode('utf-8'), headers=headers)
    except Exception as e:
        print(e)


def get_btc():
    r = requests.get(url = "https://api.coindesk.com/v1/bpi/currentprice.json") 

    # extracting data in json format
    data = r.json() 

    price = data['bpi']['USD']['rate']
    price = price.replace(',','')
    price = int(float(price))

    price = f'Bitcoint price: {price} USD'

    return price


def get_weather():
    weather_string = 'Weather forecast is not completed yet'
    return weather_string


def get_upload_temp_data(raw_api_dict):
    try:
        # current weather
        temperature = raw_api_dict['current']
        humidity = raw_api_dict['humidity']

        data_str = f'iot,room=outside_rzeszow,device=kodzuthon,sensor=openweather_api temperature={temperature},humidity={humidity}'
        influx_query(data_str)

    except Exception as e:
        print(e)


async def get_raw_temp():
    raw_api_dict = {}
    raw_api_dict['current'] = 0
    raw_api_dict['humidity'] = 0

    try:
        # declare the client. format defaults to metric system (celcius, km/h, etc.)
        client = python_weather.Client(format=python_weather.METRIC)

        # fetch a weather forecast from a city
        weather = await client.find(city_name)

        # close the wrapper once done
        await client.close()

        raw_api_dict['current'] = weather.current.temperature
        raw_api_dict['humidity'] = weather.current.humidity
    except:
        pass

    return raw_api_dict


def get_temp(raw_api_dict):
    # current weather
    current = raw_api_dict['current']
    temp = f"{current}cm"

    return temp


def get_covid():
    def make_countrystring(country):
        return f"{country['Country']}: +{country['NewConfirmed']}/{country['TotalConfirmed']}"

    try:
        url = urllib.request.urlopen('https://api.covid19api.com/summary')
        output = url.read().decode('utf-8')
        raw_api_dict = json.loads(output)
        url.close()

        countries = raw_api_dict['Countries']
        countries = {f['CountryCode']:f for f in countries}

        pl = countries['PL']
        ua = countries['UA']
        cz = countries['CZ']
        br = countries['BY']

        pl = make_countrystring(pl)
        ua = make_countrystring(ua)
        cz = make_countrystring(cz)
        br = make_countrystring(br)

        ret = f'{pl}\n{ua}\n{cz}\n{br}\n\ncovid19api.com'
        return ret
    except:
        return 'Caching in progress...'


def get_year_progress(length=20):
    def progressBar(value, total = 100, prefix = '', suffix = '', decimals = 2, length = 100, fill = '█'):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (value / float(total)))
        filledLength = int(length * value // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        return f'{prefix} |{bar}| {percent}% {suffix}'

    from datetime import datetime
    day_of_year = datetime.now().timetuple().tm_yday
    timenow = datetime.now().strftime("%H:%M")
    yr = progressBar(day_of_year, 365, length=length)
    yr = f'{yr} {day_of_year}/365'
    # yr = f'2020:{yr}{timenow} {day_of_year}/365 days'

    return yr


def get_life_progress():
    def progressBar(value, total = 100, prefix = '', suffix = '', decimals = 2, length = 100, fill = '█'):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (value / float(total)))
        filledLength = int(length * value // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        return f'{prefix} |{bar}| {percent}% {suffix}'

    # from datetime import datetime
    date_time_obj = datetime.datetime.strptime('2003-05-08', '%Y-%m-%d')
    day_of_year = (datetime.datetime.now() - date_time_obj)
    days = day_of_year.days
    # pb = progressBar(days, 29200, prefix = 'Life progress: ', length=20)
    percent = ("{0:." + str(5) + "f}").format(100 * (days / float(29200)))
    yr = f'Uptime {days} days. Progress {percent}%'

    return yr


def get_new_cases(country):
    try:
        url = urllib.request.urlopen(f'https://api.covid19api.com/dayone/country/{country}/status/confirmed/live')
        output = url.read().decode('utf-8')
        raw_api_dict = json.loads(output)
        url.close()

        cases = [f['Cases'] for f in raw_api_dict]
        cases = list(map(lambda i: i[0] - i[1], zip(cases, [0] + cases)))

        #datetime format => '2020-03-27T00:00:00Z'
        days = [ datetime.datetime.strptime(f['Date'], '%Y-%m-%dT%H:%M:%SZ') for f in raw_api_dict]

        # Remove todays day because its always zeros
        days = days[:-1]
        cases = cases[:-1]

        # Take last 2 months
        fr = 60
        days = days[-fr:]
        cases = cases[-fr:]

        return days, cases
    except:
        return [],[]


def covid_graph():
    ukraine_days, ukraine_cases = get_new_cases(country='ukraine')
    poland_days, poland_cases = get_new_cases(country='poland')
    belarus_days, belarus_cases = get_new_cases(country='belarus')

    # Calculate per population
    ukraine_cases = [case / 41.98e6 * 1e6 for case in ukraine_cases]
    poland_cases = [case / 37.97e6 * 1e6 for case in poland_cases]
    belarus_cases = [case / 9.4e6 * 1e6 for case in belarus_cases]

    # Make chart
    pio.templates.default = "plotly_dark"
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=belarus_days, y=belarus_cases,mode='lines+markers', name='Belarus'))
    fig.add_trace(go.Scatter(x=poland_days, y=poland_cases,mode='lines+markers',name='Poland'))
    fig.add_trace(go.Scatter(x=ukraine_days, y=ukraine_cases,mode='lines+markers',name='Ukraine'))

    fig.update_layout(title='Covid new cases trends per population',
                    yaxis_title='New cases per population')

    # Save to image
    image_path = 'img/' + str(uuid.uuid4()) + '.png'
    fig.write_image(image_path)
    print(f'Image saved to {image_path}')
    return image_path


def get_sat_img():
    fname = 'img/' + datetime.datetime.now().strftime("%m%d%Y%H_%M_%S") + '.jpg'

    with open(fname, 'wb') as handle:
        response = requests.get('https://en.sat24.com/image?type=visual&region=eu', stream=True)

        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)

        return fname


def random_emoji():
    f = open(file = 'emojis.txt',mode = 'r', encoding = 'utf-8')
    emojis = f.readline()
    f.close()
    return random.choice(emojis)


def random_otmazka():
    f = open(file = 'otmazki.txt', mode = 'r', encoding = 'utf-8')
    lines = f.readlines()
    f.close()
    return random.choice(lines)


def break_text(msg_text):
    count = int(len(msg_text)/4)

    for i in range(count):
        emotion = random.choice(symbols)
        ind = random.randint(0, len(msg_text))
        msg_text = msg_text[:ind] + emotion + msg_text[ind:]

    return msg_text


def translate_text(msg_text, dest = 'ru', silent_mode = False) -> str:
    try:
        translator = Translator()
        result = translator.translate(msg_text, dest=dest)

        return_text = '' if silent_mode else f'Translated from: {result.src}\n\n'
        return_text += f'{result.text}'
        return return_text
    except:
        return "Can't translate"


def google_search(text: str) -> str:
    try:
        result = search(text, num_results=1)
        result = result[0].replace('https://','').replace('http://','')
        return result
    except Exception as e:
        return str(e)


async def build_user_info(event: events.NewMessage.Event):
    try:
        msg = await event.message.get_reply_message()
        try:
            sender_name = f'{msg.sender.title}'
        except:
            sender_name = f'{msg.sender.first_name} {msg.sender.last_name}'

        reply_text = f'┌ Scan info:\n'\
                     f'├ Username: @{msg.sender.username}\n'\
                     f'├ User id: {msg.sender.id}\n'\
                     f'├ Full name: {sender_name}\n'\
                     f'├ Chat id: {event.chat_id}\n'\
                     f'└ Message id: {event._message_id}'

        return reply_text

    except Exception as e:
        print(e)
        return f'ERROR!\n\n{e}'
