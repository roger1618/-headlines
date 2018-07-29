import datetime
import feedparser
from flask import Flask,render_template, request, make_response
import json
import urllib.parse
#import urllib2
import urllib
import urllib.error
from urllib.request import urlopen
app = Flask(__name__)
RSS_FEED = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
            'cnn': 'http://rss.cnn.com/rss/edition.rss',
            'fox': 'http://feeds.foxnews.com/foxnews/latest',
            'iol': 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication':'bbc', 'city' : 'London,UK','currency_from':'GBP','currency_to':'USD'}
WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=3a238c8cc96861482b5e407c0a14fe62'
CURRENCY_URL = 'https://openexchangerates.org/api/latest.json?app_id=5f187f2176e94aa9954032b897f28d78%20'
@app.route("/")
def home() :

    # GET headlines customizadas, baseadas na entrada do usuário ou Default
    publication = get_value_with_fallback("publication")
    articles = get_news(publication)

    # GET clima customizado baseado nas entradas do usuário ou Default
    city = get_value_with_fallback("city")
    weather = get_weather(city)

    #GET moeda customizada baseado no entrada do usuário ou Default
    currency_from = get_value_with_fallback("currency_from")
    currency_to = get_value_with_fallback("currency_to")
    rate,currencies = get_rate(currency_from, currency_to)
    
    #save cookies e return template
    response = make_response( render_template("home.html", articles = articles, weather=weather,currency_from = currency_from, currency_to= currency_to, rate= rate, currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from",currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response

def get_news(query):
    if not query or query.lower() not in RSS_FEED:
        publication =DEFAULTS["publication"]
    else :
        publication = query.lower()
    feed = feedparser.parse(RSS_FEED[publication])
    return feed['entries'] 

def get_weather(query):
    query = urllib.parse.quote(query)
    url=WEATHER_URL.format(query)
    data = urlopen(url).read()
    parsed =json.loads(data)
    weather = None
    if parsed.get("weather") :
        weather = {"description":parsed["weather"][0]["description"],
                   "temperature":parsed["main"]["temp"],
                   "city":parsed["name"],
                   "country":parsed["sys"]["country"]
                   }
    return weather
def get_rate(frm, to):
    all_currency = urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate/frm_rate,parsed.keys())

def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]

if __name__ == '__main__':
    app.run(port = 5000, debug=True)
