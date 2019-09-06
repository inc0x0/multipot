from app import app
from flask import send_from_directory, request, g, jsonify
import uuid
from config import Config
from app.helpers import save_request, save_response


### --- Routes of the honeypot websites --- ###

# Drupal 7
@app.route('/', methods=['GET', 'POST'])
def index():
    # check if "?q=user" for Drupal 6/7 login (currently uses Drupal 8 login page; works because login form parameter are the same in Drupal 6,7,8)
    # TODO: find a way to implement this outside of the index route
    #if request.args['q'] == 'user':
    #    return send_from_directory('static/fake-sites/drupal/', 'login_drupal8.html')
    return send_from_directory('static/fake-sites/drupal/', 'index_drupal7.html')


# Drupal user login
@app.route('/user/login', methods=['GET', 'POST'])
def drupal8_login():
    return send_from_directory('static/fake-sites/drupal/', 'login_drupal8.html')


# Wordpress admin login
@app.route('/wp-admin', methods=['GET', 'POST'])
@app.route('/wp-admin/', methods=['GET', 'POST'])
@app.route('/wp-login.php', methods=['GET', 'POST'])
def wp_login():
    return send_from_directory('static/fake-sites/wordpress/wp-login/', 'wp-login.html')

# Wordpress xmlrpc login
@app.route('/xmlrpc.php', methods=['GET', 'POST'])
def wp_xmlrpc():
    return send_from_directory('static/fake-sites/wordpress/xmlrpc/', 'xmlrpc_faultCode_403.xml')

# Drupal changelog file
@app.route('/CHANGELOG.txt', methods=['GET', 'POST'])
def changelog():
    return send_from_directory('static/fake-sites/drupal/changelogs/', 'CHANGELOG-7.55.txt')

# Owncloud status page
@app.route('/stat')
@app.route('/status')
def status():
    d = {"installed": True, "maintenance": True, "needsDbUpgrade": True, "version": "8.1.7.2", "versionstring": "8.1.7",
         "edition": "Community", "productname": "Secure Cloud"}
    return jsonify(d)


# Catch all, for routes not otherwise covered --> Drupal 7
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:anypath>', methods=['GET', 'POST'])
def catch_all(anypath):
    return send_from_directory('static/fake-sites/drupal/', 'index_drupal7.html')


### --- app objects; used for logging requests and responses made to the server --- ###
### --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ###


@app.before_request
def before_request():
    # only save requests when path is not excluded from logging
    if request.path.startswith(tuple(Config.EXCLUDE_FROM_LOGGING)):
        g.log_response = False
        return
    g.log_response = True
    g.uuid = str(uuid.uuid4())
    save_request(g.uuid, request)


@app.after_request
def after_request(resp):
    # only save response when request was also saved
    if g.log_response is True:
        save_response(g.uuid, resp)
    return resp
