# sudo  /home/panda/anaconda3/bin/pip install flask-admin flask_login flask_sqlalchemy flask_user=1.* flask_compress flask_httpauth flask_restplus protobuf flask_dropzone flask_uploads flask-triangle  flask_restful  flask-locale flask-cors Flask-Caching Flask-BabelEx flask_babel
# sudo docker run -d -p 127.0.0.1:9211:9200 -p 127.0.0.1:9111:5601 -v /home/panda/doc:/home/elastic/data oj/oj4:latest
# nohup ./../anaconda3/bin/python3 wall.py >wall.out.txt 2>wall.err.txt &
from MarkAdmin import *
from MarkFlask import *

app = None
import logging
from logging.handlers import TimedRotatingFileHandler


def main(p=80):
    port = os.getenv('FLASK_PORT', str(p))
    addr = os.getenv('FLASK_ADDR', '0.0.0.0')
    """"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = TimedRotatingFileHandler(filename="./db/web.log",
                                       when="w0",
                                       backupCount=5)
    logger.handlers = []
    logger.addHandler(handler)

    global app
    app = CreateWallApp()

    with app.app_context():
        db = CreateWallDatabase(app)
        CreateWallAdmin(app, db)
        app.run(host=addr, port=int(port), debug=False, threaded=True)


main(5002)
