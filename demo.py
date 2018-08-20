from flask import Flask, request, Response, make_response
from werkzeug.utils import secure_filename
import os, re
from flask_restful import Api
from flask import Response

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    return """
         <!doctype html>
            <html>
            <body>
            <form action='upload/' method='post' enctype='multipart/form-data'>
             <input type='file' name='videofile'>
             <input type='submit' value='Upload'>
            </form>
    """


@app.route('/upload/', methods=["GET", "POST"])
def upload():
    if request.method=="POST":
        f = request.files["videofile"]
        filename = secure_filename(f.filename)
        upload_path = os.path.join('./', 'uploads',
                                   filename)
        f.save(upload_path)
        return filename


@app.route('/video/<name>/', methods=["GET"])
def file(name):
    p = os.getcwd()+'/uploads/' + name
    f = open(p, 'rb')
    # 获取文件大小
    f.seek(0, os.SEEK_END)
    filesize = f.tell()
    f.seek(0, os.SEEK_SET)
    resp = Response(f, mimetype="video/mp4")
    if request.headers.get("Range"):
        # 通过Range大小返回不同Content-Range
        range_value = request.headers["Range"]
        HTTP_RANGE_HEADER = re.compile(r'bytes=([0-9]+)\-(([0-9]+)?)')
        m = re.match(HTTP_RANGE_HEADER, range_value)
        if m:
            start_str = m.group(1)
            start = int(start_str)
            end_str = m.group(2)
            end = -1
            if len(end_str) > 0:
                end = int(end_str)
            resp.status_code = 206
            resp.headers["Content-Type"] = "video/mp4"

            if end == -1:
                resp.headers["Content-Length"] = str(filesize - start)
            else:
                resp.headers["Content-Length"] = str(end - start + 1)
            resp.headers["Accept-Ranges"] = "bytes"
            if end < 0:
                content_range_header_value = "bytes %d-%d/%d" % (start, filesize - 1, filesize)
            else:
                content_range_header_value = "bytes %d-%d/%d" % (start, end, filesize)
            resp.headers["Content-Range"] = content_range_header_value

            resp.headers["Connection"] = "close"

        resp.status_code = 200
    return resp


app.run(debug=True)