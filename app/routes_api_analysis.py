from app import app
from flask import request, jsonify, render_template
from config import Config
from app.wrappers import token_required
from app.analysis_functions import *
import ipaddress


# Returns an excerpt of all stored request/response pairs
# not used
@app.route('/api/analysis/data')
@token_required
def api_analysis_data():
    # omits rows when response or request is missing
    data = {"data": [{'uuid': req.uuid,
             'request': {'id': req.id, 'url': req.url, 'timestamp': req.timestamp, 'method': req.method,
                         'remote_addr': req.remote_addr},
             'response': {'status': resp.status, 'headers': resp.headers}}
            for req in models.Request.query.all()
            for resp in models.Response.query.filter_by(request_uuid=req.uuid).all()]}
    return jsonify(data)


@app.route('/api/analysis/<uuid:uuid>', methods=['GET', 'DELETE'])
@token_required
def api_analysis_data_uuid(uuid):
    uuid = str(uuid)
    if request.method == 'GET':
        req = models.Request.query.filter_by(uuid=uuid).first()
        resp = models.Response.query.filter_by(request_uuid=uuid).first()
        if req and resp:
            data = {'request': req.todict(), 'response': resp.todict()}
            return jsonify(data)
        else:
            return jsonify({'message': 'No such UUID'}), 404
    if request.method == 'DELETE':
        req = models.Request.query.filter_by(uuid=uuid).first()
        resp = models.Response.query.filter_by(request_uuid=uuid).first()
        if req and resp:
            db.session.delete(req)
            db.session.delete(resp)
            db.session.commit()
            return jsonify({'message': 'Delete success'})
        else:
            return jsonify({'message': 'No such UUID'}), 404


# not used
@app.route('/api/analysis/ip/<ip>')
@token_required
def api_analysis_ip(ip):
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return jsonify({'message': 'Not a valid IP address'}), 404
    data = [{'uuid': req.uuid,
             'request': {'id': req.id, 'url': req.url, 'timestamp': req.timestamp, 'method': req.method,
                         'remote_addr': req.remote_addr}}
            for req in models.Request.query.filter_by(remote_addr=ip).all()]
    return jsonify(data)


@app.route('/api/analysis/ip/geoinfo/<ip>')
@token_required
def api_geoinfo_ip(ip):
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return jsonify({'message': 'Not a valid IP address'}), 404
    geo_whois = gather_ip_geo_whois(ip)
    return jsonify(geo_whois)


@app.route('/api/analysis/chart/requests/days/<int:days>', methods=['GET'])
@token_required
def api_analysis_chart_requests_last_x_days(days):
    requests_chart_last_x_days_days, requests_chart_last_x_days_requests = requests_last_x_days_chart(days)
    return jsonify({'days': requests_chart_last_x_days_days, 'requests': requests_chart_last_x_days_requests})


@app.route('/api/analysis/chart/requests/hours/<int:hours>', methods=['GET'])
@token_required
def api_analysis_chart_requests_last_x_hours(hours):
    requests_chart_last_x_days_hours, requests_chart_last_x_hours_requests = requests_last_x_hours_chart(hours)
    return jsonify({'hours': requests_chart_last_x_days_hours, 'requests': requests_chart_last_x_hours_requests})


@app.route('/api/analysis/table/top-ips/<int:top>/days/<int:days>', methods=['GET'])
@token_required
def api_analysis_table_ip_addresses_top(top, days):
    data_top_ip = ip_addresses_top(top, days)
    return jsonify(data_top_ip)


@app.route('/analysis/index')
@token_required
def analysis_index():
    # row 1
    data_stored_requests_count = stored_requests_count()
    data_requests_last_24h_count = requests_last_24h_count()
    data_distinct_ip_count = distinct_ip_addresses_count()
    data_distinct_data_ips_last_24h_count = distinct_ip_addresses_last_24h_count()
    data_wp_password_tries_count = wordpress_wp_login_password_tries_count() + wordpress_xmlrpc_password_tries_count()
    data_wp_password_tries_last_24h_count = wordpress_wp_login_password_tries_last_24h_count() + wordpress_xmlrpc_password_tries_last_24h_count()
    # row 3
    data_url_path_top = paths_top(10)
    data_endpoints_top = endpoints_top(10)
    return render_template('analysis/index.html', ANALYSIS_TOKEN=Config.ANALYSIS_TOKEN,
                           data_stored_requests_count=data_stored_requests_count, data_endpoints_top=data_endpoints_top,
                           data_url_path_top=data_url_path_top, data_distinct_ip_count=data_distinct_ip_count,
                           data_wp_password_tries_count=data_wp_password_tries_count, data_wp_password_tries_last_24h_count=data_wp_password_tries_last_24h_count,
                           utc_time_now=datetime.utcnow(), data_requests_last_24h_count=data_requests_last_24h_count,
                           data_distinct_data_ips_last_24h_count=data_distinct_data_ips_last_24h_count)


@app.route('/analysis/details')
@token_required
def analysis_details():
    data = [{'uuid': req.uuid,
             'request': {'id': req.id, 'url': req.url, 'timestamp': req.timestamp, 'method': req.method,
                         'remote_addr': req.remote_addr}}
            for req in models.Request.query.all()]
    return render_template('analysis/details.html', table_content=data, ANALYSIS_TOKEN=Config.ANALYSIS_TOKEN)


@app.route('/analysis/wordpress')
@token_required
def analysis_wordpress():
    # general
    data_wordpress_wp_login_password_tries_count = wordpress_wp_login_password_tries_count()
    data_wordpress_xmlrpc_password_tries_count = wordpress_xmlrpc_password_tries_count()
    data_wordpress_wp_login_password_tries_last_24h_count = wordpress_wp_login_password_tries_last_24h_count()
    data_wordpress_xmlrpc_password_tries_last_24h_count = wordpress_xmlrpc_password_tries_last_24h_count()
    # row 1
    data_wp_password_tries_count = data_wordpress_wp_login_password_tries_count + data_wordpress_xmlrpc_password_tries_count
    data_wp_password_tries_last_24h_count = data_wordpress_wp_login_password_tries_last_24h_count + data_wordpress_xmlrpc_password_tries_last_24h_count
    #data_wordpress_wp_login_password_tries_count
    #data_wordpress_wp_login_password_tries_last_24h_count
    #data_wordpress_xmlrpc_password_tries_count
    #data_wordpress_xmlrpc_password_tries_last_24h_count
    data_distinct_passwords_tried = len(wordpress_wp_login_usernames_password_tries_top(None)[1] + wordpress_xmlrpc_username_password_tries_top(None)[1])
    # row 2
    data_wp_login_usernames_top, data_wp_login_passwords_top = wordpress_wp_login_usernames_password_tries_top(10)
    data_wp_xmlrpc_usernames_top, data_wp_xmlrpc_passwords_top = wordpress_xmlrpc_username_password_tries_top(10)
    return render_template('analysis/wordpress.html', ANALYSIS_TOKEN=Config.ANALYSIS_TOKEN,
                           data_wp_password_tries_count=data_wp_password_tries_count,
                           data_wp_password_tries_last_24h_count=data_wp_password_tries_last_24h_count,
                           data_wordpress_wp_login_password_tries_count=data_wordpress_wp_login_password_tries_count,
                           data_wordpress_wp_login_password_tries_last_24h_count=data_wordpress_wp_login_password_tries_last_24h_count,
                           data_wordpress_xmlrpc_password_tries_count=data_wordpress_xmlrpc_password_tries_count,
                           data_wordpress_xmlrpc_password_tries_last_24h_count=data_wordpress_xmlrpc_password_tries_last_24h_count,
                           data_distinct_passwords_tried=data_distinct_passwords_tried,
                           data_wp_login_usernames_top=data_wp_login_usernames_top,
                           data_wp_login_passwords_top=data_wp_login_passwords_top,
                           data_wp_xmlrpc_usernames_top=data_wp_xmlrpc_usernames_top,
                           data_wp_xmlrpc_passwords_top=data_wp_xmlrpc_passwords_top
                           )


@app.route('/analysis/ip')
@token_required
def analysis_ip():
    ip = request.args.get('ip')
    try:
        if ip is None:
            raise ValueError("No IP received.")
        ipaddress.ip_address(ip)
    except ValueError:
        return render_template('analysis/ip.html', ANALYSIS_TOKEN=Config.ANALYSIS_TOKEN, IP="")
    data_table = [{'uuid': req.uuid,
                  'request': {'id': req.id, 'url': req.url, 'timestamp': req.timestamp, 'method': req.method,
                              'remote_addr': req.remote_addr}}
                 for req in models.Request.query.filter_by(remote_addr=ip).all()]
    geo_whois = gather_ip_geo_whois(ip)
    bar_days, bar_requests = requests_all_days_chart(ip)
    return render_template('analysis/ip.html', ANALYSIS_TOKEN=Config.ANALYSIS_TOKEN, table_content=data_table, IP=ip, geo_whois=geo_whois, bar_days=bar_days, bar_requests=bar_requests)
