# coding:utf-8

from flask import request, Flask
from werkzeug.utils import secure_filename

app = Flask(__name__)


# 用 flask 库作为 server 接收文件，并保存到当前目录
@app.route('/service', methods=['POST'])
def service():
    f = request.files['file']
    f.save('./' + 'recv-' + secure_filename(f.filename))
    return 'ok'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888)
