from app import app
from flask import request, jsonify, render_template
from config import Config
from app.wrappers import token_required
from app.analysis_functions import *



# Returns an excerpt of all stored request/response pairs
@app.route('/api/analysis/data')
@token_required
def api_analysis_data():
    # omits rows when response or request is missing
    data = [{'uuid': req.uuid,
             'request': {'id': req.id, 'url': req.url, 'timestamp': req.timestamp, 'method': req.method,
                         'remote_addr': req.remote_addr},
             'response': {'status': resp.status, 'headers': resp.headers}}
            for req in models.Request.query.all()
            for resp in models.Response.query.filter_by(request_uuid=req.uuid).all()]
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
    # row 2
    requests_chart_last_24h_values, requests_chart_last_24h_index = requests_last_24h_chart()
    data_endpoints_top = endpoints_top(10)
    data_ip_top = ip_addresses_top(10)
    # row 3
    data_url_path_top = paths_top(10)

    # .. the last 30 days
    #requests_last_30d = db.session.query(models.Request).filter(
    #    models.Request.timestamp > (datetime.utcnow() - timedelta(days=30))).all()
    #days = [h.timestamp.day for h in requests_last_30d]
    #print(days)
    #print(Counter(days))

    return render_template('analysis/index.html', data_ip_top=data_ip_top,
                           data_stored_requests_count=data_stored_requests_count, data_endpoints_top=data_endpoints_top,
                           data_url_path_top=data_url_path_top, data_distinct_ip_count=data_distinct_ip_count,
                           data_wp_password_tries_count=data_wp_password_tries_count, data_wp_password_tries_last_24h_count=data_wp_password_tries_last_24h_count,
                           requests_chart_last_24h_values=requests_chart_last_24h_values, requests_chart_last_24h_index=requests_chart_last_24h_index,
                           utc_time_now=datetime.utcnow(), data_requests_last_24h_count=data_requests_last_24h_count,
                           data_distinct_data_ips_last_24h_count=data_distinct_data_ips_last_24h_count, ANALYSIS_TOKEN=Config.ANALYSIS_TOKEN)


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
