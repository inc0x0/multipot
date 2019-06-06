from app import db, models
from sqlalchemy import desc, func
from collections import Counter
from urllib.parse import urlparse
from datetime import datetime, timedelta
# from defusedxml.ElementTree import fromstring
import requests


# When "today" and not last 24h wanted:
# data_number_requests_today = len([1 for x in data_requests_last_24h if x.timestamp.day == datetime.utcnow().day])


def ip_addresses_top(x, days):
    # 0 = all time
    if days == 0:
        data_top_ip = [{'remote_addr': q.remote_addr, 'qty': q.qty}
                       for q in
                       db.session.query(func.count(models.Request.remote_addr).label('qty'), models.Request.remote_addr
                                        ).group_by(models.Request.remote_addr).order_by(desc('qty')).limit(x)]
        return data_top_ip
    else:
        data_top_ip = [{'remote_addr': q.remote_addr, 'qty': q.qty}
                       for q in
                       db.session.query(func.count(models.Request.remote_addr).label('qty'), models.Request.remote_addr
                                        ).filter(models.Request.timestamp > (datetime.utcnow() - timedelta(days=days))
                                                 ).group_by(models.Request.remote_addr).order_by(desc('qty')).limit(x)]
        return data_top_ip


def wordpress_wp_login_usernames_password_tries_top(x):
    data_form = db.session.query(models.Request.form).filter_by(endpoint='wp_login', method='POST').all()
    data_usernames = [i[0]['log'] for i in data_form]
    data_pwds = [i[0]['pwd'] for i in data_form]
    data_usernames_tries_counted = Counter(data_usernames).most_common(x)
    data_pwds_tries_counted = Counter(data_pwds).most_common(x)
    return data_usernames_tries_counted, data_pwds_tries_counted


def wordpress_wp_login_password_tries_count():
    data_count = db.session.query(models.Request.form).filter_by(endpoint='wp_login', method='POST').count()
    return data_count


def wordpress_wp_login_password_tries_last_24h_count():
    data_count = db.session.query(models.Request).filter(
        models.Request.timestamp > (datetime.utcnow() - timedelta(days=1)), models.Request.endpoint == 'wp_login',
        models.Request.method == 'POST').count()
    return data_count


def stored_requests_count():
    data_count = db.session.query(models.Request).count()
    return data_count


def endpoints_top(x):
    data_endpoints = db.session.query(models.Request.endpoint).all()
    data_endpoints_counted = Counter(data_endpoints).most_common(x)
    return data_endpoints_counted


def paths_top(x):
    data_url = db.session.query(models.Request.url).all()
    data_url_path = [urlparse(url[0]).path for url in data_url]
    data_url_path_counted = Counter(data_url_path).most_common(x)
    return data_url_path_counted


def distinct_ip_addresses_count():
    data_number_distinct_ip = db.session.query(models.Request.remote_addr).distinct().count()
    return data_number_distinct_ip


def distinct_ip_addresses_last_24h_count():
    data_distinct_ip_last_24h = db.session.query(models.Request.remote_addr).filter(
        models.Request.timestamp > (datetime.utcnow() - timedelta(days=1))).distinct().count()
    return data_distinct_ip_last_24h


def requests_last_24h_count():
    data_requests_last_24h_count = db.session.query(models.Request).filter(
        models.Request.timestamp > (datetime.utcnow() - timedelta(days=1))).count()
    return data_requests_last_24h_count


def requests_last_x_hours_chart(x):
    if int(x) > 24:
        return [], []
    requests_last_24h = db.session.query(models.Request).filter(
        models.Request.timestamp > (datetime.utcnow() - timedelta(hours=x))).all()
    dates = [h.timestamp.replace(microsecond=0, second=0, minute=0) for h in requests_last_24h]
    dates_counted = list(Counter(dates).items())
    dates_counted = sorted(dates_counted)
    # drop requests from previous hour, e.g. 4h back:  17:15 -> 13:15 (but we want till 13:00). So we go back to 12:15 and then drop all requests from 12:**, and check that it is the same day
    if ((len(dates_counted) != 0) and (dates_counted[0][0].hour == (datetime.utcnow() - timedelta(hours=x)).hour) and (dates_counted[0][0].day == (datetime.utcnow() - timedelta(hours=x)).day)):
        dates_counted.pop(0)
    # create list with all hours, to fill hours with zero requests
    print(dates_counted)
    hour_list = []
    for i in reversed(range(x)):
        hour_list.append((datetime.utcnow() - timedelta(hours=i)).replace(microsecond=0, second=0, minute=0))
    for i in hour_list:
        if i not in [x[0] for x in dates_counted]:
            dates_counted.append((i, 0))
    dates_counted_sorted = sorted(dates_counted)
    days = [i[0].strftime("%d. %b %H:%M") for i in dates_counted_sorted]
    requests = [i[1] for i in dates_counted_sorted]
    return days, requests


# todo: works, however, leaves out days where 0 requests were recorded
def requests_last_x_days_chart(x):
    requests_last_x_days = db.session.query(models.Request).filter(
        models.Request.timestamp > (datetime.utcnow().date() - timedelta(days=x-1))).all()
    days = [h.timestamp.date() for h in requests_last_x_days]
    days_counted = list(Counter(days).items())
    days_counted_sorted = sorted(days_counted, key=lambda day: day)
    days = [i[0].isoformat() for i in days_counted_sorted]
    requests = [i[1] for i in days_counted_sorted]
    return days, requests


"""
# clean (defusedxml) version of the wordpress_xmlrcp_username_password_tries_top function below, however very slow
def wordpress_xmlrcp_username_password_tries_top(x):
    usernames = []
    passwords = []
    data_form = db.session.query(models.Request.form).filter_by(endpoint='wp_xmlrpc', method='POST').all()
    for a in data_form:
        key = list(a[0].keys())[0]
        value = list(a[0].values())[0]
        root = fromstring(key+"="+value)
        username_password = root.findall("./params/param/value/array/data/value/struct/member/value/array/data/value/array/data/value/string")
        if len(username_password) == 2:
            usernames.append(username_password[0].text)
            passwords.append(username_password[1].text)
        else:
            continue
    usernames = Counter(usernames).most_common(x)
    passwords = Counter(passwords).most_common(x)
    return usernames, passwords
"""


# not ideal as it would fail to account for newlines or spaces in the form string, etc.
# TODO: evaluate sane methods to parse xml. 'defusedxml' is too slow
# ? content = re.sub('\s+', ' ', content)  # condense all whitespace
# ? content = re.sub('[^A-Za-z ]+', '', content)  # remove non-alpha chars
def wordpress_xmlrpc_username_password_tries_top(x):
    usernames = []
    passwords = []
    data_form = db.session.query(models.Request.form).filter_by(endpoint='wp_xmlrpc', method='POST').all()
    for a in data_form:
        value = list(a[0].values())[0]
        try:
            b = value.split("<member><name>params</name><value><array><data><value><array><data><value><string>")
            c = b[1].split("</string></value></data></array></value></data></array></value></member>")
            d = c[0].split("</string></value><value><string>")
            usernames.append(d[0])
            passwords.append(d[1])
        except:
            continue
    usernames = Counter(usernames).most_common(x)
    passwords = Counter(passwords).most_common(x)
    return usernames, passwords


def wordpress_xmlrpc_password_tries_count():
    counter = 0
    data_form = db.session.query(models.Request.form).filter_by(endpoint='wp_xmlrpc', method='POST').all()
    for a in data_form:
        value = list(a[0].values())[0]
        if any(x in value for x in ['getUserBlogs', 'getUsersBlogs']):
            counter = counter + 1
    return counter


def wordpress_xmlrpc_password_tries_last_24h_count():
    counter = 0
    data_form = db.session.query(models.Request.form).filter(
        models.Request.timestamp > (datetime.utcnow() - timedelta(days=1)), models.Request.endpoint == 'wp_xmlrpc',
        models.Request.method == 'POST').all()
    for a in data_form:
        value = list(a[0].values())[0]
        if any(x in value for x in ['getUserBlogs', 'getUsersBlogs']):
            counter = counter + 1
    return counter


def gather_ip_geo_whois(ip):
    r = requests.get("http://ip-api.com/json/"+ip+"?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,reverse,mobile,proxy,query").json()
    return r


def requests_all_days_chart(ip):
    data_timestamp = db.session.query(models.Request.timestamp).filter_by(remote_addr=ip).all()
    dates = [h.timestamp.date() for h in data_timestamp]
    days_counted = list(Counter(dates).items())
    days_counted_sorted = sorted(days_counted, key=lambda day: day)
    days = [i[0].isoformat() for i in days_counted_sorted]
    requests = [i[1] for i in days_counted_sorted]
    return days, requests
