import requests
from bs4 import BeautifulSoup
import dateutil.parser
import datetime
from flask import (
    Flask,
    request,
    render_template
)

app = Flask(__name__, template_folder='pages')

#finding relative time of the issue
def date_diff(issue_date):
    diff = datetime.datetime.utcnow() - issue_date
    if diff.days <= 1 and diff.days >= 0:
        return 1
    elif diff.days > 1 and diff.days < 7:
        return 2
    else:
        return 3

#formats the response
def html_formatter(one_day, seven_day, total):
    resp_template = ''
    with open('pages/response_template.txt', 'r') as file:
        resp_template = file.read().replace('\n', '')
    return resp_template.format(one_day, seven_day, total - (one_day + seven_day), total)

#counts the total open issues
def get_total_requests(soup):
    for x in soup.findAll('a', attrs={'class': 'js-selected-navigation-item selected reponav-item'}):
        for y in x.findAll('span', attrs={'class': 'Counter'}):
            total_requests = int(y.text.replace(',', ''))
    return total_requests


@app.route("/issues")
def get_issues():
    try:
        URL = request.args['GitURL'] + '/pulls'
        r = requests.get(URL)

        soup = BeautifulSoup(r.content, 'html5lib')

        one_day_old = 0
        seven_days_old = 0
        total_requests = get_total_requests(soup)

        count = 0
        for x in soup.findAll('div', attrs={'class': 'pagination'}):
            for y in x.findAll('em'):
                count = int(y['data-total-pages'])
                break
            gen_url = ''
            for w in x.findAll('a'):
                gen_url = w['href']
                break
            gen_url = gen_url.split('&')
            first = gen_url[0].split('=')[0] + '='
            for z in range(1, count + 1):
                page = 'http://github.com' + first + str(z) + '&' + gen_url[1]
                r = requests.get(page)
                mysoup = BeautifulSoup(r.content, 'html5lib')
                done = False
                for a in mysoup.findAll('span', attrs={'class': 'opened-by'}):
                    for b in a.findAll('relative-time'):
                        d = dateutil.parser.parse(b['datetime'])
                        d = d.replace(tzinfo=None)
                        days_old = date_diff(d)
                        if days_old == 1:
                            one_day_old += 1
                        elif days_old == 2:
                            seven_days_old += 1
                        else:
                            done = True
                            break
                    if done:
                        break
                if done:
                    break

        output = html_formatter(one_day_old, seven_days_old, total_requests)
        return output
    except Exception:
        return 'Invalid GitHub Repository URL'


@app.route("/")
def home():
    return render_template('home.html')
