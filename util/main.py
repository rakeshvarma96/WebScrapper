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


def prettydate(d):
    diff = datetime.datetime.utcnow() - d
    s = diff.seconds
    # print(diff.days)
    if diff.days <= 1 and diff.days >= 0:
        return 1
    elif diff.days > 1 and diff.days < 7:
        return 2
    else:
        return 3


def get_total_requests(soup):
    for x in soup.findAll('a', attrs={'class': 'js-selected-navigation-item selected reponav-item'}):
        for y in x.findAll('span', attrs={'class': 'Counter'}):
            total_requests = int(y.text.replace(',', ''))
    return total_requests


@app.route("/issues")
def get_issues():
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
                    days_old = prettydate(d)
                    if days_old == 1:
                        one_day_old += 1
                    elif days_old == 2:
                        seven_days_old += 1
                    else:
                        done = True
                        break
                if done:
                    break
                    # print(b['datetime'])
            if done:
                break

    output = '''<table border="1">
  <tr>
    <th>Less than 24 Hours old</th>
    <th>Less than 7 days and more than 24 hours old</th>
    <th>More than 7 days old</th>
    <th>Total Open Issues</th>
  </tr>
  <tr>
    <td>{0}</td>
    <td>{1}</td>
    <td>{2}</td>
    <td>{3}</td>
  </tr>
</table>'''.format(one_day_old, seven_days_old, total_requests - (one_day_old + seven_days_old), total_requests)
    return output


@app.route("/")
def home():
    return render_template('home.html')


app.run(debug=True)
