from app import db, models
from flask import  request
import tempfile, os


def save_request(uuid, req):
    files = []
    for name, fs in request.files.items():
        dst = tempfile.NamedTemporaryFile()
        fs.save(dst)
        dst.flush()
        filesize = os.stat(dst.name).st_size
        dst.close()
        files.append({'name': name, 'filename': fs.filename, 'filesize': filesize,
                      'mimetype': fs.mimetype, 'mimetype_params': fs.mimetype_params})
    r = models.Request(uuid=uuid, endpoint=req.endpoint, method=req.method, url=req.url,
                       data=req.data.decode("utf-8"), headers=dict(req.headers),
                       args=req.args, form=req.form, remote_addr=req.remote_addr,
                       files={i:item for i, item in enumerate(files)})
    db.session.add(r)
    db.session.commit()


def save_response(uuid, resp):
    # Currently not stored: data=list(resp.response)[0].decode("utf-8")
    r = models.Response(request_uuid=uuid, status=resp.status, status_code=resp.status_code,
                        headers=dict(resp.headers))
    db.session.add(r)
    db.session.commit()
