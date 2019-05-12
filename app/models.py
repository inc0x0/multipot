from datetime import datetime
from app import db


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, index=True)
    form = db.Column(db.JSON())  # POST data in request body
    headers = db.Column(db.JSON())  # HTTP request headers
    args = db.Column(db.JSON())  # url arguments
    url = db.Column(db.String(3000))  # url, incl arguments
    data = db.Column(db.String(10000))  # request data in case it came with a mimetype Werkzeug doesn't handle
    files = db.Column(db.JSON())  # metadata of uploaded files
    remote_addr = db.Column(db.String(100))  # IP address of client
    method = db.Column(db.String(7))  # HTTP method used
    endpoint = db.Column(db.String(50))  # name of flask endpoint handling the request
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return "<Request %s>" % self.uuid

    def todict(self):
        return {'id':self.id, 'uuid':self.uuid, 'form':self.form, 'headers':self.headers, 'args':self.args,
                'url':self.url, 'data':self.data, 'files':self.files, 'remote_addr':self.remote_addr,
                'method':self.method, 'endpoint':self.endpoint, 'timestamp':self.timestamp}


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_uuid = db.Column(db.String(36), db.ForeignKey('request.uuid'), index=True)
    status = db.Column(db.String(50))  # HTTP status
    status_code = db.Column(db.Integer)  # HTTP status code
    headers = db.Column(db.JSON)  # HTTP response headers
    # data = db.Column(db.String(30000))  # HTTP response content, currently not saved

    def __repr__(self):
        return "<Response %s>" % self.request_id

    def todict(self):
        return {'id':self.id, 'request_uuid':self.request_uuid, 'status':self.status, 'status_code':self.status_code,
                'headers':self.headers}
